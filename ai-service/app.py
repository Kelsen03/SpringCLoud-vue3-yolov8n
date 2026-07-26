from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import cv2
import numpy as np
from ultralytics import YOLO

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# 加载微调后的 10 类超市商品检测模型
model_path = "best.pt"  # 云服务器上与 ai_server.py 同目录
try:
    model = YOLO(model_path)
    print(f"模型加载成功: {list(model.names.values())}")
except Exception as e:
    print(f"模型加载失败: {e}")
    model = None


@app.route("/health", methods=["GET"])
def health():
    status = "ok" if model is not None else "degraded"
    return jsonify({"status": status}), 200


@app.route("/api/detect", methods=["POST", "OPTIONS"])
def detect_objects():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json()
    if not data or "image" not in data:
        return jsonify({"error": "No image provided"}), 400

    b64 = data["image"]
    if "," in b64:
        b64 = b64.split(",")[1]

    try:
        img_bytes = base64.b64decode(b64)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return jsonify({"error": "Failed to decode image"}), 400
        if model is None:
            return jsonify({"error": "Model not loaded"}), 500

        results = model(img, conf=0.10, iou=0.6, agnostic_nms=False, verbose=False)
        detected = []

        # 模型类名 → 数据库商品名映射（精确到数据库中的商品全名）
        NAME_MAP = {
            "cocacola": "可口可乐 500ml",
            "pepsi": "百事可乐 500ml",
            "sprite": "雪碧 500ml",
            "fanta": "芬达橙味 500ml",
            "nongfu spring": "农夫山泉 550ml",
            "wanglaoji": "王老吉凉茶 310ml",
            "redbull": "红牛维生素饮料 250ml",
            "mizone": "脉动青柠味 600ml",
            "lays": "乐事原味薯片 75g",       # 默认，会被颜色分析覆盖
            "masterkong": "康师傅红烧牛肉面 103g",
        }

        # 分级置信度阈值：数据少/难识别的类用低阈值，常见类用标准阈值
        CLASS_CONF = {
            "nongfu spring": 0.12,  # 透明瓶身，难识别
            "wanglaoji": 0.15,      # 数据偏少
            "redbull": 0.20,        # 金罐反光易误识别
            "pepsi": 0.30,          # 蓝色包装易与背景混淆
            "mizone": 0.28,         # 蓝色瓶身易误识别
        }
        DEFAULT_CONF = 0.20  # 其余类标准阈值

        # 易误识别类（蓝色/红色系），需额外纹理检查
        TEXTURE_CHECK_CLASSES = {"pepsi", "redbull", "mizone"}

        def edge_density(crop):
            """Canny边缘密度：纯色背景→低，真实商品→高"""
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            return np.count_nonzero(edges) / edges.size

        def classify_lays(img, box):
            """根据乐事包装主色调区分子类：绿色→青柠味，黄色→原味"""
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            crop = img[y1:y2, x1:x2]
            if crop.size == 0:
                return NAME_MAP["lays"]
            hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
            # 绿色范围 H: 35~85
            green_mask = cv2.inRange(hsv, (35, 40, 40), (85, 255, 255))
            # 黄色/橙色范围 H: 10~35
            yellow_mask = cv2.inRange(hsv, (10, 40, 40), (35, 255, 255))
            green_ratio = np.count_nonzero(green_mask) / green_mask.size
            yellow_ratio = np.count_nonzero(yellow_mask) / yellow_mask.size
            if green_ratio > 0.05:
                print(f"    乐事颜色分析: 绿={green_ratio:.1%} 黄={yellow_ratio:.1%} → 青柠味")
                return "乐事青柠味薯片 75g"
            print(f"    乐事颜色分析: 绿={green_ratio:.1%} 黄={yellow_ratio:.1%} → 原味")
            return "乐事原味薯片 75g"

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                ename = model.names[cls_id]
                # 分级阈值过滤：难类低阈值，常见类标准阈值
                min_conf = CLASS_CONF.get(ename, DEFAULT_CONF)
                if conf < min_conf:
                    continue
                # 纹理检查：纯色背景无边缘→误检，丢弃
                if ename in TEXTURE_CHECK_CLASSES:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    crop = img[max(0,y1):y2, max(0,x1):x2]
                    if crop.size > 0 and edge_density(crop) < 0.02:
                        print(f"  跳过 {ename} 纯色误检 (边缘密度={edge_density(crop):.1%}, conf={conf:.0%})")
                        continue
                if ename == "lays":
                    name = classify_lays(img, box)
                else:
                    name = NAME_MAP.get(ename, ename)
                if name not in detected:
                    detected.append(name)
                    print(f"  检测: {name} ({conf:.0%})")

        # === 遮挡救援：检出<3个时，对未检出的类降低阈值再扫 ===
        if len(detected) < 3:
            detected_en = set()  # 已检出的英文类名
            for name in detected:
                for en, cn in NAME_MAP.items():
                    if cn == name:
                        detected_en.add(en)
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    ename = model.names[cls_id]
                    if ename in detected_en:
                        continue  # 已检出，跳过
                    # 救援阈值 = 原阈值 × 0.5
                    normal_min = CLASS_CONF.get(ename, DEFAULT_CONF)
                    rescue_min = max(normal_min * 0.5, 0.06)
                    if conf < rescue_min:
                        continue
                    # 救援模式跳过纹理检查（遮挡导致边缘减少）
                    if ename == "lays":
                        name = classify_lays(img, box)
                    else:
                        name = NAME_MAP.get(ename, ename)
                    if name not in detected:
                        detected.append(name)
                        print(f"  救援检测(遮挡): {name} ({conf:.0%})")

        print(f"结果: {detected}")
        return jsonify(detected)

    except Exception as e:
        print(f"推理错误: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("AI 识别服务启动 (端口 5000)")
    app.run(host="0.0.0.0", port=5000)
