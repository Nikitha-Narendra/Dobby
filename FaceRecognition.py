from imutils.video import VideoStream
import face_recognition
import numpy as np
import pickle
import time
import cv2


def recognize(find=None):
    encodeKnown = pickle.loads(open("Models/family","rb").read())
    found = None
    identified = False
    encodes = encodeKnown["encodings"]
    classNames = encodeKnown["names"]
    video = VideoStream(src=0).start()
    time.sleep(0.5)
    while True:
        frame = video.read()
        img = cv2.resize(frame, (0,0), None, 0.25, 0.25)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        faces = face_recognition.face_locations(img)
        encode = face_recognition.face_encodings(img,faces)
        flag = 0
        for en,face in zip(encode,faces):
            matches = face_recognition.compare_faces(encodes,en)
            dist = face_recognition.face_distance(encodes, en)
            matchIndex = np.argmin(dist)
            y1,x2,y2,x1 = face
            y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(frame,(x1,y1),(x2,y2),(204,0,102),2)
            
            identified = True
            if matches[matchIndex]:
                name = classNames[matchIndex]
                print(name)
                cv2.rectangle(frame,(x1, y1),(x1 + (len(name)*12), y1 - 20),(204,0,102),-1)
                cv2.putText(frame,name,(x1 + 7, y1 - 7),cv2.FONT_HERSHEY_TRIPLEX,0.5,(255,255,255),1,cv2.LINE_AA)
                found = True if find.lower() == name.lower() else False
                
            else:
                print("Unknown")
                cv2.rectangle(frame,(x1, y1),(x1 + (len("unknown")*12), y1 - 20),(204,0,102),-1)
                cv2.putText(frame,"Unknown",(x1 + 7, y1 - 7),cv2.FONT_HERSHEY_TRIPLEX,0.5,(255,255,255),1,cv2.LINE_AA)
                found = False
    
        cv2.imshow('Webcam',frame)
        if cv2.waitKey(1) & 0xFF == ord('q') or identified:
            break
    video.stop()
    cv2.destroyAllWindows()
    return found

if __name__=='__main__':
    recognize('Mother')    


