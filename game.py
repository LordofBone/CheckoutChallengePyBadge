from components.audio import AudioEngine
from components.controls import Controls
from components.engine import PlayerStats, RaceEngine
from components.graphics import Display
from components.leds import LEDController
from components.menus import (IntroMenu, MainMenu, TrolleyShopMenu, GarageMenu, TrolleyUpgradesMenu, TrackMenu,
                              CrashMenu, WinMenu, LoseMenu, DrawMenu)

from utils.resource_manager import cleanup


class Application:
    def __init__(self):
        self.current_menu = 'intro'
        self.last_menu = None  # No last menu to start with
        self.menu_passthrough = None  # Used to pass data between menus

        self.root_display = Display()
        self.player_stats = PlayerStats()
        self.controls = Controls()
        self.led_controller = LEDController(led_count=5, brightness=0.01)
        self.audio_engine = AudioEngine()

        # We'll store class references instead of instances
        self.menu_classes = {
            'intro': IntroMenu,
            'main': MainMenu,
            'race': RaceEngine,
            'trolley_shop': TrolleyShopMenu,
            'garage': GarageMenu,
            'trolley_upgrades': TrolleyUpgradesMenu,
            'track_select': TrackMenu,
            'crash_menu': CrashMenu,
            'win_menu': WinMenu,
            'lose_menu': LoseMenu,
            'draw_menu': DrawMenu,
        }
        self.menus = {}  # Empty dictionary to store menu instances

    def menu_controller(self):
        """
        Main menu controller that handles the switching between menus.
        :return:
        """
        while True:
            # Check if the current menu is instantiated; if not, instantiate it
            if self.current_menu not in self.menus:
                self.menus[self.current_menu] = self.menu_classes[self.current_menu](self)

            # Show the current menu
            self.menu_passthrough = self.menus[self.current_menu].show(self.menu_passthrough)

            # Check if the current menu has changed after showing the menu (e.g., if an action in the menu changed
            # the current_menu)
            if self.current_menu != self.last_menu:
                # Clear resources related to the last menu
                if self.last_menu and self.last_menu in self.menus:
                    self.menus[self.last_menu].cleanup_labels_sprites()
                    del self.menus[self.last_menu]  # Remove the instance from the dictionary

                # Update the last menu to the current one after processing
                self.last_menu = self.current_menu

                # Clear the display for the new menu
                self.root_display.clear_main_display_group()

                cleanup()


cleanup()
app = Application()
app.menu_controller()
