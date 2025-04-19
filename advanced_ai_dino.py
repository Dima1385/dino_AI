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
pygame.display.set_caption("Advanced AI Dino Game")
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
        self.jump_height = 18 
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def jump(self):
        if not self.jumping:
            self.vel_y = -self.jump_height
            self.jumping = True
            
    def small_jump(self):
        """Perform a smaller jump for lower obstacles"""
        if not self.jumping:
            self.vel_y = -15 
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
        obstacle_types = ["small", "small", "medium", "medium", "large"] 
        self.type = random.choice(obstacle_types)
        
        if self.type == "small":
            self.width = 20
            self.height = random.randint(20, 30)
        elif self.type == "medium":
            self.width = 20
            self.height = random.randint(31, 50)
        else: 
            self.width = 20
            self.height = random.randint(51, 70)
            
        self.x = x
        self.y = GROUND_HEIGHT - self.height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def update(self):
        self.x -= GAME_SPEED
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self):
        if self.type == "small":
            color = (0, 200, 0)  
        elif self.type == "medium":
            color = (0, 0, 200)
        else:
            color = (200, 0, 0)  
            
        pygame.draw.rect(screen, color, self.rect)
        
class Game:
    def __init__(self):
        self.dino = Dino()
        self.obstacles = []
        self.score = 0
        self.game_over = False
        self.next_obstacle_time = 0
        self.base_game_speed = GAME_SPEED
        self.game_speed = self.base_game_speed
        self.difficulty_increase_rate = 0.001  
        self.debug = False  
        
    def add_obstacle(self):
        min_distance = 300
        if self.obstacles and random.random() < 0.2:
            min_distance = 200
            
        self.obstacles.append(Obstacle(SCREEN_WIDTH + min_distance))
        
    def update(self):
        if not self.game_over:
            self.dino.update()
            
            self.game_speed = self.base_game_speed + (self.score * self.difficulty_increase_rate)
            
            current_time = pygame.time.get_ticks()
            if current_time > self.next_obstacle_time:
                self.add_obstacle()
                if self.debug:
                    print(f"Додано перешкоду: {self.obstacles[-1].type}, висота: {self.obstacles[-1].height}")
                time_gap = max(800, 2000 - self.score * 10)
                self.next_obstacle_time = current_time + random.randint(time_gap, time_gap + 500)
            

            for obstacle in self.obstacles[:]:
                obstacle.x -= self.game_speed
                obstacle.rect = pygame.Rect(obstacle.x, obstacle.y, obstacle.width, obstacle.height)
                
                if self.dino.rect.colliderect(obstacle.rect):
                    self.game_over = True
                    if self.debug:
                        print(f"Гра закінчена. Зіткнення з перешкодою {obstacle.type}")
                
                if obstacle.x < -obstacle.width:
                    if self.debug:
                        print(f"Перешкоду {obstacle.type} успішно пройдено")
                    self.obstacles.remove(obstacle)
                    self.score += 1
    
    def get_state(self):
        """Get the game state for the AI"""
        upcoming_obstacles = []
        for obstacle in sorted(self.obstacles, key=lambda o: o.x):
            if obstacle.x > self.dino.x and len(upcoming_obstacles) < 3: 
                upcoming_obstacles.append(obstacle)
        
        state = [
            1.0, 
            0.0,  
            0.0,
            0.0, 
            0.0,  
            0.0,  
            0.0, 
            self.game_speed / 20.0, 
            1 if self.dino.jumping else 0,
            self.dino.vel_y / 20.0 
        ]
        
        if len(upcoming_obstacles) > 0:
            o1 = upcoming_obstacles[0]
            distance = (o1.x - self.dino.x) / SCREEN_WIDTH
            state[0] = distance
            state[1] = o1.width / SCREEN_WIDTH
            state[2] = o1.height / SCREEN_HEIGHT
            
        if len(upcoming_obstacles) > 1:
            o2 = upcoming_obstacles[1]
            distance = (o2.x - self.dino.x) / SCREEN_WIDTH
            state[3] = distance
            state[4] = o2.height / SCREEN_HEIGHT
            
        if len(upcoming_obstacles) > 2:
            o3 = upcoming_obstacles[2]
            distance = (o3.x - self.dino.x) / SCREEN_WIDTH
            state[5] = distance
            state[6] = o3.height / SCREEN_HEIGHT
            
        return state
                
    def draw(self):
        screen.fill(WHITE)
        
        pygame.draw.line(screen, BLACK, (0, GROUND_HEIGHT), (SCREEN_WIDTH, GROUND_HEIGHT), 2)
        
        self.dino.draw()
        

        for obstacle in self.obstacles:
            obstacle.draw()

        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {self.score}", True, BLACK)
        speed_text = font.render(f"Speed: {self.game_speed:.1f}", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(speed_text, (10, 50))
        
        if self.game_over:
            game_over_text = font.render("Game Over - Press SPACE to restart", True, BLACK)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 18))
        
        pygame.display.flip()

class AdvancedAI:
    def __init__(self):

        self.distance_threshold = 0.3 
        self.height_threshold = 0.15  
        
        self.high_score = 0
        self.last_scores = []
        
    def make_decision(self, state):
        """Advanced decision logic based on the game state"""
        if not state:
            return None 
            

        distance_to_obstacle = state[0] 
        obstacle_height = state[2]  
        is_jumping = state[8]
        vertical_velocity = state[9]  
        

        second_obstacle_distance = state[3]
        second_obstacle_height = state[4]
        action = None
        
        if is_jumping:
            return None
            
        jump_threshold = self.calculate_jump_threshold(obstacle_height, state[7])  
        
        if distance_to_obstacle < jump_threshold:
            if obstacle_height < self.height_threshold:
                action = "small_jump"
            else:
                action = "jump"
                
            if second_obstacle_distance > 0 and second_obstacle_distance < 0.4:
                action = "jump"
        
        return action
    
    def calculate_jump_threshold(self, obstacle_height, game_speed):
        """Dynamically calculate jump threshold based on obstacle height and game speed"""
        threshold = self.distance_threshold
        
        if obstacle_height < self.height_threshold:
            threshold += 0.03
        elif obstacle_height > 0.15: 
            threshold += 0.05
            
        speed_factor = game_speed - 0.5  
        if speed_factor > 0:
            threshold += speed_factor * 0.05
            
        return threshold
    
    def track_performance(self, score):
        """Track performance to potentially adjust parameters"""
        self.last_scores.append(score)
        if len(self.last_scores) > 10:
            self.last_scores.pop(0)
            
        if score > self.high_score:
            self.high_score = score
            

def main():
    game = Game()
    ai = AdvancedAI()
    
    running = True
    manual_control = False  
    debug = False
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game.game_over:
                        ai.track_performance(game.score)
                        game = Game()
                    elif manual_control:
                        game.dino.jump()
                if event.key == pygame.K_m:
                    manual_control = not manual_control
                    print(f"Режим змінено на: {'Ручний' if manual_control else 'AI'}")
                    
        if not manual_control and not game.game_over:
            nearest_obstacle = None
            nearest_distance = float('inf')
            
            for obstacle in game.obstacles:
                distance = obstacle.x - game.dino.x
                if distance > 0 and distance < nearest_distance:
                    nearest_obstacle = obstacle
                    nearest_distance = distance
            
            
            if nearest_obstacle:
                jump_distance = 200 
                jump_distance = jump_distance * (game.game_speed / 10.0)
                
                if debug and nearest_distance < 300:
                    print(f"Відстань до перешкоди: {nearest_distance:.1f}, "
                          f"Тип: {nearest_obstacle.type}, "
                          f"Висота: {nearest_obstacle.height}, "
                          f"Стрибок при: {jump_distance:.1f}")
                
                if nearest_distance < jump_distance and not game.dino.jumping:
                    if nearest_obstacle.height < 35:
                        if debug:
                            print(f"Малий стрибок над {nearest_obstacle.type}")
                        game.dino.small_jump()
                    else:
                        if debug:
                            print(f"Повний стрибок над {nearest_obstacle.type}")
                        game.dino.jump()
        
        game.update()
        game.draw()
        
        font = pygame.font.SysFont(None, 24)
        control_text = font.render(f"Mode: {'Manual' if manual_control else 'AI'} (Press M to toggle)", True, BLACK)
        screen.blit(control_text, (SCREEN_WIDTH - 300, 10))
        
       
        high_score_text = font.render(f"High Score: {ai.high_score}", True, BLACK)
        screen.blit(high_score_text, (SCREEN_WIDTH - 160, 40))
        
        pygame.display.flip()
        
        clock.tick(60)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 