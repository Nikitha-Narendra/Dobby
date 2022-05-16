from pycoral.utils.edgetpu import make_interpreter
from pycoral.utils.dataset import read_label_file
from pycoral.adapters import common,detect
from VoiceRecognition import speak
from imutils.video import VideoStream
from ReturnHome import *
import threading
import turtle
import serial
import time
import cv2


port = serial.Serial('/dev/arduino',9600)
read_degree = 0
x = 150
y = 150
area = 45
run = True
found = False
location = ''
r_x = 0
r_y = 0
r_degree = 0


def map_robot():
    global read_degree,r_x,r_y,r_degree
    try:
        rover = turtle.Turtle()
    except Exception:
        rover = turtle.Turtle()
    direction = 'x'
    start = time.time()
    begin = False
    while direction!='z':
        if begin:
            rover.left(0.01)
            rover.forward(0.5)
            
        if port.in_waiting:
            direction = port.readline().decode('utf-8').rstrip()

            if direction == 'q':
                time.sleep(2)
                begin = True
            if direction.isalpha() and begin: 
                    
                if direction == 'l':
                    rover.left(85)

                if direction == 'b':
                    rover.back(1)

                if direction == 'r':
                    rover.right(85)

                stop = time.time()
                if ((stop - start) > 200):
                    port.write('x'.encode())
                    time.sleep(1)
                    break
                time.sleep(1)
            else:
                read_degree = direction if direction.isnumeric() and direction!='300' else read_degree
        
   
    r_x,r_y = rover.position()
    r_degree = rover.heading() - rover.towards(0,0)
    print(f'Exiting at : {rover.position()} - {r_degree}')
    try:
        if r_degree > 0:
            turtle.done()
        turtle.getscreen().clear()
        turtle.bye()
    except Exception:
        print('closing turtle')


def move_robot(thresh):
    print("Moving to object")
    global run
    port.write('i'.encode())
    degree = 70
    movement = 'x'
    prev_movement = 'x'
    distance = 100
    count = 0
    port.flush()
    while run:

        if 100 <= x <= 200  and 100 <= y <= 200:
            if area > 90:
                movement = 'b'
            elif area < thresh:
                movement = 'f'
                count = 0
            else:
                if area == 50:
                    pass                
                else:
                    port.write('u'.encode())
                    _=port.readline().decode('utf-8').rstrip()
                    distance=port.readline().decode('utf-8').rstrip()
                    if (distance.isnumeric() and int(distance) < 30) or area >70:
                        movement = 'x'
                        print(f'area = {area}')
                        run=False
                    else:
                        movement = 'f'
                
        else:
            
            if x > 200:
                movement = 'r'
            elif x < 100:
                movement = 'l'
            
            
            if y < 100:
                degree -= 10
                port.write('t'.encode())
                port.write(b'%d' %degree)
                time.sleep(0.5)
            elif y > 200:
                degree += 10
                port.write('t'.encode())
                port.write(b'%d' %degree)
                time.sleep(0.5)
        
        if prev_movement != movement:
            port.write(movement.encode())
    
            if movement == 'r' or movement == 'l':
                time.sleep(0.15)
                movement = 'x'
                port.write(movement.encode())
                   
        prev_movement=movement

    print("stopping\n")
    port.write('i'.encode())
    port.write('z'.encode())
        

def load_model():
    labels = read_label_file('Models/labels.txt')
    interpreter = make_interpreter('Models/mobilenet2.tflite')
    interpreter.allocate_tensors()
    return interpreter,labels

def get_object(mobNet,labels,name=None):
    if name == 'person':
        objs = detect.get_objects(mobNet,0.5)
    else:
        objs = detect.get_objects(mobNet,0.3)
    if name:
        objs = [obj for obj in objs if labels.get(obj.id)==name]
    return objs

def draw_objects(frame, objs, labels):
    global x,y,area
    height,width = frame.shape[:2]
    for obj in objs:
        bbox = obj.bbox
        name = labels.get(obj.id,obj.id)
        x,y = (int((bbox.xmax+bbox.xmin)/2) , int((bbox.ymax+bbox.ymin)/2))
        area = int(((bbox.xmax-bbox.xmin)/width) *100)
        cv2.circle(frame, (x, y), 3, (255, 255, 255), -1)
        cv2.rectangle(frame,(bbox.xmin, bbox.ymin), (bbox.xmax, bbox.ymax),(204,0,102),2)
        cv2.rectangle(frame,(bbox.xmin, bbox.ymin),(bbox.xmin + (len(name)*12), bbox.ymin - 20),(204,0,102),-1)
        cv2.putText(frame,name,(bbox.xmin + 7, bbox.ymin - 7),cv2.FONT_HERSHEY_TRIPLEX,0.5,(255,255,255),1,cv2.LINE_AA)
    return frame
              
def find(mobNet = None,labels = None,ser = None,name = None):
    global run,x,y,area,port,location
    timer = 15
    start = time.time()
    movement ,mapping = None, None
    degree = -2
    run=True
    found=False
    print(f"finding {name}")
    
    if mobNet is None or labels is None:
        mobNet, labels = load_model()
    if ser:
        port = ser
    port.flush()
        
    camera = VideoStream(src=0).start()
    port.write('i'.encode())
    if name == 'person':
        port.write('t'.encode())
        port.write(b'40')
    
    else:
        port.write('t'.encode())
        port.write(b'70')

    
    port.write('p'.encode())
    port.write('t'.encode())
       
    thresh = 70 if name == 'person' else 50
    mapping = threading.Thread(target=map_robot)
    mapping.daemon = True
    mapping.start()
    time.sleep(0.5)
    while True:
        frame = camera.read()
        frame = cv2.resize(frame, (300,300))
        common.set_input(mobNet, frame)
        mobNet.invoke()
        objs = get_object(mobNet,labels,name)
        
        
        if len(objs)==0:
            end = time.time()  
            if found:
                y = 150
                area = thresh
                      
            if (end - start > timer and not found):
                if timer == 100:
                    print('Time up')
                    break
                speak(f"No {name} in vicinity")
                print(f"No {name} in vicinity")
                timer=200
                port.write('q'.encode())
            
                
        else:
            
            if not found:
                port.write('x'.encode())
                port.write('z'.encode())
                time.sleep(1)
                degree = int(read_degree)
                print(f"Degree: {degree}")
                location = turn_towards_angle('p',degree)
                found=True         
                movement = threading.Thread(target=move_robot, args=(thresh,))
                movement.start()
                
            frame = draw_objects(frame, [objs[0]], labels)
        
        frame = cv2.line(frame, (100, 0), (100, 300), (0, 255, 0), 1)
        frame = cv2.line(frame, (0, 100), (300, 100), (0, 255, 0), 1)
        
        frame = cv2.line(frame, (150, 0), (150, 300), (0, 0, 0), 1)
        frame = cv2.line(frame, (0, 150), (300, 150), (0, 0, 0), 1)
        
        frame = cv2.line(frame, (200, 0), (200, 300), (0, 255, 0), 1)
        frame = cv2.line(frame, (0, 200), (300, 200), (0, 255, 0), 1)
        
        frame = cv2.resize(frame, (640,480))
        cv2.imshow("Detection",frame)
        if not run:
            break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            run=False
            break
        
    cv2.destroyAllWindows()
    port.write('x'.encode())
    port.write('z'.encode())
    camera.stop() 
             
    
    return [found,location,degree,r_x,r_y,r_degree]
    
    
if __name__=='__main__':
    name = 'pizza'
    values = find(name=name)
    if values[0]:
        speak(f'Found {name} on your {values[1]}')
        print(values)
        #if values[-1] != 0:
            #port.write('b'.encode())
            #time.sleep(1)
            #turn = 150 + (150-int(values[2]))
            #location = turn_towards_angle('p',turn)
            #time.sleep(1)
            #location = turn_towards_angle('r',values[-1])
            #return_home(port,values[3],values[4])
        
        #turtle.bye()
        
    #degree = int(input("enter degree: "))
    #turn_towards_angle('p',degree)
    
