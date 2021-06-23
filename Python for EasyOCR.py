import easyocr
reader = easyocr.Reader(['ch_sim', 'en', 'ch_tra'])
result = reader.readtext('d:/test2.png')
print(result)