import cv2 as cv
import numpy as np
from limits import get_limits
import time

# 1. Diccionario con nombres, valores BGR y códigos HEXADECIMALES
colores = {
    'ROJO': {
        'bgr': [0, 0, 255],
        'hex': '#FF0000'
    },
    'AZUL Rey': {
        'bgr': [255, 0, 0],
        'hex': '#0000FF'
    },
    'AZUL CLARO': {
        'bgr': [235, 206, 135],
        'hex': '#87CEEB'
    },
    'VERDE lima': {
        'bgr': [50, 205, 50],
        'hex': '#32CD32'
    },
    'VERDE': {
        'bgr': [0, 255, 0],
        'hex': '#00FF00'
    },
    'AMARILLO': {
        'bgr': [0, 255, 255],
        'hex': '#FFFF00'
    }
}

lista_nombres = list(colores.keys())
idx_color_seleccionado = 0  # Comienza rastreando el primer color (ROJO)

# Variables de conteo y seguimiento
contador_objetos = 0
objetos_rastreados = {}  # id -> [prev_x, prev_y, ya_cruzo]
siguiente_id = 0
flash_linea = 0  # Temporizador para que la línea parpadee al contar

# Variables de rendimiento
prev_time = time.time()
show_mask_mode = False
kernel = np.ones((5, 5), np.uint8)

# Captura de video
cap = cv.VideoCapture(0, cv.CAP_DSHOW)

while True:
    ret, frame = cap.read()
    if not ret:
        print('No se encontro video de la camara')
        break

    # FPS
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
    prev_time = curr_time

    alto, ancho = frame.shape[:2]
    cx, cy = ancho // 2, alto // 2
    radio = 10

    # Posición de la línea virtual de conteo
    linea_x = ancho // 2

    # Color actualmente seleccionado para contar
    nombre_objetivo = lista_nombres[idx_color_seleccionado]
    info_objetivo = colores[nombre_objetivo]

    # 2. LECTURA DE LA MIRA CENTRAL (Muestreo del color en el centro)
    zona = frame[cy - radio : cy + radio, cx - radio : cx + radio]
    b_avg, g_avg, r_avg = np.mean(zona, axis=(0, 1))
    hex_mira = f"#{int(r_avg):02X}{int(g_avg):02X}{int(b_avg):02X}"

    # 3. PROCESAMIENTO Y DETECCION DE COLORES
    hsvImage = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    mask_visual = np.zeros((alto, ancho), dtype=np.uint8)
    centroides_objetivo = []  # Almacena los centros de los objetos del color seleccionado

    for nombre_color, datos in colores.items():
        bgr_color = datos['bgr']
        hex_color = datos['hex']

        if nombre_color == 'ROJO':
            lower1 = np.array([0, 75, 75], dtype=np.uint8)
            upper1 = np.array([10, 255, 255], dtype=np.uint8)
            lower2 = np.array([165, 75, 75], dtype=np.uint8)
            upper2 = np.array([180, 255, 255], dtype=np.uint8)
            mask1 = cv.inRange(hsvImage, lower1, upper1)
            mask2 = cv.inRange(hsvImage, lower2, upper2)
            mask = cv.bitwise_or(mask1, mask2)
        else:
            lowerLimit, upperLimit = get_limits(color=bgr_color)
            mask = cv.inRange(hsvImage, lowerLimit, upperLimit)

        mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
        mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)

        # Si es el color que queremos contar, guardamos su máscara para el modo depuración
        if nombre_color == nombre_objetivo:
            mask_visual = mask

        contornos, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        for cnt in contornos:
            if cv.contourArea(cnt) > 5000:
                x, y, w, h = cv.boundingRect(cnt)
                cx_obj, cy_obj = x + w // 2, y + h // 2

                # Dibujar recuadro y etiqueta con Nombre + Hexadecimal
                cv.rectangle(frame, (x, y), (x + w, y + h), bgr_color, 2)
                etiqueta = f"{nombre_color} ({hex_color})"
                cv.putText(frame, etiqueta, (x, y - 10), cv.FONT_HERSHEY_DUPLEX, 0.6, bgr_color, 2)
                cv.circle(frame, (cx_obj, cy_obj), 4, (0, 0, 255), -1)

                # Si este contorno pertenece al color que estamos contando, lo registramos
                if nombre_color == nombre_objetivo:
                    centroides_objetivo.append((cx_obj, cy_obj))

    # 4. SISTEMA DE CONTEO POR CRUCE DE LINEA (Evita contar dos veces el mismo objeto)
    nuevos_rastreados = {}
    for (obj_x, obj_y) in centroides_objetivo:
        matched_id = None
        menor_dist = 60  # Distancia máxima para considerar que es el mismo objeto
        for obj_id, (px, py, ya_cruzo) in objetos_rastreados.items():
            dist = ((obj_x - px) ** 2 + (obj_y - py) ** 2) ** 0.5
            if dist < menor_dist:
                menor_dist = dist
                matched_id = obj_id

        if matched_id is not None:
            px, py, ya_cruzo = objetos_rastreados[matched_id]
            # Verificar si cruzó la línea (de izquierda a derecha o viceversa)
            if not ya_cruzo:
                if (px < linea_x <= obj_x) or (px > linea_x >= obj_x):
                    contador_objetos += 1
                    ya_cruzo = True
                    flash_linea = 8  # Hace parpadear la línea en verde
            nuevos_rastreados[matched_id] = [obj_x, obj_y, ya_cruzo]
        else:
            nuevos_rastreados[siguiente_id] = [obj_x, obj_y, False]
            siguiente_id += 1

    objetos_rastreados = nuevos_rastreados

    #  DIBUJAR LINEA DE CONTEO VIRTUAL
    color_linea = (0, 255, 0) if flash_linea > 0 else (0, 255, 255)
    if flash_linea > 0:
        flash_linea -= 1
    cv.line(frame, (linea_x, 0), (linea_x, alto), color_linea, 2)
    cv.putText(frame, "LINEA DE CONTEO", (linea_x + 8, 25), cv.FONT_HERSHEY_SIMPLEX, 0.5, color_linea, 1)

    #  DIBUJAR LA MIRA CENTRAL
    cv.circle(frame, (cx, cy), radio + 4, (255, 255, 255), 2)
    cv.circle(frame, (cx, cy), 2, (0, 0, 255), -1)
    cv.line(frame, (cx - 20, cy), (cx + 20, cy), (255, 255, 255), 1)
    cv.line(frame, (cx, cy - 20), (cx, cy + 20), (255, 255, 255), 1)

    # PANEL HUD INTERACTIVO (Telemetría y Controles)
    hud = frame.copy()
    cv.rectangle(hud, (10, 10), (320, 215), (20, 20, 25), -1)
    frame = cv.addWeighted(hud, 0.72, frame, 0.28, 0)

    # Textos del HUD
    cv.putText(frame, "SISTEMA CONTROL DE CALIDAD", (20, 32), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 200), 2)
    cv.putText(frame, f"FPS: {fps:.1f}", (20, 52), cv.FONT_HERSHEY_SIMPLEX, 0.42, (200, 200, 200), 1)

    # Color objetivo y su HEX
    cv.putText(frame, f"CONTANDO: {nombre_objetivo}", (20, 80), cv.FONT_HERSHEY_SIMPLEX, 0.55, info_objetivo['bgr'], 2)
    cv.putText(frame, f"HEX COLOR: {info_objetivo['hex']}", (20, 102), cv.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1)

    # Contador destacado
    cv.putText(frame, f"OBJETOS PASADOS: {contador_objetos}", (20, 130), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    # Lectura de la mira central
    cv.putText(frame, f"MIRA HEX: {hex_mira}", (20, 155), cv.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

    # Teclas de ayuda
    cv.putText(frame, "[TAB / 1-6] Cambiar Color", (20, 180), cv.FONT_HERSHEY_SIMPLEX, 0.4, (160, 160, 160), 1)
    cv.putText(frame, "[R] Reiniciar Conteo | [Q] Salir", (20, 200), cv.FONT_HERSHEY_SIMPLEX, 0.4, (160, 160, 160), 1)

    # Alternar vista
    vista = cv.cvtColor(mask_visual, cv.COLOR_GRAY2BGR) if show_mask_mode else frame
    cv.imshow('Vision Artificial - Exposoftware 2026', vista)

    key = cv.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('r'):  # Reiniciar contador a 0
        contador_objetos = 0
        objetos_rastreados.clear()
        print(">> Contador reiniciado a 0")
    elif key == 9:  # Tecla TAB: Pasar al siguiente color
        idx_color_seleccionado = (idx_color_seleccionado + 1) % len(lista_nombres)
        objetos_rastreados.clear()
        print(f">> Cambiado a: {lista_nombres[idx_color_seleccionado]}")
    elif ord('1') <= key <= ord('6'):  # Teclas 1 a 6 para elegir directamente
        idx_color_seleccionado = (key - ord('1')) % len(lista_nombres)
        objetos_rastreados.clear()
        print(f">> Cambiado a: {lista_nombres[idx_color_seleccionado]}")
    elif key == ord('m'):
        show_mask_mode = not show_mask_mode
    elif key == ord('s'):
        filename = f"captura_{int(time.time())}.png"
        cv.imwrite(filename, frame)
        print(f"Captura guardada: {filename}")

cap.release()
cv.destroyAllWindows()
