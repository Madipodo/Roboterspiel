import urllib.request
import cv2
import numpy as np
import rtde.rtde as rtde
import rtde.rtde_config as rtde_config
import sys

# Inizialisierung 
# Variablen Deklarieren
hostname = "10.1.91.167"
ROBOT_PORT = 30004
config_filename = 'control_loop_configuration.xml'
DEBUG = True

# Kamerabild auslesen
def get_image():
    global hostname
    cv2.waitKey(1) # Verzögerung, damit Kamera den Fokus findet (nur 1ms evtl. unnötig)
    resp = urllib.request.urlopen(f"http://{hostname}:4242/current.jpg?type=color")
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image

# Buchstaben aus Bild erkennen
def get_letter_from_image(image):
    # Bild zu HSV-Format umwandeln
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Bereich der geprüft werden soll extrahieren
    height, widgth, _ = image.shape
    squareToCheck = hsv[height - 95: height - 55, int(widgth / 2 - 20): int(widgth / 2 + 20), :]
    return get_color_of_area(squareToCheck)

# Farbe aus übergebene Bildbereich erkennen
def get_color_of_area(area):
    # Mögliche Rückgaben
    dict_letters = {"A":1, "I":2, "F":3, "O":4,"R":5, "U":6, "Error": 99}
    dict_colors = {"grau":1, "rot":2, "grün":3, "gelb":4,"blau":5, "weiß":6, "Error": 99}
    # Durschschnitts HSV-Werte des Bildbereichs ermitteln
    sum = [0, 0, 0]
    posibility = 0
    numberOfPixelToCheck = 0
    for line in area:
        for pixel in line:
            sum[0] += pixel[0]
            sum[1] += pixel[1]
            sum[2] += pixel[2]
            numberOfPixelToCheck += 1

            if pixel[0] < 10 or pixel[1] > 330:
                posibility += 1
    
    average = [sum[0] / numberOfPixelToCheck, sum[1] / numberOfPixelToCheck, sum[2] / numberOfPixelToCheck]

    # Funktion zum umnormieren des Durchschnittwertes (H - 360, S - 100, V - 100)
    def normalize(value, value_max, norm_max):
        return value * norm_max / value_max

    # Anhand der Durchschnittswerte, Farbe (Buchstabe) erkennen und Ergebnis zurückgeben
    if posibility / numberOfPixelToCheck > 0.75:
        if DEBUG: 
            print("I")
        return dict_letters["I"]
    elif normalize(60, 360, 255) <= average[0] <= normalize(140, 360, 255):
        if normalize(0, 100, 255) <= average[1] <= normalize(50, 100, 255):
            if DEBUG: 
                print("A")
            return dict_letters["A"]
        elif normalize(50, 100, 255) <= average[1] <= normalize(100, 100, 255):
            if DEBUG: 
                print("F")
            return dict_letters["F"]
    elif normalize(22, 360, 255) <=  average[0] <= normalize(55, 360, 255):
        if normalize(0, 100, 255) <= average[1] <= normalize(50, 100, 255):
            if DEBUG: 
                print("U")
            return dict_letters["U"]
        elif normalize(50, 100, 255) <= average[1] <= normalize(100, 100, 255):
            if DEBUG: 
                print("O")
            return dict_letters["O"]
    elif normalize(150, 360, 255) <=  average[0] <= normalize(240, 360, 255):
        if DEBUG: 
            print("R")
        return dict_letters["R"]
    
    # Rückgabe, wenn kein Buchstabe erkannt wurde
    return dict_letters["Error"]

# Kommunikation mit Roboter herstellen und Konfigurieren
# Konfigurationsfile für Kommunikation laden
conf = rtde_config.ConfigFile(config_filename)
input_names, input_types = conf.get_recipe('input_vals')
output_names, output_types = conf.get_recipe('output_vals')

# RTDE Client erstellen und verbinden
con = rtde.RTDE(hostname, ROBOT_PORT)
con.connect()

# setup recipes 
input_vals = con.send_input_setup(input_names, input_types)
output_vals = con.send_output_setup(output_names, output_types)

# Variablen Initialisieren
input_vals.input_int_register_0 = 0

#start data synchronization
if not con.send_start():
    sys.exit()

# Main Loop
running = True
letter_detected = False
while running:
    output_vals = con.receive()
    if output_vals is None:
        break

    # Warte darauf das der Roboterbereit steht
    while output_vals.output_int_register_0 == 0:
        # Wenn RB nicht bereit Inputdaten rücksetzen und senden
        input_vals.input_int_register_0 = 0
        if DEBUG:
            print(input_vals.input_int_register_0)
        letter_detected = False
        con.send(input_vals)

        # kurz warten und dann Daten vom Roboter erneut überprüfen
        cv2.waitKey(500)
        output_vals = con.receive()
        # Wenn keine Daten empfangen abbrechen
        if output_vals is None:
            running = False
            break

    # Sobald Roboter bereitsteht -> Buchstaben erkennen
    if output_vals.output_int_register_0 == 1 and letter_detected == False:        
        while True:
            feedback = [99, 99, 99]
            for i in range(3):
                image = get_image()
                feedback[i] = get_letter_from_image(image)
            if feedback[0] == feedback[1] == feedback[2]:
                break
        input_vals.input_int_register_0 = feedback[0] 
        letter_detected = True
    # Programm abbrechen
    elif output_vals.output_int_register_0 == 99:
        input_vals.input_int_register_0 = 0
        con.send(input_vals)
        break
    
    con.send(input_vals)

# RTDE Client Verbindung trennen
con.disconnect()