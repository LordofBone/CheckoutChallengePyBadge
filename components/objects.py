from components.graphics import sprite_extractor
from utils.resource_manager import cleanup


class SpriteFunctions:
    def __init__(self, object_id, x=70, y=-16, width=None, height=None, pixel_shadow=True, background_color=0xffffff,
                 transparent_background=False, shadow_angle=135, shadow_strength=1, color_shift=(0, 0, 0),
                 **kwargs):
        self.object_id = object_id
        self.sprite = sprite_extractor.get_sprite(self.object_id, pixel_shadow=pixel_shadow,
                                                  transparent_background=transparent_background,
                                                  background_color=background_color, shadow_angle=shadow_angle,
                                                  shadow_strength=shadow_strength, color_shift=color_shift)
        self.width = width or sprite_extractor.sprite_width  # Use provided width or default from extractor
        self.height = height or sprite_extractor.sprite_height  # Use provided height or default from extractor
        self.sprite.x = x
        self.sprite.y = y

    def move(self, dx, dy):
        """
        Move the sprite by the specified amount.
        :param dx:
        :param dy:
        :return:
        """
        self.sprite.x += dx
        self.sprite.y += dy

    def remove(self, obstacles):
        """
        Remove the sprite from the obstacles list.
        :param obstacles:
        :return:
        """
        obstacles.remove(self)


class Block(SpriteFunctions):
    def __init__(self, **kwargs):
        super().__init__(object_id="block_1", **kwargs)


class Block2(SpriteFunctions):
    def __init__(self, **kwargs):
        super().__init__(object_id="block_2", **kwargs)


class Block3(SpriteFunctions):
    def __init__(self, **kwargs):
        super().__init__(object_id="block_3", **kwargs)


class Block4(SpriteFunctions):
    def __init__(self, **kwargs):
        super().__init__(object_id="block_4", **kwargs)


class Block5(SpriteFunctions):
    def __init__(self, **kwargs):
        super().__init__(object_id="block_5", **kwargs)


class WaterSpill(SpriteFunctions):
    def __init__(self, **kwargs):
        super().__init__(object_id="water_spill_1", **kwargs)


class Sign(SpriteFunctions):
    def __init__(self, **kwargs):
        super().__init__(object_id="sign", **kwargs)


class Person(SpriteFunctions):
    def __init__(self, **kwargs):
        super().__init__(object_id="person", **kwargs)


class Money(SpriteFunctions):
    def __init__(self, **kwargs):
        super().__init__(object_id="money", **kwargs)


class TrolleyObject(SpriteFunctions):
    trolley_properties = {}

    def __init__(self, **kwargs):
        super().__init__(self.object_id, **kwargs)

        for prop, value in self.trolley_properties.items():
            setattr(self, prop, value)

        self.max_health = self.trolley_properties['max_health']
        self.health = self.max_health
        self.weight = self.trolley_properties['base_weight']
        self.speed = self.trolley_properties['base_speed']
        self.current_speed = 0
        self.acceleration = self.trolley_properties['base_acceleration']
        self.deceleration = self.trolley_properties['base_deceleration']
        self.grip = self.trolley_properties['base_grip']
        self.brake_strength = self.trolley_properties['base_brake_strength']
        self.boost_strength = self.trolley_properties['base_boost_strength']

        self.upgrades = {
            'carbon_fibre_wheels': False,
            'racing_handle': False,
            'scanning_computer': False,
            'carbon_fibre_frame': False,
            'nitrous_oxide': False,
            'brake_upgrade': False,
            'exhaust_upgrade': False,
            'turbo_upgrade': False,
            'air_filter_upgrade': False,
            'computer_chip_upgrade': False,
            'suspension_upgrade': False,
        }

        self.actions = ['buy_trolley']

        cleanup()

    # todo: make this dynamically apply stats rather than list them all out row by row
    def apply_upgrade(self, upgrade):
        """
        Apply the upgrade to the trolley.
        :param upgrade:
        :return:
        """
        if upgrade.object_id in self.upgrades and not self.upgrades[upgrade.object_id]:
            self.upgrades[upgrade.object_id] = True  # Mark the upgrade as applied

            self.max_health += upgrade.max_health
            self.weight += upgrade.weight
            self.speed += upgrade.speed
            self.current_speed = 0
            self.acceleration += upgrade.acceleration
            self.deceleration += upgrade.deceleration
            self.grip += upgrade.grip
            self.brake_strength += upgrade.brake_strength
            self.boost_strength += upgrade.boost_strength

        cleanup()


# Trolley Classes

class BasicTrolley(TrolleyObject):
    menu_id = 27
    object_id = 'trolley_basic'
    cost = 100
    name = 'CartMaster 1000 by BudgetMart'
    trolley_properties = {
        'max_health': 120,
        'base_weight': 36,
        'base_speed': 1.8,
        'base_acceleration': 0.5,
        'base_deceleration': 0.35,
        'base_grip': 0.2,
        'base_boost_strength': 1.5,
        'base_brake_strength': 1.4,
    }


class SportsTrolley(TrolleyObject):
    menu_id = 28
    object_id = 'trolley_better'
    cost = 5000
    name = 'Speedy Shopper by QuickCart Co.'
    trolley_properties = {
        'max_health': 80,
        'base_weight': 28,
        'base_speed': 2.4,
        'base_acceleration': 0.7,
        'base_deceleration': 0.5,
        'base_grip': 0.38,
        'base_boost_strength': 1.8,
        'base_brake_strength': 1.6,
    }


class BigTrolley(TrolleyObject):
    menu_id = 29
    object_id = 'trolley_big'
    cost = 10000
    name = 'Mega Mover by BulkBuy'
    trolley_properties = {
        'max_health': 300,
        'base_weight': 80,
        'base_speed': 2.04,
        'base_acceleration': 0.8,
        'base_deceleration': 0.4,
        'base_grip': 0.3,
        'base_boost_strength': 1.2,
        'base_brake_strength': 1.7,
    }


class SuperTrolley(TrolleyObject):
    menu_id = 30
    object_id = 'trolley_super'
    cost = 20000
    name = 'Turbo Trolley by HyperMart'
    trolley_properties = {
        'max_health': 250,
        'base_weight': 30,
        'base_speed': 2.52,
        'base_acceleration': 1.0,
        'base_deceleration': 0.5,
        'base_grip': 0.18,
        'base_boost_strength': 2.4,
        'base_brake_strength': 2.2,
    }


class UpgradeObject(SpriteFunctions):
    upgrade_properties = {}

    def __init__(self, **kwargs):
        super().__init__(self.upgrade_properties['object_id'], **kwargs)
        self.actions = ['upgrade_trolley']
        for prop, value in self.upgrade_properties.items():
            setattr(self, prop, value)


# Upgrade Classes

class CarbonFibreWheels(UpgradeObject):
    menu_id = 16
    upgrade_properties = {
        'object_id': 'carbon_fibre_wheels',
        'max_health': 35,
        'weight': -6,
        'speed': 0.05,
        'acceleration': 0.0,
        'deceleration': 0.35,
        'grip': 0.2,
        'boost_strength': 0.0,
        'brake_strength': 0.4,
        'cost': 700,
        'name': 'Carbon Fibre Wheels'
    }


class RacingHandle(UpgradeObject):
    menu_id = 17
    upgrade_properties = {
        'object_id': 'racing_handle',
        'max_health': 20,
        'weight': -4,
        'speed': 0.075,
        'acceleration': 0.0,
        'deceleration': 0.15,
        'grip': 0.22,
        'boost_strength': 0.0,
        'brake_strength': 0.0,
        'cost': 1000,
        'name': 'Racing Handle'
    }


class ScanningComputer(UpgradeObject):
    menu_id = 18
    upgrade_properties = {
        'object_id': 'scanning_computer',
        'max_health': 0,
        'weight': 0,
        'speed': 0.025,
        'acceleration': 0.05,
        'deceleration': 0.05,
        'grip': 0.0,
        'boost_strength': 0.0,
        'brake_strength': 0.0,
        'cost': 2000,
        'name': 'Scanning Computer'
    }


class CarbonFibreFrame(UpgradeObject):
    menu_id = 19
    upgrade_properties = {
        'object_id': 'carbon_fibre_frame',
        'max_health': 120,
        'weight': -12,
        'speed': 0.04,
        'acceleration': 0.075,
        'deceleration': 0.175,
        'grip': 0.0,
        'boost_strength': 0.0,
        'brake_strength': 0.0,
        'cost': 5000,
        'name': 'Carbon Fibre Frame'
    }


class NitrousOxide(UpgradeObject):
    menu_id = 20
    upgrade_properties = {
        'object_id': 'nitrous_oxide',
        'max_health': 0,
        'weight': 15,
        'speed': 0.06,
        'acceleration': 0.3,
        'deceleration': -0.45,
        'grip': 0.0,
        'boost_strength': 0.2,
        'brake_strength': 0.0,
        'cost': 6000,
        'name': 'Nitrous Oxide'
    }


class BrakeUpgrade(UpgradeObject):
    menu_id = 21
    upgrade_properties = {
        'object_id': 'brake_upgrade',
        'max_health': 0,
        'weight': 0,
        'speed': 0.0,
        'acceleration': 0.0,
        'deceleration': 0.25,
        'grip': 0.0,
        'boost_strength': 0.0,
        'brake_strength': 0.35,
        'cost': 500,
        'name': 'Brake Upgrade'
    }


class ExhaustUpgrade(UpgradeObject):
    menu_id = 22
    upgrade_properties = {
        'object_id': 'exhaust_upgrade',
        'max_health': 0,
        'weight': 10,
        'speed': 0.02,
        'acceleration': 0.25,
        'deceleration': 0.00,
        'grip': 0.00,
        'boost_strength': 0.12,
        'brake_strength': 0.0,
        'cost': 800,
        'name': 'Exhaust Upgrade'
    }


class TurboUpgrade(UpgradeObject):
    menu_id = 23
    upgrade_properties = {
        'object_id': 'turbo_upgrade',
        'max_health': 0,
        'weight': 55,
        'speed': 0.025,
        'acceleration': 0.2,
        'deceleration': -0.5,
        'grip': 0.0,
        'boost_strength': 0.15,
        'brake_strength': 0.0,
        'cost': 4500,
        'name': 'Turbo Upgrade'
    }


class AirFilterUpgrade(UpgradeObject):
    menu_id = 24
    upgrade_properties = {
        'object_id': 'air_filter_upgrade',
        'max_health': 0,
        'weight': 0,
        'speed': 0.01,
        'acceleration': 0.015,
        'deceleration': 0.0,
        'grip': 0.0,
        'boost_strength': 0.02,
        'brake_strength': 0.0,
        'cost': 350,
        'name': 'Air Filter Upgrade'
    }


class ComputerChipUpgrade(UpgradeObject):
    menu_id = 25
    upgrade_properties = {
        'object_id': 'computer_chip_upgrade',
        'max_health': 0,
        'weight': 0,
        'speed': 0.02,
        'acceleration': 0.025,
        'deceleration': 0.03,
        'grip': 0.0,
        'boost_strength': 0.15,
        'brake_strength': 0.0,
        'cost': 2500,
        'name': 'Computer Chip Upgrade'
    }


class SuspensionUpgrade(UpgradeObject):
    menu_id = 26
    upgrade_properties = {
        'object_id': 'suspension_upgrade',
        'max_health': 0,
        'weight': 0,
        'speed': 0.0,
        'acceleration': 0.025,
        'deceleration': 0.085,
        'grip': 0.15,
        'boost_strength': 0.0,
        'brake_strength': 0.5,
        'cost': 700,
        'name': 'Suspension Upgrade'
    }


class BackMenuItem:
    name = "Back"
    actions = ['switch_menu']
    object_id = 'previous_menu'

    menu_id = 1


class PressStartMenuItem:
    name = "Press Start"
    actions = ['switch_menu']
    object_id = 'main'

    menu_id = 2


class TrackSelectMenuItem:
    name = "Track Select"
    actions = ['switch_menu']
    object_id = 'track_select'

    menu_id = 3


class TrolleyShopMenuItem:
    name = "Trolley Shop"
    actions = ['switch_menu']
    object_id = 'trolley_shop'

    menu_id = 4


class TrolleyGarageMenuItem:
    name = "Trolley Garage"
    actions = ['switch_menu']
    object_id = 'garage'

    menu_id = 5


class UpgradeShopMenuItem:
    name = "Upgrade Shop"
    actions = ['switch_menu']
    object_id = 'trolley_upgrades'

    menu_id = 6


class DifficultyMenuItemEasy:
    actions = ['switch_menu', "change_difficulty"]
    object_id = 'race'
    difficulty = 'easy'
    name = 'Bargain Hunt - Prize: $1500'

    menu_id = 7


class DifficultyMenuItemMedium:
    actions = ['switch_menu', "change_difficulty"]
    object_id = 'race'
    difficulty = 'medium'
    name = 'Everyday Shopper - Prize: $4000'

    menu_id = 8


class DifficultyMenuItemDifficult:
    actions = ['switch_menu', "change_difficulty"]
    object_id = 'race'
    difficulty = 'difficult'
    name = 'Black Friday Frenzy - Prize: $9000'

    menu_id = 9


class DifficultyMenuItemInsane:
    actions = ['switch_menu', "change_difficulty"]
    object_id = 'race'
    difficulty = 'insane'
    name = 'Clearance Chaos - Prize: $20000'

    menu_id = 10


class TrolleyMovetoCrashMenuItem:
    name = None
    actions = ['switch_menu']
    object_id = 'crash_menu'

    menu_id = 12


class TrolleyCrashMenuItem:
    actions = ['switch_menu']
    object_id = 'main'

    menu_id = 13

    def __init__(self, **kwargs):
        self.name = f"You crashed! Repairs cost ${kwargs['previous_menu_items']['repair_cost']}"


class TrolleyMovetoWinMenuItem:
    name = None
    actions = ['switch_menu']
    object_id = 'win_menu'

    menu_id = 14


class TrolleyWinMenuItem:
    actions = ['switch_menu']
    object_id = 'main'

    menu_id = 15

    def __init__(self, **kwargs):
        self.name = f"You win! Prize money: ${kwargs['previous_menu_items']['reward']}"


class TrolleyMovetoLoseMenuItem:
    name = None
    actions = ['switch_menu']
    object_id = 'lose_menu'

    menu_id = 31


class TrolleyLoseMenuItem:
    actions = ['switch_menu']
    object_id = 'main'

    menu_id = 32

    def __init__(self, **kwargs):
        self.name = f"You lost! Better luck next time!"


class TrolleyMovetoDrawMenuItem:
    name = None
    actions = ['switch_menu']
    object_id = 'draw_menu'

    menu_id = 31


class TrolleyDrawMenuItem:
    actions = ['switch_menu']
    object_id = 'main'

    menu_id = 33

    def __init__(self, **kwargs):
        self.name = f"You draw! You split the prize money: ${kwargs['previous_menu_items']['reward']}"
