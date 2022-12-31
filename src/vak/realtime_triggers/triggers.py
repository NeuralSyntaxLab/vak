from abc import ABC, abstractmethod
import regex as re

TRIGGER_TYPES = ["transition"]

# Todo - Maybe add priority field so they will run in a specific order?

class Trigger(ABC):
    NOT_TRIGGERED = -1

    def __init__(self, callback):
        self.callback = callback

    @abstractmethod
    def check_trigger(self, cur_stream):
        """
        A function that is called to check if a stream for a specific trigger, defined in an extanding class.
        If the trigger is indeed triggered - the callback function is called.
        The function will return the index in cur_stream in which the trigger occured, or -1 if not triggered.
        """
        raise(NotImplementedError)

    @abstractmethod
    def __str__(self):
        return "Generic Trigger"


class TransitionTrigger(Trigger):
    """
    A class representing a trigger that is enabled whenever a specific transition occurs in the song.
    The 'from_seg' can be a regex enabling more complex behavior.
    """
    def __init__(self, callback, from_seg, to_seg):
        super().__init__(callback)
        self.from_seg = from_seg
        self.to_seg = to_seg

    def check_trigger(self, cur_stream):
        stream_regex = ".*" + self.from_seg + self.to_seg + ".*" # Checks that the stream contains the trigger.
        m = re.search(stream_regex, ''.join(cur_stream))
        if m:
            self.callback(self, cur_stream, m)
            return m.end()
        else:
            return Trigger.NOT_TRIGGERED

    def __str__(self):
        return f"Trigger: {self.from_seg} -> {self.to_seg}"