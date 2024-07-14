from time import monotonic

from components.objects import (BackMenuItem, PressStartMenuItem, TrackSelectMenuItem, TrolleyShopMenuItem,
                                TrolleyGarageMenuItem, UpgradeShopMenuItem, DifficultyMenuItemEasy,
                                DifficultyMenuItemMedium, DifficultyMenuItemDifficult, DifficultyMenuItemInsane,
                                TrolleyCrashMenuItem, TrolleyWinMenuItem,
                                TrolleyLoseMenuItem, TrolleyDrawMenuItem)
from utils.resource_manager import cleanup


class BaseMenu:
    def __init__(self, app, background_image=None):
        self.app = app
        self.app.root_display.fade_screen('instant_out')
        self.menu_tune = None
        self.selected_index = 0
        self.visible_start_index = 0  # First index of the visible menu items
        self.item_selection_changed = False
        self.menu_options = []
        self.previous_menu = "main"
        self.first_run = True
        self.labels = {}  # Stores all labels currently on screen
        self.sprites = {}  # Stores all sprites currently on screen
        self.scrolling_text = True
        self.scroll_offset = 0  # Offset for scrolling text
        self.last_scroll_time = 0  # Time when we last scrolled text
        self.max_text_length = 18  # Maximum characters to display before scrolling
        # example colours: black: 0x000000, grey: 0x808080, light grey: 0xC0C0C0, white: 0xFFFFFF, red: 0xeb3d34,
        # purple: 0x8132a8
        self.text_colour = 0xFFFFFF
        self.text_background_colour = 0x8132a8
        self.text_position = (10, 10)
        self.notification_showing = False
        self.notification_root_text = ""
        self.sprite_x = 130
        self.sprite_y = 20
        self.sprite_y_offset = 8
        self.label_offset = 20

        # todo: move all combination logic into controls.py
        self.combination = []
        self.button_sequence = []
        self.combinations = [
            {'combination': ['up', 'down', 'left', 'right', 'up', 'up', 'select'], 'callback': self.money_cheat},
        ]

        # Define function map
        self.function_map = {
            'buy_trolley': app.player_stats.trolley_controller.buy_select_trolley,
            'upgrade_trolley': app.player_stats.upgrade_controller.apply_upgrade_to_trolley,
            'switch_menu': self.switch_menu,
            'change_difficulty': app.player_stats.set_difficulty,
            'money_update': app.player_stats.money_update,
        }

        self.notification_label = None
        self.scrolling_notification = True
        self.notification_start_time = None
        self.notification_duration = 3  # Duration in seconds for which the notification is visible
        self.notification_min_duration = 0.1  # Minimum duration for the notification to be visible

        if background_image:
            self.app.root_display.show_image(background_image)

        cleanup()

    def show(self, previous_menu_items=None):
        """
        Display the menu on the screen.
        :param previous_menu_items:
        :return:
        """
        self.app.controls.input_enabled = False
        while True:
            if self.check_inputs():
                return

            # Update the scroll offset for the selected menu item
            current_time = monotonic()
            if current_time - self.last_scroll_time > 0.2:
                self.scroll_offset += 1  # Move text one character to the left
                self.last_scroll_time = current_time

            menu_diff = False

            if self.check_inputs():
                return

            # Generate the new set of visible menu options
            visible_options = self.menu_options[
                              self.visible_start_index:self.visible_start_index + 4]

            # Assume a dictionary has been formed from these options
            options_dict = {option.menu_id: option for option in visible_options}

            if self.check_inputs():
                return

            # Get the list of dictionary keys
            visible_keys = list(options_dict.keys())

            existing_keys = list(self.labels.keys())

            order_difference = any(x != y for x, y in zip(visible_keys, existing_keys))

            if order_difference or existing_keys == []:
                self.cleanup_labels_sprites()
                menu_diff = True
            else:
                self.app.controls.input_enabled = True

            if self.check_inputs():
                return

            for i, instance in enumerate(visible_options):
                if self.item_selection_changed:
                    self.scroll_offset = 0
                    self.item_selection_changed = False

                option = instance(
                    transparent_background=False,
                    background_color=0x8132a8,
                    pixel_shadow=True,
                    previous_menu_items=previous_menu_items,
                )

                scroll_label = False

                if self.check_inputs():
                    return

                # todo: make this more menu item agnostic
                if hasattr(option, 'cost'):
                    base_text = f"{option.name} - ${option.cost}"
                else:
                    base_text = option.name
                if i == (self.selected_index - self.visible_start_index):
                    prefix = '>'
                    self.current_option = option
                    if not self.notification_showing:
                        scroll_label = True
                else:
                    prefix = ' '
                    scroll_label = False

                if self.scrolling_text:
                    text = prefix + self.format_option(base_text,
                                                       self.visible_start_index + i,
                                                       scroll=scroll_label,
                                                       max_text_length=self.max_text_length)
                else:
                    text = prefix + base_text

                label_key = option.menu_id

                if self.check_inputs():
                    return

                if menu_diff:
                    label_y_position = self.text_position[1] + i * self.label_offset
                    self.labels[label_key] = self.app.root_display.label_factory(text,
                                                                                 (self.text_position[0],
                                                                                  label_y_position),
                                                                                 color=self.text_colour,
                                                                                 background_color=self.text_background_colour)
                    self.app.root_display.main_display_group.append(self.labels[label_key])

                    if self.check_inputs():
                        return

                    # Handle sprites
                    if hasattr(option, 'sprite'):
                        if option.sprite.icon:
                            sprite_key = option.menu_id

                            option.sprite.x = self.sprite_x
                            option.sprite.y = label_y_position - self.sprite_y_offset
                            self.sprites[sprite_key] = option.sprite

                            self.app.root_display.main_display_group.append(self.sprites[sprite_key])

                            if self.check_inputs():
                                return
                else:
                    selected_item = self.labels[label_key]
                    for index, item in enumerate(self.app.root_display.main_display_group):
                        if item == selected_item:
                            self.app.root_display.main_display_group[index].text = text

                del option
                cleanup()

            if self.check_inputs():
                return

            if self.notification_showing:
                self.notification_label.text = self.notification_root_text
                """Update the notification display (remove it if the duration has passed)."""
                if self.notification_label is not None and self.notification_start_time is not None:
                    # Check if the notification duration has passed
                    if monotonic() - self.notification_start_time > self.notification_duration:
                        self.close_notification()

            if self.check_inputs():
                return

            if self.first_run:
                self.first_run = False
                self.app.root_display.fade_screen('in')
                if self.menu_tune:
                    self.app.audio_engine.play_tune(self.menu_tune)

            cleanup()

    def format_option(self, option, index, scroll=True, max_text_length=None):
        """
        Format the menu option text for display, scrolling if necessary.
        :param option:
        :param index:
        :param scroll:
        :param max_text_length:
        :return:
        """
        if max_text_length is None:
            max_text_length = self.max_text_length
        # Format menu option text for display, scrolling if necessary
        if index == self.selected_index and len(option) > max_text_length and scroll:
            # Scroll the selected option if it's too long
            start = self.scroll_offset % len(option)  # Calculate the start position for visible text
            visible_text = (option + '   ' + option)[
                           start:start + max_text_length]  # Add spaces for readability at end
            return visible_text
        else:
            # No scrolling needed, just truncate if too long
            return option[:max_text_length]

    def check_inputs(self):
        """
        Check for button inputs and execute the corresponding functions.
        :return:
        """
        button_pressed = False

        if self.app.controls.up_button():
            self.update_button_sequence('up')
            if self.on_up():
                button_pressed = True
        elif self.app.controls.down_button():
            self.update_button_sequence('down')
            if self.on_down():
                button_pressed = True
        elif self.app.controls.left_button():
            self.update_button_sequence('left')
            if self.on_left():
                button_pressed = True
        elif self.app.controls.right_button():
            self.update_button_sequence('right')
            if self.on_right():
                button_pressed = True
        elif self.app.controls.a_button():
            self.update_button_sequence('a')
            if self.on_a():
                button_pressed = True
        elif self.app.controls.b_button():
            self.update_button_sequence('b')
            if self.on_b():
                button_pressed = True
        elif self.app.controls.start_button():
            self.update_button_sequence('start')
            if self.on_start():
                button_pressed = True
        elif self.app.controls.select_button():
            self.update_button_sequence('select')
            if self.on_select():
                button_pressed = True
        if button_pressed:
            if self.notification_showing and monotonic() - self.notification_start_time > self.notification_min_duration:
                self.close_notification()
            return True
        else:
            return False

    def show_notification(self, message="test_notification", scroll=True):
        """
        Display a temporary notification message on the screen.
        :param message:
        :param scroll:
        :return:
        """
        if type(message) is str:
            if self.notification_label is not None:
                self.close_notification()
            else:
                self.notification_root_text = message
                # Create a new label for the notification
                self.notification_label = self.app.root_display.label_factory(text=message, pos=(10, 110),
                                                                              color=self.text_colour,
                                                                              background_color=self.text_background_colour)
                self.app.root_display.main_display_group.append(self.notification_label)
                self.notification_start_time = monotonic()
                self.notification_showing = True
        else:
            pass

    def close_notification(self):
        """
        Close the current notification message.
        :return:
        """
        self.app.root_display.main_display_group.remove(self.notification_label)
        self.notification_label = None
        self.notification_start_time = None
        self.notification_showing = False
        self.scroll_offset = 0
        cleanup()

    def cleanup_labels_sprites(self):
        """
        Remove all labels and sprites from the screen.
        :return:
        """
        for label in self.labels.values():
            if label in self.app.root_display.main_display_group:
                self.app.root_display.main_display_group.remove(label)
        for sprite in self.sprites.values():
            if sprite in self.app.root_display.main_display_group:
                self.app.root_display.main_display_group.remove(sprite)
        self.labels.clear()
        self.sprites.clear()
        cleanup()

    def switch_menu(self, menu_name, fade=True):
        """
        Switch to a different menu.
        :param menu_name:
        :param fade:
        :return:
        """
        if fade:
            self.app.root_display.fade_screen('out')
        if menu_name.object_id == 'previous_menu':
            self.app.current_menu = self.previous_menu
        else:
            self.app.current_menu = menu_name.object_id
        self.previous_menu = self.app.current_menu
        cleanup()
        return True

    def money_cheat(self):
        """
        Activate the money cheat.
        :return:
        """
        self.app.player_stats.money_update(10000)
        self.show_notification("Money cheat activated!")

    def check_combination(self):
        """
        Check the button sequence for any matching combinations.
        :return:
        """
        # If the sequence has exceeded 20 button presses, reset the sequence
        if len(self.button_sequence) > 20:
            self.button_sequence.clear()

        for combo in self.combinations:
            self.combination, callback = combo['combination'], combo['callback']
            if len(self.button_sequence) >= len(self.combination):
                if self.button_sequence[-len(self.combination):] == self.combination:
                    callback()  # Call the custom function
                    self.button_sequence.clear()  # Reset the button sequence after a successful match
                    break  # Stop checking other combinations
                # Move the partial combination check and clearing logic outside the loop
        else:  # This 'else' belongs to the 'for' loop and executes if the loop wasn't broken (no match found)
            # If the last sequence doesn't match or isn't a partial match for any combination, consider clearing
            partial_match_found = any(
                self.combination[:len(self.button_sequence)] == self.button_sequence for combination in
                self.combinations)
            if not partial_match_found and len(self.button_sequence) >= max(
                    len(c['combination']) for c in self.combinations):
                # Clear only if there's no partial match and the sequence is as long as the longest combination
                self.button_sequence.clear()

    def update_button_sequence(self, button):
        """
        Update the button sequence and check for any matching combinations.
        :param button:
        :return:
        """
        # Add the button to the sequence and check the combination
        self.button_sequence.append(button)
        self.check_combination()

    def on_up(self):
        """
        Move the selection up in the menu.
        :return:
        """
        self.selected_index -= 1
        # Rollover to the bottom if we reach the top
        if self.selected_index < 0:
            self.selected_index = len(self.menu_options) - 1
            self.visible_start_index = max(0, len(self.menu_options) - 4)

        self.update_visible_start_index()

        return True

    def on_down(self):
        """
        Move the selection down in the menu.
        :return:
        """
        self.selected_index += 1
        # Rollover to the top if we reach the bottom
        if self.selected_index >= len(self.menu_options):
            self.selected_index = 0
            self.visible_start_index = 0

        self.update_visible_start_index()

        return True

    def update_visible_start_index(self):
        """
        Update the visible start index based on the selected index.
        :return:
        """
        # Update visible start index if necessary (for scrolling the menu)
        if self.selected_index < self.visible_start_index:
            self.visible_start_index = self.selected_index
        elif self.selected_index >= self.visible_start_index + 4:
            self.visible_start_index = self.selected_index - 4 + 1
        self.item_selection_changed = True

    def on_left(self):
        """
        Optionally implemented by subclasses.
        :return:
        """
        pass

    def on_right(self):
        """
        Optionally implemented by subclasses.
        :return:
        """
        pass

    def on_a(self):
        """
        By default, selects current menu item, but function can be optionally changed by subclasses.
        :return:
        """
        self.select_option()
        return True

    def on_b(self):
        """
        Optionally implemented by subclasses.
        :return:
        """
        pass

    def on_start(self):
        """
        Optionally implemented by subclasses.
        :return:
        """
        pass

    def on_select(self):
        """
        Optionally implemented by subclasses.
        :return:
        """
        self.show_notification(message=f"Money: ${self.app.player_stats.money}", scroll=False)
        return True

    def select_option(self):
        """
        Executes the action associated with the currently selected menu option.
        :return:
        """
        cleanup()
        for actions in self.current_option.actions:
            return_text = self.function_map[actions](self.current_option)
            self.show_notification(return_text)  # Display the return text as a notification
        cleanup()


class IntroMenu(BaseMenu):
    def __init__(self, app):
        super().__init__(app, background_image='images/intro_background.bmp')
        self.menu_options = [PressStartMenuItem]

        self.text_position = (45, 115)
        self.text_background_colour = 0xFA3871

        self.menu_tune = self.app.audio_engine.main_theme
        cleanup()

    def on_up(self):
        """
        Override the default behavior to prevent moving the selection.
        :return:
        """
        pass

    def on_down(self):
        """
        Override the default behavior to prevent moving the selection.
        :return:
        """
        pass

    def on_a(self):
        """
        Override the default behavior to switch to the main menu.
        :return:
        """
        pass

    def on_start(self):
        """
        Override the default behavior to switch to the main menu.
        :return:
        """
        self.select_option()
        return True

    def on_select(self):
        """
        Override the default behavior to prevent showing the money.
        :return:
        """
        pass


class MainMenu(BaseMenu):
    def __init__(self, app):
        super().__init__(app, background_image='images/main_menu_background.bmp')
        self.menu_options = [
            TrackSelectMenuItem,
            TrolleyShopMenuItem,
            TrolleyGarageMenuItem,
            UpgradeShopMenuItem,
        ]
        cleanup()


class TrackMenu(BaseMenu):
    def __init__(self, app):
        super().__init__(app, background_image='images/track_menu_background.bmp')
        self.menu_options = [
            DifficultyMenuItemEasy,
            DifficultyMenuItemMedium,
            DifficultyMenuItemDifficult,
            DifficultyMenuItemInsane,
        ]

        self.menu_options.append(BackMenuItem)

        cleanup()


class CrashMenu(BaseMenu):
    def __init__(self, app):
        super().__init__(app, background_image='images/trolley_crash_background.bmp')
        self.menu_options = [
            TrolleyCrashMenuItem,
        ]

        self.max_text_length = 23

        cleanup()


class WinMenu(BaseMenu):
    def __init__(self, app):
        super().__init__(app, background_image='images/winning_background.bmp')
        self.menu_options = [
            TrolleyWinMenuItem,
        ]

        self.max_text_length = 23

        cleanup()


class LoseMenu(BaseMenu):
    def __init__(self, app):
        super().__init__(app, background_image='images/losing_background.bmp')
        self.menu_options = [
            TrolleyLoseMenuItem,
        ]

        self.max_text_length = 23

        cleanup()


class DrawMenu(BaseMenu):
    def __init__(self, app):
        super().__init__(app, background_image='images/drawing_background.bmp')
        self.menu_options = [
            TrolleyDrawMenuItem,
        ]

        self.max_text_length = 23

        cleanup()


class GarageMenu(BaseMenu):
    def __init__(self, app):
        super().__init__(app, background_image='images/garage_background.bmp')
        # Dynamically generate menu options based on the trolleys in the garage
        self.menu_options = []

        for trolley_id in app.player_stats.garage.keys():
            if trolley_id in app.player_stats.trolley_controller.trolleys:
                trolley_class = app.player_stats.trolley_controller.trolleys[trolley_id]
                self.menu_options.append(trolley_class)

        # Add 'Back' option at the end as a dictionary
        self.menu_options.append(BackMenuItem)

        cleanup()


class TrolleyShopMenu(BaseMenu):
    def __init__(self, app):
        super().__init__(app, background_image='images/trolley_shop_background.bmp')

        for trolley_class in app.player_stats.trolley_controller.trolleys.values():
            self.menu_options.append(trolley_class)

        self.menu_options.append(BackMenuItem)

        cleanup()


class TrolleyUpgradesMenu(BaseMenu):
    def __init__(self, app):
        super().__init__(app, background_image='images/trolley_upgrade_background.bmp')
        for upgrade_class in app.player_stats.upgrade_controller.upgrades.values():
            self.menu_options.append(upgrade_class)

        self.menu_options.append(BackMenuItem)

        cleanup()
