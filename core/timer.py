import threading
import time

_active_timer = None

def start_timer(minutes, callback_speak):
    global _active_timer

    def _run():
        seconds = int(minutes) * 60
        time.sleep(seconds)
        callback_speak(f"Time is up! Your {minutes} minute timer has ended. Take a short break.")

    if _active_timer and _active_timer.is_alive():
        return f"A timer is already running. Please wait for it to finish."

    _active_timer = threading.Thread(target=_run, daemon=True)
    _active_timer.start()
    return f"Timer started for {minutes} minutes. I will notify you when it's done."

def start_pomodoro(callback_speak):
    def _run():
        callback_speak("Pomodoro started. Focus for 25 minutes.")
        time.sleep(25 * 60)
        callback_speak("25 minutes done! Take a 5 minute break.")
        time.sleep(5 * 60)
        callback_speak("Break over. Ready for the next Pomodoro session?")

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return "Pomodoro session started: 25 minutes focus, then 5 minutes break."
