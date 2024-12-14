import pygame
import os

# 基本設置
FPS = 30
WIDTH, HEIGHT = 1000, 700
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_SPEED = 5
PLAYER_SIZE = (50, 50)

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
        if filename.endswith('.png') or filename.endswith('.jpg'):  # 支援 PNG 和 JPG
            img_path = os.path.join(frames_folder, filename)
            img = pygame.image.load(img_path).convert_alpha()  # 確保透明度支援
            img.set_colorkey(WHITE)  # 將白色設為透明
            img = scale_image(img, size)  # 縮小圖片
            frames.append(img)
    return frames

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
        self.jump_speed = 15
        self.gravity = 1
        self.jump_velocity = 0
        self.stop = False

    def jump(self):
        if not self.is_jumping:  # 僅在地面上允許跳躍
            self.is_jumping = True
            self.jump_velocity = -self.jump_speed

    def update(self, keys, background, obstacles):
        self.moving = False
        on_ground = False

        # 垂直移動與重力
        self.jump_velocity += self.gravity
        self.rect.y += self.jump_velocity

        # 障礙物碰撞檢測
        for obstacle in obstacles:
            # 玩家從上方接觸障礙物（落在障礙物上）
            if (
                self.rect.colliderect(obstacle.rect)
                and self.rect.bottom >= obstacle.rect.top
                and self.rect.bottom - self.jump_velocity <= obstacle.rect.top
            ):
                self.rect.bottom = obstacle.rect.top
                self.is_jumping = False
                self.jump_velocity = 0
                on_ground = True

            # 玩家頭部碰撞障礙物底部
            if (
                self.rect.colliderect(obstacle.rect)
                and self.rect.top <= obstacle.rect.bottom
                and self.rect.top - self.jump_velocity >= obstacle.rect.bottom
            ):
                self.rect.top = obstacle.rect.bottom  # 防止玩家穿過障礙物
                self.jump_velocity = 0  # 停止向上的速度

            # 玩家從左側撞到障礙物
            if (
                self.rect.colliderect(obstacle.rect)
                and self.rect.right >= obstacle.rect.left
                and self.rect.left < obstacle.rect.left
                and self.rect.bottom > obstacle.rect.top
                and self.rect.top < obstacle.rect.bottom
            ):
                self.rect.right = obstacle.rect.left  # 停止在障礙物的左側
                self.stop = True

            # 玩家從右側撞到障礙物
            if (
                self.rect.colliderect(obstacle.rect)
                and self.rect.left <= obstacle.rect.right
                and self.rect.right > obstacle.rect.right
                and self.rect.bottom > obstacle.rect.top
                and self.rect.top < obstacle.rect.bottom
            ):
                self.rect.left = obstacle.rect.right  # 停止在障礙物的右側
                self.stop = True
        # 地面碰撞
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.is_jumping = False
            self.jump_velocity = 0
            on_ground = True
            self.stop = False

        if not on_ground:
            self.is_jumping = True

        # 水平移動
        if pygame.K_d in keys :
            self.moving = True
            if self.rect.x < 200 or background.backgrounds[4][1].x <= 0:
                self.rect.x += PLAYER_SPEED
        if pygame.K_a in keys:
            self.rect.x -= PLAYER_SPEED
            self.moving = True

        # 邊界檢查
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

        # 動畫更新
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


# 定義背景類
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
    # 檢查鍵盤輸入
        keys = pygame.key.get_pressed()
        # 確保背景移動只在按下 D 鍵時進行
        if keys[pygame.K_d] and self.backgrounds[4][1].x >0 and player.stop == False:
             for i, (background_image, rect) in enumerate(self.backgrounds):
                rect.x -= PLAYER_SPEED * 2

    def draw(self, surface):
        for background_image, rect in self.backgrounds:
            surface.blit(background_image, rect.topleft)

class Obstacle:
    def __init__(self, size, x, y):
        self.image = pygame.Surface(size, pygame.SRCALPHA)  # 创建一个支持透明度的表面
        self.image.fill((0, 0, 0, 128))  # 填充颜色和透明度
        self.rect = self.image.get_rect()  # 设置位置
        self.rect.topleft = (x, y)

    def update(self, player):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]  and player.stop == False:
            self.rect.x -= PLAYER_SPEED * 2
       

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

# 創建玩家和背景
obstacles = []
player = Player()
obstacles.append(Obstacle((WIDTH+480, 50), 0, 610))
obstacles.append(Obstacle((315, 45), 480, 430))
obstacles.append(Obstacle((265, 43), 735, 291))
obstacles.append(Obstacle((268, 43), 1275, 375))
background = Background(background_frames)

class EntryScreen:
    def __init__(self, screen, image_path, font_path, font_size=74):
        self.screen = screen
        self.image = pygame.image.load(image_path).convert()  # 加載背景圖
        self.image = scale_image(self.image, (WIDTH, HEIGHT))  # 縮放到窗口大小
        self.font = pygame.font.Font(font_path, font_size)  # 加載字體
        self.text_surface = self.font.render("請按 Enter 開始", True, WHITE)  # 渲染文本
        self.text_rect = self.text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))  # 設置文本位置在畫面中央

    def show(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # 檢查是否按下 Enter 鍵
                        return  # 返回以開始遊戲

            # 畫面渲染初始畫面
            self.screen.blit(self.image, (0, 0))  # 畫背景
            self.screen.blit(self.text_surface, self.text_rect)  # 畫文本
            pygame.display.flip()  # 更新顯示

entry_screen = EntryScreen(screen, "entryscream.png", None)

# 顯示初始畫面
entry_screen.show()

# 遊戲主循環
running = True
keys_pressed = set() 

while running:
    clock.tick(FPS)
    
    # 處理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            keys_pressed.add(event.key)
            if event.key == pygame.K_SPACE:  
                player.jump()  # 調用玩家的跳躍方法
        if event.type == pygame.KEYUP:
            keys_pressed.discard(event.key)

    # 更新遊戲畫面
    player.update(keys_pressed, background, obstacles) 
    background.update(player)  
    for obstacle in obstacles:
        obstacle.update(player)
    # 畫面渲染
    screen.fill(BLACK)
    background.draw(screen)  
    for obstacle in obstacles:
        obstacle.draw(screen)
    player.draw(screen)
    pygame.display.flip()

pygame.quit()