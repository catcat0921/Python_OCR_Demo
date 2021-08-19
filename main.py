from math import log
import os
import threading
import fitz
from PIL import Image
from threading import Thread
import time
from numpy.lib.arraypad import pad
from numpy.lib.utils import safe_eval
from paddleocr import PaddleOCR, draw_ocr
import cv2
import numpy as np
from ocr_sys import OCR
from my_FTP import MyFTP
import datetime
import cx_Oracle
from PyPDF2 import PdfFileMerger
from logging import handlers
import logging
from PyPDF2 import PdfFileReader, PdfFileWriter
import bar_code
import shutil
import threading

# import PdfFileMerger
logger = logging.getLogger(__name__)
log_file="./log/log.txt"
fh = handlers.TimedRotatingFileHandler(filename=log_file,when="D",interval=5,backupCount=3)

formatter = logging.Formatter("%(asctime)s : %(message)s")

fh.setFormatter(formatter)
logger.addHandler(fh)


pdf_dir = []
dir = 'PDF'


def get_file():
    docunames = os.listdir("PDF")
    for docuname in docunames:
        if os.path.splitext(docuname)[1] == '.pdf':  # 目录下包含.pdf的文件
            pdf_dir.append(docuname)


def get_filelist(dir):
    global pdf_dir

    while 1:
        print("get PDF file .........")
        total = 0
        pdf_dir = []
        for home, dirs, files in os.walk(dir):
            # for dir in dirs:
            #     # print(dir)
            for filename in files:
                fullname = os.path.join(home, filename)
                if os.path.splitext(fullname)[1] == '.pdf':  # 目录下包含.pdf的文件
                    pdf_dir.append(fullname)
                    total += 1
        print("found %i PDF file done ..........." % total)
        conver_img()
        # ocr.ocr()
        time.sleep(10)


def conver_img():

    for pdf in pdf_dir:
        doc = fitz.open(pdf)
        pdf_name = os.path.splitext(pdf)[0]
        name = os.path.split(pdf_name)
        father_path="E:\\Scan\\"
        src = os.path.join("E:\\Scan\\Temp", pdf)
##1.PDF旋转
        for pg in range(doc.pageCount):
            page = doc[pg]
            rotate = int(0)
            zoom_x = 1
            zoom_y = 1
            trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
            pm = page.getPixmap(matrix=trans, alpha=False)
            mode = "RGBA" if pm.alpha else "RGB"
            img = Image.frombytes(mode, [pm.width, pm.height], pm.samples)
            img = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
            result=bar_code.detect(img)
            # result=ocr_sys.detec_angel(img)
            makepdftemp(src,result)
            print('rotate=',result)
            logger.warning('rotate='+str(result))
            break
        doc.close()


##2.OCR识别
        doc = fitz.open('rotated.pdf')
        for pg in range(doc.pageCount):
            page = doc[pg]
            rotate = int(0)
            zoom_x = 1.5
            zoom_y = 1.5
            trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
            pm = page.getPixmap(matrix=trans, alpha=False)
            mode = "RGBA" if pm.alpha else "RGB"
            img = Image.frombytes(mode, [pm.width, pm.height], pm.samples)
            img = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
            result = ocr_sys.ocr_rec(img)
            print(result)
            logger.warning(result)
            break
        doc.close()


##3.文件保存

        filetype=getfiletype(result)

        current_path = os.path.abspath(__file__)
        PDFtemp_path = os.path.abspath(
            os.path.dirname(current_path) + os.path.sep + ".")
        src_temp = os.path.join(PDFtemp_path, 'rotated.pdf')
        

        day = time.strftime("%d", time.localtime())
        FTP_PATH = result['cust_no']+'\\'+time.strftime("%Y", time.localtime())+"\\"+time.strftime(
            "%m", time.localtime())+"\\" + time.strftime("%d", time.localtime()) + "\\"+filetype+"\\"+result['cust_no']+"_"+result['order_no']+".pdf"

        if result['cust_no']=="UNKNOWN":
            dst = os.path.join(father_path, 'Failure')
            dst = os.path.join(dst, name[1]+'.pdf')
        else:
             dst = os.path.join(father_path, 'Success')
             dst = os.path.join(dst, FTP_PATH)

        print("Ori file=",src)
        logger.warning("Ori file="+src)
        # 执行操作
        dirName, fileName = os.path.split(dst)
        if not os.path.exists(dirName):
            os.makedirs(dirName)

        #这个是存储到scan文件夹下面的    
        while 1:
            try:
                os.rename(src_temp, dst)
                print("dest file=",dst)
                logger.warning("dest file="+dst)
                break
            except Exception as e:
                # print(e)
                # fileName=os.path.splitext(fileName)[0]+'_1'+os.path.splitext(fileName)[1]
                # dst = os.path.join(dirName, fileName)
                print("appen file=",dst)
                logger.warning("appen file="+dst)
                file_lsit=[dst,src_temp]
                pdfappen(file_lsit)                
                os.remove(src_temp)
                break

        #这个是存储到tomcat文件夹下面的：
        #tomcat_file='E:\\Tomcat9\\webapps\\i\\pdf\\'+fileName #update for delete the file name in path column. zic 20210720
        tomcat_file='E:\\Tomcat9\\webapps\\i\\pdf\\'           #update for delete the file name in path column. zic 20210720
        shutil.copy(dst, tomcat_file) 
        os.remove(src)

        ORDER_NUMBER = result['order_no']
        CUSTOMER_NUMBER = result['cust_no']
        TYPE = filetype
        #PATH = dst   #update for delete the file name in path column. zic 20210720
        PATH = "E:\\Scan\\Success"+'\\'+result['cust_no']+'\\'+time.strftime("%Y", time.localtime())+"\\"+time.strftime("%m", time.localtime())+"\\" + time.strftime("%d", time.localtime())+ "\\"+filetype+"\\"
        SCAN_DATE = datetime.date.today().strftime('%Y-%m-%d')
        if  result['order_no']!='UNKNOWN' and  result['cust_no']!='UNKNOWN' and len(result['cust_no'])>=8:
            STATUS = 'OK'
        else:
            STATUS = 'NG'
        PATH_TOMCAT = tomcat_file
               
# 4 回传数据库--todo
        connection = cx_Oracle.connect(user="PDF", password="pdf",dsn="LOCALHOST/XE")
        cursor = connection.cursor()
        sql = "insert into pdf_info_upload (ORDER_NUMBER,CUSTOMER_NUMBER,TYPE,PATH,SCAN_DATE,STATUS,PATH_TOMCAT,FILE_NAME)values('" + \
            ORDER_NUMBER+"','"+CUSTOMER_NUMBER+"','"+TYPE+"','"+PATH+"',to_date('"+SCAN_DATE+"','YYYY-MM-DD'),'"+STATUS+"','"+PATH_TOMCAT+"','"+fileName+"')"
        print(sql)
        result=cursor.execute(sql)
        connection.commit()
        #many_data=cursor.fetchall()
        print(result)
    


def getfiletype(result):
    connection = cx_Oracle.connect(user="apps", password="apps",dsn="10.26.1.102:1523/R12UAT")
    cursor = connection.cursor()
    base_result=cursor.execute('Select * from pdf_order_type')
    data=cursor.fetchall()
    #print(data)
    filetype='UNKOWN'
    #data=[('HSH_GL_Manual', 4100000001, '4100', 'INVOICE'), ('HSH_FA_AF', 4200000001, '4200', 'INVOICE'), ('HSH_Costing_Doc_No', 700001, '7000', 'INVOICE'), ('HSH_GL_Costing', 710001, '7100', 'INVOICE'), ('HSH_Costing_Doc', 720001, '7200', 'INVOICE'), ('HGZ GL Doc No', 2026000001, '2026', 'INVOICE'), ('SH/TJ期初导入规则', None, None, 'INVOICE'), ('HTJ Local Standard Order', 13010000001, '1301', 'INVOICE'), ('HTJ Export Standard Order', 13020000001, '1302', 'INVOICE'), ('HTJ Consignment Order', 13030000001, '1303', 'INVOICE'), ('HTJ Local I/C Order', 13040000001, '1304', 'INVOICE'), ('HTJ Sample Order', 13050000001, '1305', 'INVOICE'), ('HTJ Replenishment Order', 13060000001, '1306', 'INVOICE'), ('HTJ Gift Order', 13070000001, '1307', 'INVOICE'), ('HTJ RMA Order', 13080000001, '1308', 'RMA'), ('HTJ Export I/C Order', 13090000001, '1309', 'INVOICE'), ('HTJ Internal Order', 13100000001, '1310', 'INVOICE'), ('HSH Local Standard Order', 12010000001, '1201', 'INVOICE'), ('HSH Export Standard Order', 12020000001, '1202', 'INVOICE'), ('HSH Consignment Order', 12030000001, '1203', 'INVOICE'), ('HSH Local I/C Order', 12040000001, '1204', 'INVOICE'), ('HSH Sample Order', 12050000001, '1205', 'INVOICE'), ('HSH Replenishment Order', 12060000001, '1206', 'INVOICE'), ('HSH Gift Order', 12070000001, '1207', 'INVOICE'), ('HSH RMA Order', 12080000001, '1208', 'RMA'), ('HSH Export I/C Order', 12090000001, '1209', 'INVOICE'), ('HSH Internal Order', 12100000001, '1210', 'INVOICE'), ('IC Export Order -HHK', 1111001001, '1111', 'INVOICE'), ('IC Export DS Order', 1111501001, '1111', 'INVOICE'), ('RMA IC Export -HHK', 1111901001, '1111', 'RMA'), ('HTJ GL Doc No', 2043000191, '2043', 'INVOICE'), ('HSH GL Doc No', 4170000191, '4170', 'INVOICE'), ('AR Receipt - HGZ', 53101684, '5310', 'INVOICE'), ('AR Transaction - HKJ', 114591935, '1145', 'INVOICE'), ('Audit Adjustment - HKJ', 1700009, '1700', 'INVOICE'), ('Expenses - HKJ', 1500047, '1500', 'INVOICE'), ('Fund Transfer - HKJ', 1302624, '1302', 'INVOICE'), ('General Journal - HHK', 21401301, '2140', 'INVOICE'), ('General Journal - HKJ', 1428171, '1428', 'INVOICE'), ('HGZ_AP_CRM', 4000069, '4000', 'INVOICE'), ('HGZ_AP_DRM', 4000036, '4000', 'INVOICE'), ('HGZ_AP_Invoice', 4000255, '4000', 'INVOICE'), ('HGZ_AP_Payments', 5000129, '5000', 'INVOICE'), ('HGZ_AR_Invoice', 1000104, '1000', 'INVOICE'), ('HGZ_AR_Receiving', 3000112, '3000', 'INVOICE'), ('HGZ_GL_Manual', 2001766, '2001', 'INVOICE'), ('HKJ AP Invoice', 8054, '8054', 'INVOICE'), ('HKJ AP Payments', 5205, '5205', 'INVOICE'), ('HKJ AR Invoice', 12599, '1259', 'INVOICE'), ('HKJ Revaluation', 433, '433', 'INVOICE'), ('HUH_GZ_EFT', 105, '105', 'INVOICE'), ('HUH_HK_EFT', 6259, '6259', 'INVOICE'), ('MTL HKJ', 11765, '1176', 'INVOICE'), ('P and A - HKJ', 1603157, '1603', 'INVOICE'), ('Payment Voucher (A) - HKJ', 1264986, '1264', 'INVOICE'), ('Payment Voucher (C) - HKJ', 1210397, '1210', 'INVOICE'), ('Receipt Voucher - HKJ', 1103560, '1103', 'INVOICE'), ('Receiving HKJ', 5767, '5767', 'INVOICE'), ('AR Receipt - HKJ', 120684638, '1206', 'INVOICE'), ('HSH Distribution Order', 12110000001, '1211', 'INVOICE'), ('HUH-HK PackSlip', 10000000, '1000', 'INVOICE'),
    # ('HGZ Consignment Order', 10030000001, '1003', 'INVOICE'), ('HGZ Export I/C Order', 10090000001, '1009', 'INVOICE'), ('HGZ Export Standard Order', 10020000001, '1002', 'INVOICE'), ('HGZ Gift Order', 10070000001, '1007', 'INVOICE'), ('HGZ Local I/C Order', 10040000001, '1004', 'INVOICE'), ('HGZ Local Standard Order', 10010000001, '1001', 'INVOICE'), ('HGZ RMA Order', 10080000001, '1008', 'RMA'), ('HGZ Replenishment Order', 10060000001, '1006', 'INVOICE'), ('HGZ Sample Order', 10050000001, '1005', 'INVOICE'), ('HHK Local Standard Order', 11010000001, '1101', 'INVOICE'), ('HHK Sales Quotation', 11020000001, '1102', 'INVOICE'), ('HHK Local Dropship Order', 11030000001, '1103', 'INVOICE'), ('HHK Export Mixed Order', 11040000001, '1104', 'INVOICE'), ('HHK Local DO MI Mixed Order', 11050000001, '1105', 'INVOICE'), ('HHK DO No-Bill Standard Order', 11060000001, '1106', 'DN'), ('HHK RMA-Local Std w Cr Order', 11070000001, '1107', 'RMA'), ('HHK RMA-Local DS w Cr Order', 11080000001, '1108', 'RMA'), ('HHK RMA-Local DOMI w Cr Order', 11090000001, '1109', 'RMA'), ('HHK RMA 畫單 w Cr Order', 11100000001, '1110', 'RMA'), ('HHK InterCo Mixed Order', 11110000001, '1111', 'INVOICE'), ('HHK DO No-Bill Order-Cleaning', 11120000001, '1112', 'DN'), ('HHK Sales Job Order', 11130000001, '1113', 'INVOICE'), ('HHK RMA-Exp. Mixed w Cr Order', 11140000001, '1114', 'RMA'), ('HHK Local Dropship Order-TM', 11150000001, '1115', 'INVOICE'), ('HHK Export DO No-Bill Order', 11160000001, '1116', 'DN'), ('HHK Local Mcdonald Order', 11170000001, '1117', 'INVOICE'), ('HHK DO No-Bill Promo Order', 11180000001, '1118', 'DN'), ('HHK HK DropShip Order', 11190000001, '1119', 'INVOICE'), ('HHK RMA-Dropship w Cr Order', 11200000001, '1120', 'RMA'), ('HHK BWH DO No-Bill Order', 11210000001, '1121', 'DN'), ('HSH_Manual_GL', 400001, '4000', 'INVOICE'), ('HTJ_Manual_GL', 400001, '4000', 'INVOICE'), ('HTJ_AP_Pre', 1100000001, '1100', 'INVOICE'), ('HTJ_AP_KR', 1200000001, '1200', 'INVOICE'), ('HTJ_AP_Invoice', 1300000001, '1300', 'INVOICE'), ('HTJ_AP_Payments', 1400000001, '1400', 'INVOICE'), ('HTJ_AR_Invoice', 2100000001, '2100', 'INVOICE'), ('HTJ_AR_Receiving', 2200000001, '2200', 'INVOICE'), ('HTJ_FA_AF', 4200000001, '4200', 'INVOICE'), ('HTJ_GL_Manual', 4100000001, '4100', 'INVOICE'), ('HSH_AP_Pre', 1100000001, '1100', 'INVOICE'), ('HSH_AP_KR', 1200000001, '1200', 'INVOICE'), ('HSH_AP_Invoice', 1300000001, '1300', 'INVOICE'), ('HSH_AP_Payments', 1400000001, '1400', 'INVOICE'), ('HSH_AR_Invoice', 2100000001, '2100', 'INVOICE'), ('HSH_AR_Receiving', 2200000001, '2200', 'INVOICE'), ('HGZ Sales Reference Order', 20010000001, '2001', 'INVOICE'), ('HSH Local Dropship Order', 12120000001, '1212', 'INVOICE'), ('TJ_Costing_Doc_No', 8700000001, '8700', 'INVOICE'), ('HGZ Management Adj', 8500001, '8500', 'INVOICE'), ('HSH Management Adj', 10300001, '1030', 'INVOICE'), ('HTJ Management Adj', 10400001, '1040', 'INVOICE'), ('期初导入编码规则', None, None, 'INVOICE'), ('HGZ Internal Order', 10100000001, '1010', 'INVOICE'), ('HHK Management Adj', 1, '1', 'INVOICE'), ('SHA GL Doc No', 4170010011, '4170', 'INVOICE'), ('HHK HK DropShip Order TJ', 11220000001, '1122', 'INVOICE')]
    for row_data in data:
        if result['order_no'][0:4]  in row_data:
            filetype=row_data[3]
            print("fiele is",row_data[3])
    return filetype

def pdfappen(pdf_lst):
    file_merger = PdfFileMerger()
    for pdf in pdf_lst:
        file_merger.append(pdf)     
    file_merger.write('temp.pdf')
    file_merger.close()
    os.remove(pdf_lst[0])
    os.rename('temp.pdf', pdf_lst[0])


def makepdftemp(src,angle):
    # 用pypdf2旋转PDF某一页
    pdf_reader = PdfFileReader(src)
    pdf_writer = PdfFileWriter()
    # 顺时针旋转90度  90的倍数
    ss=angle
    page = pdf_reader.getPage(0).rotateClockwise(int(ss))
    pdf_writer.addPage(page)
    with open('rotated.pdf', 'wb') as f:
        pdf_writer.write(f)

def copyfile():
    connection = cx_Oracle.connect(user="PDF", password="pdf",dsn="LOCALHOST/XE")
    cursor = connection.cursor()
    sql='SELECT id,customer_number,order_number,type,path,scan_date,status,path_tomcat,file_name, after_filename,apex_status, \
    \'E:\\Scan\\Success\\\'||customer_number||\'\\\'||to_char(scan_date,\'YYYY\\MM\\DD\')||\'\\\'||type||\'\\\' \
    FROM pdf.pdf_info_upload \
    where (order_number <> \'UNKNOWN\' and customer_number <> \'UNKNOWN\') and path LIKE \'%UNKNOWN%\' and status=\'NG\''
    result=cursor.execute(sql)
    many_data=cursor.fetchall()
    for file_name in many_data:
        src_file=file_name[7]+file_name[8]
        dest_path=file_name[11]
        dest_file=file_name[9]

        # 1.判断文件是不是存在
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        
        if not os.path.exists(src_file):
            print("file not found")
            sql='UPDATE pdf.pdf_info_upload SET STATUS=\'OK\' WHERE ID='+str(file_name[0])
            print(sql)
            result=cursor.execute(sql)
            connection.commit()
            continue
        #2.复制文件
        shutil.copy(src_file, dest_path+dest_file)
        print("copy file")

        #3.update database
        sql='UPDATE pdf.pdf_info_upload SET STATUS=\'OK\',path=\''+dest_path+'\' WHERE ID='+str(file_name[0])
        print(sql)
        result=cursor.execute(sql)
        connection.commit()
    cursor.close()
    connection.close()

def de_file():
    while 1:
        print("check database and copy file")
        copyfile()
        time.sleep(20)
        
    
if __name__ == '__main__':
    #copyfile()
    thread1 = threading.Thread(target=de_file)
    thread1.start()
    ocr_sys = OCR()
    get_filelist('E:/Scan/Temp')  #"E:/Scan/Temp"
