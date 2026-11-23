import numpy as np
import cv2 as cv

def get_limits(color):
    
    #Calcula los límites HSV evitando desbordamiento numérico (underflow).
   
    c = np.uint8([[color]])
    hsvC = cv.cvtColor(c, cv.COLOR_BGR2HSV)
    hue = int(hsvC[0][0][0])

    # Protegemos contra underflow/overflow en el rango de matiz HSV de OpenCV (0 a 179)
    lower_hue = max(0, hue - 12)
    upper_hue = min(179, hue + 12)

    lowerLimit = np.array([lower_hue, 80, 80], dtype=np.uint8)
    upperLimit = np.array([upper_hue, 255, 255], dtype=np.uint8)

    return lowerLimit, upperLimit
