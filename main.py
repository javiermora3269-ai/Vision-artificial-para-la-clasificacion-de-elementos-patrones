import cv2 as cv
import numpy as np
from limits import get_limits
from PIL import Image
import time

#Diccionario con nombres y valores de los colores en BGR
colores={

    'NEGRO #191919': (25, 25, 25),
    'BLANCO #F0F0F0': (240, 240, 240),
    'GRIS #808080': (128, 128, 128),
    'ROJO #F00000': (0, 0, 240),
    'ROSA #F096C8': (200, 150, 240),
    'NARANJA #FF8C00': (0, 140, 255),
    'AMARILLO #FFE600': (0, 230, 255),
    'VERDE #00C800': (0, 200, 0),
    'VERDE OLIVA / MILITAR #5A6E1E': (30, 110, 90),
    'VERDE LIMA #32E632': (50, 230, 50),
    'TURQUESA / CIAN #00C8DC': (220, 200, 0),
    'AZUL CIELO / CELESTE #64B4EB': (235, 180, 100),
    'AZUL REY #0046E6': (230, 70, 0),
    'AZUL MARINO #001464': (100, 20, 0),
    'MORADO / VIOLETA #781482': (130, 20, 120),
    'MARRON / CAFE #7D4119': (25, 65, 125),
    

}
#Variables de rendimiento
prev_time=time.time()
show_mask_mode=False
#Filtro para limpieza del ruido 
kernel=np.ones((5,5),np.uint8)
#Aqui enl metodo CAP_SHOW AYUDA A QUE SE HABRA MAS RAPIDO LA VENTANA
cap=cv.VideoCapture(0,cv.CAP_DSHOW)
while True:
    ret,frame=cap.read()
    if not ret:
        print('No se encontro video de la camara')
        break

    #calculo de fps
    curr_time=time.time()
    fps=1/(curr_time-prev_time)if(curr_time-prev_time)>0 else 0
    prev_time=curr_time
    #Convertimos la imagen bgr a hsv con este filtro
    hsvImage=cv.cvtColor(frame,cv.COLOR_BGR2HSV)

    for nombres_colores, bgr_color in colores.items():
        if nombres_colores=='ROJO':
            # El rojo envuelve los dos extremos del 
            # espectro HSV (0-10 y 170-180)
            lower1 = np.array([0, 75, 75], dtype=np.uint8)
            upper1 = np.array([10, 255, 255], dtype=np.uint8)
            lower2 = np.array([165, 75, 75], dtype=np.uint8)
            upper2 = np.array([180, 255, 255], dtype=np.uint8)

            mask1 = cv.inRange(hsvImage, lower1, upper1)
            mask2 = cv.inRange(hsvImage, lower2, upper2)
            mask = cv.bitwise_or(mask1, mask2)
        else:
             # Para los demasd colores usamos la función dinámicamente
            lowerLimit, upperLimit = get_limits(color=bgr_color)
            #Mascarade todos los colores que queremos rastrear
            mask = cv.inRange(hsvImage, lowerLimit, upperLimit)
        #Filtrado morfologico el que se declaro arriba como el kernel
        mask=cv.morphologyEx(mask,cv.MORPH_OPEN,kernel)
        mask=cv.morphologyEx(mask,cv.MORPH_CLOSE,kernel)

         #Contornos mas cerrados
        contornos,_=cv.findContours(mask,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
        #limite de area para que no detecte cosas muy pequeñas
        for cnt in contornos:
              if cv.contourArea(cnt)>4500:
                   x,y,w,h=cv.boundingRect(cnt)

                   #Metodos para el texto y los recuadros
                   
                   cv.rectangle(frame,(x,y),(x+w,y+h),bgr_color,2)
                   cv.putText(frame,nombres_colores,(x,y-10),cv.FONT_HERSHEY_SIMPLEX,1,bgr_color,2)
    
    hud = frame.copy()
    cv.rectangle(hud, (10, 10), (270, 175), (20, 20, 20), -1)
    frame = cv.addWeighted(hud, 0.65, frame, 0.35, 0)
    # Texto en el HUD
    cv.putText(frame, f"SISTEMA VISION CV", (20, 32), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 200), 2)
    cv.putText(frame, f"FPS: {fps:.1f}", (20, 55), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)       

       
           
     # Alternar entre vista procesada y máscara binaria
    vista = cv.cvtColor(mask, cv.COLOR_GRAY2BGR) if show_mask_mode else frame
    cv.imshow('Vision Artificial - Exposoftware 2026', vista)
    key = cv.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('m'):
        show_mask_mode = not show_mask_mode
    elif key == ord('s'):
        filename = f"captura_{int(time.time())}.png"
        cv.imwrite(filename, frame)
        print(f"Captura guardada: {filename}")   


cap.release()
cv.destroyAllWindows()
