from math import log
from random import random, randint, choice, uniform
from time import monotonic

from components.menus import BaseMenu
from components.objects import Block, Block2, Block3, Block4, Block5, WaterSpill, Money, Person, BasicTrolley, \
    SportsTrolley, BigTrolley, SuperTrolley, CarbonFibreWheels, RacingHandle, ScanningComputer, CarbonFibreFrame, \
    NitrousOxide, BrakeUpgrade, ExhaustUpgrade, TurboUpgrade, AirFilterUpgrade, ComputerChipUpgrade, SuspensionUpgrade, \
    TrolleyMovetoWinMenuItem, TrackSelectMenuItem, TrolleyMovetoCrashMenuItem, TrolleyMovetoLoseMenuItem, \
    TrolleyMovetoDrawMenuItem, TrolleyGarageMenuItem, TrolleyShopMenuItem
from utils.resource_manager import cleanup


class AIEngine:
    def __init__(self, track_generator, player_stats):
        self.track_generator = track_generator
        self.player_stats = player_stats

        difficulty_to_trolley = {
            'easy': 'trolley_basic',
            'medium': 'trolley_better',
            'difficult': 'trolley_big',
            'insane': 'trolley_super',
            'performance_test': 'trolley_super'
        }

        trolley_key = difficulty_to_trolley.get(self.player_stats.difficulty, 'trolley_basic')
        trolley_class = self.player_stats.trolley_controller.trolleys.get(trolley_key)
        if trolley_class:
            self.ai_trolley = trolley_class(x=70, y=50, transparent_background=True, pixel_shadow=True,
                                            color_shift=(255, 0, 0))

        self.x_wall_buffer = 5
        self.y_wall_buffer = 25

        self.detection_range = {
            'sides': 10,
            'up': 10,
            'down': 10
        }
        self.move_interval = 0.1
        self.min_distance_ahead = 10
        self.max_distance_ahead = 30
        self.random_movement_chance = 0.075
        self.max_y_position = 35

        self.reset_random_movement()
        self.velocity_x = 0
        self.velocity_y = 0
        self.smoothing_factor = 0.9

        self.ai_last_move_time = 0

        self.ai_trolley_obstacle_drag_speed_x = 3
        self.ai_trolley_obstacle_drag_speed_y = 5

        cleanup()

    def reset_random_movement(self):
        """
        Reset the random movement parameters to their default values
        """
        self.random_move_start_time = 0
        self.random_move_duration = 0
        self.random_direction_x = 0
        self.random_direction_y = 0

    def check_collision(self, sprite1, sprite2):
        """
        Check for collision between two sprites.
        :param sprite1:
        :param sprite2:
        :return:
        """
        return (sprite1.x < sprite2.x + 16 and
                sprite1.x + 16 > sprite2.x and
                sprite1.y < sprite2.y + 16 and
                sprite1.y + 16 > sprite2.y)

    def determine_best_direction(self):
        """
        Determine the best direction for the AI trolley to move.
        :return:
        """
        ai_trolley = self.ai_trolley
        left_obstacles = sum(
            1 for obstacle in self.track_generator.obstacles if obstacle.sprite.x < ai_trolley.sprite.x)
        right_obstacles = sum(
            1 for obstacle in self.track_generator.obstacles if obstacle.sprite.x > ai_trolley.sprite.x)

        if left_obstacles < right_obstacles:
            return -ai_trolley.speed
        elif right_obstacles < left_obstacles:
            return ai_trolley.speed
        else:
            return choice([-ai_trolley.speed, ai_trolley.speed])

    def update_ai_movement(self, current_time, player_trolley):
        """
        Update the AI trolley's movement based on the player's trolley position and obstacles.
        :param current_time:
        :param player_trolley:
        :return:
        """
        if current_time - self.ai_last_move_time > self.move_interval:
            if self.random_move_duration > 0:
                self.velocity_x = self.random_direction_x * self.ai_trolley.speed
                self.velocity_y = self.random_direction_y * self.ai_trolley.speed

                if current_time - self.random_move_start_time >= self.random_move_duration:
                    self.reset_random_movement()
            elif random() < self.random_movement_chance:
                self.random_direction_x = choice([-1, 1])
                self.random_direction_y = choice([-1, 1])
                self.random_move_duration = uniform(1, 5)
                self.random_move_start_time = current_time

            distance_ahead_y = self.ai_trolley.sprite.y - player_trolley.sprite.y

            if distance_ahead_y < self.min_distance_ahead:
                self.velocity_y = -self.ai_trolley.speed

            ai_trolley = self.ai_trolley

            for obstacle in self.track_generator.obstacles + [player_trolley]:
                distance_x, distance_y = self.get_distance(ai_trolley, obstacle)

                if abs(distance_x) < self.detection_range['sides']:
                    if self.detection_range['down'] > distance_y > -self.detection_range['up']:
                        self.set_avoidance_velocity(distance_x, distance_y, ai_trolley, obstacle)
                        if self.check_collision(ai_trolley.sprite, obstacle.sprite):
                            if self.ai_trolley.sprite.y < obstacle.sprite.y + 16:
                                # Move backwards
                                self.velocity_y += self.ai_trolley_obstacle_drag_speed_y
                                # Check if the obstacle is to the left of the AI trolley
                                if obstacle.sprite.x + 16 > self.ai_trolley.sprite.x > obstacle.sprite.x:
                                    if self.ai_trolley.sprite.x + 16 < 160 - (self.x_wall_buffer + 16):
                                        # Move right
                                        self.velocity_x += self.ai_trolley_obstacle_drag_speed_x
                                    else:
                                        # Move left
                                        self.velocity_x = -self.ai_trolley_obstacle_drag_speed_x
                                # Check if the obstacle is to the right of the AI trolley
                                elif (self.ai_trolley.sprite.x + 16 > obstacle.sprite.x and self.ai_trolley.sprite.x
                                      < obstacle.sprite.x + 16):
                                    if self.ai_trolley.sprite.x > (self.x_wall_buffer + 16):
                                        # Move left
                                        self.velocity_x -= self.ai_trolley_obstacle_drag_speed_x
                                    else:
                                        # Move right
                                        self.velocity_x = self.ai_trolley_obstacle_drag_speed_x
                            break

            self.ai_last_move_time = current_time

        ai_trolley = self.ai_trolley
        current_grip = ai_trolley.grip * (1 + log(1 + ai_trolley.weight))
        max_grip_increase = ai_trolley.grip * 0.2
        current_grip = min(ai_trolley.grip + max_grip_increase, current_grip)

        acceleration = ai_trolley.acceleration / (1 + ai_trolley.weight * 0.1)
        deceleration = ai_trolley.deceleration / (1 + max(0.9, ai_trolley.weight * 0.05))

        self.velocity_x *= self.smoothing_factor
        self.velocity_y *= self.smoothing_factor

        if self.velocity_x > 0:
            self.velocity_x = max(0, self.velocity_x - (deceleration * current_grip))
        elif self.velocity_x < 0:
            self.velocity_x = min(0, self.velocity_x + (deceleration * current_grip))

        if self.velocity_y > 0:
            self.velocity_y = max(0, self.velocity_y - (deceleration * current_grip))
        elif self.velocity_y < 0:
            self.velocity_y = min(0, self.velocity_y + (deceleration * current_grip))

        self.velocity_x += acceleration * current_grip
        self.velocity_y += acceleration * current_grip

        self.velocity_x = max(-ai_trolley.speed, min(ai_trolley.speed, self.velocity_x))
        self.velocity_y = max(-ai_trolley.speed, min(ai_trolley.speed, self.velocity_y))

        ai_trolley.sprite.x = int(max(self.x_wall_buffer, min(160 - self.x_wall_buffer - 16,
                                                              ai_trolley.sprite.x + self.velocity_x)))
        ai_trolley.sprite.y = int(max(self.y_wall_buffer, min(128 - self.y_wall_buffer - 16,
                                                              ai_trolley.sprite.y + self.velocity_y)))

    def get_distance(self, ai_trolley, obstacle):
        """
        Calculate the horizontal and vertical distances between the AI trolley and an obstacle.
        :param ai_trolley:
        :param obstacle:
        :return:
        """
        ai_trolley_left = ai_trolley.sprite.x
        ai_trolley_right = ai_trolley.sprite.x + 16
        ai_trolley_top = ai_trolley.sprite.y
        ai_trolley_bottom = ai_trolley.sprite.y + 16

        obstacle_left = obstacle.sprite.x
        obstacle_right = obstacle.sprite.x + 16
        obstacle_top = obstacle.sprite.y
        obstacle_bottom = obstacle.sprite.y + 16

        # Calculate horizontal and vertical distances
        if ai_trolley_right < obstacle_left:  # AI trolley is to the left of the obstacle
            distance_x = obstacle_left - ai_trolley_right
        elif ai_trolley_left > obstacle_right:  # AI trolley is to the right of the obstacle
            distance_x = ai_trolley_left - obstacle_right
        else:  # Overlapping in x-axis
            distance_x = 0

        if ai_trolley_bottom < obstacle_top:  # AI trolley is above the obstacle
            distance_y = obstacle_top - ai_trolley_bottom
        elif ai_trolley_top > obstacle_bottom:  # AI trolley is below the obstacle
            distance_y = ai_trolley_top - obstacle_bottom
        else:  # Overlapping in y-axis
            distance_y = 0

        return distance_x, distance_y

    def set_avoidance_velocity(self, distance_x, distance_y, ai_trolley, obstacle):
        """
        Set the avoidance velocity based on the distance between the AI trolley and an obstacle.
        :param distance_x:
        :param distance_y:
        :param ai_trolley:
        :param obstacle:
        :return:
        """
        if ai_trolley.sprite.x < obstacle.sprite.x:
            self.velocity_x = -ai_trolley.speed
        else:
            self.velocity_x = ai_trolley.speed

        if ai_trolley.sprite.y < obstacle.sprite.y:
            self.velocity_y = -ai_trolley.speed
        else:
            self.velocity_y = ai_trolley.speed


class TrackGenerator:
    def __init__(self, difficulty='easy'):
        self.obstacles = []
        self.max_obstacles = 15
        self.update_counter = 0
        self.update_interval = 1  # Update every frame
        self.track_moving = True
        self.difficulty = difficulty
        self.winning_money = 500

        self.start_time = None  # Track the start time of the race
        self.elapsed_time = 0  # Track the elapsed time
        self.last_cleanup_time = monotonic()  # Initialize last cleanup time

        self.obstacle_classes = {
            'Block': (Block, 0.20),
            'Block2': (Block2, 0.20),
            'Block3': (Block3, 0.15),
            'Block4': (Block4, 0.15),
            'Block5': (Block5, 0.10),
            'WaterSpill': (WaterSpill, 0.08),
            'Money': (Money, 0.05),
            'Person': (Person, 0.07),
        }

        """Set parameters based on the selected difficulty level."""
        if self.difficulty == 'easy':
            self.max_obstacles = 5
            self.race_duration = 60
            self.winning_money = 1500
        elif self.difficulty == 'medium':
            self.max_obstacles = 8
            self.race_duration = 120
            self.winning_money = 4000
        elif self.difficulty == 'difficult':
            self.max_obstacles = 12
            self.race_duration = 180
            self.winning_money = 9000
        elif self.difficulty == 'insane':
            self.max_obstacles = 18
            self.race_duration = 300
            self.winning_money = 20000
        elif self.difficulty == 'performance_test':
            # for testing the performance of the game and how it handles constantly generated objects, has no collisions
            self.max_obstacles = 22
            self.race_duration = 7200
            self.winning_money = 1000000

        # Reset the obstacle list whenever the difficulty changes
        self.obstacles = []
        self.update_counter = 0

        cleanup()

    def check_overlap(self, new_obstacle):
        """
        Checks whether the new obstacle overlaps with any existing obstacles.
        :param new_obstacle:
        :return:
        """
        for existing_obstacle in self.obstacles:
            # Calculate the ending coordinates for comparison without a large buffer.
            existing_right = existing_obstacle.sprite.x + existing_obstacle.width
            existing_bottom = existing_obstacle.sprite.y + existing_obstacle.height
            new_right = new_obstacle.sprite.x + new_obstacle.width
            new_bottom = new_obstacle.sprite.y + new_obstacle.height

            # Check for overlap
            if (new_obstacle.sprite.x < existing_right and
                    new_right > existing_obstacle.sprite.x and
                    new_obstacle.sprite.y < existing_bottom and
                    new_bottom > existing_obstacle.sprite.y):
                return True
        return False

    def cleanup_obstacles(self):
        """
        Remove obstacles that have moved past the bottom of the screen.
        :return:
        """
        # Iterate in reverse to avoid skipping elements after removal
        for i in range(len(self.obstacles) - 1, -1, -1):
            obstacle = self.obstacles[i]
            # Check if the obstacle should be removed (e.g., moved past bottom of screen)
            if obstacle.sprite.y > 128 + 16:  # Adjust condition as necessary
                # Remove from obstacles list
                del self.obstacles[i]
                # Signal that obstacle should be removed from display group as well
                yield obstacle
        cleanup()

    def update(self, total_pause_duration=0):
        """
        Update the track and obstacles.
        :param total_pause_duration:
        :return:
        """
        if self.track_moving:
            if self.start_time is None:
                self.start_time = monotonic()  # Start the timer

            current_time = monotonic() - total_pause_duration

            self.elapsed_time += current_time - self.start_time
            self.start_time = current_time  # Reset start time for continuous tracking

            self.update_counter += 1

            if len(self.obstacles) < self.max_obstacles and self.update_counter % self.update_interval == 0:
                for _ in range(10):  # Try multiple times to place a new obstacle
                    new_x = randint(0, 160 - 16)
                    new_y = randint(-256, 0)

                    options = list(self.obstacle_classes.items())

                    # Sum the weights to get the total weight.
                    total = sum(weight for _, (_, weight) in options)

                    # Generate a random number between 0 and the total weight.
                    r = uniform(0, total)
                    # Initialize the cumulative weight.
                    upto = 0
                    # Iterate over the options.
                    for item, (cls, weight) in options:
                        upto += weight
                        # Check if the random number is less than the current cumulative weight.
                        if upto >= r:
                            # If it is, return the class associated with the current item.
                            obstacle_class = cls
                            break

                    temp_obstacle = obstacle_class(x=new_x, y=new_y, transparent_background=True,
                                                   pixel_shadow=True)

                    if temp_obstacle and not self.check_overlap(temp_obstacle):
                        self.obstacles.append(temp_obstacle)
                        break

            # Move existing obstacles down the screen, regardless of new additions
            if self.update_counter % self.update_interval == 0:
                for obstacle in self.obstacles:
                    obstacle.move(0, 1)

        else:
            self.start_time = None  # Pause the timer


class TrolleyController:
    def __init__(self, player_stats):
        self.player_stats = player_stats

        # Store trolley classes, not instantiated objects
        self.trolleys = {
            'trolley_basic': BasicTrolley,
            'trolley_better': SportsTrolley,
            'trolley_big': BigTrolley,
            'trolley_super': SuperTrolley,
        }

        cleanup()

    def instantiate_trolley(self, trolley_key, transparent_background=True, background_color=0xffffff,
                            pixel_shadow=True, x=70, y=90):
        """
        Helper method to instantiate trolleys as needed.
        :param trolley_key:
        :param transparent_background:
        :param background_color:
        :param pixel_shadow:
        :param x:
        :param y:
        :return:
        """
        trolley_class = self.trolleys.get(self.trolleys[trolley_key].object_id)
        if trolley_class:
            return trolley_class(transparent_background=transparent_background, background_color=background_color,
                                 pixel_shadow=pixel_shadow, x=x, y=y)

    def buy_select_trolley(self, trolley_key):
        """
        Attempt to purchase a trolley.
        :param trolley_key:
        :return:
        """
        if trolley_key.object_id not in self.player_stats.garage:
            if self.player_stats.has_enough_money(self.trolleys[trolley_key.object_id].cost):
                self.player_stats.money_update(self.trolleys[trolley_key.object_id].cost, add=False)
                self.player_stats.garage[self.trolleys[trolley_key.object_id].object_id] = self.instantiate_trolley(
                    self.trolleys[trolley_key.object_id].object_id)
                return_text = "Purchased."
            else:
                return_text = "Not enough money."
        else:
            self.current_trolley = trolley_key.object_id
            return_text = "Selected."

        cleanup()
        return return_text


class UpgradeController:
    def __init__(self, player_stats):
        self.player_stats = player_stats

        self.upgrades = {
            'carbon_fiber_wheel': CarbonFibreWheels,
            'racing_handle': RacingHandle,
            'scanning_computer': ScanningComputer,
            'carbon_fiber_frame': CarbonFibreFrame,
            'nitrous_oxide': NitrousOxide,
            'brake_upgrade': BrakeUpgrade,
            'exhaust_upgrade': ExhaustUpgrade,
            'turbo_upgrade': TurboUpgrade,
            'air_filter_upgrade': AirFilterUpgrade,
            'computer_chip_upgrade': ComputerChipUpgrade,
            'suspension_upgrade': SuspensionUpgrade,
        }

        cleanup()

    def apply_upgrade_to_trolley(self, upgrade):
        """
        Apply an upgrade to the current trolley.
        :param upgrade:
        :return:
        """
        try:
            current_trolley = self.player_stats.garage.get(self.player_stats.trolley_controller.current_trolley)
        except AttributeError:
            return "No Trolley."

        if not current_trolley.upgrades.get(upgrade.object_id):
            if self.player_stats.has_enough_money(upgrade.cost):
                current_trolley.apply_upgrade(upgrade)
                self.player_stats.money_update(upgrade.cost, add=False)
                return_text = "Installed."
            else:
                return_text = "Not enough money."
        else:
            return_text = "Already applied."
        del current_trolley
        cleanup()
        return return_text


class PlayerStats:
    def __init__(self):
        self.money = 500
        self.garage = {}
        self.trolley_controller = TrolleyController(self)
        self.upgrade_controller = UpgradeController(self)
        self.difficulty = 'easy'

        cleanup()

    def set_difficulty(self, difficulty_option):
        """
        Set the game difficulty.
        :param difficulty_option:
        :return:
        """
        self.difficulty = difficulty_option.difficulty

    def has_enough_money(self, amount):
        """
        Check if the player has enough money.

        :param amount: The amount of money to check.
        :return: True if the player has enough money, False otherwise.
        """
        return self.money >= amount

    def money_update(self, amount, add=True):
        """
        Update the player's money. Increase if add is True, decrease otherwise.

        :param amount: The amount by which to update the player's money.
        :param add: A boolean indicating whether to add (True) or subtract (False) the amount.
        """
        if add:
            self.money += amount
        else:
            if self.has_enough_money(amount):  # Only subtract money if the player has enough
                self.money -= amount
            else:
                return "Not enough money."


class RaceEngine(BaseMenu):
    # # Add new variables for trolley movement and speed
    player_dx, player_dy = 0.0, 0.0  # Player's velocity
    ai_dx, ai_dy = 0.0, 0.0  # AI's velocity

    no_trolley_text = "You need to select\na Trolley first.\nPress Start."

    pause_text = "Paused"

    collision_buffer = 2
    water_grip_timer = 0  # Tracks how long the reduced grip should last
    bounce_factor = -0.5  # This value can be adjusted based on desired bounce strength
    trolley_drag_speed_x = 3  # Speed at which the trolley is pushed back when hitting an obstacle
    trolley_drag_speed_y = 4  # Speed at which the trolley is pushed back when hitting an obstacle

    grip_affected = False
    max_grip_multiplier = 1.2  # Maximum allowed grip multiplier
    boost_multiplier = 10
    brake_multiplier = 10

    block_above = block_below = block_left = block_right = False

    acceleration_factor = 1
    deceleration_factor = 1

    # Constants for weight to acceleration/deceleration adjustments
    acceleration_weight_factor = 0.1
    deceleration_weight_factor = 0.05
    min_deceleration_denominator = 0.9  # Minimum value for deceleration denominator to prevent unrealistic values

    grip_factor = 1.0  # Reset grip factor to default

    move_interval = 0.05  # Time between movement updates in seconds

    def __init__(self, app):
        super().__init__(app, background_image='images/floor.bmp')

        self.obstacle_type_handlers = {
            'money': self.handle_money_obstacle,
            'water_spill_1': self.handle_water_spill,
            # Additional obstacle types and their handlers can be added here
        }

    def handle_money_obstacle(self, obstacle):
        """
        Handle the money obstacle.
        :param obstacle:
        :return:
        """
        obstacle.remove(self.track_generator.obstacles)
        self.app.root_display.main_display_group.remove(obstacle.sprite)
        self.app.player_stats.money_update(randint(10, 1000), add=True)

    def handle_water_spill(self, obstacle):
        """
        Handle the water spill obstacle.
        :param obstacle:
        :return:
        """
        self.grip_affected = True
        self.water_grip_timer = self.current_time  # Reset timer every time we hit a new water spill

    def handle_default_obstacle(self, obstacle):
        """
        Handle the default obstacle.
        :param obstacle:
        :return:
        """
        if obstacle.sprite.y > self.player_trolley.sprite.y:
            self.player_dy = -self.bounce_factor * abs(self.player_dy)
            self.block_below = True
        if obstacle.sprite.y < self.player_trolley.sprite.y:
            self.player_dy = self.bounce_factor * abs(self.player_dy)
            self.block_above = True
        if obstacle.sprite.x > self.player_trolley.sprite.x:
            self.player_dx = -self.bounce_factor * abs(self.player_dx)
            self.block_right = True
        if obstacle.sprite.x < self.player_trolley.sprite.x:
            self.player_dx = self.bounce_factor * abs(self.player_dx)
            self.block_left = True

        # Update damage, block movements, etc.
        # Apply the velocity changes if blocks are around
        if self.block_above:
            self.app.player_stats.trolley_dy = self.player_dy
            # Push the trolley backwards and also to the left or right
            self.player_dy += self.trolley_drag_speed_y  # Move backwards
            # Check if the obstacle is to the right of the player trolley
            if self.player_trolley.sprite.x > obstacle.sprite.x:
                if self.player_trolley.sprite.x + 16 < 160 - 16 or self.player_trolley.sprite.y + 16 == 0:
                    # Move right
                    self.player_dx += self.trolley_drag_speed_x
                else:
                    # Move left
                    self.player_dx = -self.trolley_drag_speed_x
            # Check if the obstacle is to the left of the player trolley
            elif self.player_trolley.sprite.x < obstacle.sprite.x + 16 or self.player_trolley.sprite.y + 16 == 0:
                if self.player_trolley.sprite.x > 16:
                    # Move left
                    self.player_dx -= self.trolley_drag_speed_x
                else:
                    # Move right
                    self.player_dx = self.trolley_drag_speed_x

        if self.block_left or self.block_right:
            self.app.player_stats.trolley_dx = self.player_dx

        # Check for damage and apply it based on timing to prevent rapid damage accumulation
        if self.current_time - self.last_damage_time > 0.5:
            self.player_trolley.health -= 20  # Adjust health by some damage value
            self.last_damage_time = self.current_time

    def exit(self, menu):
        """
        Exit
        :param menu:
        :return:
        """
        self.app.root_display.fade_screen('out')
        self.app.controls.set_debounce_time('up', self.app.controls.default_debounce_time)
        self.app.controls.set_debounce_time('down', self.app.controls.default_debounce_time)
        self.app.controls.set_debounce_time('left', self.app.controls.default_debounce_time)
        self.app.controls.set_debounce_time('right', self.app.controls.default_debounce_time)
        self.app.root_display.clear_main_display_group()
        self.app.led_controller.clear_leds()
        self.app.root_display.display.auto_refresh = True
        self.switch_menu(menu, fade=False)
        cleanup()

    def show(self, menu_passthrough=None):
        """
        Update the display and handle user input while processing game functions
        :param menu_passthrough:
        :return:
        """
        self.app.root_display.fade_screen('in')
        try:
            self.player_trolley = self.app.player_stats.trolley_controller.instantiate_trolley(
                self.app.player_stats.trolley_controller.current_trolley, pixel_shadow=True,
                background_color=0xffffff,
                transparent_background=True,
                x=70, y=90)

        except AttributeError:
            if self.app.player_stats.garage == {}:  # Check if the garage is empty
                next_menu = TrolleyShopMenuItem()
            else:
                next_menu = TrolleyGarageMenuItem()
            no_trolley_label = self.app.root_display.label_factory(self.no_trolley_text, (30, 50),
                                                                   color=0xFFFFFF, background_color=0x8132a8)
            self.app.root_display.main_display_group.append(no_trolley_label)
            while not self.app.controls.start_button():
                pass
            self.exit(next_menu)

            return

        self.trolley_x = self.player_trolley.sprite.x * 1.0
        self.trolley_y = self.player_trolley.sprite.y * 1.0

        self.player_trolley.health = self.player_trolley.max_health
        self.player_trolley.speed = self.app.player_stats.garage[
            self.app.player_stats.trolley_controller.current_trolley].speed
        self.player_trolley.acceleration = self.app.player_stats.garage[
            self.app.player_stats.trolley_controller.current_trolley].acceleration
        self.player_trolley.deceleration = self.app.player_stats.garage[
            self.app.player_stats.trolley_controller.current_trolley].deceleration
        self.player_trolley.grip = self.app.player_stats.garage[
            self.app.player_stats.trolley_controller.current_trolley].grip

        self.track_generator = TrackGenerator(self.app.player_stats.difficulty)
        reward = self.track_generator.winning_money
        self.ai_engine = AIEngine(self.track_generator, self.app.player_stats)

        self.paused = False
        self.pause_start_time = 0
        self.total_pause_duration = 0
        self.app.root_display.auto_refresh = False
        self.app.root_display.main_display_group.append(self.player_trolley.sprite)
        self.app.root_display.main_display_group.append(self.ai_engine.ai_trolley.sprite)

        self.app.controls.set_debounce_time('up', 0.0)
        self.app.controls.set_debounce_time('down', 0.0)
        self.app.controls.set_debounce_time('left', 0.0)
        self.app.controls.set_debounce_time('right', 0.0)
        self.track_generator.start_time = monotonic()

        self.last_move_time = monotonic()
        self.last_damage_time = self.last_move_time

        cleanup()

        while True:
            # Start/pause functionality
            if self.app.controls.start_button():
                self.paused = not self.paused
                if self.paused:
                    self.pause_start_time = monotonic()  # Record the pause start time
                    pause_label = self.app.root_display.label_factory(self.pause_text, (60, 60),
                                                                      color=0xFFFFFF, background_color=0x8132a8)
                    self.app.root_display.main_display_group.append(pause_label)
                else:
                    self.total_pause_duration += monotonic() - self.pause_start_time  # Calculate and add pause duration
                    self.app.root_display.main_display_group.remove(pause_label)
                while self.app.controls.start_button():
                    pass
            cleanup()

            # Exiting to menu
            if self.paused and self.app.controls.select_button():
                self.exit(TrackSelectMenuItem())
                break

            if not self.paused:
                self.current_time = monotonic()

                # Update LED progress based on elapsed time
                self.app.led_controller.update_progress(self.track_generator.elapsed_time,
                                                        self.track_generator.race_duration)

                self.block_above = self.block_below = self.block_left = self.block_right = False

                # Update track and obstacles
                self.track_generator.update(self.total_pause_duration)

                # Update AI movement
                self.ai_engine.update_ai_movement(self.current_time, self.player_trolley)

                # Clean up obstacles and remove them from the display group as needed
                for obstacle_to_remove in self.track_generator.cleanup_obstacles():
                    if obstacle_to_remove.sprite in self.app.root_display.main_display_group:
                        self.app.root_display.main_display_group.remove(obstacle_to_remove.sprite)

                # 2. Detect and handle collisions
                for obstacle in self.track_generator.obstacles + [self.ai_engine.ai_trolley]:
                    if obstacle.sprite not in self.app.root_display.main_display_group:
                        self.app.root_display.main_display_group.append(obstacle.sprite)

                    if ((obstacle.sprite.x < self.player_trolley.sprite.x + 16 + self.collision_buffer and
                         obstacle.sprite.x + 16 + self.collision_buffer > self.player_trolley.sprite.x and
                         obstacle.sprite.y < self.player_trolley.sprite.y + 16 + self.collision_buffer and
                         obstacle.sprite.y + 16 + self.collision_buffer > self.player_trolley.sprite.y)
                            and self.track_generator.difficulty != 'performance_test'):
                        # Call the appropriate handler based on the obstacle type
                        handler = self.obstacle_type_handlers.get(obstacle.object_id, self.handle_default_obstacle)
                        handler(obstacle)

                # 3. Update trolley position based on control input and grip
                # Time check to control movement updates
                if self.current_time - self.last_move_time > self.move_interval:
                    # Calculate the grip increase based on weight using log
                    grip_increase = self.player_trolley.grip * log(1 + self.player_trolley.weight)

                    # Cap the grip increase to ensure it doesn't exceed the maximum allowed grip
                    max_grip_increase = self.player_trolley.grip * (self.max_grip_multiplier - 1)
                    limited_grip_increase = min(grip_increase, max_grip_increase)

                    # Calculate the final grip
                    current_grip = (self.player_trolley.grip + limited_grip_increase) * self.grip_factor

                    # Adjust boost and brake factors incrementally for smooth changes
                    if self.app.controls.a_button():
                        self.acceleration_factor += (self.player_trolley.boost_strength * self.boost_multiplier
                                                     - self.acceleration_factor) * 0.1
                    else:
                        self.acceleration_factor += (1 - self.acceleration_factor) * 0.1

                    if self.app.controls.b_button():
                        self.deceleration_factor += (self.player_trolley.brake_strength * self.brake_multiplier
                                                     - self.deceleration_factor) * 0.1
                    else:
                        self.deceleration_factor += (1 - self.deceleration_factor) * 0.1

                    # Update speed limits based on boost
                    max_speed = self.player_trolley.speed * self.acceleration_factor

                    # Calculate adjusted acceleration
                    acceleration = self.player_trolley.acceleration * self.acceleration_factor / (
                            1 + self.player_trolley.weight * self.acceleration_weight_factor)

                    # Calculate adjusted deceleration
                    deceleration = self.player_trolley.deceleration * self.deceleration_factor / (
                            1 + max(self.min_deceleration_denominator,
                                    self.player_trolley.weight * self.deceleration_weight_factor))

                    # Horizontal movement
                    if self.app.controls.left_button() and not self.block_left:
                        self.player_dx = max(-max_speed, self.player_dx - (acceleration * current_grip))
                    elif self.app.controls.right_button() and not self.block_right:
                        self.player_dx = min(max_speed, self.player_dx + (acceleration * current_grip))
                    else:
                        # Apply natural deceleration
                        if self.player_dx > 0:
                            self.player_dx = max(0, self.player_dx - (deceleration * current_grip))
                        elif self.player_dx < 0:
                            self.player_dx = min(0, self.player_dx + (deceleration * current_grip))

                    # Vertical movement
                    if self.app.controls.up_button() and not self.block_above:
                        self.player_dy = max(-max_speed, self.player_dy - (acceleration * current_grip))
                    elif self.app.controls.down_button() and not self.block_below:
                        self.player_dy = min(max_speed, self.player_dy + (acceleration * current_grip))
                    else:
                        # Apply natural deceleration
                        if self.player_dy > 0:
                            self.player_dy = max(0, self.player_dy - (deceleration * current_grip))
                        elif self.player_dy < 0:
                            self.player_dy = min(0, self.player_dy + (deceleration * current_grip))

                    # Update logical position
                    self.trolley_x += self.player_dx
                    self.trolley_y += self.player_dy

                    # Ensure trolley stays within bounds
                    self.trolley_x = max(0, min(self.app.root_display.display.width - 16, self.trolley_x))
                    self.trolley_y = max(0, min(self.app.root_display.display.height - 16, self.trolley_y))

                    # Update actual sprite position
                    self.player_trolley.sprite.x = int(self.trolley_x)
                    self.player_trolley.sprite.y = int(self.trolley_y)

                    self.last_move_time = self.current_time  # Reset movement timer

                # 4. Update game state variables if necessary (e.g., reset blocks, handle grip factor updates)
                # Check if the grip has been affected by a recent water spill
                if self.grip_affected:
                    self.grip_factor = 0.2  # Reduce grip due to water
                if self.grip_affected and self.current_time - self.water_grip_timer > 3.0:
                    self.grip_factor = 1.0
                    self.grip_affected = False  # Reset flag after grip change applied

                self.block_above = self.block_below = self.block_left = self.block_right = False

                if self.player_trolley.health <= 0:
                    self.app.player_stats.money_update(250, add=False)
                    self.exit(TrolleyMovetoCrashMenuItem())
                    return_menu_items = {'repair_cost': 250}
                    return return_menu_items
            if self.track_generator.elapsed_time >= self.track_generator.race_duration:
                # Calculate the reward based on difficulty
                if self.player_trolley.sprite.y < self.ai_engine.ai_trolley.sprite.y:
                    self.app.player_stats.money_update(reward, add=True)
                    self.exit(TrolleyMovetoWinMenuItem())
                    return_menu_items = {'reward': reward}
                    return return_menu_items
                elif self.player_trolley.sprite.y > self.ai_engine.ai_trolley.sprite.y:
                    self.exit(TrolleyMovetoLoseMenuItem())
                    return_menu_items = {}
                    return return_menu_items
                else:
                    reward = reward // 2
                    self.app.player_stats.money_update(reward, add=True)
                    self.exit(TrolleyMovetoDrawMenuItem())
                    return_menu_items = {'reward': reward}
                    return return_menu_items
            # show_free_memory()
            self.app.root_display.display.refresh(minimum_frames_per_second=0, target_frames_per_second=60)
