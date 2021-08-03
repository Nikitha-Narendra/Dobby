import serial
import turtle

port = serial.Serial('/dev/arduino',9600)

def return_home(port,x_cord,y_cord):
    home = turtle.Turtle()
    home.penup()
    home.goto(x_cord,y_cord)
    home.pendown()
    print("returning home")
    home.setheading(home.towards(0,0))
    port.flush()
    begin = False
    while int(x_cord) != 0 or int(y_cord)!=0:
        x_cord,y_cord = home.position()
        if begin:
            home.forward(0.20)
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
                    degree = home.heading() - rover.towards(0,0)
                    home.setheading(degree)
                    turn_towards_angle('r',degree)
                time.sleep(1)
            
    print("exiting")
    port.write('z'.encode())
    turtle.bye()

if __name__=='__main__':
    return_home(port,83,1.2)