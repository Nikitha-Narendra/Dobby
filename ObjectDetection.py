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
location = ''
r_x = 0
r_y = 0
r_degree = 0


def map_robot():
    global read_degree,r_x,r_y,r_degree
    rover = turtle.Turtle()
    direction = 'q'
    start = time.time()
    begin = False
    while direction != 'z':
        if begin:
            rover.left(0.01)
            rover.forward(0.5)
            
        if port.in_waiting:
            direction = port.readline().decode('utf-8').rstrip()
            #print(f'Direction: {direction}')
                    
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
                #print(f'direction - {direction}')
                read_degree = direction if direction.isnumeric() and direction!='300' else read_degree
        
   
    r_x,r_y = rover.position()
    r_degree = rover.heading() - rover.towards(0,0)
    print(f'Exiting at : {rover.position()} - {r_degree}')
    turtle.done()
    #turn_towards_angle('r',degree)
    #port.write('b'.encode())
    #time.sleep(1)
    #port.write('x'.encode())
    #port.write('h'.encode())
    #return_home(rover)
    

def turn_towards_angle(func,degree):
    global location
    print(degree)
    offset_x = 0.025
    offset_p = 0.020
    movement = 'x'
    if func == 'p':
        if degree < 150:
            movement = 'r'
            delay = (150 - degree)*offset_p
            print(delay)
            location = 'right'
        elif degree >150:
            movement ='l'
            delay = (degree-150)*offset_p
            print(delay)
            location = 'left'
        else:
            port.write('x'.encode())
            delay = 0
            location = 'front'
    else:
        if degree < 0:
            movement = 'l'
            delay = abs(degree) * offset_x
            location = 'right'
        else:
            movement = 'r'
            delay = degree * offset_x
            location = 'left'
    
    port.write(movement.encode())
    time.sleep(delay)
    port.write('i'.encode())

def move_robot():
    print("Moving to object")
    global run
    port.write('i'.encode())
    degree = 70
    movement = 'x'
    prev_movement = 'x'
    count = 0
    while run:
        #print(f'{x} {y} {area}')
        if 100 <= x <= 200  and 100 <= y <= 200:
            if area > 90:
                movement = 'b'
                count = 0
            elif area < 50:
                movement = 'f'
                count = 0
            else:
                count= count+1
                movement = 'x'
                if count > 500:
                    port.write('f'.encode())
                    time.sleep(3)
                    run=False
                
        else:
            
            if x > 200:
                movement = 'r'
            if x < 100:
                movement = 'l'
            if y < 100:
                degree -= 10
                port.write('t'.encode())
                port.write(b'%d' %degree)
                time.sleep(0.5)
            if y > 200:
                degree += 10
                port.write('t'.encode())
                port.write(b'%d' %degree)
                time.sleep(0.5)
        
        if prev_movement != movement:
            port.write(movement.encode())
            
            
        prev_movement=movement
        #port.write('u'.encode())
        #print(port.readline().decode('utf-8').rstrip())
    
    print("stopping\n")
    port.write('i'.encode())
    port.write('z'.encode())
        

def load_model():
    labels = read_label_file('Models/labels.txt')
    interpreter = make_interpreter('Models/mobilenet2.tflite')
    interpreter.allocate_tensors()
    return interpreter,labels

def get_object(mobNet,labels,name=None):
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
        cv2.putText(frame,name + str(area),(bbox.xmin + 7, bbox.ymin - 7),cv2.FONT_HERSHEY_TRIPLEX,0.5,(255,255,255),1,cv2.LINE_AA)
    return frame
              
def find(mobNet = None,labels = None,ser = None,name = None):
    global run,x,y,area,port
    timer = 15
    start = time.time()
    first = False
    run = True
    degree = -2
    #print(f"finding {name}")
    
    if mobNet is None or labels is None:
        mobNet, labels = load_model()
    if ser:
        port = ser
        port.flush()
        
    camera = VideoStream(src=0).start()
    port.write('i'.encode())
    port.write('t'.encode())
    port.write(b'70')
    if name!='person':    
        port.write('p'.encode())
        port.write('t'.encode())
       
    
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
        
        if not run:
            break
        if len(objs)==0:
            #port.write('x'.encode())
            x=150
            y=150
            area = 50
            end = time.time()            
            if (end - start > timer and not first) or name=='person':
                x=150
                y=150
                area = 50
                if timer == 100: break
                speak(f"No {name} in vicinity")
                timer=200
                port.write('q'.encode())
            
                
        else:
            
            if not first:
                port.write('x'.encode())
                port.write('z'.encode())
                time.sleep(1)
                degree = read_degree
                print(f"Degree: {degree}")
                turn_towards_angle('p',int(degree))
                mapping.join()                
                movement = threading.Thread(target=move_robot)
                movement.start()
                first = True
                timer = 15
            frame = draw_objects(frame, objs, labels)
        
        #frame = cv2.line(frame, (100, 0), (100, 300), (0, 255, 0), 1)
        #frame = cv2.line(frame, (0, 100), (300, 100), (0, 255, 0), 1)
        
        #frame = cv2.line(frame, (150, 0), (150, 300), (0, 0, 0), 1)
        #frame = cv2.line(frame, (0, 150), (300, 150), (0, 0, 0), 1)
        
        #frame = cv2.line(frame, (200, 0), (200, 300), (0, 255, 0), 1)
        #frame = cv2.line(frame, (0, 200), (300, 200), (0, 255, 0), 1)
        
        frame = cv2.resize(frame, (640,480))
        cv2.imshow("Detection",frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            run=False
            break
        
    cv2.destroyAllWindows()
    port.write('x'.encode())
    port.write('z'.encode())
    #turtle.bye()    
    #mapping.join()
    #movement.join()
    camera.stop()        
    
    return [first,location,degree,r_x,r_y,r_degree]
    
    
if __name__=='__main__':
    name = 'cup'
    values = find(name=name)
    if values[0]:
        speak(f'Found {name} on your {values[1]}')
        print(values)
        if values[-1] != 0:
            port.write('b'.encode())
            time.sleep(2)
            turn = 150 + (150-int(values[2]))
            turn_towards_angle('p',turn)
            turn_towards_angle('r',values[-1])
            #port.write('h'.encode())
            #home = turtle.Turtle()
            #return_home(port,values[3],values[4])
        
    #degree = int(input("enter degree: "))
    #turn_towards_angle('p',degree)
    
