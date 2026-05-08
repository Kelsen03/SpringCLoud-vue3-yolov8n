from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import base64
import cv2
import numpy as np
from ultralytics import YOLO

app = Flask(__name__)
# 允许跨域请求
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# ---------------------------------------------------------
# 1. 加载 YOLO 模型 (放弃耗内存的 OCR，改用轻量级 OpenCV 色彩分析)
# ---------------------------------------------------------
try:
    print("正在加载 YOLO 模型...")
    model = YOLO('yolov8n.pt')
    print("YOLO 模型加载成功！(内存占用 < 200MB)")
except Exception as e:
    print(f"模型加载失败: {e}")
    model = None

# =========================================================
# 定义一个轻量级的颜色分析函数
# =========================================================
def analyze_bottle_color(bottle_img):
    """
    将瓶子的图片转换到 HSV 颜色空间，统计红色、绿色、透明/白色的像素点比例，
    从而判断是可口可乐(红)、雪碧(绿)还是农夫山泉(透明/红盖)。
    """
    # 转为 HSV 格式更容易判断颜色
    hsv = cv2.cvtColor(bottle_img, cv2.COLOR_BGR2HSV)
    
    # 定义红色的范围 (HSV里红色分布在两头)
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    
    # 定义绿色的范围 (雪碧)
    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])

    # 生成掩码 (Mask)，也就是把符合这些颜色的像素抠出来
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)
    
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    
    # 计算红绿像素的占比
    total_pixels = bottle_img.shape[0] * bottle_img.shape[1]
    red_ratio = cv2.countNonZero(mask_red) / total_pixels
    green_ratio = cv2.countNonZero(mask_green) / total_pixels
    
    print(f"🎨 颜色分析: 红色占比={red_ratio:.2%}, 绿色占比={green_ratio:.2%}")
    
    # 简单的决策树逻辑
    if red_ratio > 0.15:  # 如果红色面积超过 15%，认为是可口可乐
        return "可口可乐 500ml"
    elif green_ratio > 0.15: # 如果绿色面积超过 15%，认为是雪碧
        return "雪碧 500ml"
    else:
        # 既不红也不绿，大概率是农夫山泉
        return "农夫山泉 550ml"

@app.route('/api/detect', methods=['POST', 'OPTIONS'])
def detect_objects():
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({"error": "No image provided"}), 400

    base64_image = data['image']
    
    try:
        # ---------------------------------------------------------
        # 2. 将前端传来的 Base64 字符串解码并转换为 OpenCV 图像格式 (numpy array)
        # ---------------------------------------------------------
        # 移除 base64 头部 (例如: data:image/jpeg;base64,)
        if "," in base64_image:
            base64_image = base64_image.split(",")[1]
            
        image_bytes = base64.b64decode(base64_image)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
             return jsonify({"error": "Failed to decode image"}), 400
             
        if model is None:
             return jsonify({"error": "AI Model not loaded"}), 500

        # ---------------------------------------------------------
        # 3. 使用 YOLO 进行真实推理 (Inference)
        # ---------------------------------------------------------
        print("开始进行 YOLO 识别推理...")
        results = model.predict(source=img, conf=0.5, save=False) # conf=0.5 表示只保留置信度大于50%的结果

        detected_keywords = []
        
        # ---------------------------------------------------------
        # 4. 解析推理结果并引入 OCR (文字识别)
        # ---------------------------------------------------------
        
        # 毕业答辩保留的后备映射
        demo_mapping = {
            "cell phone": "手机",
            "apple": "苹果",
            "banana": "香蕉"
        }

        for result in results:
            boxes = result.boxes  
            for box in boxes:
                class_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                raw_class_name = model.names[class_id]
                
                # ==== 方案B：轻量级颜色分析法 (不占内存) ====
                if raw_class_name == "bottle":
                    # 1. 裁剪瓶子区域
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    bottle_img = img[y1:y2, x1:x2]
                    
                    # 2. 调用 OpenCV 色彩分析函数判断具体是哪款饮料
                    class_name = analyze_bottle_color(bottle_img)
                else:
                    # 如果不是瓶子，就用普通的映射
                    class_name = demo_mapping.get(raw_class_name, raw_class_name)
                
                # 将识别到的物体名称加入列表
                if class_name not in detected_keywords:
                    detected_keywords.append(class_name)
                    print(f"-> 最终识别: {class_name} (YOLO置信度: {conf:.2f})")

        print(f"AI 识别完成！提取到的最终关键词：{detected_keywords}")
        
        # ---------------------------------------------------------
        # 5. 企业级：数据飞轮 (主动学习/数据收集)
        # 将低置信度的图片或者特定图片保存下来，用于未来二次训练
        # ---------------------------------------------------------
        # if len(detected_keywords) == 0 or (boxes and float(boxes[0].conf[0].item()) < 0.6):
        #     timestamp = int(time.time())
        #     cv2.imwrite(f"./dataset/unrecognized/img_{timestamp}.jpg", img)
        #     print("⚠️ 置信度较低或未识别，已保存图片用于未来 AI 迭代训练！")

        return jsonify(detected_keywords)

    except Exception as e:
        print(f"推理过程中发生错误: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 YOLO 企业级智能识别服务已启动 (运行在 5000 端口)...")
    app.run(host='0.0.0.0', port=5000)
