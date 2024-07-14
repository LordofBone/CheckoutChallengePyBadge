from adafruit_pybadger import pybadger

from utils.resource_manager import cleanup


class AudioEngine:
    def __init__(self):
        self.notes = {
            'C4': 261.63,
            'D4': 293.66,
            'E4': 329.63,
            'F4': 349.23,
            'G4': 392.00,
            'A4': 440.00,
            'B4': 493.88,
            'C5': 523.25,
            'D5': 587.33,
            'E5': 659.25,
            'F5': 698.46,
            'G5': 783.99,
            'A5': 880.00,
        }

        self.main_theme = [
            ('C4', 0.2), ('E4', 0.2), ('G4', 0.2), ('C5', 0.4),
            ('D4', 0.2), ('F4', 0.2), ('A4', 0.4),
            ('E4', 0.2), ('G4', 0.2), ('B4', 0.2), ('E5', 0.4),
            ('F4', 0.2), ('A4', 0.2), ('C5', 0.4),
        ]

        cleanup()

    def play_tone(self, note, duration):
        """
        Play a single note for a specified duration.
        :param note:
        :param duration:
        :return:
        """
        frequency = self.notes.get(note)
        if frequency:
            pybadger.play_tone(frequency, duration)
        else:
            raise ValueError(
                f"Note '{note}' is not a valid note. Please use one of the following: {', '.join(self.notes.keys())}")

    def play_tune(self, tune):
        """
        Play a tune.
        :param tune:
        :return:
        """
        for note, duration in tune:
            frequency = self.notes.get(note, None)
            if frequency:
                self.play_tone(note, duration)
            else:
                raise ValueError(
                    f"Note '{note}' in the tune is not a valid note. Please use one of the following: {', '.join(self.notes.keys())}")
