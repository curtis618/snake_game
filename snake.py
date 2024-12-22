import pygame
import random
from collections import namedtuple
import numpy as np
# 初始化 Pygame
pygame.init()

# 定義基本元素
Point = namedtuple('Point', 'x, y')

# 顏色
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# 遊戲參數
BLOCK_SIZE = 20
SPEED = 10

# 方向
class Direction:
    RIGHT = "RIGHT"
    LEFT = "LEFT"
    UP = "UP"
    DOWN = "DOWN"

DIRECTION_OFFSETS = {
    Direction.RIGHT: Point(BLOCK_SIZE, 0),
    Direction.LEFT: Point(-BLOCK_SIZE, 0),
    Direction.DOWN: Point(0, BLOCK_SIZE),
    Direction.UP: Point(0, -BLOCK_SIZE),
}

class SnakeGame:
    def __init__(self, width, height):
        self.w = width
        self.h = height
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("貪食蛇")
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        """初始化遊戲狀態"""
        self.direction = Direction.RIGHT
        self.head = Point(self.w // 2, self.h // 2)
        self.snake = [
            self.head,
            Point(self.head.x - BLOCK_SIZE, self.head.y),
            Point(self.head.x - 2 * BLOCK_SIZE, self.head.y),
        ]
        self.score = 0
        self.food = None
        self._place_food()
        self.game_over = False

    def _place_food(self):
        """隨機放置食物，確保不與蛇體重疊"""
        while True:
            x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            food = Point(x, y)
            if food not in self.snake:
                self.food = food
                break

    def step(self, action):
        """根據動作更新遊戲狀態"""
        # 將動作 [0, 1, 2] 映射為方向
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if action == 0:  # 保持原方向
            new_dir = clock_wise[idx]
        elif action == 1:  # 右轉
            new_dir = clock_wise[(idx + 1) % 4]
        else:  # 左轉
            new_dir = clock_wise[(idx - 1) % 4]

        self.direction = new_dir

        # 移動蛇
        offset = DIRECTION_OFFSETS[self.direction]
        self.head = Point(self.head.x + offset.x, self.head.y + offset.y)
        self.snake.insert(0, self.head)

        # 計算回報
        reward = 0
        if self.is_collision():
            self.game_over = True
            reward = -10
            return self.get_state(), reward, self.game_over, self.score

        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()

        # 返回當前狀態、回報、遊戲是否結束
        return self.get_state(), reward, self.game_over, self.score

    def get_state(self):
        """將遊戲狀態編碼為數組，用於輸入 DQN"""
        head = self.head

        # 定義相對位置的危險狀態
        danger_straight = self.is_collision(head)
        danger_right = self.is_collision(Point(head.x + BLOCK_SIZE, head.y))
        danger_left = self.is_collision(Point(head.x - BLOCK_SIZE, head.y))

        # 食物方向
        food_left = self.food.x < head.x
        food_right = self.food.x > head.x
        food_up = self.food.y < head.y
        food_down = self.food.y > head.y

        state = [
            danger_straight, danger_right, danger_left,
            food_left, food_right, food_up, food_down
        ]
        return np.array(state, dtype=int)

    def is_collision(self, pt=None):
        """檢查是否發生碰撞"""
        if pt is None:
            pt = self.head
        # 邊界碰撞
        if pt.x < 0 or pt.x >= self.w or pt.y < 0 or pt.y >= self.h:
            return True
        # 自體碰撞
        if pt in self.snake[1:]:
            return True
        return False


    def _update_ui(self):
        """更新遊戲畫面"""
        self.display.fill(BLACK)

        # 畫蛇
        for pt in self.snake:
            pygame.draw.rect(self.display, GREEN, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))

        # 畫食物
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        # 顯示分數
        font = pygame.font.Font(None, 35)
        text = font.render(f"Score: {self.score}", True, WHITE)
        self.display.blit(text, [10, 10])

        pygame.display.flip()


if __name__ == "__main__":
    game = SnakeGame(640, 480)
    
    while not game.game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                # 根據按鍵改變方向
                if event.key == pygame.K_UP and game.direction != Direction.DOWN:
                    game.direction = Direction.UP
                elif event.key == pygame.K_DOWN and game.direction != Direction.UP:
                    game.direction = Direction.DOWN
                elif event.key == pygame.K_LEFT and game.direction != Direction.RIGHT:
                    game.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT and game.direction != Direction.LEFT:
                    game.direction = Direction.RIGHT
        
        # 執行一個步驟
        state, reward, game_over, score = game.step(0)  # 此處的 action 暫時保持 0（直行）
        game._update_ui()
        game.clock.tick(SPEED)
    
    print("Game Over! Final Score:", game.score)
    pygame.quit()

