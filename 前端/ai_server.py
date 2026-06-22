from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import cv2
import numpy as np
import onnxruntime as ort

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# ===================== 模型加载 =====================
MODEL_PATH = "best.onnx"
CLASS_NAMES = ['cocacola', 'fanta', 'lays', 'masterkong', 'mizone',
               'nongfu spring', 'pepsi', 'redbull', 'sprite', 'wanglaoji']

session = None
try:
    session = ort.InferenceSession(MODEL_PATH, providers=['CPUExecutionProvider'])
    print(f"ONNX 模型加载成功: {CLASS_NAMES}")
except Exception as e:
    print(f"ONNX 加载失败: {e}")
    # 回退 PyTorch
    try:
        from ultralytics import YOLO
        pt_model = YOLO("best.pt")
        print(f"PyTorch 回退加载成功: {list(pt_model.names.values())}")
    except:
        pt_model = None

# ===================== 预处理 =====================
def letterbox(img, new_shape=640, color=(114, 114, 114)):
    """等比例缩放+填充，保持长宽比"""
    h, w = img.shape[:2]
    r = min(new_shape / h, new_shape / w)
    new_h, new_w = int(h * r), int(w * r)
    # 缩放
    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    # 填充到 640x640
    dw = (new_shape - new_w) // 2
    dh = (new_shape - new_h) // 2
    padded = cv2.copyMakeBorder(resized, dh, new_shape - new_h - dh,
                                dw, new_shape - new_w - dw,
                                cv2.BORDER_CONSTANT, value=color)
    return padded, r, (dw, dh)

def preprocess(img):
    """预处理：resize + normalize + CHW"""
    img_padded, ratio, (dw, dh) = letterbox(img, 640)
    # BGR → RGB, HWC → CHW, /255
    blob = img_padded[:, :, ::-1].transpose(2, 0, 1).astype(np.float32) / 255.0
    blob = np.expand_dims(blob, axis=0)
    return blob, ratio, (dw, dh)

# ===================== 后处理 =====================
def postprocess(output, ratio, pad, img_shape, conf_threshold=0.10, iou_threshold=0.6):
    """解析 ONNX 输出，NMS，返回 [(cls_id, conf, xyxy), ...]"""
    # output shape: (1, 14, 8400) → transpose to (8400, 14)
    preds = output[0].transpose()  # (8400, 14)

    boxes_raw = preds[:, :4]  # cx, cy, w, h (归一化到640)
    scores = preds[:, 4:]      # 10类置信度

    # 每个预测取最高分类分
    class_ids = scores.argmax(axis=1)
    confs = scores.max(axis=1)

    # 过滤低置信度
    mask = confs > conf_threshold
    boxes_raw = boxes_raw[mask]
    confs = confs[mask]
    class_ids = class_ids[mask]

    if len(boxes_raw) == 0:
        return []

    # cx,cy,w,h → xyxy (640坐标系)
    cx, cy, w, h = boxes_raw[:, 0], boxes_raw[:, 1], boxes_raw[:, 2], boxes_raw[:, 3]
    x1 = cx - w / 2
    y1 = cy - h / 2
    x2 = cx + w / 2
    y2 = cy + h / 2

    # 去除 padding，缩回原图坐标
    dw, dh = pad
    r = ratio
    x1 = (x1 - dw) / r
    y1 = (y1 - dh) / r
    x2 = (x2 - dw) / r
    y2 = (y2 - dh) / r

    # 裁剪到图片边界
    h_img, w_img = img_shape
    x1 = np.clip(x1, 0, w_img)
    y1 = np.clip(y1, 0, h_img)
    x2 = np.clip(x2, 0, w_img)
    y2 = np.clip(y2, 0, h_img)

    # 过滤无效框
    valid = (x2 > x1) & (y2 > y1)
    boxes = np.stack([x1, y1, x2, y2], axis=1)[valid]
    confs = confs[valid]
    class_ids = class_ids[valid]

    if len(boxes) == 0:
        return []

    # NMS（按类分别做）
    results = []
    for cls in np.unique(class_ids):
        idx = np.where(class_ids == cls)[0]
        cls_boxes = boxes[idx]
        cls_confs = confs[idx]

        nms_idx = cv2.dnn.NMSBoxes(
            cls_boxes.tolist(), cls_confs.tolist(),
            conf_threshold, iou_threshold
        )
        if len(nms_idx) > 0:
            for i in nms_idx.flatten():
                results.append((int(cls), float(cls_confs[i]), cls_boxes[i].tolist()))

    results.sort(key=lambda x: x[1], reverse=True)
    return results

# ===================== 辅助函数 =====================
def edge_density(crop):
    """Canny边缘密度：纯色背景→低，真实商品→高"""
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    return np.count_nonzero(edges) / edges.size

def classify_lays(img, box_xyxy, default_name):
    """根据乐事包装主色调区分子类"""
    x1, y1, x2, y2 = map(int, box_xyxy)
    crop = img[y1:y2, x1:x2]
    if crop.size == 0:
        return default_name
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    green_mask = cv2.inRange(hsv, (35, 40, 40), (85, 255, 255))
    yellow_mask = cv2.inRange(hsv, (10, 40, 40), (35, 255, 255))
    green_ratio = np.count_nonzero(green_mask) / green_mask.size
    yellow_ratio = np.count_nonzero(yellow_mask) / yellow_mask.size
    if green_ratio > 0.05:
        print(f"    乐事颜色分析: 绿={green_ratio:.1%} 黄={yellow_ratio:.1%} → 青柠味")
        return "乐事青柠味薯片 75g"
    print(f"    乐事颜色分析: 绿={green_ratio:.1%} 黄={yellow_ratio:.1%} → 原味")
    return "乐事原味薯片 75g"


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

        # ===== 推理 =====
        if session is not None:
            # ONNX 推理
            blob, ratio, pad = preprocess(img)
            output = session.run(None, {'images': blob})
            detections = postprocess(output, ratio, pad, img.shape[:2])
        elif pt_model is not None:
            # PyTorch 回退
            from ultralytics.engine.results import Results
            results = pt_model(img, conf=0.10, iou=0.6, agnostic_nms=False, verbose=False)
            detections = []
            for r in results:
                for box in r.boxes:
                    detections.append((
                        int(box.cls[0]),
                        float(box.conf[0]),
                        box.xyxy[0].tolist()
                    ))
        else:
            return jsonify({"error": "Model not loaded"}), 500

        detected = []

        NAME_MAP = {
            "cocacola": "可口可乐 500ml",
            "pepsi": "百事可乐 500ml",
            "sprite": "雪碧 500ml",
            "fanta": "芬达橙味 500ml",
            "nongfu spring": "农夫山泉 550ml",
            "wanglaoji": "王老吉凉茶 310ml",
            "redbull": "红牛维生素饮料 250ml",
            "mizone": "脉动青柠味 600ml",
            "lays": "乐事原味薯片 75g",
            "masterkong": "康师傅红烧牛肉面 103g",
        }

        # F1-最优置信度阈值（验证集234张图校准）
        CLASS_CONF = {
            "cocacola": 0.68,        # 模型极其自信，严格过滤
            "masterkong": 0.72,       # 特征明显，误检少
            "mizone": 0.78,           # 蓝色瓶身需严格过滤
            "lays": 0.61,             # 包装特征丰富
            "wanglaoji": 0.47,        # 数据量恢复后提升
            "nongfu spring": 0.45,    # v5模型大幅改善
            "fanta": 0.43,            # 橙色瓶身特征明显
            "sprite": 0.40,           # 绿色瓶身特征明显
            "redbull": 0.33,          # 金罐特征稳定
        }
        DEFAULT_CONF = 0.20
        TEXTURE_CHECK_CLASSES = {"pepsi", "redbull", "mizone"}

        # === 第一轮检测 ===
        for cls_id, conf, xyxy in detections:
            ename = CLASS_NAMES[cls_id]
            min_conf = CLASS_CONF.get(ename, DEFAULT_CONF)
            if conf < min_conf:
                continue
            # 纹理检查
            if ename in TEXTURE_CHECK_CLASSES:
                x1, y1, x2, y2 = map(int, xyxy)
                crop = img[max(0, y1):y2, max(0, x1):x2]
                if crop.size > 0 and edge_density(crop) < 0.02:
                    print(f"  跳过 {ename} 纯色误检 (边缘密度={edge_density(crop):.1%}, conf={conf:.0%})")
                    continue
            if ename == "lays":
                name = classify_lays(img, xyxy, NAME_MAP["lays"])
            else:
                name = NAME_MAP.get(ename, ename)
            if name not in detected:
                detected.append(name)
                print(f"  检测: {name} ({conf:.0%})")

        # === 遮挡救援 ===
        if len(detected) < 3:
            detected_en = set()
            for name in detected:
                for en, cn in NAME_MAP.items():
                    if cn == name:
                        detected_en.add(en)
            for cls_id, conf, xyxy in detections:
                ename = CLASS_NAMES[cls_id]
                if ename in detected_en:
                    continue
                normal_min = CLASS_CONF.get(ename, DEFAULT_CONF)
                rescue_min = max(normal_min * 0.5, 0.06)
                if conf < rescue_min:
                    continue
                if ename == "lays":
                    name = classify_lays(img, xyxy, NAME_MAP["lays"])
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
    print("AI 识别服务启动 (端口 5000, ONNX模式)")
    app.run(host="0.0.0.0", port=5000)
