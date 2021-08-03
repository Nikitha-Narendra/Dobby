import serial
import os
if __name__=='__main__':
    try:
        
        #os.system('arduino --upload /home/pi/Arduino/robot/robot.ino')
        port = serial.Serial('/dev/arduino',9600)
        port.write('p'.encode())
        print(port.readline().decode('utf-8').rstrip())
    except Exception:
        print(e.message)
        print("Cannot connect to arduino")
 