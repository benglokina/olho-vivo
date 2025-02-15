import pygame
import random
import time

# Configurações do jogo
WIDTH = 800
HEIGHT = 600
CELL_SIZE = 20
FPS = 15

# Inicializa Pygame
pygame.init()

# Cria a janela
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Coisas necessárias para o jogo
snake_block = CELL_SIZE
snake = [
    [WIDTH // 2, HEIGHT // 2],
    [WIDTH // 2 - CELL_SIZE, HEIGHT // 2],
    [WIDTH // 2 - 2 * CELL_SIZE, HEIGHT // 2]
]
direction = "right"  # variável para a direção inicial
food_pos = None
score = 0
game_over = False

# Cores do jogo
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Função para geração aleatória de food
def generate_food():
    global food_pos
    food_pos = [random.randint(0, WIDTH // CELL_SIZE - 1) * CELL_SIZE,
                random.randint(0, HEIGHT // CELL_SIZE - 1) * CELL_SIZE]

# Função para atualizar o score
def update_score():
    score += 1
    pygame.font.init(size=50)
    font = pygame.font.Font(None, 50)
    text = font.render(f"Score: {score}", True, WHITE)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    window.blit(text, text_rect)
    pygame.display.flip()

# Função para mover o snake
def move_snake():
    global snake, direction, food_pos
    if direction == "up":
        snake[0] = [snake[0][0], snake[0][1] - CELL_SIZE]
    elif direction == "down":
        snake[0] = [snake[0][0], snake[0][1] + CELL_SIZE]
    elif direction == "left":
        snake[0] = [snake[0][0] - CELL_SIZE, snake[0][1]]
    elif direction == "right":
        snake[0] = [snake[0][0] + CELL_SIZE, snake[0][1]]
    
    # Verifica colisão com os wall
    head = snake[0]
    if head[0] < 0 or head[0] >= WIDTH // CELL_SIZE or head[1] < 0 or head[1] >= HEIGHT // CELL_SIZE:
        game_over = True
        pygame.time.wait(2000)
    
    # Verifica colisão com o corpo do snake
    for body_part in snake[1:]:
        if head[0] == body_part[0] and head[1] == body_part[1]:
            game_over = True
            pygame.time.wait(2000)
    
    if not game_over:
        snake.pop(-1)
        snake.append(direction)
    
    # Verifica se o snake coletou o food
    head = snake[0]
    if head[0] == food_pos[0] and head[1] == food_pos[1]:
        generate_food()
        update_score()

# Função para pular frame
def jump_frame():
    window.fill(BLACK)
    pygame.time.wait(FPS * 1000)
    window.fill(BLACK)
    pygame.time.wait(FPS * 1000)
    window.fill(BLACK)

# Função para geração aleatória de food
def generate_food():
    global food_pos
    food_pos = [random.randint(0, WIDTH // CELL_SIZE - 1) * CELL_SIZE,
                random.randint(0, HEIGHT // CELL_SIZE - 1) * CELL_SIZE]

# Loop principal do jogo
while not game_over:
    move_snake()
    
    # Verifica se o jogo terminou
    if game_over:
        break
    
    # Verifica se o jogador apertou a tecla para parar
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if direction != "down":
                    direction = "up"
            elif event.key == pygame.K_DOWN:
                if direction != "up":
                    direction = "down"
            elif event.key == pygame.K_LEFT:
                if direction != "right":
                    direction = "left"
            elif event.key == pygame.K_RIGHT:
                if direction != "left":
                    direction = "right"
    
    # Desenha o jogo
    window.fill(BLACK)
    
    # Desenha o snake
    for body_part in snake:
        pygame.draw.rect(window, GREEN, [body_part[0], body_part[1], CELL_SIZE, CELL_SIZE])
    
    # Desenha o food
    pygame.draw.rect(window, RED, [food_pos[0], food_pos[1], CELL_SIZE, CELL_SIZE])
    
    # Mostra a pontuação
    font = pygame.font.Font(None, 50)
    text = font.render(f"Score: {score}", True, WHITE)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    window.blit(text, text_rect)
    
    # Mostra o menu de再来一次
    font = pygame.font.Font(None, 50)
    text = font.render("再来一次", True, WHITE)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    window.blit(text, text_rect)
    
    # Mostra a pontuação
    font = pygame.font.Font(None, 50)
    text = font.render(f"Score: {score}", True, WHITE)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    window.blit(text, text_rect)
    
    pygame.display.flip()

pygame.quit()