# Visión Artificial para la Clasificación de Elementos y Patrones

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green?logo=opencv&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-Procesamiento%20Matricial-013243?logo=numpy&logoColor=white)
![Evento](https://img.shields.io/badge/Exposoftware-2026-orange)
![Licencia](https://img.shields.io/badge/Licencia-MIT-lightgrey)

Sistema de visión artificial en tiempo real desarrollado en Python y OpenCV para la detección, clasificación cromática, muestreo hexadecimal y conteo automatizado de elementos por cruce de línea virtual, orientado a procesos de control de calidad industrial (**Exposoftware 2026**).

---

## Tabla de contenidos

- [Descripción general](#descripción-general)
- [Características principales](#características-principales)
- [Arquitectura y archivos del proyecto](#arquitectura-y-archivos-del-proyecto)
- [Tecnologías utilizadas](#tecnologías-utilizadas)
- [Instalación](#instalación)
- [Uso](#uso)
- [Controles interactivos](#controles-interactivos)
- [Paletas de colores soportadas](#paletas-de-colores-soportadas)
- [Autor](#autor)
- [Licencia](#licencia)

---

## Descripción general

El proyecto implementa un pipeline determinístico de procesamiento digital de imágenes sobre flujo de video en vivo (`cv2.VideoCapture` con backend `CAP_DSHOW` para inicialización rápida):

1. **Conversión de espacio de color (BGR → HSV):** Transforma cada fotograma capturado para aislar el matiz (*Hue*), la saturación (*Saturation*) y el valor (*Value*) frente a variaciones de iluminación.
2. **Umbralización dinámica segura (`limits.py`):** Calcula rangos inferiores y superiores (`hue ± 12`) evitando desbordamientos numéricos (*underflow* / *overflow*) en el espectro de `0` a `179` de OpenCV, además de manejar mediante doble máscara el envolvente del color rojo (`0–10` y `165–180`).
3. **Filtrado morfológico:** Aplica operaciones de apertura (`MORPH_OPEN`) y cierre (`MORPH_CLOSE`) con un kernel de `5×5` para eliminar ruido y consolidar regiones.
4. **Detección de contornos y centroides:** Extrae contornos externos (`RETR_EXTERNAL`), filtra objetos por área mínima (`> 5000 px²` en `_main.py` y `> 4500 px²` en `main.py`) y calcula su cuadro delimitador (*bounding box*) y centroide.
5. **Conteo por cruce de línea y telemetría HUD:** Rastrea el desplazamiento de los centroides mediante distancia euclidiana (`< 60 px`) para contabilizar cada pieza una sola vez al cruzar la línea virtual central.

---

## Características principales

- **Sistema de Control de Calidad con Conteo (`_main.py`):**
  - Detección simultánea de 6 colores industriales con selección dinámica del color objetivo a contabilizar.
  - **Línea virtual de conteo** bidireccional (izquierda ↔ derecha) con memoria de estado por ID para evitar duplicados y parpadeo visual en verde al registrar un cruce.
  - **Mira central de muestreo (`MIRA HEX`):** Calcula en tiempo real el promedio RGB/BGR de una región central de `20×20` píxeles y muestra su código hexadecimal equivalente.
  - **Panel HUD semitransparente:** Muestra FPS en vivo, color objetivo, código HEX, total de objetos contabilizados, lectura de la mira y atajos de teclado.
- **Detector Multicolor Extendido (`main.py`):**
  - Clasificación simultánea de una paleta ampliada de **16 tonalidades** con etiqueta de nombre y código HEX sobre cada objeto detectado.
- **Modo de Depuración y Captura:**
  - Alternancia instantánea entre la vista procesada y la máscara binaria HSV (`M`), además de exportación de capturas con marca de tiempo (`S`).

---

## Arquitectura y archivos del proyecto

```text
Vision-artificial-para-la-clasificacion-de-elementos-patrones/
├── _main.py      # Sistema principal de control de calidad, mira HEX y conteo por cruce de línea (6 colores)
├── main.py       # Módulo de detección y clasificación simultánea de paleta extendida (16 colores)
├── limits.py     # Función get_limits() para cálculo de rangos HSV con protección de límites (0-179)
└── README.md     # Documentación del proyecto
