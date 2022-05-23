# The module needed
from tkinter import filedialog as fd
import time
from PIL import ImageGrab
import cv2
import numpy as np
import face_recognition
from win32api import GetSystemMetrics
import os
from datetime import datetime

# Step 1
# Import Images from a list
# this function allows us to manually choose a file
path = fd.askdirectory()
images = []
classnames = []
myList = os.listdir(path)
#use names and import images one by one
for cl in myList:
    #load image is not used, instead use cv2 to read path function
    curImg = cv2.imread(f'{path}/{cl}')
    #append images and classnames from the reading of curImg and hide the format of files
    images.append(curImg)
    classnames.append(os.path.splitext(cl)[0])
print(classnames)


###############################################################################################
# Step 2
# Encode the images in path
def findEncodings(images):
    #encode all images in path/directory
    begin = time.time()
    encodeList = []
    for img in images:
        #convert BGR to RGB
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        #encode
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    # to record the total encoding time, if we want to record encoding time for each image, put these coding below under for loop above
    end = time.time()
    elapsed = end - begin
#   elapsed = int(elapsed)
    print('Encoding Time:', elapsed, 'seconds')
    return encodeList

#run the function of encodings
encodeListKnown = findEncodings(images)
print("Encoding Completed")


################################################################################################
# Step 4
# Record Attendance
def markAttendance(name):
    #where the names will be recorded; file etc.
    with open('ClassAttendance.csv', 'r+') as f:
        # not repeating the same recording
        mydatalist = f.readlines()
        namelist = []
        for line in mydatalist:
            entry = line.split(',')
            namelist.append(entry[0])
        if name not in namelist:
            now = datetime.now()
            dtstring = now.strftime('%H:%M:%S')
            f.writelines(f'\n{name},{dtstring}')


#############################################################################################################
# Step 3
# Find matches/test images - screen capture
width = GetSystemMetrics(0)
height = GetSystemMetrics(1)


while True:
    imgS = np.array(ImageGrab.grab(bbox=(0,0,width,height)))
    img_final = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(img_final)
    encodeCurFrame = face_recognition.face_encodings(img_final, faceCurFrame)

    for encodeface,faceloc in zip(encodeCurFrame,faceCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown,encodeface)
        facedis = face_recognition.face_distance(encodeListKnown,encodeface)
#       print(facedis)
        matchindex = np.argmin(facedis)

        if matches[matchindex]:
            name = classnames[matchindex]
            print(name)
            y1, x2, y2, x1 = faceloc
            cv2.rectangle(img_final, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img_final, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img_final, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            markAttendance(name)

    cv2.imshow("Screen capture", img_final)

    if cv2.waitKey(25) == ord('q'): # press q from your keyboard to stop recording
        cv2.destroyAllWindows()
        break

