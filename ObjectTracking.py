from imutils.video import VideoStream
from pycoral.adapters import common
from VoiceRecognition import *
from ObjectDetection import *
from Models.sort import Sort
import threading
import numpy as np
import time
import cv2
import os

port = serial.Serial('/dev/arduino',9600)
right = 150
top = 150
x = 150
y = 150
area = 45
run = True
def follow_person():
    print("Moving to object")
    global run,right,top
    port.write('i'.encode())
    degree = 40
    movement = 'x'
    prev_movement = 'x'
    
    while run:
        query = get_statement()
        print(query)
        if query:
            words = set(query.split(' '))
            stop_command = set(['stop','following','me'])
            print(list(words & stop_command))
            break
        if 100 <= right <= 200  and 100 <= top <= 200:
            
            if area > 90:
                movement = 'b'
            elif area < 70:
                movement = 'f'
            else:
                movement = 'x'
                
                
        else:          
            if right > 200:
                movement = 'r'
            if right < 100:
                movement = 'l'
            
        if y < 100:
            degree -= 10
            degree = max(degree,0)
            port.write('t'.encode())
            port.write(b'%d' %degree)
            time.sleep(1)
        if y > 200:
            degree += 10
            degree = min(degree,180)
            port.write('t'.encode())
            port.write(b'%d' %degree)
            time.sleep(1)

        
        #if prev_movement != movement:
            
        if prev_movement != movement:
            #print(f'{right} {top} {x} {y} {movement}')
            port.write(movement.encode())        
        prev_movement=movement
        if movement == 'r' or movement == 'l':
            time.sleep(0.25)
            port.write('x'.encode())
            movement = 'x'
        #port.write('x'.encode())
    
    print("stopping\n")
    port.write('i'.encode())
    port.write('z'.encode())
    run=False
    
def draw_boxes(frame, obj, labels):
    global right,top,x,y,area
    height,width = frame.shape[:2]
    x,y,w,h = np.array(obj[:4], dtype=np.int32)
    right , top = (int((w+x)/2) , int((h+y)/2))
    name = str(obj[4])
    area = int(((w-x)/width) * 100)
    cv2.circle(frame, (right, top), 3, (255, 255, 255), -1)
    cv2.rectangle(frame, (x,y), (w,h),(204,0,102),2)
    cv2.rectangle(frame,(x,y),(x+(len(name)*12), y-20),(204,0,102),-1)
    cv2.putText(frame,name,(x + 7, y - 7),cv2.FONT_HERSHEY_TRIPLEX,0.5,(255,255,255),1,cv2.LINE_AA)
    
    return frame
def track(ser=None,mobNet=None,labels=None):
    global run,port
    if mobNet == None or labels == None:
        mobNet,labels = load_model()
    if ser:
        port = ser
        port.write('t'.encode())
        port.write(b'40')
    tracker = Sort()
    camera = VideoStream(src=0).start()    
    time.sleep(0.2)
    first = True
    tracker_data = []
    port.write('i'.encode())
    
    while True:
        frame = camera.read()
        frame = cv2.resize(frame, (300,300))
        common.set_input(mobNet, frame)
        mobNet.invoke()
        objs = get_object(mobNet, labels,'person')
        
        detections = []
        
            
        for i in range(len(objs)):
            obj = [objs[i].bbox.xmin,objs[i].bbox.ymin,objs[i].bbox.xmax,objs[i].bbox.ymax,objs[i].score]
            detections.append(obj)
        
        detections = np.array(detections)
        
        track_id = 0
        if detections.any():
            if first:
                run=True
                mapping = threading.Thread(target=follow_person)
                mapping.start()
                first = False
                
            tracked_data = tracker.update(detections)
            tracker_data = [data for data in tracked_data if data[4] == 1]
                    
        if len(tracker_data)>0:
            frame= draw_boxes(frame,tracker_data[0],labels)
        
        else:
            port.write('x'.encode())
        cv2.circle(frame, (150, 150), 3, (0, 0, 0), -1)
        frame = cv2.resize(frame, (640,480))
        cv2.imshow("Tracking",frame)
        if not run:
            break
        if cv2.waitKey(1) & 0xFF == ord('q') :
            run=False
            break
        
    cv2.destroyAllWindows()
    port.write('i'.encode())
    camera.stop()    
    
if __name__=='__main__':
    angle = os.popen('sudo python3 -W ignore ~/usb_4_mic_array/tuning.py DOAANGLE').read().rstrip().split(':')[1]
    print(angle)
    Command_back()
    #turn_towards_angle('r',360-int(angle))
    track()
    stop_sound()
                