import speech_recognition as sr


def Command():
    r = sr.Recognizer()

    print(sr.Microphone.list_microphone_names())
    mic = sr.Microphone(device_index=2)

    with mic as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        
        try:
            statement = r.recognize_google(audio)
            print(f"You said: {statement}")
        except sr.UnknownValueError:
            print("Sorry! can your repeat?")

if __name__=='__main__':
    Command()