import pygame
import os

# 基本設置
FPS = 60
WIDTH, HEIGHT = 1000, 700
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_SPEED = 8
PLAYER_SIZE = (50, 50)
POINT = 0
START_TIME = 100.0

# 初始化 Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("呂靜妍的大冒險")
clock = pygame.time.Clock()

# 縮放圖片的函數
def scale_image(image, size):
    return pygame.transform.scale(image, size)

# 加載幀數
def load_frames(frames_folder, size):
    frames = []
    for filename in os.listdir(frames_folder):
        if filename.endswith('.png') : 
            img_path = os.path.join(frames_folder, filename)
            img = pygame.image.load(img_path).convert_alpha() 
            img.set_colorkey(WHITE)  
            img = scale_image(img, size)  
            frames.append(img)
    return frames

font_name =pygame.font.match_font('Microsoft YaHei')
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)
# 加載圖片幀
player_frames = load_frames("player_frames", PLAYER_SIZE)
background_frames = load_frames("background_frames", (WIDTH, HEIGHT))
jump_sound = pygame.mixer.Sound(os.path.join("Sound", "jump.mp3"))
end_sound = pygame.mixer.Sound(os.path.join("Sound", "end.mp3"))
dead_sound = pygame.mixer.Sound(os.path.join("Sound", "dead.mp3"))
# 定義玩家類
class Player:
    def __init__(self):
        self.frames = player_frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (200, 535)
        self.animation_timer = 0
        self.frame_rate = 6
        self.moving = False
        self.is_jumping = False
        self.jump_speed = 21
        self.gravity = 1
        self.jump_velocity = 0
        self.stop = False
        self.is_game_over = False
        self.game_reach = False
        self.is_on_flagpole = False  # 玩家是否在旗桿上
        self.sliding_down = False  # 玩家是否正在下滑旗桿

    def jump(self):
        if not self.is_jumping and not self.is_on_flagpole:  # 僅在地面上允許跳躍
            self.is_jumping = True
            jump_sound.play()
            self.jump_velocity = -self.jump_speed

    def handle_collision(self, obstacles):
        on_ground = False

        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                # 頂部碰撞
                if self.jump_velocity > 0 and self.rect.bottom > obstacle.rect.top and self.rect.bottom - self.jump_velocity <= obstacle.rect.top:
                    self.rect.bottom = obstacle.rect.top
                    self.jump_velocity = 0
                    on_ground = True
                    self.is_jumping = False
                # 底部碰撞
                elif self.jump_velocity < 0 and self.rect.top < obstacle.rect.bottom and self.rect.top - self.jump_velocity >= obstacle.rect.bottom:
                    self.rect.top = obstacle.rect.bottom
                    self.jump_velocity = 0
                # 左側碰撞
                elif self.rect.right > obstacle.rect.left and self.rect.left < obstacle.rect.left and self.rect.bottom > obstacle.rect.top and self.rect.top < obstacle.rect.bottom:
                    self.rect.right = obstacle.rect.left
                    self.stop = True
                # 右側碰撞
                elif self.rect.left < obstacle.rect.right and self.rect.right > obstacle.rect.right and self.rect.bottom > obstacle.rect.top and self.rect.top < obstacle.rect.bottom:
                    self.rect.left = obstacle.rect.right
                    self.stop = True
        return on_ground

    def update(self, keys, background, obstacles, toilet, tap, monsters, flag):
        if self.is_game_over:
            return
        
        if self.is_on_flagpole:  # 玩家在旗桿上滑動
            if not self.sliding_down:
                self.rect.y = self.rect.y
                if self.rect.y <= flag.rect.y:
                    self.sliding_down = True
            else:
                if self.rect.bottom < HEIGHT - 100:
                    self.rect.y += 2
                    global POINT 
                    POINT += 10
                    end_sound.play()
                else:
                    if self.rect.x < 800:
                        self.rect.x += 2
                        self.moving = True
                    else:
                        self.game_reach = True
                        self.is_game_over = True
            return

        self.moving = False
        if self.rect.colliderect(toilet.rect)  and self.rect.bottom >= toilet.rect.top and pygame.K_s in keys:
            self.rect.y = tap.rect.y + 40
            self.rect.x = tap.rect.x + 20
      
        for monster in monsters[:]:  # 遍历怪物
            if self.rect.colliderect(monster.rect):
                # 玩家的底部碰到怪物的頭
                if self.jump_velocity > 0 and self.rect.bottom > monster.rect.top and self.rect.bottom - self.jump_velocity <= monster.rect.top:
                    monsters.remove(monster) 
                    self.jump_velocity = -self.jump_speed // 2
                    POINT += 100 
                else:
                    dead_sound.play()
                    self.is_game_over = True
                    return  
        # 垂直移動與重力
        self.jump_velocity += self.gravity
        self.rect.y += self.jump_velocity
        # 處理碰撞
        on_ground = self.handle_collision(obstacles)

        if not on_ground:
            self.is_jumping = True
            self.stop = False

        # 檢查是否掉出畫面
        if self.rect.top > HEIGHT:
            dead_sound.play()
            self.is_game_over = True

        # 水平移動
        if pygame.K_d in keys:
            self.moving = True
            if self.rect.x < 200 or background.backgrounds[4][1].x <= 0:
                self.rect.x += PLAYER_SPEED
        if pygame.K_a in keys:
            self.rect.x -= PLAYER_SPEED
            self.moving = True

        # 限制玩家在畫面內
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

        # 處理動畫
        if self.moving:
            self.animation_timer += clock.get_time()
            if self.animation_timer > 1000 // self.frame_rate:
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.animation_timer = 0
        else:
            self.frame_index = 0

        self.image = self.frames[self.frame_index]

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

class Background:
    def __init__(self, frames):
        self.frames = frames
        self.frame_index = 5
        self.backgrounds = []
        for i in range(self.frame_index):
            background_image = self.frames[i % len(self.frames)]
            image_rect = background_image.get_rect(topleft=(i * WIDTH, 0))
            self.backgrounds.append((background_image, image_rect))

    def update(self, player):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d] and self.backgrounds[4][1].x > 0 and player.stop == False and player.rect.x >100:
            for i, (background_image, rect) in enumerate(self.backgrounds):
                rect.x -= PLAYER_SPEED 

    def draw(self, surface):
        for background_image, rect in self.backgrounds:
            surface.blit(background_image, rect.topleft)

class Obstacle:
    def __init__(self, size, x, y):
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self, player, background):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d] and player.stop == False and player.rect.x >100:
            if background.backgrounds[4][1].x > 0:
                self.rect.x -= PLAYER_SPEED

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

class Monster:
    def __init__(self, x, y):
        image = pygame.image.load("monster.png").convert_alpha()
        img = scale_image(image, (50, 50))
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y) #(3800,570)

    def update(self, player, background):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d] and player.stop == False :
            if background.backgrounds[4][1].x > 0:
                self.rect.x -= PLAYER_SPEED 
        if self.rect.x < WIDTH:
            self.rect.x -= 2 
    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)
    
class Flag:
    def __init__(self):
        self.image = scale_image(pygame.image.load("flag.png"), (50, 50))
        self.rect = self.image.get_rect()
        self.rect.topleft = (4550, 200)
        self.flagpole_image = pygame.Surface((10, 400), pygame.SRCALPHA)
        self.flagpole_image.fill((0, 0, 0, 128))
        self.flagpole_rect = self.image.get_rect()
        self.flagpole_rect = pygame.Rect(4540, 210, 10, 400)
        self.flagpole_rect.topleft = (4540, 210)
        self.is_flag_moving = False  # 旗子是否正在下降
        self.touch = False

    def update(self, player, background):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d] and player.stop == False and player.rect.x >100:
            if background.backgrounds[4][1].x > 0:
                self.rect.x -= PLAYER_SPEED 
                self.flagpole_rect.x -= PLAYER_SPEED 

        if player.rect.colliderect(self.flagpole_rect):
            player.is_on_flagpole = True
            player.stop = True
            self.is_flag_moving = True

        if self.is_flag_moving:
            if self.rect.y < HEIGHT - 180:
                self.rect.y += 2
            else:
                self.is_flag_moving = False  # 停止旗子的移動

    def draw(self, screen):
        screen.blit(self.flagpole_image, self.flagpole_rect.topleft)
        screen.blit(self.image, self.rect.topleft)

class Toilet:
    def __init__(self):
        image = pygame.image.load("toilet.png").convert_alpha()  # 使用 convert_alpha() 以保留透明度
        img = scale_image(image, (60, 50))
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = (1435, 565)
    
    def update(self, player, background):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d] and player.stop == False and player.rect.x >100:
            if background.backgrounds[4][1].x > 0:
                self.rect.x -= PLAYER_SPEED 

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

class Tap:
    def __init__(self):
        image = pygame.image.load("tap.png").convert_alpha()  # 使用 convert_alpha() 以保留透明度
        img = scale_image(image, (60, 40))
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = (1543, 375)
    
    def update(self, player, background):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d] and player.stop == False and player.rect.x >100:
            if background.backgrounds[4][1].x > 0:
                self.rect.x -= PLAYER_SPEED 

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)
class Coin:
    def __init__(self, x, y):
        image = pygame.image.load("coin.png").convert_alpha()  # 使用 convert_alpha() 以保留透明度
        img = scale_image(image, (50, 50))
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self, player, background):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d] and player.stop == False:
            if background.backgrounds[4][1].x > 0:
                self.rect.x -= PLAYER_SPEED 

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def check_collision(self, player):
        return self.rect.colliderect(player.rect)  # 检查与玩家的碰撞

class EntryScreen:
    def __init__(self, screen, image_path, font_path, font_size=74):
        self.screen = screen
        self.image = pygame.image.load(image_path).convert()  
        self.image = scale_image(self.image, (WIDTH, HEIGHT))  
        self.font = pygame.font.Font(font_path, font_size)  
        self.text_surface = self.font.render("請按 Enter 開始", True, WHITE)  
        self.text_rect = self.text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    def show(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN: 
                        return 
                    
            # 畫面渲染初始畫面
            self.screen.blit(self.image, (0, 0)) 
            self.screen.blit(self.text_surface, self.text_rect)  
            pygame.display.flip() 
class GameOverScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(font_name, 74)

    def show(self, player):
        if player.game_reach:
            text_surface = self.font.render("恭喜過關", True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(text_surface, text_rect)
            pygame.display.flip()
            pygame.time.delay(2000)
        else:
            text_surface = self.font.render("遊戲結束", True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(text_surface, text_rect)
            pygame.display.flip()
            pygame.time.delay(2000)
# 創建玩家和背景
obstacles = []
coins = []
monsters = []
player = Player()
toilet = Toilet()
tap =Tap()
flag = Flag()
obstacles.append(Obstacle((WIDTH+480, 100), 0, 610))
obstacles.append(Obstacle((315, 45), 480, 430))
obstacles.append(Obstacle((265, 43), 735, 291))
obstacles.append(Obstacle((60, 47), 1435, 570)) #pipe
obstacles.append(Obstacle((268, 43), 1275, 375))
obstacles.append(Obstacle((268, 43), 1613, 212))
obstacles.append(Obstacle((60, 40), 1543, 375)) #pipe
obstacles.append(Obstacle((500, 100), 1855, 610))
#stair
obstacles.append(Obstacle((355, 43), 2100, 567))
obstacles.append(Obstacle((325, 43), 2145, 524))
obstacles.append(Obstacle((285, 43), 2190, 483))
obstacles.append(Obstacle((240, 45), 2235, 448))
obstacles.append(Obstacle((195, 46), 2280, 403))
obstacles.append(Obstacle((145, 43), 2325, 358))
obstacles.append(Obstacle((98, 43), 2375, 315))
#stair
obstacles.append(Obstacle((375, 43), 2570, 567))
obstacles.append(Obstacle((325, 43), 2570, 524))
obstacles.append(Obstacle((285, 43), 2570, 483))
obstacles.append(Obstacle((240, 46), 2570, 448))
obstacles.append(Obstacle((195, 45), 2570, 403))
obstacles.append(Obstacle((145, 43), 2570, 358))
obstacles.append(Obstacle((98, 43), 2570, 315))
#stair
obstacles.append(Obstacle((325, 43), WIDTH*4+45, 567))
obstacles.append(Obstacle((280, 43), WIDTH*4+90, 524))
obstacles.append(Obstacle((230, 43), WIDTH*4+140, 483))
obstacles.append(Obstacle((185, 45), WIDTH*4+185, 448))
obstacles.append(Obstacle((140, 43), WIDTH*4+230, 403))
obstacles.append(Obstacle((90, 43), WIDTH*4+275, 358))
obstacles.append(Obstacle((WIDTH*3, 100), 2570, 610))
obstacles.append(Obstacle((10, 230),4530 , 0))
coins.append(Coin(600, 385))
coins.append(Coin(750, 570))
coins.append(Coin(935, 241))
coins.append(Coin(1235, 570))
coins.append(Coin(1543, 470))
coins.append(Coin(1475, 325))
coins.append(Coin(2425, 265))
coins.append(Coin(2472, 215))
coins.append(Coin(2530, 215))
coins.append(Coin(2570, 265))
monsters.append(Monster(3800,570))
monsters.append(Monster(3900,570))
background = Background(background_frames)
game_over_screen = GameOverScreen(screen)

entry_screen = EntryScreen(screen, "entryscream.png", font_name)

entry_screen.show()
# 遊戲主循環
running = True
keys_pressed = set()
time_remaining = START_TIME
timer_font = pygame.font.Font(font_name, 18)

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            keys_pressed.add(event.key)
            if event.key == pygame.K_SPACE:
                player.jump()
        if event.type == pygame.KEYUP:
            keys_pressed.discard(event.key)
            
    time_remaining -= clock.get_time() / 1000  
    if time_remaining <= 0:
        time_remaining = 0  
        player.is_game_over = True 

    if player.is_game_over:
        game_over_screen.show(player)
        running = False
        continue

    player.update(keys_pressed, background, obstacles, toilet, tap, monsters, flag)
    flag.update(player, background)
    tap.update(player, background)
    background.update(player)
    for obstacle in obstacles:
        obstacle.update(player, background)
    toilet.update(player, background)
    for coin in coins[:]: 
        if coin.check_collision(player):
            POINT += 100
            coins.remove(coin)

    for coin in coins:
        coin.update(player, background)
    for monster in monsters:
        monster.update(player, background)
    screen.fill(BLACK)
    background.draw(screen)
    for obstacle in obstacles:
        obstacle.draw(screen)
    for coin in coins:
        coin.draw(screen)
    for monster in monsters:
        monster.draw(screen)
    toilet.draw(screen)
    player.draw(screen)
    tap.draw(screen)
    flag.draw(screen)
    draw_text(screen, "SCRODE:" + str(POINT), 18, WIDTH - 70, 10)
    draw_text(screen, "TIME:", 18, WIDTH - 230, 10)
    formatted_time = f"{int(time_remaining * 100):06}"  # 轉為毫秒並固定 6 位數
    timer_surface = timer_font.render(formatted_time, True, (255, 255, 255))
    screen.blit(timer_surface, (WIDTH - 200, 10)) 

    pygame.display.flip()  # 更新屏幕

pygame.quit()