
import cv2 as cv
import os
import numpy as np
from handtrackingmodule import handDetector

folderPath = "static/model"
myList = os.listdir(folderPath)
overleyList = [cv.imread(f'{folderPath}/{path}') for path in myList]

brushThickness = 15
erseThickness = 70
tipId = [4, 8, 12, 16, 20]

header = overleyList[0]
Color = (0, 128, 0)
xp, yp = 0, 0
imgCanvas = np.zeros((720, 1280, 3), np.uint8)

cap = cv.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = handDetector(detectionCon=0.9)

def fingersUp(lmList):
    fingers = []
    if lmList[tipId[0]][1] > lmList[tipId[0] - 1][1]:
        fingers.append(1)
    else:
        fingers.append(0)

    for id in range(1, 5):
        if lmList[tipId[id]][2] < lmList[tipId[id] - 2][2]:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers

def generate_frames():
    global xp, yp, header, Color, imgCanvas

    while True:
        success, img = cap.read()
        if not success:
            break

        img = cv.flip(img, 1)
        img = cv.resize(img, (1280, 720))
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)

        if lmList:
            x1, y1 = lmList[8][1], lmList[8][2]
            x2, y2 = lmList[12][1], lmList[12][2]
            fingers = fingersUp(lmList)

            if fingers[1] and fingers[2]:  # Selection Mode
                xp, yp = 0, 0
                if y1 < 109:
                    if 0 < x1 < 320:
                        header = overleyList[0]
                        Color = (0, 128, 0)
                    elif 320 < x1 < 640:
                        header = overleyList[1]
                        Color = (0, 0, 255)
                    elif 640 < x1 < 960:
                        header = overleyList[2]
                        Color = (255, 0, 0)
                    elif 960 < x1 < 1280:
                        header = overleyList[3]
                        Color = (0, 0, 0)

                cv.rectangle(img, (x1, y1 - 30), (x2, y2 + 30), Color, cv.FILLED)

            elif fingers[1] and not fingers[2]:  # Drawing Mode
                cv.circle(img, (x1, y1), 15, Color, cv.FILLED)

                if xp == 0 and yp == 0:
                    xp, yp = x1, y1

                thickness = erseThickness if Color == (0, 0, 0) else brushThickness
                cv.line(img, (xp, yp), (x1, y1), Color, thickness)
                cv.line(imgCanvas, (xp, yp), (x1, y1), Color, thickness)
                xp, yp = x1, y1

        img[0:109, 0:1280] = header

        imgGray = cv.cvtColor(imgCanvas, cv.COLOR_BGR2GRAY)
        _, imgInv = cv.threshold(imgGray, 50, 255, cv.THRESH_BINARY_INV)
        imgInv = cv.cvtColor(imgInv, cv.COLOR_GRAY2BGR)
        img = cv.bitwise_and(img, imgInv)
        img = cv.bitwise_or(img, imgCanvas)

        ret, buffer = cv.imencode('.jpg', img)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
