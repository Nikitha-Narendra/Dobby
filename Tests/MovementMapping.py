import serial
import turtle
import time
import math

def map_robot(rover,direction):
    if direction == 'f':
        rover.forward(1)

    if direction == 'l':
        rover.left(90)

    if direction == 'b':
        rover.back(1)

    if direction == 'r':
        rover.right(90)
    

def return_home(ser, rover):
    start_x,start_y =  rover.position()
    #ser.write('s'.encode());
    
    while start_x != 0 and start_y != 0:
        
        angle_to_turn = rover.towards(0,0)
        max_angle = 180 if angle_to_turn > 90 else 0
        direction = 'l' if max_angle > 90 else 'r'
        
        ser.write(str(angle_to_turn).encode)
        ser.write(str(max_angle).encode)
        ser.write(direction.encode())
        
        time.sleep(1)
        
        status = ser.readline().decode('utf-8').rstrip()

        if status == 'h':        
            rover.setheading(rover.towards(0,0))
        else:
            map_robot(rover,status)

        start_x,start_y = rover.position()
        
        

def ultrasonic_sensor(ser, rover):

    direction = 'q'
    ser.write(direction.encode())
    start = time.perf_counter()

    while direction != 'z':
        direction = input()
        print(f'{direction} : {type(direction)}')
        
        if direction.isalpha():
            map_robot(rover,direction)

        stop = time.perf_counter()
        if ((stop - start) > 30):
            #direction = 'z'
            ser.write('x'.encode())

    return rover.position()
    

if __name__=='__main__':
   
    rover = turtle.Turtle()
    print(rover.position())
    (x,y) = ultrasonic_sensor(ser,rover)
    print(x,y)
    rover.setheading(rover.towards(0,0))
    dist = math.sqrt(x**2 + y**2)
    rover.forward(dist)
    turtle.done()

        
    
