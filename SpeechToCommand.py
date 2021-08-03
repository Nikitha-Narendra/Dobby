from VoiceRecognition import *
from ObjectDetection import *
from FaceRecognition import *
from ObjectTracking import *
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
    print("Hello Im dobby ! May I know your name")
    speak("Hello Im dobby ! May I know your name")
    while name == '' or name is None:
        name = Command()
        if name:
            name = name.split(' ')[-1]
            
            
    print(f"Hello {name} how may I help you?")
    
    
    while True:
        speak(f"Hello {name} how may I help you?")
        statement = Command()
        angle = os.popen('sudo python3 -W ignore ~/usb_4_mic_array/tuning.py DOAANGLE').read().rstrip().split(':')[1]
        print(angle)
        if statement:
            statement = statement.replace('me', name)
            print(statement)            
            words = statement.split(' ')
            
            command = list(set(words) & set(commands.keys()))
            command = commands.get(command[0]) if len(command)>0 else None
            
            article = list(set(words) & set(labels.values()))
            
            person =  list(set(words) & set(people))
       
            if command and (len(article)>0 or len(person)>0):
                speak(f"{command}ing {'a '+article[0] if article else person[0]}.")
                
                if "find" in command or "tell" in command:
                    if article:
                        #print(f"finding {article[0]}") 
                        found,location,r_x,r_y = find(model,labels,port,article[0])
                        if found:
                            speak(f"Your {article[0]} is to your {location}")
                        else:
                            speak(f"Sorry I could not find a {article[0]}. ")
                    else:
                        speak(f"finding {person[0]}") 
                        found,location,r_x,r_y = find(model,labels,port,'person')
                        time.sleep(1)
                        if found:
                            speak(f"Hello, may I verify if you are {person[0]}")
                            found = recognize(person[0])
                            if found:
                                index = statement.index("tell")
                                messsage = name + " has sent a message: "+statement.substring(index+9)
                                speak(message)
                                print(message)
            
                elif "follow" in command:
                    #angle = os.popen('sudo python3 -W ignore ~/usb_4_mic_array/tuning.py DOAANGLE').read().rstrip().split(':')[1]
                    turn_towards_angle('r',360-int(angle))
                    track(port,model,labels)
                
                
            elif "bye" in statement or "stop" in statement:
                speak("Bye! Have a good day")
                break
            
            else:
                speak("Sorry your request was not understood or incomplete. Please repeat")
                
        
