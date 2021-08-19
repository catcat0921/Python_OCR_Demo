import cv2
import numpy as np
from numpy.lib.function_base import angle

def detect(image):
    # img=cv2.imread(image_name,cv2.IMREAD_GRAYSCALE)
    # img_out=cv2.imread(image_name)
    img=image
    if  img.shape[2]==3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_out=image   
    # cv2.imshow('img',img)
    # cv2.waitKey(0)
    # cv2.destroyWindow
    scale=800/img.shape[1]
    img=cv2.resize(img,(int(img.shape[1]*scale),int(img.shape[0]*scale)))

    # cv2.imshow('img1',img)
    # cv2.waitKey(0)
    # cv2.destroyWindow
    #blackhat
    kernel = np.ones((1, 3), np.uint8)
    img = cv2.morphologyEx(img, cv2.MORPH_BLACKHAT, kernel, anchor=(1, 0))

    #sogliatura
    thresh, img = cv2.threshold(img, 10, 255, cv2.THRESH_BINARY)
    #operazioni  morfologiche
    kernel = np.ones((1, 5), np.uint8) 
    img = cv2.morphologyEx(img, cv2.MORPH_DILATE, kernel, anchor=(2, 0), iterations=2) #dilatazione
    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel, anchor=(2, 0), iterations=2)  #chiusura

    kernel = np.ones((21, 35), np.uint8)
    img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel, iterations=1)
    # cv2.imshow('img1',img)
    # cv2.waitKey(0)
    # cv2.destroyWindow
    #estrazione dei componenti connessi
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    unscale = 1.0 / scale
    if contours != None:
        for contour in contours:
            
            # se l'area non è grande a sufficienza la salto 
            if cv2.contourArea(contour) <= 2000:
                continue
            
            #estraggo il rettangolo di area minima (in formato (centro_x, centro_y), (width, height), angolo)
            rect = cv2.minAreaRect(contour)
            #l'effetto della riscalatura iniziale deve essere eliminato dalle coordinate rilevate
            rect = \
                ((int(rect[0][0] * unscale), int(rect[0][1] * unscale)), \
                (int(rect[1][0] * unscale), int(rect[1][1] * unscale)), \
                rect[2])
            
            
            #disegno il tutto sull'immagine originale
            box = np.int0(cv2.boxPoints(rect))
            cv2.drawContours(img_out, [box], 0, (0, 255, 0), thickness = 2)
            
    # cv2.imshow('img1',img_out)
    # cv2.waitKey(0)
    # cv2.destroyWindow
    if  box[0][1]>img.shape[0]/2:
        rotain=180
    else:
        rotain=0
    return rotain


# detect('11010398629.png')