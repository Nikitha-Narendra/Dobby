import speech_recognition as sr
import pyttsx3

query = None
stop_listening = None

def get_statement():
    return query

def callback(r,audio):
    global query
    
    try:
        speak(" Listening")
        query = r.recognize_google(audio)        
        #print(f"user said : {query}\n")

    except Exception:
        print("Sorry, can you repeat?")
        
    

def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1)
    index = 0
    voices = engine.getProperty('voices')
    engine.setProperty('voice', 'voices[1].id')
    engine.say(text)
    engine.runAndWait()


def Command():
    r = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        speak("Listening..")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        
        try:
            statement = r.recognize_google(audio)
            print(f"You said: {statement}")
            return statement
        except sr.UnknownValueError:
            speak("Sorry can your repeat?")
            return None
        

def Command_back():
    global stop_listening
    print("starting microphone")
    r = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        r.adjust_for_ambient_noise(source)
        
    stop_listening = r.listen_in_background(mic,callback)
    
    
def stop_sound():
    print("Stoping microphone")
    stop_listening() if stop_listening is not None else print("Background not in function")
    
print("Loading...")
#speak("Loading... ")


if __name__=='__main__':


    print("Good Morning! How may i help you")
    speak("Good Morning! How may i help you")
    
    while True:
       statement = Command()
       if statement:
            if "hello" in statement:
                Command_back()
                print("hello Nikitha")
                stop_sound()
            if statement and "bye" in statement:
                speak("bye!")
                break
        
          
