from PIL import Image
import os
import pytesseract 
import cv2 as cv
import fitz

def pdf_image(pdfPath,imgPath,zoom_x,zoom_y,rotation_angle):
  # 打开PDF文件
  pdf = fitz.open(pdfPath)
  # 逐页读取PDF
  for pg in range(0, pdf.pageCount):
    page = pdf[pg]
    # 设置缩放和旋转系数
    trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotation_angle)
    pm = page.getPixmap(matrix=trans, alpha=False)
    # 开始写图像
    pm.writePNG(imgPath+str(pg)+".png")
    #pm.writePNG(imgPath)
  pdf.close()
pdf_path ='D:/123.pdf'
img_path ='D:/123.png'
pdf_image(pdf_path,img_path,5,5,0)
# 依赖opencv
img=cv.imread(img_path)
text=pytesseract.image_to_string(Image.fromarray(img),lang='chi_tra')
# 不依赖opencv写法
# text=pytesseract.image_to_string(Image.open(img_path))
print(text)