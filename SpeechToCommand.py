from VoiceRecognition import *
from ObjectDetection import *
from FaceRecognition import *
from ObjectTracking import *
from ReturnHome import *
import turtle
import os
commands = {'follow':'follow',
            'come':'follow',
            'find':'find',
            'say':'tell',
            'tell':'tell',
            'ask':'tell'
            }
people = ['mother','Nikita','Rohan','father']

if __name__=='__main__':
    port = serial.Serial('/dev/arduino',9600)
    speak('Connecting...')
    model,labels = load_model()
    name = ''
    print("Hello i am dobby  May I know your name")
    speak("Hello i am dobby  May I know your name")
    while name == '' or name is None or name == 'is':
        name = Command()
        if name:
            name = name.split(' ')[-1]
        else:
            speak('Sorry i did not get you name')
            
    print(f"Hello {name} how may I help you?")
    
    
    while True:
        
        speak(f"Hello {name} how may I help you?")
        statement = Command()
        speak(f'You said {statement}')                
        angle = os.popen('sudo python3 -W ignore ~/usb_4_mic_array/tuning.py DOAANGLE').read().rstrip().split(':')[1]

        if statement:
            statement = statement.replace(' me ', ' '+name+' ' )
                       
            words = statement.split(' ')
            
            command = list(set(words) & set(commands.keys()))
            
            for com in command:
                statement = statement.replace(com,commands.get(com))
        
            
            article = list(set(words) & set(labels.values()))
            person =  list(set(words) & set(people))
            if command:
                if(len(article)>0 or len(person)>0):                    
                    if "find" in command:
                        if article:
                            speak(f'{command[0]}ing a {article[0]}.')
                            values = find(model,labels,port,article[0])
                            port.write('b'.encode())
                            time.sleep(1)
                            turn = 150 + (150-int(values[2]))
                            location = turn_towards_angle('p', 150)
                            time.sleep(1)
                            if values[-1] != 0:
                                location = turn_towards_angle('r',values[-1])
                                return_home(port,values[3],values[4])
                                
                            else:
                                port.write('b'.encode())
                                time.sleep(1)
                                port.write('x'.encode())
                                
                            if values[0]:
                                speak(f"Your {article[0]} is to your {values[1]}")
                            else:
                                speak(f"Sorry I could not find a {article[0]}. ")
                    
                    if "tell" in command:
                        speak(f'finding {person[0]}')
                        print(f'finding {person[0]}')
                        while True:
                            values = find(model,labels,port,'person')
                            time.sleep(1)
                            if values[1]:
                                port.write('t'.encode())
                                port.write(b'10')
                                print(f"Hello may I verify if you are {person[0]}")
                                speak(f"Hello may I verify if you are {person[0]}")
                                found = recognize(person[0])
                                if found:
                                    index = statement.index("tell")
                                    message = name + " has sent a message: "+statement[index+9:]
                                    speak(message)
                                    print(message)
                                    turn_towards_angle('r',180)
                                    name = person[0]
                                    break
                                else:
                                    turn_towards_angle('r',180)
                            else:
                                if values[-1] != 0:
                                    location = turn_towards_angle('r',values[-1])
                                    return_home(port,values[3],values[4])
                                    speak('Sorry could not find {person[0]}')
                                break
                                    
                
                if "follow" in command:
                    speak('Following')
                    Command_back()
                    turn_towards_angle('r',360-int(angle))
                    track(port,model,labels)
                    stop_sound()
            
                
                
            elif "bye" in statement or "stop" in statement:
                speak("Bye! Have a good day")
                break
            
            else:
                speak("Sorry your request was not understood or incomplete. Please repeat")
                