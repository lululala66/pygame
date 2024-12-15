import pygame
import os

# 基本設置
FPS = 30
WIDTH, HEIGHT = 1000, 700
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_SPEED = 5
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
        self.jump_speed = 20
        self.gravity = 1
        self.jump_velocity = 0
        self.stop = False
        self.is_game_over = False

    def jump(self):
        if not self.is_jumping:  # 僅在地面上允許跳躍
            self.is_jumping = True
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

    def update(self, keys, background, obstacles):
        if self.is_game_over:
            return

        self.moving = False

        # 垂直移動與重力
        self.jump_velocity += self.gravity
        self.rect.y += self.jump_velocity

        # 處理碰撞
        on_ground = self.handle_collision(obstacles)

        # 檢查是否在地面
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.jump_velocity = 0
            on_ground = True
            self.is_jumping = False
            self.stop = False

        if not on_ground:
            self.is_jumping = True
            self.stop = False

        # 檢查是否掉出畫面
        if self.rect.top > HEIGHT:
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
        if keys[pygame.K_d] and self.backgrounds[4][1].x > 0 and player.stop == False:
            for i, (background_image, rect) in enumerate(self.backgrounds):
                rect.x -= PLAYER_SPEED * 2

    def draw(self, surface):
        for background_image, rect in self.backgrounds:
            surface.blit(background_image, rect.topleft)

class Obstacle:
    def __init__(self, size, x, y):
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 128))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self, player, background):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d] and player.stop == False:
            if background.backgrounds[4][1].x > 0:
                self.rect.x -= PLAYER_SPEED * 2

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
                self.rect.x -= PLAYER_SPEED * 2

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

    def show(self):
        text_surface = self.font.render("遊戲結束", True, (255, 0, 0))
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(text_surface, text_rect)
        pygame.display.flip()
        pygame.time.delay(2000)
# 創建玩家和背景
obstacles = []
coins = []
player = Player()
obstacles.append(Obstacle((WIDTH+480, 100), 0, 610))
obstacles.append(Obstacle((315, 45), 480, 430))
obstacles.append(Obstacle((265, 43), 735, 291))
obstacles.append(Obstacle((60, 50), 1135, 565)) #pipe
obstacles.append(Obstacle((268, 43), 1275, 375))
obstacles.append(Obstacle((268, 43), 1613, 212))
obstacles.append(Obstacle((65, 50), 1733, 252)) #pipe
obstacles.append(Obstacle((500, 100), 1855, 610))
#stair
obstacles.append(Obstacle((355, 43), 2100, 567))
obstacles.append(Obstacle((325, 43), 2145, 524))
obstacles.append(Obstacle((285, 43), 2190, 483))
obstacles.append(Obstacle((240, 43), 2235, 448))
obstacles.append(Obstacle((195, 43), 2280, 403))
obstacles.append(Obstacle((145, 43), 2325, 358))
obstacles.append(Obstacle((98, 43), 2375, 315))
#stair
obstacles.append(Obstacle((375, 43), 2570, 567))
obstacles.append(Obstacle((325, 43), 2570, 524))
obstacles.append(Obstacle((285, 43), 2570, 483))
obstacles.append(Obstacle((240, 43), 2570, 448))
obstacles.append(Obstacle((195, 43), 2570, 403))
obstacles.append(Obstacle((145, 43), 2570, 358))
obstacles.append(Obstacle((98, 43), 2570, 315))
obstacles.append(Obstacle((WIDTH*3, 100), 2570, 610))
coins.append(Coin(500,385))
background = Background(background_frames)
game_over_screen = GameOverScreen(screen)

entry_screen = EntryScreen(screen, "entryscream.png", font_name)

entry_screen.show()
# 遊戲主循環
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
            
    time_remaining -= clock.get_time() / 1000  # 減去每幀過去的秒數
    if time_remaining <= 0:
        time_remaining = 0  # 確保時間不會變為負數
        player.is_game_over = True  # 倒計時結束觸發遊戲結束

    if player.is_game_over:
        game_over_screen.show()
        running = False
        continue

    player.update(keys_pressed, background, obstacles)
    background.update(player)
    for obstacle in obstacles:
        obstacle.update(player, background)

    for coin in coins[:]: 
        if coin.check_collision(player):
            POINT += 100
            coins.remove(coin)

    for coin in coins:
        coin.update(player, background)

    screen.fill(BLACK)
    background.draw(screen)
    for obstacle in obstacles:
        obstacle.draw(screen)
    for coin in coins:
        coin.draw(screen)
    player.draw(screen)
    draw_text(screen, "SCRODE:" + str(POINT), 18, WIDTH - 70, 10)
    draw_text(screen, "TIME:", 18, WIDTH - 230, 10)
    formatted_time = f"{int(time_remaining * 100):06}"  # 轉為毫秒並固定 6 位數
    timer_surface = timer_font.render(formatted_time, True, (255, 255, 255))
    screen.blit(timer_surface, (WIDTH - 200, 10))  # 設置顯示位置（右上角偏左一些）

    pygame.display.flip()  # 更新屏幕

pygame.quit()