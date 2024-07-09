import os
import sys

import pygame
import numpy as np
from .utils import *
from ..items import Tomato, Lettuce, Plate, Knife, Delivery, Agent, Food

graphics_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "graphics"))
_image_library = {}

ITEMNAME = [
    "space",
    "counter",
    "agent",
    "tomato",
    "lettuce",
    "plate",
    "knife",
    "delivery",
    "onion",
    "pan",
    "steak",
]
ITEMIDX = {
    "space": 0,
    "counter": 1,
    "agent": 2,
    "tomato": 3,
    "lettuce": 4,
    "plate": 5,
    "knife": 6,
    "delivery": 7,
    "onion": 8,
    "pan": 9,
    "steak": 10,
    "sink": 11,
    "trash_can": 12,
}


def get_image(path):
    global _image_library
    image = _image_library.get(path)
    if image == None:
        canonicalized_path = path.replace("/", os.sep).replace("\\", os.sep)
        image = pygame.image.load(canonicalized_path)
        _image_library[path] = image
    return image


class Game:
    def __init__(self, env):
        self._running = True
        self.env = env

        # Visual parameters
        self.scale = 80  # num pixels per tile
        self.holding_scale = 0.5
        self.container_scale = 0.7
        self.width = self.scale * self.env.xlen
        self.height = self.scale * self.env.ylen
        self.tile_size = (self.scale, self.scale)
        self.holding_size = tuple(
            (self.holding_scale * np.asarray(self.tile_size)).astype(int)
        )
        self.container_size = tuple(
            (self.container_scale * np.asarray(self.tile_size)).astype(int)
        )
        self.holding_container_size = tuple(
            (self.container_scale * np.asarray(self.holding_size)).astype(int)
        )

        pygame.init()
        pygame.font.init()

    def on_init(self):
        pygame.init()
        pygame.font.init()
        if self.play:
            self.screen = pygame.display.set_mode((self.width, self.height))
        else:
            # Create a hidden surface
            self.screen = pygame.Surface((self.width, self.height))
        self._running = True

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_render(self):
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.screen.fill(Color.FLOOR)
        for x in range(self.env.xlen):
            for y in range(self.env.ylen):
                sl = self.scaled_location((y, x))
                if self.env.map[x][y] == ITEMIDX["counter"]:
                    fill = pygame.Rect(sl[0], sl[1], self.scale, self.scale)
                    pygame.draw.rect(self.screen, Color.COUNTER, fill)
                    pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
                elif self.env.map[x][y] == ITEMIDX["delivery"]:
                    fill = pygame.Rect(sl[0], sl[1], self.scale, self.scale)
                    pygame.draw.rect(self.screen, Color.DELIVERY, fill)
                    self.draw("delivery", self.tile_size, sl)
                    for k in self.env.delivery:
                        if k.x == x and k.y == y:
                            if k.holding:
                                self.draw(k.holding.name, self.tile_size, sl)
                                if k.holding.name == "plate":
                                    if k.holding.containing:
                                        self.draw_contained(
                                            k.holding.containedName[-2:][-2:],
                                            self.container_size,
                                            self.container_location((y, x)),
                                        )
                elif self.env.map[x][y] == ITEMIDX["knife"]:
                    fill = pygame.Rect(sl[0], sl[1], self.scale, self.scale)
                    pygame.draw.rect(self.screen, Color.COUNTER, fill)
                    pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
                    self.draw("cutboard", self.tile_size, sl)
                    for k in self.env.knife:
                        if k.x == x and k.y == y:
                            if k.holding:
                                self.draw(k.holding.name, self.tile_size, sl)
                                if k.holding.name == "plate":
                                    if k.holding.containing:
                                        self.draw_contained(
                                            k.holding.containedName[-2:][-2:],
                                            self.container_size,
                                            self.container_location((y, x)),
                                        )
                elif self.env.map[x][y] == ITEMIDX["pan"]:
                    fill = pygame.Rect(sl[0], sl[1], self.scale, self.scale)
                    pygame.draw.rect(self.screen, Color.COUNTER, fill)
                    pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
                    self.draw("pan", self.tile_size, sl)
                    for p in self.env.pan:
                        if p.x == x and p.y == y:
                            if p.holding:
                                self.draw(p.holding.name, self.tile_size, sl)
                elif self.env.map[x][y] == ITEMIDX["tomato"]:
                    fill = pygame.Rect(sl[0], sl[1], self.scale, self.scale)
                    pygame.draw.rect(self.screen, Color.COUNTER, fill)
                    pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
                    for t in self.env.tomato:
                        if t.x == x and t.y == y:
                            self.draw(t.name, self.tile_size, sl)
                elif self.env.map[x][y] == ITEMIDX["lettuce"]:
                    fill = pygame.Rect(sl[0], sl[1], self.scale, self.scale)
                    pygame.draw.rect(self.screen, Color.COUNTER, fill)
                    pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
                    for l in self.env.lettuce:
                        if l.x == x and l.y == y:
                            self.draw(l.name, self.tile_size, sl)
                elif self.env.map[x][y] == ITEMIDX["onion"]:
                    fill = pygame.Rect(sl[0], sl[1], self.scale, self.scale)
                    pygame.draw.rect(self.screen, Color.COUNTER, fill)
                    pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
                    for l in self.env.onion:
                        if l.x == x and l.y == y:
                            self.draw(l.name, self.tile_size, sl)
                elif self.env.map[x][y] == ITEMIDX["steak"]:
                    fill = pygame.Rect(sl[0], sl[1], self.scale, self.scale)
                    pygame.draw.rect(self.screen, Color.COUNTER, fill)
                    pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
                    for l in self.env.steak:
                        if l.x == x and l.y == y:
                            self.draw(l.name, self.tile_size, sl)
                elif self.env.map[x][y] == ITEMIDX["plate"]:
                    fill = pygame.Rect(sl[0], sl[1], self.scale, self.scale)
                    pygame.draw.rect(self.screen, Color.COUNTER, fill)
                    pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
                    for p in self.env.plate:
                        if p.x == x and p.y == y:
                            self.draw(p.name, self.tile_size, sl)
                            if p.containing:
                                self.draw_contained(
                                    p.containedName[-2:],
                                    self.container_size,
                                    self.container_location((y, x)),
                                )
                elif self.env.map[x][y] == ITEMIDX["sink"]:
                    fill = pygame.Rect(sl[0], sl[1], self.scale, self.scale)
                    pygame.draw.rect(self.screen, Color.COUNTER, fill)
                    pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
                    self.draw(self.env.sink[0].name, self.tile_size, sl)
                elif self.env.map[x][y] == ITEMIDX["trash_can"]:
                    fill = pygame.Rect(sl[0], sl[1], self.scale, self.scale)
                    pygame.draw.rect(self.screen, Color.COUNTER, fill)
                    pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
                    self.draw("trash_can", self.tile_size, sl)
                elif self.env.map[x][y] == ITEMIDX["agent"]:
                    for agent in self.env.agent:
                        if agent.x == x and agent.y == y:
                            self.draw(
                                "agent-{}".format(agent.color), self.tile_size, sl
                            )
                            if agent.holding:
                                if isinstance(agent.holding, Plate):
                                    self.draw(
                                        agent.holding.name,
                                        self.holding_size,
                                        self.holding_location((y, x)),
                                    )
                                    if agent.holding.containing:
                                        self.draw_contained(
                                            agent.holding.containedName[-2:],
                                            self.holding_container_size,
                                            self.holding_container_location((y, x)),
                                        )
                                else:
                                    self.draw(
                                        agent.holding.name,
                                        self.holding_size,
                                        self.holding_location((y, x)),
                                    )

        self.display_info()
        pygame.display.flip()
        pygame.display.update()

        img_int = pygame.PixelArray(self.screen)
        img_rgb = np.zeros([img_int.shape[1], img_int.shape[0], 3], dtype=np.uint8)
        for i in range(img_int.shape[0]):
            for j in range(img_int.shape[1]):
                color = pygame.Color(img_int[i][j])
                img_rgb[j, i, 0] = color[1]
                img_rgb[j, i, 1] = color[2]
                img_rgb[j, i, 2] = color[3]
        del img_int
        return img_rgb

    def draw(self, path, size, location):
        sorted_path = "-".join(sorted(path.split("-")))
        image_path = "{}/{}.png".format(graphics_dir, sorted_path)
        image = pygame.transform.scale(get_image(image_path), size)
        self.screen.blit(image, location)

    def draw_contained(self, foodlist, size, location):
        veg, meat = foodlist
        if veg:
            self.draw(veg, size, location)
        if meat:
            self.draw(meat, size, location)

    def scaled_location(self, loc):
        """Return top-left corner of scaled location given coordinates loc, e.g. (3, 4)"""
        return tuple(self.scale * np.asarray(loc))

    def holding_location(self, loc):
        """Return top-left corner of location where agent holding will be drawn (bottom right corner) given coordinates loc, e.g. (3, 4)"""
        scaled_loc = self.scaled_location(loc)
        return tuple(
            (np.asarray(scaled_loc) + self.scale * (1 - self.holding_scale)).astype(int)
        )

    def container_location(self, loc):
        """Return top-left corner of location where contained (i.e. plated) object will be drawn, given coordinates loc, e.g. (3, 4)"""
        scaled_loc = self.scaled_location(loc)
        return tuple(
            (
                np.asarray(scaled_loc) + self.scale * (1 - self.container_scale) / 2
            ).astype(int)
        )

    def holding_container_location(self, loc):
        """Return top-left corner of location where contained, held object will be drawn given coordinates loc, e.g. (3, 4)"""
        scaled_loc = self.scaled_location(loc)
        factor = (1 - self.holding_scale) + (
            1 - self.container_scale
        ) / 2 * self.holding_scale
        return tuple((np.asarray(scaled_loc) + self.scale * factor).astype(int))

    def on_cleanup(self):
        pygame.display.quit()
        pygame.quit()

    def get_image_obs(self):
        self.screen = pygame.Surface((self.width, self.height))
        self.screen.fill(Color.FLOOR)
        for x in range(self.env.xlen):
            for y in range(self.env.ylen):
                sl = self.scaled_location((y, x))
                if self.env.map[x][y] == ITEMIDX["counter"]:
                    fill = pygame.Rect(sl[0], sl[1], self.scale, self.scale)
                    pygame.draw.rect(self.screen, Color.COUNTER, fill)
                    pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
                elif self.env.map[x][y] == ITEMIDX["delivery"]:
                    fill = pygame.Rect(sl[0], sl[1], self.scale, self.scale)
                    pygame.draw.rect(self.screen, Color.DELIVERY, fill)
                    self.draw("delivery", self.tile_size, sl)
                    for k in self.env.delivery:
                        if k.x == x and k.y == y:
                            if k.holding:
                                self.draw(k.holding.name, self.tile_size, sl)
                                if k.holding.name == "plate":
                                    if k.holding.containing:
                                        self.draw_contained(
                                            k.holding.containedName[-2:],
                                            self.container_size,
                                            self.container_location((y, x)),
                                        )
                elif self.env.map[x][y] == ITEMIDX["knife"]:
                    fill = pygame.Rect(sl[0], sl[1], self.scale, self.scale)
                    pygame.draw.rect(self.screen, Color.COUNTER, fill)
                    pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
                    self.draw("cutboard", self.tile_size, sl)
                    for k in self.env.knife:
                        if k.x == x and k.y == y:
                            if k.holding:
                                self.draw(k.holding.name, self.tile_size, sl)
                                if k.holding.name == "plate":
                                    if k.holding.containing:
                                        self.draw_contained(
                                            k.holding.containedName[-2:],
                                            self.container_size,
                                            self.container_location((y, x)),
                                        )
                elif self.env.map[x][y] == ITEMIDX["pan"]:
                    fill = pygame.Rect(sl[0], sl[1], self.scale, self.scale)
                    pygame.draw.rect(self.screen, Color.COUNTER, fill)
                    pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
                    self.draw("pan", self.tile_size, sl)
                    for p in self.env.pan:
                        if p.x == x and p.y == y:
                            if p.holding:
                                self.draw(p.holding.name, self.tile_size, sl)
                elif self.env.map[x][y] == ITEMIDX["tomato"]:
                    fill = pygame.Rect(sl[0], sl[1], self.scale, self.scale)
                    pygame.draw.rect(self.screen, Color.COUNTER, fill)
                    pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
                    for t in self.env.tomato:
                        if t.x == x and t.y == y:
                            self.draw(t.name, self.tile_size, sl)
                elif self.env.map[x][y] == ITEMIDX["lettuce"]:
                    fill = pygame.Rect(sl[0], sl[1], self.scale, self.scale)
                    pygame.draw.rect(self.screen, Color.COUNTER, fill)
                    pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
                    for l in self.env.lettuce:
                        if l.x == x and l.y == y:
                            self.draw(l.name, self.tile_size, sl)
                elif self.env.map[x][y] == ITEMIDX["onion"]:
                    fill = pygame.Rect(sl[0], sl[1], self.scale, self.scale)
                    pygame.draw.rect(self.screen, Color.COUNTER, fill)
                    pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
                    for l in self.env.onion:
                        if l.x == x and l.y == y:
                            self.draw(l.name, self.tile_size, sl)
                elif self.env.map[x][y] == ITEMIDX["steak"]:
                    fill = pygame.Rect(sl[0], sl[1], self.scale, self.scale)
                    pygame.draw.rect(self.screen, Color.COUNTER, fill)
                    pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
                    for l in self.env.steak:
                        if l.x == x and l.y == y:
                            self.draw(l.name, self.tile_size, sl)
                elif self.env.map[x][y] == ITEMIDX["plate"]:
                    fill = pygame.Rect(sl[0], sl[1], self.scale, self.scale)
                    pygame.draw.rect(self.screen, Color.COUNTER, fill)
                    pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
                    for p in self.env.plate:
                        if p.x == x and p.y == y:
                            self.draw(p.name, self.tile_size, sl)
                            if p.containing:
                                self.draw_contained(
                                    p.containedName[-2:],
                                    self.container_size,
                                    self.container_location((y, x)),
                                )
                elif self.env.map[x][y] == ITEMIDX["sink"]:
                    fill = pygame.Rect(sl[0], sl[1], self.scale, self.scale)
                    pygame.draw.rect(self.screen, Color.COUNTER, fill)
                    pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
                    self.draw(self.env.sink[0].name, self.tile_size, sl)
                elif self.env.map[x][y] == ITEMIDX["trash_can"]:
                    fill = pygame.Rect(sl[0], sl[1], self.scale, self.scale)
                    pygame.draw.rect(self.screen, Color.COUNTER, fill)
                    pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
                    self.draw("trash_can", self.tile_size, sl)
                elif self.env.map[x][y] == ITEMIDX["agent"]:
                    for agent in self.env.agent:
                        if agent.x == x and agent.y == y:
                            self.draw(
                                "agent-{}".format(agent.color), self.tile_size, sl
                            )
                            if agent.holding:
                                if isinstance(agent.holding, Plate):
                                    self.draw(
                                        agent.holding.name,
                                        self.holding_size,
                                        self.holding_location((y, x)),
                                    )
                                    if agent.holding.containing:
                                        self.draw_contained(
                                            agent.holding.containedName[-2:],
                                            self.holding_container_size,
                                            self.holding_container_location((y, x)),
                                        )
                                else:
                                    self.draw(
                                        agent.holding.name,
                                        self.holding_size,
                                        self.holding_location((y, x)),
                                    )

        img_int = pygame.PixelArray(self.screen)
        img_rgb = np.zeros([img_int.shape[1], img_int.shape[0], 3], dtype=np.uint8)
        for i in range(img_int.shape[0]):
            for j in range(img_int.shape[1]):
                color = pygame.Color(img_int[i][j])
                img_rgb[j, i, 0] = color[1]
                img_rgb[j, i, 1] = color[2]
                img_rgb[j, i, 2] = color[3]
        del img_int
        return img_rgb

    def display_info(self):
        task_text = "task:" + str([str(task["ingredients"]) for task in self.env.tasks])
        """Display a list of text information on the screen."""
        # Ensure the font module is initialized right before using it
        if not pygame.font.get_init():
            pygame.font.init()

        font = pygame.font.Font(None, 18)  # Choose the font and size
        start_y = 20  # Starting y position of the text
        text = font.render(
            task_text, True, (0, 0, 0)
        )  # Create a text surface (white color)
        self.screen.blit(
            text, (20, start_y)
        )  # Draw the text surface at the specified position
        start_y += 40  # Move down the y position for the next text
