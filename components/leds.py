from adafruit_pybadger import pybadger

from utils.resource_manager import cleanup


class LEDController:
    def __init__(self, led_count=5, brightness=0.0):
        self.led_count = led_count
        pybadger.pixels.brightness = brightness
        self.current_colors = [(0, 0, 0)] * led_count  # To store the current colors of the LEDs
        cleanup()

    def set_led_color(self, index, color):
        """
        Set the color of an LED.
        :param index:
        :param color:
        :return:
        """
        if self.current_colors[index] != color:  # Only update if the color is different
            self.current_colors[index] = color
            pybadger.pixels[index] = color
            pybadger.pixels.show()

    def clear_leds(self):
        """
        Clear all the LEDs.
        :return:
        """
        for i in range(self.led_count):
            pybadger.pixels[i] = (0, 0, 0)
        pybadger.pixels.show()
        cleanup()

    def interpolate_color(self, ratio):
        """
        Interpolate color from green to red based on the ratio.
        ratio: float between 0 (green) and 1 (red)
        :return tuple (red, green, blue)
        """
        green_value = int(max(0, 255 * (1 - ratio)))
        red_value = int(max(0, 255 * ratio))
        return red_value, green_value, 0

    def update_progress(self, elapsed_time, total_duration):
        """
        Update the LEDs to indicate the progress of an operation.
        :param elapsed_time:
        :param total_duration:
        :return:
        """
        progress_ratio = elapsed_time / total_duration
        leds_to_light = int(progress_ratio * self.led_count)

        for i in range(self.led_count):
            if i < leds_to_light or (i == leds_to_light and total_duration - elapsed_time <= 10):
                # Calculate the color based on the progress ratio
                color_ratio = i / self.led_count
                color = self.interpolate_color(color_ratio)
                self.set_led_color(i, color)
            else:
                self.set_led_color(i, (0, 0, 0))  # Turn off the remaining LEDs
