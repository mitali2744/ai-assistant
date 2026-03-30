import speech_recognition as sr

def listen():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=5, phrase_time_limit=8)

        command = r.recognize_google(audio)
        return command.lower()

    except sr.WaitTimeoutError:
        print("No speech detected.")
        return None
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return None
    except Exception as e:
        print(f"Microphone error: {e}")
        return None
