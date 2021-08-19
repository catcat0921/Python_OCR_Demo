import cx_Oracle
#connection = cx_Oracle.connect(user="apps", password="apps",dsn="10.26.1.102:1523/R12UAT")
#connection = cx_Oracle.connect(user="apps1", password="apps1",dsn="10.26.1.91:1521/PROD")
connection = cx_Oracle.connect(user="PDF", password="pdf",dsn="LOCALHOST/XE")

cursor = connection.cursor()
#sql = 'insert into pdf.pdf_info_upload (ORDER_NUMBER,SCAN_DATE,STATUS) Values (\'11523200\',to_date(\'07-21-2021\',\'MM-DD-YYYY\'),\'OK\')'
#result=cursor.execute(sql)
#connection.commit()
#print("insert done")
#print(result)


#sql='select * from pdf.pdf_info_upload'
sql='SELECT id,customer_number,order_number,type,path,scan_date,status,path_tomcat,file_name, after_filename,apex_status, \
\'E:\\Scan\\Success\\\'||customer_number||\'\\\'||to_char(scan_date,\'YYYY\\MM\\DD\')||\'\\\'||type||\'\\\' \
FROM pdf.pdf_info_upload \
where (order_number <> \'UNKNOWN\' and customer_number <> \'UNKNOWN\') and path LIKE \'%UNKNOWN%\''

result=cursor.execute(sql)
many_data=cursor.fetchall()
print(many_data)
for row in many_data:
    #if '1105' in row:
    print('path_tomcat:'+row[7])
    print('file_name:'+row[8])
    print('after_filename:'+row[9])
    print('act_path'+row[11])
#print(len(many_data))
