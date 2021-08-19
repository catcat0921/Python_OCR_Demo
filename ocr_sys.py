from paddleocr import PaddleOCR, draw_ocr
import cv2
class OCR:
    def __init__(self):
        # need to run only once to download and load model into memory
        self.ocr = PaddleOCR(use_angle_cls=False, lang="ch",gpu_mem=1000,use_gpu=False) 
    def ocr_rec(self, img):
            ret={'cust_no':'UNKNOWN','order_no':'UNKNOWN'}
            #第一个区域的OCR
            cropImg = img[230:338, 5:476]
            result = self.ocr.ocr(cropImg, cls=False)
            result_list=[]
            if result is not None:
                for line in result:                
                    box=line[0]
                    text=line[1][0]
                    
                    #解码完整
                    if "HHK" in text :# and ('orde' in text or 'nex' in text  or 'Pls' in text):
                        result_list.append(line)
                        # logger.info(line)
                if len(result_list)==0:
                    tem1=[]
                    tem2=[]
                    for line in result:
                        box=line[0]
                        text=line[1][0]
                        if  "HHK" in text :
                            tem1.append(line)
                        if 'orde' in text or 'nex' in text  or 'Pls' in text:
                            tem2.append(line)
                    #两个都找到需要合并
                    if len(tem1)==1 and len(tem2)==1:
                        newline=[[[tem2[0][0][0][0],tem2[0][0][0][1]], 
                                    [tem1[0][0][1][0], tem1[0][0][1][1]], 
                                    [tem1[0][0][2][0], tem1[0][0][2][1]], 
                                    [tem2[0][0][3][0], tem2[0][0][3][1]]],
                                (tem2[0][1][0]+tem1[0][1][0], tem1[0][1][1])]
                        result_list.append(newline)
                        # logger.info(newline)                    

            for ocr_res in result_list:
                box=ocr_res[0]
                text=ocr_res[1][0]
                text=text.replace('O','0')
                color = (0,255,0)

                str_s= text.split('HHK')
                str_ss=filter(str.isdigit,str_s[1])
                str_r="".join(list(str_ss))
                if  str_r=='4542':
                    str_r='45421'

                ret['cust_no']='HHK'+str_r
                cv2.rectangle(img,(int(box[0][0]),int(box[0][1])+430),(int(box[2][0]),int(box[2][1])+430),color,3)
                cv2.putText(img,'HHK'+str_r,(int(box[1][0])-200,int(box[0][1])+425), cv2.FONT_HERSHEY_SIMPLEX,1,(0,100,255),2)

            #第二个区域的OCR
            cropImg = img[175:247, 635:763]
            # cv2.imshow('crop',cropImg)
            # cv2.waitKey()
            result = self.ocr.ocr(cropImg, cls=True)
            if result is not None:
                for line in result:                
                    box=line[0]
                    text=line[1][0]                
                    # logger.info(line)
                    str_ss=filter(str.isdigit,text)
                    str_r="".join(list(str_ss))
                    if  len(str_r)==11:
                        ret['order_no']=str_r
                        cv2.rectangle(img,(int(box[0][0])+1075,int(box[0][1])+285),(int(box[2][0])+1075,int(box[2][1])+285),(0,255,0),3)
                        cv2.putText(img,str_r,(int(box[1][0])-200+1075,int(box[0][1])+285), cv2.FONT_HERSHEY_SIMPLEX,1,(0,100,255),2)
                        break

            # saveimg= str.split(pdf,'\\')
            # name=saveimg[len(saveimg)-1]
            # name=name.replace("pdf", "png")
            # cv2.imwrite("ret/"+name,img)
            # cv2.imshow("OpenCV",img)
            # cv2.waitKey(0)
            return ret
    def detec_angel(self,img):
        cropImg = img[int(0):int(img.shape[0]/3), 0:int(img.shape[1])]
        cv2.imshow("crop",cropImg)
        cv2.waitKey()
        result = self.ocr.ocr(cropImg, cls=True,det=False,rec=False)
        return result
