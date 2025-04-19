import pygame
import random
import time
import sys
import numpy as np

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
GROUND_HEIGHT = 350
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAVITY = 1
GAME_SPEED = 10

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AI Dino Game")
clock = pygame.time.Clock()

class Dino:
    def __init__(self):
        self.width = 44
        self.height = 48
        self.x = 50
        self.y = GROUND_HEIGHT - self.height
        self.vel_y = 0
        self.jumping = False
        self.ducking = False
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def jump(self):
        if not self.jumping:
            self.vel_y = -18
            self.jumping = True
            
    def update(self):
        self.vel_y += GRAVITY
        self.y += self.vel_y
        
        if self.y >= GROUND_HEIGHT - self.height:
            self.y = GROUND_HEIGHT - self.height
            self.jumping = False
            self.vel_y = 0
            
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self):
        
        pygame.draw.rect(screen, BLACK, self.rect)
        
class Obstacle:
    def __init__(self, x):
        self.width = 20
        self.height = random.randint(30, 60)
        self.x = x
        self.y = GROUND_HEIGHT - self.height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def update(self):
        self.x -= GAME_SPEED
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self):
        pygame.draw.rect(screen, BLACK, self.rect)
        
class Game:
    def __init__(self):
        self.dino = Dino()
        self.obstacles = []
        self.score = 0
        self.game_over = False
        self.next_obstacle_time = 0
        
    def add_obstacle(self):
        self.obstacles.append(Obstacle(SCREEN_WIDTH))
        
    def update(self):
        if not self.game_over:

            self.dino.update()
            
           
            current_time = pygame.time.get_ticks()
            if current_time > self.next_obstacle_time:
                self.add_obstacle()
                self.next_obstacle_time = current_time + random.randint(1000, 2000)
            
          
            for obstacle in self.obstacles[:]:
                obstacle.update()
                
                if self.dino.rect.colliderect(obstacle.rect):
                    self.game_over = True
                
                if obstacle.x < -obstacle.width:
                    self.obstacles.remove(obstacle)
                    self.score += 1
    
    def get_state(self):
        """Get the game state for the AI"""
        nearest_obstacle = None
        nearest_distance = float('inf')
        
        for obstacle in self.obstacles:
            distance = obstacle.x - self.dino.x
            if distance > 0 and distance < nearest_distance:
                nearest_obstacle = obstacle
                nearest_distance = distance
        
        if nearest_obstacle:
            return [
                nearest_distance / SCREEN_WIDTH,  
                nearest_obstacle.width / SCREEN_WIDTH,  
                nearest_obstacle.height / SCREEN_HEIGHT,  
                GAME_SPEED / 20,  
                1 if self.dino.jumping else 0  
            ]
        else:
           
            return [1.0, 0, 0, GAME_SPEED / 20, 1 if self.dino.jumping else 0]
                
    def draw(self):

        screen.fill(WHITE)
        
        pygame.draw.line(screen, BLACK, (0, GROUND_HEIGHT), (SCREEN_WIDTH, GROUND_HEIGHT), 2)
        self.dino.draw()
        
        for obstacle in self.obstacles:
            obstacle.draw()
        
        
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {self.score}", True, BLACK)
        screen.blit(score_text, (10, 10))
        
        if self.game_over:
            game_over_text = font.render("Game Over", True, BLACK)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 18))
        
        
        pygame.display.flip()

class AI:
    def __init__(self):
        self.distance_threshold = 0.3 
        
    def make_decision(self, state):
        """Decide whether to jump or not based on the game state"""
        if not state:
            return False  
            
        distance_to_obstacle = state[0]  
        obstacle_height = state[2]  
        is_jumping = state[4]  
        
        
        if distance_to_obstacle < self.distance_threshold and not is_jumping:
            return True  
        return False  

def main():
    game = Game()
    ai = AI()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game.game_over:
                        # Restart game
                        game = Game()
                    else:
                        game.dino.jump()
                        
        state = game.get_state()
        if ai.make_decision(state) and not game.game_over:
            game.dino.jump()
        
        game.update()
        game.draw()
        
        clock.tick(60)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 