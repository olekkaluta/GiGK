import math
from math import sin, cos

import pygame.gfxdraw
import tkinter as tk
from lab2gui import ManipulatorGUI


class Manipulator:
    _hand = "/hand.png"
    _arm = "/arm.png"
    graphics_path = "./graphics/"
    arm_width = 5
    hand_width = 20
    hand_ratio = 1.4

    def __init__(self, M, w3, w2, w1, lock=False, params=None):
        self.arm = None
        self.hand = None
        self.lock = lock
        self.vertices = (M, w3, w2, w1)
        self.S = tuple(
            Manipulator.distance(self.vertices[i], self.vertices[i + 1]) for i in range(len(self.vertices) - 1))
        self._scale = [1, 1, 1]
        self._rotate = [0, 0, 0, 0]
        if params is None:
            params = [
                tuple([(-180, 180)] + [(-180, 180) for _ in range(len(self._rotate) - 1)]),  # angle restrictions
            ]
        else:
            assert len(params) == 1
            assert len(params[0]) == len(self._rotate)

        self.angle_limits = params[0]

        try:
            self.loadAssets()
        except:
            pass

    def loadAssets(self):
        self.hand = pygame.image.load(Manipulator.graphics_path + Manipulator._hand)
        self.arm = pygame.image.load(Manipulator.graphics_path + Manipulator._arm)

    @staticmethod
    def distance(p1, p2):
        return sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

    @staticmethod
    def angle(p1, p2):
        return math.atan2(p2[1] - p1[1], p2[0] - p1[0]) - math.atan2(-p1[1], 0)

    @staticmethod
    def rotate_around_point(xy, radians, origin=(0, 0)):
        """Rotate a point around a given point.
        """
        x, y = xy
        offset_x, offset_y = origin
        adjusted_x = (x - offset_x)
        adjusted_y = (y - offset_y)
        cos_rad = cos(radians)
        sin_rad = sin(radians)
        qx = offset_x + cos_rad * adjusted_x + sin_rad * adjusted_y
        qy = offset_y + -sin_rad * adjusted_x + cos_rad * adjusted_y
        return [qx, qy]

    def draw(self, surface: pygame.Surface):
        vertices = self._eval_vertices()
        for _i in range(1, len(vertices)):
            Manipulator._draw_arm(surface, vertices[_i - 1], vertices[_i], Manipulator.arm_width, self.hand)

        v1 = vertices[3]
        sc = [vertices[2][0] - v1[0], vertices[2][1] - v1[1]]
        l = Manipulator.distance((0, 0), sc)
        sc = [-x / l * Manipulator.hand_width * Manipulator.hand_ratio for x in sc]
        v2 = [v1[i] + sc[i] for i in range(len(v1))]
        v2 = Manipulator.rotate_around_point(v2, self._rotate[3] / 180 * math.pi, v1)

        self._draw_hand(surface, v1, v2, Manipulator.hand_width, self.arm)

    def _eval_vertices(self):
        return self._eval_scaled_points(self._eval_rotated_points())

    def rotate(self, vert_num, angle):
        if self.lock and vert_num > 0:
            return
        self._rotate[vert_num] += angle
        min_r, max_r = self.angle_limits[vert_num]
        self._rotate[vert_num] = min(max_r, max(min_r, self._rotate[vert_num]))
        if abs(self._rotate[vert_num]) >= 180:
            self._rotate[vert_num] = -self._rotate[vert_num]

    @staticmethod
    def rotate_surface(surface, angle, pivot, offset):
        """Rotate the surface around the pivot point.
        Args:
            surface (pygame.Surface): The surface that is to be rotated.
            angle (float): Rotate by this angle.
            pivot (tuple, list, pygame.math.Vector2): The pivot point.
            offset (pygame.math.Vector2): This vector is added to the pivot.
        """
        rotated_image = pygame.transform.rotozoom(surface, -angle, 1)
        rotated_offset = offset.rotate(angle)
        rect = rotated_image.get_rect(center=pivot + rotated_offset)
        return rotated_image, rect

    def scale(self, vert_num, coeff):
        self._scale[vert_num] = coeff

    def _eval_rotated_points(self):
        V = [x for x in self.vertices]
        for k in range(len(self._rotate)):
            r = self._rotate[k]
            for _i in range(k + 1, len(V)):
                V[_i] = Manipulator.rotate_around_point(V[_i], r / 180 * math.pi, V[k])
        return V

    def _eval_scaled_points(self, V):
        for _i in range(1, len(V)):
            vec_x = V[_i][0] - V[_i - 1][0]
            vec_y = V[_i][1] - V[_i - 1][1]
            vec_x = vec_x * self._scale[_i - 1] - vec_x
            vec_y = vec_y * self._scale[_i - 1] - vec_y
            for j in range(_i, len(V)):
                V[j][0] += vec_x
                V[j][1] += vec_y
        return V

    @staticmethod
    def _draw_arm(surface: pygame.Surface, V1, V2, arm_width, arm=None, ):
        if arm is None:
            pygame.draw.line(surface, "black", V1, V2)
        else:
            angle = Manipulator.angle(V1, V2)
            dist = Manipulator.distance(V1, V2)
            arm = pygame.transform.scale(arm, (arm_width, dist * 1.1))
            surface.blit(*Manipulator.rotate_surface(arm, angle * 180 / math.pi, V1, pygame.math.Vector2(0, -dist / 2)))

    def _draw_hand(self, surface: pygame.Surface, V, V1, hand_width, hand=None):
        if hand is None:
            pygame.draw.line(surface, "blue", V, V1)
        else:
            self._draw_arm(surface, V, V1, hand_width, hand)

    def translate(self, point):
        self.vertices = [(x[0] + point[0], x[1] + point[1]) for x in self.vertices]


if __name__ == '__main__':
    from pygame.locals import *
    import pygame.gfxdraw
    from math import sqrt
    from sys import exit
    import os

    pygame.init()

    WINDOW_SIZE = (700, 700)
    WINDOW_POSITION = (500, 30)

    FONT_SIZE = 24
    FONT_BOLD = False

    FLAGS = pygame.DOUBLEBUF | pygame.HWSURFACE

    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % WINDOW_POSITION

    screen = pygame.display.set_mode(WINDOW_SIZE, FLAGS)

    scale_coeff = 3
    surf_size = (WINDOW_SIZE[0] / scale_coeff, WINDOW_SIZE[1] / scale_coeff)
    manipulator = Manipulator((0, 0), (0, 20), (0, 40), (0, 70))
    manipulator.translate((surf_size[0] / 2, surf_size[1] / 2))

    window = tk.Tk()
    window.geometry('450x300+10+100')
    embed = tk.Frame(window, width=500, height=300)
    embed.pack()
    os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
    os.environ["SDL_VIDEODRIVER"] = "dummy"

    gui = ManipulatorGUI(window, manipulator, {
        "scale_max": 5
    })

    clock = pygame.time.Clock()
    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        screen.fill((0xff, 0xff, 0xff))

        s = pygame.Surface(surf_size)
        s.fill((0xff, 0xff, 0xff))

        gui.update()
        manipulator.draw(s)
        screen.blit(pygame.transform.scale(s, WINDOW_SIZE), (0, 0))

        pygame.display.flip()
        window.update()
