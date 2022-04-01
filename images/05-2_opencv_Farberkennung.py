import numpy as np
import cv2 as cv

# Farberkennung mit Bild
# https://de.wikipedia.org/wiki/HSV-Farbraum
# https://alloyui.com/examples/color-picker/hsv.html
# Varibalen
max_value_H = 360
max_value_S = 100
max_value_V = 100
low_H = 0
low_S = 0
low_V = 0
high_H = max_value_H
high_S = max_value_S
high_V = max_value_V
# Namen für Fenster
parameter_window_name = "Parameter"
low_H_name = 'Low H'
low_S_name = 'Low S'
low_V_name = 'Low V'
high_H_name = 'High H'
high_S_name = 'High S'
high_V_name = 'High V'

# Normalisierung für Trackbar Werte
def normalize(value, value_max, norm_max):
    return value * norm_max / value_max

# --- Trackbar Funktionen bei Wert Änderung ---
def on_low_H_thresh_trackbar(val):
    global low_H
    global high_H
    low_H = int(normalize(val, max_value_H, max_value_H//2))
    if low_H >= high_H:
        low_H = high_H - 1
        cv.setTrackbarPos(low_H_name, parameter_window_name, int(normalize(low_H, max_value_H//2, max_value_H)))

def on_high_H_thresh_trackbar(val):
    global low_H
    global high_H
    high_H = int(normalize(val, max_value_H, max_value_H//2))
    if low_H >= high_H:
        high_H = low_H + 1
        cv.setTrackbarPos(high_H_name, parameter_window_name, int(normalize(high_H, max_value_H//2, max_value_H)))

def on_low_S_thresh_trackbar(val):
    global low_S
    global high_S
    low_S = int(normalize(val, max_value_S, 255))
    if low_S >= high_S:
        low_S = high_S - 1
        cv.setTrackbarPos(low_S_name, parameter_window_name, int(normalize(low_S, 255, max_value_S)))

def on_high_S_thresh_trackbar(val):
    global low_S
    global high_S
    high_S = int(normalize(val, max_value_S, 255))
    if low_S >= high_S:
        high_S = low_S + 1
        cv.setTrackbarPos(high_S_name, parameter_window_name, int(normalize(high_S, 255, max_value_S)))

def on_low_V_thresh_trackbar(val):
    global low_V
    global high_V
    low_V = int(normalize(val, max_value_V, 255))
    if low_V >= high_V:
        low_V = high_V - 1
        cv.setTrackbarPos(low_V_name, parameter_window_name, int(normalize(low_V, 255, max_value_V)))

def on_high_V_thresh_trackbar(val):
    global low_V
    global high_V
    high_V = int(normalize(val, max_value_V, 255))
    if low_V >= high_V:
        high_V = low_V + 1
        cv.setTrackbarPos(high_V_name, parameter_window_name, int(normalize(high_V, 255, max_value_V)))

# --- Fenster mit Trackbars erstellen ---
cv.namedWindow("Parameter")
# --- Trackbar für HSV ---
cv.createTrackbar(low_H_name,parameter_window_name,0,max_value_H,on_low_H_thresh_trackbar)
cv.createTrackbar(high_H_name,parameter_window_name,max_value_H,max_value_H,on_high_H_thresh_trackbar)

cv.createTrackbar(low_S_name,parameter_window_name,0,max_value_S,on_low_S_thresh_trackbar)
cv.createTrackbar(high_S_name,parameter_window_name,max_value_S,max_value_S,on_high_S_thresh_trackbar)

cv.createTrackbar(low_V_name,parameter_window_name,0,max_value_V,on_low_V_thresh_trackbar)
cv.createTrackbar(high_V_name,parameter_window_name,max_value_V,max_value_V,on_high_V_thresh_trackbar)

# Bild einlesen
img = cv.imread('images/R/image_0.jpg')
img = cv.resize(img, (0, 0), fx = 1, fy = 1)
# --- main loop ---
while True:
    # Bild in HSV konvfertieren für Farberkennung
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    # Trackbar Werte in Array eintragen
    lower_color = np.array([low_H, low_S, low_V])
    upper_color = np.array([high_H, high_S, high_V])

    # Maske zur Farberkennung erstellen und UND-Verknüpfen
    mask = cv.inRange(hsv, lower_color, upper_color)
    result = cv.bitwise_and(img, img, mask= mask)

    # Orignal Bild und Neues Bild in Fenster öffnen
    cv.imshow('Original', img)
    cv.imshow('Result', result)

    # Benden, wenn 'q' gedückt wird
    if cv.waitKey(1) == ord('q'):
        break

# cap wieder freilassen und Fenster zerstören
cv.destroyAllWindows()