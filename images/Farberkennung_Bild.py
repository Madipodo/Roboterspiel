from fileinput import filename
import cv2
import numpy as np
import os

letter = "Sample"
DEBUG = False

f = []
for (dirpath, dirnames, filenames) in os.walk(f"images/{letter}"):
    f.extend(filenames)

for item in f:
    if not item.startswith("image"):
        f.remove(item)

for item in f:

    img = cv2.imread(f"images/{letter}/{item}")
    print(item)
    #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    height, widgth, _ = img.shape
    numberOfPixelToCheck = 40*40

    #cv2.rectangle(img, (int(widgth / 2 - 25), height - 100), (int(widgth / 2 + 25), height - 50), (0,255,0), 2)
    squareToCheck = hsv[height - 95: height - 55, int(widgth / 2 - 20): int(widgth / 2 + 20), :]

    sum = [0, 0, 0]
    posibility = 0
    for line in squareToCheck:
        for pixel in line:
            sum[0] += pixel[0]
            sum[1] += pixel[1]
            sum[2] += pixel[2]

            if pixel[0] < 10 or pixel[1] > 330:
                posibility += 1

    average = [sum[0] / numberOfPixelToCheck, sum[1] / numberOfPixelToCheck, sum[2] / numberOfPixelToCheck]

    def normalize(value, value_max, norm_max):
        return value * norm_max / value_max

    if DEBUG:
        print(normalize(180, 360, 255))
        print(normalize(260, 360, 255))
        print(normalize(average[0], 255, 360))

    print(average)
    if posibility / numberOfPixelToCheck > 0.75:
        #print(posibility / numberOfPixelToCheck)
        print("I")
    elif normalize(60, 360, 255) <= average[0] <= normalize(140, 360, 255):
        if normalize(0, 100, 255) <= average[1] <= normalize(50, 100, 255):
            print("A")
        elif normalize(50, 100, 255) <= average[1] <= normalize(100, 100, 255):
            print("F")
    elif normalize(22, 360, 255) <=  average[0] <= normalize(55, 360, 255):
        if normalize(0, 100, 255) <= average[1] <= normalize(50, 100, 255):
            print("U")
        elif normalize(50, 100, 255) <= average[1] <= normalize(100, 100, 255):
            print("O")
    elif normalize(150, 360, 255) <=  average[0] <= normalize(240, 360, 255):
        print("R")

    #cv2.imshow("Bild", img)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows
