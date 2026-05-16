from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import base64
import cv2
import numpy as np
from ultralytics import YOLO

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# 1. 加载 YOLOv8n 模型（~3.2M 参数，内存 <200MB）
try:
    print("正在加载 YOLO 模型...")
    model = YOLO('yolov8n.pt')
    print("YOLO 模型加载成功")
except Exception as e:
    print(f"模型加载失败: {e}")
    model = None

# ============================================================
# 2. COCO 超市商品映射（YOLO 80类 → 中文商品名）
# ============================================================
SUPERMARKET_MAP = {
    # 水果饮品（必须与数据库 product_import.sql 中的商品名匹配）
    "apple": "苹果", "orange": "橙",
    "banana": "香蕉", "carrot": "胡萝卜",
    # 烘焙
    "cake": "蛋糕", "donut": "面包", "sandwich": "面包",
    "pizza": "披萨", "hot dog": "热狗",
    # 饮料(bottle单独颜色分析)
    "bottle": None, "cup": "杯子",
    "wine glass": "酒杯",
    # 零食
    "broccoli": "蔬菜",
    # 日杂
    "cell phone": "手机", "book": "书",
    "backpack": "包", "umbrella": "伞",
    "scissors": "剪刀", "clock": "钟",
    "keyboard": "键盘", "mouse": "鼠标",
    "toothbrush": "牙刷",
    # 宠物(暂不映射到商品)
    "cat": None, "dog": None, "bird": None,
    "person": None,
}

# ============================================================
# 3. 饮料颜色分析扩展版（支持更多饮料）
# ============================================================
def analyze_bottle_color(bottle_img):
    hsv = cv2.cvtColor(bottle_img, cv2.COLOR_BGR2HSV)
    total = bottle_img.shape[0] * bottle_img.shape[1]

    # 红色（可口可乐）
    r1 = cv2.inRange(hsv, np.array([0, 50, 50]), np.array([10, 255, 255]))
    r2 = cv2.inRange(hsv, np.array([170, 50, 50]), np.array([180, 255, 255]))
    red_ratio = cv2.countNonZero(cv2.bitwise_or(r1, r2)) / total

    # 绿色（雪碧）
    g = cv2.inRange(hsv, np.array([35, 50, 50]), np.array([85, 255, 255]))
    green_ratio = cv2.countNonZero(g) / total

    # 橙色（芬达）
    o = cv2.inRange(hsv, np.array([11, 50, 50]), np.array([25, 255, 255]))
    orange_ratio = cv2.countNonZero(o) / total

    # 黄色（维他柠檬茶/佳得乐）
    y = cv2.inRange(hsv, np.array([26, 50, 50]), np.array([34, 255, 255]))
    yellow_ratio = cv2.countNonZero(y) / total

    # 蓝色（百事/百岁山）
    b = cv2.inRange(hsv, np.array([100, 50, 50]), np.array([130, 255, 255]))
    blue_ratio = cv2.countNonZero(b) / total

    # 棕色（茶类：东方树叶/三得利乌龙茶）
    br = cv2.inRange(hsv, np.array([10, 20, 20]), np.array([30, 200, 150]))
    brown_ratio = cv2.countNonZero(br) / total

    print(f"色彩分析: 红{red_ratio:.1%} 绿{green_ratio:.1%} 橙{orange_ratio:.1%} 黄{yellow_ratio:.1%} 蓝{blue_ratio:.1%} 棕{brown_ratio:.1%}")

    # 决策树（按占比从高到低）
    if red_ratio > 0.12:       return "可口可乐 500ml"
    if green_ratio > 0.12:     return "雪碧 500ml"
    if orange_ratio > 0.12:    return "芬达橙味 500ml"
    if yellow_ratio > 0.10:    return "维他柠檬茶 250ml"
    if blue_ratio > 0.12:      return "百事可乐 500ml"
    if brown_ratio > 0.10:     return "东方树叶茉莉花茶 500ml"
    return "农夫山泉 550ml"


@app.route('/api/detect', methods=['POST', 'OPTIONS'])
def detect_objects():
    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({"error": "No image provided"}), 400

    b64 = data['image']
    if "," in b64:
        b64 = b64.split(",")[1]

    try:
        img_bytes = base64.b64decode(b64)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return jsonify({"error": "Failed to decode image"}), 400
        if model is None:
            return jsonify({"error": "AI Model not loaded"}), 500

        print("YOLO 推理中...")
        results = model.predict(source=img, conf=0.35, save=False)

        detected = []

        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                raw = model.names[cls_id]

                # 跳过无关类别
                if raw == "person":
                    continue

                # bottle 走颜色分析
                if raw == "bottle":
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    crop = img[y1:y2, x1:x2]
                    if crop.size > 0:
                        name = analyze_bottle_color(crop)
                    else:
                        continue
                else:
                    name = SUPERMARKET_MAP.get(raw)
                    if name is None:
                        continue  # 跳过不在映射中的

                if name not in detected:
                    detected.append(name)
                    print(f"  识别: {name} (YOLO:{raw} {conf:.0%})")

        print(f"结果: {detected}")
        return jsonify(detected)

    except Exception as e:
        print(f"推理错误: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("AI 识别服务启动 (端口5000)")
    app.run(host='0.0.0.0', port=5000)
