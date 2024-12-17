from paddleocr import PaddleOCR
import math
import re

def recognize_captcha(image_path):
    """
    使用 PaddleOCR 识别验证码文本，支持中文，过滤置信度低于0.8的结果，返回数字。
    :param image_path: 验证码截图路径
    :return: 识别到的验证码中的数字字符串
    """
    print("[*] 正在进行验证码识别...")
    ocr = PaddleOCR(use_angle_cls=False, lang="ch")  # 支持中文初始化
    result = ocr.ocr(image_path, cls=True)

    texts = []
    for line in result:
        for word in line:
            confidence = word[1][1]  # 置信度分数
            if isinstance(confidence, (float, int)) and not math.isnan(confidence) and confidence >= 0.8:
                text = word[1][0]  # 文本内容
                texts.append(text)

    # 筛选出数字内容
    captcha_numbers = ''.join(re.findall(r'\d+', ''.join(texts)))
    print(f"[+] 识别到的验证码数字: {captcha_numbers}")
    return captcha_numbers