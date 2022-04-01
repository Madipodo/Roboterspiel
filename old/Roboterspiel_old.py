import cv2 
import numpy as np
import urllib
import sys
import rtde.rtde as rtde
import rtde.rtde_config as rtde_config
from keras.models import load_model
from PIL import Image, ImageOps

# Inizialisierung 
# Keras Model Laden
#model = load_model('keras_model.h5')

# Variablen Deklarieren
hostname = "10.1.91.167"
ROBOT_PORT = 30004
config_filename = 'control_loop_configuration.xml'
running = True
letter_detected = False
DEBUG = True

# Konfiguationsfile für Kommunikation laden
conf = rtde_config.ConfigFile(config_filename)
input_names, input_types = conf.get_recipe('setp')
output_names, output_types = conf.get_recipe('getp')

# Position dictionary
dict_letters = {"A":1, "I":2, "F":3, "O":4,"R":5, "U":6,}
dict_positions = {"A":1, "I":2, "F":3, "O":4,"R":5, "U":6,}

# Kamerabild auslesen
def get_image():
    cv2.waitKey(500) # Verzögerung, damit Kamera den fokus findet
    resp = urllib.request.urlopen(f"http://{hostname}:4242/current.jpg?type=color")
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image

# Buchstaben aus Bild erkennen
def probability_of_letter_from_image(image: np.ndarray):
    # Create the array of the right shape to feed into the keras model
    # The 'length' or number of images you can put into the array is
    # determined by the first position in the shape tuple, in this case 1.
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

    #resize the image to a 224x224 with the same strategy as in TM2:
    image_array = cv2.resize(image, (224, 224))

    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
    # Load the image into the array
    data[0] = normalized_image_array

    # run the inference
    #return model.predict(data)

# Box reihenfolge erkennen
def get_box_order():
    image = get_image()
    return   

def get_posnumber_by_alpha():
    pass

# Kommunikation mit Roboter herstellen und Konfigurieren
# RTDE Client erstellen und verbinden
con = rtde.RTDE(hostname, ROBOT_PORT)
con.connect()

# setup recipes 
input_vals = con.send_input_setup(input_names, input_types)
output_vals = con.send_output_setup(output_names, output_types)

# Variablen Inizialisieren
input_vals.input_int_register_0 = 0
input_vals.input_int_register_1 = 0

#start data synchronization
if not con.send_start():
    sys.exit()

# Main Loop
while running:
    output_vals = con.receive()
    if output_vals is None:
        break

    # Warte darauf das der Roboterbereit steht
    while output_vals.output_int_register_0 == 0:
        # Wenn RB nicht bereit Inputdaten rücksetzen und senden
        if DEBUG: 
            print(output_vals.output_int_register_0)
        input_vals.input_int_register_0 = 0
        letter_detected = False
        con.send(input_vals)

        # kurz warten und dann Daten vom Roboter erneut überprüfen
        cv2.waitKey(500)
        output_vals = con.receive()
        # Wenn keine Daten empfangen abbrechen
        if output_vals is None:
            break

        # Manueller Exit
        if cv2.waitKey(1) == ord('q'):
            running = False
            break

    # Sobald Roboter bereitsteht -> Buchstaben erkennen
    if output_vals.output_int_register_0 == 1 and letter_detected == False:       
        image = get_image()
        input_vals.input_int_register_0 = np.argmax(probability_of_letter_from_image(image)) + 1   # Überprüfen ob Image im richtigne Format ist RGB BGR
        if DEBUG:
            print(input_vals.input_int_register_0)
        letter_detected = True
    # Box Reihenfolge ermitteln
    elif output_vals.output_int_register_0 == 2:
        get_box_order()
    # Programm abbrechen
    elif output_vals.output_int_register_0 == 99:
        break

    # Ergebnis an Roboter senden
    con.send(input_vals)

# RTDE Client verbindung trennen
con.disconnect()