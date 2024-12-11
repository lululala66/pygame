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
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.frames = player_frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (200, 585)
        self.animation_timer = 0
        self.frame_rate = 6
        self.moving = False
        self.is_jumping = False  # 跳躍狀態
        self.jump_speed = 40  # 跳躍速度
        self.gravity = 5  # 重力

    def jump(self):
        if not self.is_jumping:  # 確保只有在不跳躍的情況下才能跳躍
            self.is_jumping = True
            self.jump_velocity = -self.jump_speed  # 設置跳躍速度為負值

    def update(self, keys, background):
        self.moving = False  # 每次更新時重置移動狀態

        if pygame.K_d in keys:
            self.moving = True
            if  background.image1 == background_frames[4] and background.rect1.right <= WIDTH or self.rect.x !=200 :
                self.rect.x += PLAYER_SPEED
        if pygame.K_a in keys:
            self.rect.x -= PLAYER_SPEED
            self.moving = True

        # 處理跳躍邏輯
        if self.is_jumping:
            self.rect.y += self.jump_velocity  # 更新 y 位置
            self.jump_velocity += self.gravity  # 增加重力影響

            # 檢查是否回到地面
            if self.rect.y >= 555:  # 假設地面在 y=585
                self.rect.y = 555  # 確保角色不會掉出地面
                self.is_jumping = False  # 跳躍結束

        # 邊界檢查
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

        # 更新動畫幀
        if self.moving:
            self.animation_timer += clock.get_time()
            if self.animation_timer > 1000 // self.frame_rate:
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.animation_timer = 0
        else:
            self.frame_index = 0

        self.image = self.frames[self.frame_index]

# 定義背景類
class Background:
    def __init__(self, frames):
        self.frames = frames
        self.frame_index = 0
        self.image1 = self.frames[self.frame_index]
        self.image2 = self.frames[(self.frame_index + 1) % len(self.frames)]
        self.frame_index = 1
        self.rect1 = self.image1.get_rect(topleft=(0, 0))  # 第一張圖片的初始位置
        self.rect2 = self.image2.get_rect(topleft=(WIDTH, 0))  # 第二張圖片的初始位置在右側

    def update(self, player):
        # 只有當玩家移動時才更新背景位置
        keys = pygame.key.get_pressed()
        if self.image2 != self.frames[5] :
            if  keys[pygame.K_d]:
                self.rect1.x -= PLAYER_SPEED*2
                self.rect2.x -= PLAYER_SPEED*2
                if self.rect1.right < 0:  # 當第一張圖片完全移出畫面
                    self.frame_index = (self.frame_index + 1) % len(self.frames)
                    self.image1 = self.frames[self.frame_index]
                    self.rect1.x = self.rect2.right  # 將第一張圖片的位置設置為第二張圖片的右側

                if self.rect2.right < 0:  # 當第二張圖片完全移出畫面
                    self.frame_index = (self.frame_index + 1) % len(self.frames)
                    self.image2 = self.frames[self.frame_index]
                    self.rect2.x = self.rect1.right  # 將第二張圖片的位置設置為第一張圖片的右側

    def draw(self, surface):
        surface.blit(self.image1, self.rect1.topleft)  # 畫第一張背景
        surface.blit(self.image2, self.rect2.topleft)  # 畫第二張背景

class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((175,50), pygame.SRCALPHA)  # 创建一个支持透明度的表面
        self.image.fill((0, 0, 0, 128))  # 填充颜色和透明度
        self.rect = self.image.get_rect()  # 设置位置
        self.rect.center = (200, 585)

    def update(self, keys, background):
         self.rect.center = (200, 585)  # 長方形位置
        



# 創建玩家和背景
all_sprites = pygame.sprite.Group()
player = Player()
obstacle = Obstacle()
all_sprites.add(player)
all_sprites.add(obstacle)

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

# 調用顯示初始畫面的方法
entry_screen.show()

# 遊戲主循環
running = True
keys_pressed = set()  # 用來跟蹤當前按下的鍵

while running:
    clock.tick(FPS)
    
    # 處理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            keys_pressed.add(event.key)  # 當按鍵被按下時，將其添加到集合中
            if event.key == pygame.K_SPACE:  # 檢查是否按下空白鍵
                player.jump()  # 調用玩家的跳躍方法
        if event.type == pygame.KEYUP:
            keys_pressed.discard(event.key)  # 當按鍵被釋放時，將其從集合中移除

    # 更新遊戲畫面
    all_sprites.update(keys_pressed, background)  # 將按鍵狀態和背景傳遞給玩家更新方法
    background.update(player)  # 更新背景，傳入玩家對象

    # 畫面渲染
    screen.fill(BLACK)
    background.draw(screen)  # 畫背景
    all_sprites.draw(screen)  # 畫玩家
    pygame.display.flip()

pygame.quit()