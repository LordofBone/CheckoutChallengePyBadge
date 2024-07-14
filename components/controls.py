from adafruit_pybadger import pybadger
from time import monotonic

from utils.resource_manager import cleanup


class Controls:
    def __init__(self):
        self.input_enabled = True
        self.default_debounce_time = 0.4
        self.debounce_times = {
            'up': self.default_debounce_time,
            'down': self.default_debounce_time,
            'left': self.default_debounce_time,
            'right': self.default_debounce_time,
            'a': self.default_debounce_time,
            'b': self.default_debounce_time,
            'start': self.default_debounce_time,
            'select': self.default_debounce_time,
        }
        self.last_press_times = {button: 0 for button in self.debounce_times.keys()}

        # Use lambda functions to defer the evaluation of the button states
        self.buttons = {button: lambda button=button: getattr(pybadger.button, button) for button in
                        self.debounce_times.keys()}
        cleanup()

    def set_debounce_time(self, button_name, debounce_time):
        """
        Set a custom debounce time for a specific button.
        :param button_name:
        :param debounce_time:
        :return:
        """
        if button_name in self.debounce_times:
            self.debounce_times[button_name] = debounce_time

    def button_pressed(self, button_name):
        """
        Check if a button is pressed and has passed the debounce time.
        :param button_name:
        :return:
        """
        current_time = monotonic()  # Get the current time
        if self.buttons[button_name]() and (current_time - self.last_press_times[button_name]) >= self.debounce_times[
            button_name] and self.input_enabled:
            self.last_press_times[button_name] = current_time  # Update the last press time for the button
            return True
        return False

    def up_button(self):
        """
        Check if the up button is pressed and has passed the debounce time.
        :return:
        """
        return self.button_pressed('up')

    def down_button(self):
        """
        Check if the down button is pressed and has passed the debounce time.
        :return:
        """
        return self.button_pressed('down')

    def left_button(self):
        """
        Check if the left button is pressed and has passed the debounce time.
        :return:
        """
        return self.button_pressed('left')

    def right_button(self):
        """
        Check if the right button is pressed and has passed the debounce time.
        :return:
        """
        return self.button_pressed('right')

    def a_button(self):
        """
        Check if the A button is pressed and has passed the debounce time.
        :return:
        """
        return self.button_pressed('a')

    def b_button(self):
        """
        Check if the B button is pressed and has passed the debounce time.
        :return:
        """
        return self.button_pressed('b')

    def start_button(self):
        """
        Check if the start button is pressed and has passed the debounce time.
        :return:
        """
        return self.button_pressed('start')

    def select_button(self):
        """
        Check if the select button is pressed and has passed the debounce time.
        :return:
        """
        return self.button_pressed('select')
