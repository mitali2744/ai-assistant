import pyttsx3

_engine = None

def _get_engine():
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
        _engine.setProperty('rate', 170)
        _engine.setProperty('volume', 1.0)
    return _engine

def speak(text):
    print(f"Aria: {text}")
    try:
        engine = _get_engine()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[TTS Error]: {e}")
