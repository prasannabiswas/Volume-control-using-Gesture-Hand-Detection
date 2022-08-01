import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
volBar = 400
vol = 0
volPer = 0
area = 0
colorVol = (255, 0, 0)

wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.8, maxHands=1)

while True:
    success, img = cap.read()

    # Find Hand
    img = detector.findHands(img)
    lmlist, bbox = detector.findPosition(img, draw=True)
    if len(lmlist) != 0:

        # Filter based on size
        area = (bbox[2]-bbox[0])*(bbox[3]-bbox[1]) // 100
        # print(area)
        # if 500 < area < 1000:
            # print("yes")
        # print(bbox)

        # Find distance between index and Thumb
        length, img, lineInfo = detector.findDistance(4, 8, img)
        # print(length)

        # Convert Volume
        volBar = np.interp(length, [50, 160], [400, 130])
        volPer = np.interp(length, [50, 160], [0, 100])

        # Reduce Resolution to make it smoother
        smoothness = 10
        volPer = smoothness * round(volPer/smoothness)

        # Check fingers up
        fingers = detector.fingersUp()
        # print(fingers)

        # If pinky is down set volume
        if not fingers[4]:
            volume.SetMasterVolumeLevelScalar(volPer / 100, None)
            cv2.circle
            colorVol = (0, 255, 0)
            # time.sleep(0.25)
        else:
            colorVol = (255, 0, 0)


    # Drawings
    cv2.rectangle(img, (50, 130), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)
    cVol = int(volume.GetMasterVolumeLevelScalar()*100)
    cv2.putText(img, f'Vol Set: {int(cVol)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX,
                1, colorVol, 3)

    # Frame rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (400, 50), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)

    # print(lmlist[4], lmlist[8])

    # Hand range = 50 - 300
    # Volume Range = -63 - 0

    cv2.imshow("Img", img)
    cv2.waitKey(1)
