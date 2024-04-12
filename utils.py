from itertools import cycle
from shutil import get_terminal_size
from threading import Thread, Event
from time import sleep

class Loader:
    def __init__(self, desc="Loading...", end="{task} complete.", timeout=0.1):
        self._desc = desc
        self.end = end
        self.timeout = timeout

        self._thread = Thread(target=self._animate, daemon=True)
        self.steps = cycle(["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"])
        self.done = False
        self.paused = Event()
        self.update_desc_event = Event()

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, value):
        self._desc = value
        self.update_desc_event.set()  # Signal that description has been updated

    def start(self):
        cols = get_terminal_size((80, 20)).columns  # Get width of the terminal
        print("\r" + " " * cols, end="", flush=True)  # Clear line
        self.paused.clear()
        self._thread.start()
        return self

    def pause(self):
        self.paused.set()

    def resume(self):
        self.paused.clear()
        self.update_desc_event.clear()  # Clear the update event on resume

    def _animate(self):
        while not self.done:
            if self.paused.wait(timeout=self.timeout):  # Wait for resume or timeout
                continue
            cols = get_terminal_size((80, 20)).columns  # Get the width of the terminal
            if self.update_desc_event.is_set():
                self.update_desc_event.clear()  # Acknowledge the update
                print("\r" + " " * cols, end="", flush=True)  # Clear the line
            print(f"\r{self.desc} {next(self.steps)}", flush=True, end="")

    def stop(self):
        self.done = True
        self.resume()  # Resume to allow the thread to complete
        cols = get_terminal_size((80, 20)).columns  # Get the width of the terminal
        print("\r" + " " * cols, end="", flush=True)  # Clear the line
        end_message = self.end.format(task=self.desc)
        print(f"\r{end_message}", flush=True)

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_value, tb):
        self.stop()


# For fancy CLI formatting.
# Access with color.<attribute> + "string" + color.END
class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


