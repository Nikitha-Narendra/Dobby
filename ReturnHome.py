import serial
import turtle
import time
port = serial.Serial('/dev/arduino',9600)

def turn_towards_angle(func,degree):
    location = 'front'
    #print(degree)
    offset_x = 0.025
    offset_p = 0.025
    movement = 'x'
    if func == 'p':
        if degree < 150:
            movement = 'r'
            delay = (150 - degree)*offset_p
            #print(delay)
            location = 'right'
        elif degree >150:
            movement ='l'
            delay = (degree-150)*offset_p
            #print(delay)
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
    return location

def return_home(port,x_cord,y_cord):
    try:
        home = turtle.Turtle()
    except Exception:
        home = turtle.Turtle()
    port.flush()
    port.write('h'.encode())
    home.penup()
    home.goto(x_cord,y_cord)
    home.pendown()
    print("returning home")
    home.setheading(home.towards(0,0))
    
    begin = False
    while int(x_cord) != 0 or int(y_cord)!=0:
        x_cord,y_cord = home.position()
        if begin:
            home.forward(0.5)
        if port.in_waiting:
            direction = port.readline().decode('utf-8').rstrip()
            #print(f'Direction - {direction}')
            if direction == 'h':
                begin = True
            if direction.isalpha() and begin:
                
                if direction == 'l':
                    home.left(80)

                if direction == 'b':
                    home.back(1)
                    
                if direction == 'r':
                    home.right(80)
                    
                if direction == 'c':
                    degree = home.heading() - home.towards(0,0)
                    home.setheading(degree)
                    _=turn_towards_angle('r',degree)
                time.sleep(1)
            
    print("exiting")
    port.write('z'.encode())
    turtle.bye()
    
  

if __name__=='__main__':
    #return_home(port,83,1.2)
    degree = int(input("enter degree: "))
    turn_towards_angle('p',degree)