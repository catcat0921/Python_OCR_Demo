import cx_Oracle
import os
import shutil
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
        

copyfile()

