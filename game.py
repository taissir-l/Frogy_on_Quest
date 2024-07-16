import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
from pygame import mixer

pygame.init()

game_over = False
main_menu = True


# title and logo

pygame.display.set_caption("Frogy on Quest")
icon = pygame.image.load('assets/logo/frog-prince.png')
pygame.display.set_icon(icon)

WIDTH, HEIGHT = 1300, 700
FPS = 50
PLAYER_VEL = 14

window = pygame.display.set_mode((WIDTH, HEIGHT))
gameover = 0

# background sound
mixer.music.load('assets/music/back_music.mp3')
mixer.music.play(-1)
pygame.mixer.music.set_volume(0.5)
jump_fx = pygame.mixer.Sound('assets/music/jump.mp3')


# menur images
start_img = pygame.image.load('assets/Menu/start_btn.png')
exit_img = pygame.image.load('assets/Menu/exit_btn.png')
restart_img = pygame.image.load('assets/Menu/restart_btn.png')
background_img = pygame.image.load('assets/Menu/mmenu.png')



def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.clicked = False

	def draw(self):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False


		#draw button
		window.blit(self.image, self.rect)

		return action




class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "NinjaFrog", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.pain = 0
        self.saw_collisions = 0
        self.fire_collisions = 0
        self.rect = pygame.Rect(0, 0, 50, 50)  # Placeholder rect

        self.dead_img = pygame.image.load('assets/Other/gost.png')
    
    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)
 
        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0
        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()
    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))
    
    def reset(self, x, y):
        # Reset player state
        self.rect.x = x
        self.rect.y = y
        self.jump_count = 0
        self.x_vel = 0


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Saw(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "saw")
        self.saw = load_sprite_sheets("Traps", "Saw", width, height)
        self.image = self.saw["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.saw[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image

def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()
        
    window.blit(background_img, (0, 0))  # Draw the background image



def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    keys = pygame.key.get_pressed()
    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj:
            if obj.name == "fire" or obj.name == "saw":
                player.make_hit()
                global game_over
                game_over = True  # Set game over state
                return  # Exit the function early


def draw_game_over(window):
    font = pygame.font.Font('assets/Other/fonts.ttf', 80)
    #font = pygame.font.SysFont('Pixelify Sans', 64)
    text = font.render('Game Over', True, (20, 0, 0))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    window.blit(text, text_rect)
    pygame.display.update()

def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    block_size = 96
    global game_over
    global main_menu

    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size * 3, (WIDTH * 2) // block_size * 3)]
    player = Player(0, 0, 50, 50)
    saw = [Saw(block_size * 77,HEIGHT - block_size - 64, 38, 38), 
           Saw(block_size * 66,HEIGHT - block_size - 64, 38, 38), 
           Saw(block_size * 67,HEIGHT - block_size - 64, 38, 38),
           Saw(block_size * 66.5,HEIGHT - block_size * 3, 38, 38),
           Saw(block_size * 16,HEIGHT - block_size * 5, 38, 38),
           Saw(block_size * 31,HEIGHT - block_size * 2, 38, 38),
           Saw(block_size * 41,HEIGHT - block_size * 2, 38, 38),
           Saw(block_size * 60,HEIGHT - block_size * 4, 38, 38),
           Saw(block_size * 61,HEIGHT - block_size * 3.5, 38, 38),
           Saw(block_size * 37,HEIGHT - block_size * 1.8, 38, 38),
           Saw(block_size * 9,HEIGHT - block_size * 1.8, 38, 38)]
    floor.extend(saw)
    for s in saw:
        s.on()
    fire = [Fire(200, HEIGHT - block_size - 64, 16, 32),
            Fire(block_size * 7, HEIGHT - block_size - 64, 16, 32),
            Fire(block_size * 7.5, HEIGHT - block_size - 64, 16, 32), 
            Fire(block_size * 14, HEIGHT - block_size - 64, 16, 32),
            Fire(block_size * 14.5, HEIGHT - block_size - 64, 16, 32), 
            Fire(block_size * 18, HEIGHT - block_size - 64, 16, 32),
            Fire(block_size * 18.5, HEIGHT - block_size - 64, 16, 32), 
            Fire(block_size * 27, HEIGHT - block_size - 64, 16, 32),
            Fire(block_size * 27.5, HEIGHT - block_size - 64, 16, 32), 
            Fire(block_size * 32, HEIGHT - block_size - 64, 16, 32),
            Fire(block_size * 32.5, HEIGHT - block_size - 64, 16, 32), 
            Fire(block_size * 33, HEIGHT - block_size - 64, 16, 32),
            Fire(block_size * 39, HEIGHT - block_size - 64, 16, 32),
            Fire(block_size * 39.5, HEIGHT - block_size - 64, 16, 32),
            Fire(block_size * 45, HEIGHT - block_size - 64, 16, 32),
            Fire(block_size * 45.5, HEIGHT - block_size - 64, 16, 32),
            Fire(block_size * 47, HEIGHT - block_size - 64, 16, 32),
            Fire(block_size * 47.5, HEIGHT - block_size - 64, 16, 32),
            Fire(block_size * 49, HEIGHT - block_size - 64, 16, 32),
            Fire(block_size * 49.5, HEIGHT - block_size - 64, 16, 32),
            Fire(block_size * 51, HEIGHT - block_size - 64, 16, 32),
            Fire(block_size * 51.5, HEIGHT - block_size - 64, 16, 32),
            Fire(block_size * 53, HEIGHT - block_size - 64, 16, 32),
            Fire(block_size * 53.5, HEIGHT - block_size - 64, 16, 32),
            Fire(block_size * 55, HEIGHT - block_size - 64, 16, 32),
            Fire(block_size * 55.5, HEIGHT - block_size - 64, 16, 32),
            Fire(block_size * 56, HEIGHT - block_size - 64, 16, 32),
            Fire(block_size * 56.5, HEIGHT - block_size - 64, 16, 32)]
    floor.extend(fire)
    for f in fire:
        f.on()
    
    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size),
               Block(block_size * 3, HEIGHT - block_size * 4, block_size), 
               Block(block_size * 8, HEIGHT - block_size * 2, block_size),
               Block(block_size * 8, HEIGHT - block_size * 4, block_size),
               Block(block_size * 8, HEIGHT - block_size * 5, block_size),
               Block(block_size * 8, HEIGHT - block_size * 6, block_size),
               Block(block_size * 12, HEIGHT - block_size * 2, block_size),
               Block(block_size * 13, HEIGHT - block_size * 2, block_size),
               Block(block_size * 13, HEIGHT - block_size * 3, block_size),
               Block(block_size * 15, HEIGHT - block_size * 4, block_size),
               Block(block_size * 16, HEIGHT - block_size * 4, block_size),
               Block(block_size * 17, HEIGHT - block_size * 4, block_size),
               Block(block_size * 21, HEIGHT - block_size * 2, block_size),
               Block(block_size * 22, HEIGHT - block_size * 3, block_size),
               Block(block_size * 23, HEIGHT - block_size * 4, block_size),
               Block(block_size * 24, HEIGHT - block_size * 5, block_size),
               Block(block_size * 25, HEIGHT - block_size * 6, block_size),
               Block(block_size * 26, HEIGHT - block_size * 6, block_size),
               Block(block_size * 28, HEIGHT - block_size * 4, block_size),
               Block(block_size * 29, HEIGHT - block_size * 4, block_size),
               Block(block_size * 36, HEIGHT - block_size * 3, block_size),
               Block(block_size * 37, HEIGHT - block_size * 3, block_size),
               Block(block_size * 38, HEIGHT - block_size * 3, block_size),
               Block(block_size * 38, HEIGHT - block_size * 2, block_size),
               Block(block_size * 44, HEIGHT - block_size * 2, block_size),
               Block(block_size * 44, HEIGHT - block_size * 4, block_size),
               Block(block_size * 44, HEIGHT - block_size * 5, block_size),
               Block(block_size * 44, HEIGHT - block_size * 6, block_size),
               Block(block_size * 44, HEIGHT - block_size * 7, block_size),
               Block(block_size * 46, HEIGHT - block_size * 2, block_size),
               Block(block_size * 46, HEIGHT - block_size * 3, block_size),
               Block(block_size * 46, HEIGHT - block_size * 5, block_size),
               Block(block_size * 46, HEIGHT - block_size * 6, block_size),
               Block(block_size * 46, HEIGHT - block_size * 7, block_size),
               Block(block_size * 48, HEIGHT - block_size * 2, block_size),
               Block(block_size * 48, HEIGHT - block_size * 3, block_size),
               Block(block_size * 48, HEIGHT - block_size * 4, block_size),
               Block(block_size * 48, HEIGHT - block_size * 6, block_size),
               Block(block_size * 48, HEIGHT - block_size * 7, block_size),
               Block(block_size * 50, HEIGHT - block_size * 2, block_size),
               Block(block_size * 50, HEIGHT - block_size * 3, block_size),
               Block(block_size * 50, HEIGHT - block_size * 5, block_size),
               Block(block_size * 50, HEIGHT - block_size * 6, block_size),
               Block(block_size * 50, HEIGHT - block_size * 7, block_size),
               Block(block_size * 52, HEIGHT - block_size * 2, block_size),
               Block(block_size * 52, HEIGHT - block_size * 3, block_size),
               Block(block_size * 52, HEIGHT - block_size * 4, block_size),
               Block(block_size * 52, HEIGHT - block_size * 6, block_size),
               Block(block_size * 52, HEIGHT - block_size * 7, block_size),
               Block(block_size * 54, HEIGHT - block_size * 2, block_size),
               Block(block_size * 54, HEIGHT - block_size * 3, block_size),
               Block(block_size * 54, HEIGHT - block_size * 4, block_size),
               Block(block_size * 54, HEIGHT - block_size * 5, block_size),
               Block(block_size * 54, HEIGHT - block_size * 7, block_size),
               Block(block_size * 57, HEIGHT - block_size * 4, block_size),
               Block(block_size * 58, HEIGHT - block_size * 4, block_size),
               Block(block_size * 59, HEIGHT - block_size * 4, block_size),
               Block(block_size * 61, HEIGHT - block_size * 2, block_size),
               Block(block_size * 62, HEIGHT - block_size * 2, block_size),
               Block(block_size * 63, HEIGHT - block_size * 2, block_size),
               Block(block_size * 64, HEIGHT - block_size * 2, block_size),
               Block(block_size * 65, HEIGHT - block_size * 2, block_size),
               Block(block_size * 68, HEIGHT - block_size * 2, block_size),
               Block(block_size * 69, HEIGHT - block_size * 2, block_size),
               Block(block_size * 70, HEIGHT - block_size * 2, block_size),
               Block(block_size * 71, HEIGHT - block_size * 2, block_size),
               Block(block_size * 72, HEIGHT - block_size * 1, block_size),
               Block(block_size * 73, HEIGHT - block_size * 1, block_size),
               Block(block_size * 74, HEIGHT - block_size * 1, block_size),
               Block(block_size * 75, HEIGHT - block_size * 1, block_size),
               Block(block_size * 76, HEIGHT - block_size * 1, block_size),
               Block(block_size * 78, HEIGHT - block_size * 1, block_size),
               Block(block_size * 79, HEIGHT - block_size * 1, block_size),
               Block(block_size * 80, HEIGHT - block_size * 1, block_size),
               Block(block_size * 81, HEIGHT - block_size * 1, block_size),
               Block(block_size * 82, HEIGHT - block_size * 1, block_size),
               Block(block_size * 83, HEIGHT - block_size * 1, block_size)]


    offset_x = 0
    scroll_area_width = 200

    #create buttons
    restart_button = Button(WIDTH // 2 - 50, HEIGHT // 2 + 100, restart_img)
    start_button = Button(WIDTH // 2 - 350, HEIGHT // 2, start_img)
    exit_button = Button(WIDTH // 2 + 150, HEIGHT // 2, exit_img)



    run = True
    while run:
        clock.tick(FPS)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2 and not main_menu and not game_over:
                    jump_fx.play()
                    player.jump()

        if main_menu:
            window.blit(background_img, (0, 0))  # Clear the screen with a background color
            if exit_button.draw():
                run = False
            if start_button.draw():
                main_menu = False
            pygame.display.update()
            continue

        if game_over:
            draw_game_over(window)
            if restart_button.draw():
                player.reset(100, HEIGHT - 130)
                game_over = False
            pygame.display.update()
            continue

        player.loop(FPS)
        for s in saw:
            s.loop()
        # Loop through each fire object and call its loop method
        for f in fire:
            f.loop()

        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel
    
    
    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)
