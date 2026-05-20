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

        results = model(img, conf=0.4, verbose=False)
        detected = []

        # 模型类名 → 数据库商品名映射
        NAME_MAP = {
            "cocacola": "可口可乐", "pepsi": "百事可乐", "sprite": "雪碧",
            "fanta": "芬达", "nongfu spring": "农夫山泉", "wanglaoji": "王老吉",
            "redbull": "红牛", "mizone": "脉动", "lays": "乐事",
            "masterkong": "康师傅",
        }
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                ename = model.names[cls_id]
                name = NAME_MAP.get(ename, ename)
                if name not in detected:
                    detected.append(name)
                    print(f"  检测: {name} ({conf:.0%})")

        print(f"结果: {detected}")
        return jsonify(detected)

    except Exception as e:
        print(f"推理错误: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("AI 识别服务启动 (端口 5000)")
    app.run(host="0.0.0.0", port=5000)
