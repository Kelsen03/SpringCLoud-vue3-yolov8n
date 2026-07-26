from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import cv2
import numpy as np
import onnxruntime as ort

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# ============================================================
# 类名映射（顺序必须与训练时的 names 一致！）
# ============================================================
CLASS_NAMES_EN = [
    "cocacola", "pepsi", "sprite", "fanta",
    "nongfu spring", "wanglaoji", "redbull", "mizone",
    "lays", "masterkong",
]

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

CLASS_CONF = {
    "nongfu spring": 0.12,
    "wanglaoji": 0.15,
    "redbull": 0.20,
    "pepsi": 0.30,
    "mizone": 0.28,
}
DEFAULT_CONF = 0.20
TEXTURE_CHECK_CLASSES = {"pepsi", "redbull", "mizone"}

# ============================================================
# 加载 ONNX 模型
# ============================================================
session = None
try:
    session = ort.InferenceSession("best.onnx",
        providers=['CPUExecutionProvider'])
    input_name = session.get_inputs()[0].name
    input_shape = session.get_inputs()[0].shape  # [1,3,H,W]
    IMG_SIZE = input_shape[2]
    print(f"ONNX 模型加载成功: input={input_shape}")
except Exception as e:
    print(f"模型加载失败: {e}")


def letterbox(img, new_shape=640, color=(114, 114, 114)):
    """等比缩放 + 填充"""
    shape = img.shape[:2]
    r = min(new_shape / shape[0], new_shape / shape[1])
    new_unpad = (int(round(shape[1] * r)), int(round(shape[0] * r)))
    dw, dh = new_shape - new_unpad[0], new_shape - new_unpad[1]
    dw, dh = dw // 2, dh // 2
    img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = dh, new_shape - new_unpad[1] - dh
    left, right = dw, new_shape - new_unpad[0] - dw
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
    return img, r, (dw, dh)


def edge_density(crop):
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    return np.count_nonzero(edges) / edges.size


def classify_lays(img, box):
    x1, y1, x2, y2 = map(int, box[:4])
    crop = img[y1:y2, x1:x2]
    if crop.size == 0:
        return NAME_MAP["lays"]
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    green_mask = cv2.inRange(hsv, (35, 40, 40), (85, 255, 255))
    yellow_mask = cv2.inRange(hsv, (10, 40, 40), (35, 255, 255))
    green_ratio = np.count_nonzero(green_mask) / green_mask.size
    yellow_ratio = np.count_nonzero(yellow_mask) / yellow_mask.size
    if green_ratio > 0.05:
        return "乐事青柠味薯片 75g"
    return "乐事原味薯片 75g"


def process_results(output, img_h, img_w, ratio, pad):
    """
    解析 ONNX 输出 [1, 4+num_classes, num_boxes]
    返回 list of (x1,y1,x2,y2, conf, ename)
    """
    num_classes = len(CLASS_NAMES_EN)
    output = output[0]  # [4+num_classes, num_boxes]
    bboxes_raw = output[:4, :]  # [4, N] — cx, cy, w, h
    scores = output[4:4+num_classes, :]  # [num_classes, N]

    # 转 xyxy（相对于模型输入尺寸 640x640）
    cx, cy, w, h = bboxes_raw[0], bboxes_raw[1], bboxes_raw[2], bboxes_raw[3]
    x1 = cx - w / 2
    y1 = cy - h / 2
    x2 = cx + w / 2
    y2 = cy + h / 2

    # 每框取最高分类分
    class_ids = np.argmax(scores, axis=0)
    confidences = np.max(scores, axis=0)

    # 缩放回原图
    # 1. 先还原 letterbox 填充
    x1 = (x1 - pad[0]) / ratio
    y1 = (y1 - pad[1]) / ratio
    x2 = (x2 - pad[0]) / ratio
    y2 = (y2 - pad[1]) / ratio

    # 2. 裁剪到原图范围
    x1 = np.clip(x1, 0, img_w)
    y1 = np.clip(y1, 0, img_h)
    x2 = np.clip(x2, 0, img_w)
    y2 = np.clip(y2, 0, img_h)

    # NMS
    boxes_list = np.stack([x1, y1, x2, y2], axis=1)
    indices = cv2.dnn.NMSBoxes(
        boxes_list.tolist(),
        confidences.tolist(),
        score_threshold=0.05,
        nms_threshold=0.6,
    )
    if len(indices) == 0:
        return []

    results = []
    for idx in indices.flatten():
        results.append((
            float(x1[idx]), float(y1[idx]), float(x2[idx]), float(y2[idx]),
            float(confidences[idx]),
            CLASS_NAMES_EN[int(class_ids[idx])],
            boxes_list[idx],  # full box for crop
        ))
    return results


@app.route("/health", methods=["GET"])
def health():
    status = "ok" if session is not None else "degraded"
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
        if session is None:
            return jsonify({"error": "Model not loaded"}), 500

        h, w = img.shape[:2]

        # 预处理 — letterbox + normalize + CHW + batch
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_lb, ratio, pad = letterbox(img_rgb, IMG_SIZE)
        img_norm = img_lb.astype(np.float32) / 255.0
        img_chw = np.transpose(img_norm, (2, 0, 1))
        img_batch = np.expand_dims(img_chw, 0)

        # 推理
        outputs = session.run(None, {input_name: img_batch})
        dets = process_results(outputs[0], h, w, ratio, pad)

        detected = []
        for x1, y1, x2, y2, conf, ename, box_arr in dets:
            min_conf = CLASS_CONF.get(ename, DEFAULT_CONF)
            if conf < min_conf:
                continue

            # 纹理检查
            if ename in TEXTURE_CHECK_CLASSES:
                bx1, by1, bx2, by2 = map(int, [x1, y1, x2, y2])
                crop = img[max(0, by1):by2, max(0, bx1):bx2]
                if crop.size > 0 and edge_density(crop) < 0.02:
                    continue

            if ename == "lays":
                name = classify_lays(img, (x1, y1, x2, y2))
            else:
                name = NAME_MAP.get(ename, ename)

            if name not in detected:
                detected.append(name)
                print(f"  检测: {name} ({conf:.0%})")

        # 遮挡救援
        if len(detected) < 3:
            detected_en = set()
            for name in detected:
                for en, cn in NAME_MAP.items():
                    if cn == name:
                        detected_en.add(en)

            for x1, y1, x2, y2, conf, ename, box_arr in dets:
                if ename in detected_en:
                    continue
                normal_min = CLASS_CONF.get(ename, DEFAULT_CONF)
                rescue_min = max(normal_min * 0.5, 0.06)
                if conf < rescue_min:
                    continue
                if ename == "lays":
                    name = classify_lays(img, (x1, y1, x2, y2))
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
    print("AI 识别服务启动 (ONNX Runtime, 端口 5000)")
    app.run(host="0.0.0.0", port=5000)
