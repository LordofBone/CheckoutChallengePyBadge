from adafruit_display_text import label
from adafruit_imageload import load as imageload
from board import DISPLAY as board_display
from displayio import Bitmap as display_bitmap
from displayio import Group as display_group
from displayio import OnDiskBitmap as display_on_disk_bitmap
from displayio import Palette as display_palette
from displayio import TileGrid as display_tilegrid
from terminalio import FONT as terminalio_font
from time import sleep

from utils.resource_manager import cleanup


class Display:
    def __init__(self):
        self.display = board_display
        self.main_display_group = display_group()
        self.display.root_group = self.main_display_group
        self.full_brightness = 0.75
        cleanup()

    def fade_screen(self, direction='in', steps=100, delay=0.0025):
        """ Gradually change the brightness of the screen.

        Args: direction (str): 'in' to fade in, 'out' to fade out, 'instant_in' to instantly turn on, 'instant_out'
        to instantly turn off. steps (int): Number of steps to fade in or out. Higher steps give smoother
        transitions. delay (float): Time delay between each step in seconds.

        Returns: None
        """
        if direction == 'instant_in':
            self.display.brightness = self.full_brightness
        elif direction == 'instant_out':
            self.display.brightness = 0
        elif direction == 'in':
            for b in range(steps):
                self.display.brightness = b / steps * self.full_brightness
                sleep(delay)
        elif direction == 'out':
            for b in range(steps, -1, -1):
                self.display.brightness = b / steps * self.full_brightness
                sleep(delay)

    def clear_main_display_group(self):
        """
        Clear the main display group.
        :return:
        """
        while len(self.main_display_group):
            del self.main_display_group[-1]
        cleanup()

    def show_image(self, image_path):
        """
        Display an image on the screen.
        :param image_path:
        :return:
        """
        odb = display_on_disk_bitmap(image_path)
        loaded_image = display_tilegrid(odb, pixel_shader=odb.pixel_shader)
        del odb
        self.main_display_group.append(loaded_image)
        del loaded_image
        cleanup()

    def label_factory(self, text, pos, color=0xFFFFFF, background_color=0x000000, font=terminalio_font):
        """
        Create a label object.
        :param text:
        :param pos:
        :param color:
        :param background_color:
        :param font:
        :return:
        """
        x, y = pos
        cleanup()
        return label.Label(font, text=text, color=color, background_color=background_color, x=x, y=y)


class SpriteExtractor:
    class CustomTileGrid(display_tilegrid):
        """
        Custom TileGrid class that adds an extra attribute to store whether the TileGrid is an icon or not.
        Allows for easier identification of TileGrids that are icons during cleanup, to ensure sprites are clearn up
        on menus.
        """

        def __init__(self, bitmap, *args, icon=False, **kwargs):
            super().__init__(bitmap, *args, **kwargs)
            # Initialize the new attribute
            self.icon = icon

            cleanup()

    def __init__(self, sprite_sheet, sprite_width, sprite_height, columns, rows):
        # todo: fix why sprite width and height aren't working as expected, for example 'trolley.sprite.height'
        #  brings back '1' instead of the actual height
        self.sprite_sheet = sprite_sheet
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height
        self.columns = columns
        self.rows = rows
        self.sprites = self.load_sprites()
        
        # Cache for generated sprites with shadows/palettes to avoid regeneration
        self.sprite_cache = {}
        # Cache for palettes by color_shift to avoid redundant palette creation
        self.palette_cache = {}

        # x, y position of each sprite in the sprite sheet
        self.sprite_matrix = {
            "trolley_basic": (0, 0),
            "trolley_better": (0, 1),
            "trolley_big": (0, 2),
            "trolley_super": (0, 3),
            "block_1": (1, 0),
            "money": (1, 1),
            "carbon_fibre_frame": (1, 2),
            "turbo_upgrade": (1, 3),
            "water_spill_1": (2, 0),
            "carbon_fibre_wheels": (2, 1),
            "nitrous_oxide": (2, 2),
            "air_filter_upgrade": (2, 3),
            "sign": (3, 0),
            "racing_handle": (3, 1),
            "brake_upgrade": (3, 2),
            "computer_chip_upgrade": (3, 3),
            "person": (4, 0),
            "scanning_computer": (4, 1),
            "exhaust_upgrade": (4, 2),
            "suspension_upgrade": (4, 3),
            "block_2": (5, 0),
            "block_3": (5, 1),
            "block_4": (5, 2),
            "block_5": (5, 3),
        }

        cleanup()

    def load_sprites(self):
        """
        Load the sprites from the sprite sheet.
        :return:
        """
        sprite_sheet, palette = imageload(self.sprite_sheet, bitmap=display_bitmap, palette=display_palette)
        palette.make_transparent(0)  # Make the color at index 0 transparent

        sprites = []
        for row in range(self.rows):
            row_sprites = []
            for col in range(self.columns):
                # todo: look into tile_width and tile_height for collision testing, could maybe simplify objects
                sprite = self.CustomTileGrid(sprite_sheet, pixel_shader=palette,
                                             width=1, height=1,
                                             tile_width=self.sprite_width,
                                             tile_height=self.sprite_height,
                                             default_tile=col + row * self.columns,
                                             icon=False)
                row_sprites.append(sprite)
            sprites.append(row_sprites)

        cleanup()

        return sprites

    def adjust_color(self, color, offset):
        """
        Adjust the given 8-bit color to create a different shade for the AI trolley.
        :param color:
        :param offset:
        :return:
        """
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF

        # Adjust the color components to create a different shade
        r = max(0, min(255, r + offset[0]))  # Increase red component
        g = max(0, min(255, g + offset[1]))  # Decrease green component
        b = max(0, min(255, b + offset[2]))  # Increase blue component

        return (r << 16) | (g << 8) | b

    def get_sprite(self, name, pixel_shadow=False, shadow_angle=135, shadow_strength=1, transparent_background=True,
                   background_color=0xffffff,
                   shadow_color=0x000000, color_shift=(0, 0, 0)):
        """
        Get a sprite from the sprite sheet.
        :param name:
        :param pixel_shadow:
        :param shadow_angle:
        :param shadow_strength:
        :param transparent_background:
        :param background_color:
        :param shadow_color:
        :param color_shift:
        :return:
        """
        # Create cache key for this specific sprite configuration
        cache_key = (name, pixel_shadow, shadow_angle, shadow_strength, 
                    transparent_background, background_color, shadow_color, color_shift)
        
        # Return cached sprite if it exists
        if cache_key in self.sprite_cache:
            cached_sprite = self.sprite_cache[cache_key]
            # Return a new instance with the same bitmap and palette
            return self.CustomTileGrid(cached_sprite.bitmap, pixel_shader=cached_sprite.pixel_shader,
                                      width=1, height=1,
                                      tile_width=cached_sprite.tile_width, 
                                      tile_height=cached_sprite.tile_height,
                                      default_tile=cached_sprite[0], icon=True)
        
        column, row = self.sprite_matrix[name]
        original_sprite = self.sprites[row][column]

        # Check palette cache first
        if color_shift in self.palette_cache:
            alternate_palette = self.palette_cache[color_shift]
        else:
            # Define a new palette for the AI trolley to differentiate it
            palette_len = len(original_sprite.pixel_shader)
            alternate_palette = display_palette(palette_len)
            for i in range(palette_len):
                original_color = original_sprite.pixel_shader[i]
                # Change the color slightly to differentiate the AI trolley
                alternate_palette[i] = self.adjust_color(original_color, color_shift)
            # Cache the palette for reuse
            if color_shift != (0, 0, 0):  # Only cache non-default palettes
                self.palette_cache[color_shift] = alternate_palette

        if pixel_shadow:
            # Calculate shadow offsets based on the angle and strength (WiP) it works with basic shadows,
            # but not with adjustments to angles etc.
            shadow_offset_x = shadow_strength
            shadow_offset_y = shadow_strength
            if shadow_angle == 45:
                shadow_offset_x, shadow_offset_y = shadow_strength, -shadow_strength
            elif shadow_angle == 225:
                shadow_offset_x, shadow_offset_y = -shadow_strength, shadow_strength
            elif shadow_angle == 315:
                shadow_offset_x, shadow_offset_y = -shadow_strength, -shadow_strength

            # Calculate new bitmap dimensions to accommodate both sprite and shadow
            expanded_width = self.sprite_width + abs(shadow_offset_x)
            expanded_height = self.sprite_height + abs(shadow_offset_y)

            # Adjust the number of colors to include the shadow color
            palette_len = len(alternate_palette)
            num_colors = palette_len + 1
            combined_bitmap = display_bitmap(expanded_width, expanded_height, num_colors)
            combined_palette = display_palette(num_colors)

            # Copy original palette colors and add shadow color
            for i in range(palette_len):
                combined_palette[i] = alternate_palette[i]
            if transparent_background:
                combined_palette.make_transparent(0)
            else:
                combined_palette[0] = background_color
            shadow_color_index = palette_len
            combined_palette[shadow_color_index] = shadow_color

            # Optimized shadow generation with pre-calculated bounds
            col_offset = column * self.sprite_width
            row_offset = row * self.sprite_height
            max_shadow_x = expanded_width - 1
            max_shadow_y = expanded_height - 1
            
            # Iterate through the original sprite's pixels to draw it and its shadow
            for y in range(self.sprite_height):
                row_offset_y = row_offset + y
                shadow_y = y + shadow_offset_y
                shadow_y_valid = 0 <= shadow_y <= max_shadow_y
                for x in range(self.sprite_width):
                    original_index = original_sprite.bitmap[col_offset + x, row_offset_y]
                    if original_index:  # If the pixel is not transparent (faster than != 0)
                        # Draw the original sprite pixel
                        combined_bitmap[x, y] = original_index
                        # Draw the shadow pixel, offset by the shadow's x and y offsets
                        if shadow_y_valid:
                            shadow_x = x + shadow_offset_x
                            if 0 <= shadow_x <= max_shadow_x:
                                combined_bitmap[shadow_x, shadow_y] = shadow_color_index

            new_sprite = self.CustomTileGrid(combined_bitmap, pixel_shader=combined_palette,
                                             width=1, height=1,
                                             tile_width=expanded_width, tile_height=expanded_height,
                                             default_tile=0, icon=True)
        else:
            if transparent_background:
                alternate_palette.make_transparent(0)
                modified_palette = alternate_palette
            else:
                palette_len = len(alternate_palette)
                modified_palette = display_palette(palette_len)

                for i in range(palette_len):
                    modified_palette[i] = alternate_palette[i]
                if transparent_background:
                    modified_palette.make_transparent(0)
                else:
                    modified_palette[0] = background_color

            # Create a TileGrid using the original sprite's attributes if no shadow is needed
            new_sprite = self.CustomTileGrid(original_sprite.bitmap, pixel_shader=modified_palette,
                                             width=1, height=1,
                                             tile_width=self.sprite_width, tile_height=self.sprite_height,
                                             default_tile=(row * self.columns + column), icon=True)
        
        # Cache the generated sprite for future reuse (limit cache size to avoid memory issues)
        if len(self.sprite_cache) < 50:  # Limit cache size for PyBadge memory constraints
            self.sprite_cache[cache_key] = new_sprite
        
        return new_sprite


sprite_extractor = SpriteExtractor("../images/sprites.bmp", 16, 16, 6, 4)
