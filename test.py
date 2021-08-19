from paddleocr import PaddleOCR, draw_ocr
ocr = PaddleOCR(use_angle_cls=True, lang="ch")
img_path = 'E:/OCR_SYS/test.JPG'
result = ocr.ocr(img_path, cls=True)
for line in result:
    print(line)
