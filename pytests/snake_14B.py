import pygame
import random

# Inicialização do Pygame
pygame.init()

# Configurações do jogo
LARGURA = 800
ALTURA = 600
TAMANHO_BLOCO = 20
VELOCIDADE = 10

# Cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
VERDE = (0, 255, 0)
VIOLETA = (127, 0, 255)

# Inicialização da tela
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo da Cobra")

# Relógio para controlar a velocidade do jogo
relogio = pygame.time.Clock()

# Função para criar comida aleatória
def criar_comida(snake):
    x = random.randint(0, (LARGURA - 1) // TAMANHO_BLOCO) * TAMANHO_BLOCO
    y = random.randint(0, (ALTURA - 1) // TAMANHO_BLOCO) * TAMANHO_BLOCO
    while (x, y) in snake:
        x = random.randint(0, (LARGURA - 1) // TAMANHO_BLOCO) * TAMANHO_BLOCO
        y = random.randint(0, (ALTURA - 1) // TAMANHO_BLOCO) * TAMANHO_BLOCO
    return x, y

# Função principal do jogo
def jogo():
    game_over = False
    score = 0

    # Snake inicial
    snake = [(LARGURA//2, ALTURA//2)]
    comida = criar_comida(snake)

    # Direção inicial
    direcao = "UP"

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direcao != "DOWN":
                    direcao = "UP"
                elif event.key == pygame.K_DOWN and direcao != "UP":
                    direcao = "DOWN"
                elif event.key == pygame.K_LEFT and direcao != "RIGHT":
                    direcao = "LEFT"
                elif event.key == pygame.K_RIGHT and direcao != "LEFT":
                    direcao = "RIGHT"

        # Atualização da cobra
        head = snake[0]
        x, y = head

        if direcao == "UP":
            y -= TAMANHO_BLOCO
        elif direcao == "DOWN":
            y += TAMANHO_BLOCO
        elif direcao == "LEFT":
            x -= TAMANHO_BLOCO
        elif direcao == "RIGHT":
            x += TAMANHO_BLOCO

        new_head = (x, y)
        snake.insert(0, new_head)

        # Verificação de colisão com comida
        if new_head == (comida[0], comida[1]):
            score += 1
            comida = criar_comida(snake)
        else:
            snake.pop()

        # Verificação de colisão com paredes
        if x < 0 or x >= LARGURA or y < 0 or y >= ALTURA:
            game_over = True

        # Verificação de colisão com si mesma
        for segmento in snake[1:]:
            if new_head == segmento:
                game_over = True
                break

        # Limpar a tela
        tela.fill(PRETO)

        # Desenhar a comida
        pygame.draw.rect(tela, VIOLETA, (comida[0], comida[1], TAMANHO_BLOCO, TAMANHO_BLOCO))

        # Desenhar a cobra
        for i, segmento in enumerate(snake):
            if i == 0:
                pygame.draw.rect(tela, VERDE, (segmento[0], segmento[1], TAMANHO_BLOCO, TAMANHO_BLOCO))
            else:
                pygame.draw.rect(tela, PRETO, (segmento[0], segmento[1], TAMANHO_BLOCO, TAMANHO_BLOCO))

        # Atualizar a pontuação
        fonte = pygame.font.Font(None, 36)
        texto = fonte.render(f"Pontuação: {score}", True, BRANCO)
        tela.blit(texto, (10, 10))

        pygame.display.flip()
        relogio.tick(VELOCIDADE)

    # Tela de Game Over
    while True:
        tela.fill(PRETO)
        fonte = pygame.font.Font(None, 74)
        texto_game_over = fonte.render("Game Over", True, BRANCO)
        texto_pontuação = fonte.render(f"Pontuação Final: {score}", True, BRANCO)
        
        # Botão para reiniciar
        botao = pygame.Surface((200, 50))
        botao.fill(BRANCO)
        botao_rect = botao.get_rect(center=(LARGURA//2, 300))
        
        # Posicionar textos
        texto_game_over_rect = texto_game_over.get_rect(center=(LARGURA//2, 150))
        texto_pontuação_rect = texto_pontuação.get_rect(center=(LARGURA//2, 200))
        
        # Desenhar elementos
        tela.blit(texto_game_over, texto_game_over_rect)
        tela.blit(texto_pontuação, texto_pontuação_rect)
        tela.blit(botao, botao_rect)

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if botao_rect.collidepoint(event.pos):
                    return  # Reinicia o jogo

        pygame.display.flip()

# Função para pausar o jogo
def pausar():
    pausado = True
    while pausado:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pausado = False
        tela.fill(PRETO)
        fonte = pygame.font.Font(None, 74)
        texto = fonte.render("Pausa", True, BRANCO)
        tela.blit(texto, (LARGURA//2 - 100, ALTURA//2 - 50))
        pygame.display.flip()

# Menu principal
def menu():
    while True:
        tela.fill(PRETO)
        fonte = pygame.font.Font(None, 74)
        texto = fonte.render("Jogo da Cobra", True, BRANCO)
        texto2 = fonte.render("Pressione espaço para jogar", True, BRANCO)
        
        # Botão para jogar
        botao = pygame.Surface((200, 50))
        botao.fill(BRANCO)
        botao_rect = botao.get_rect(center=(LARGURA//2, 300))
        
        # Posicionar textos
        texto_rect = texto.get_rect(center=(LARGURA//2, 150))
        texto2_rect = texto2.get_rect(center=(LARGURA//2, 250))
        
        # Desenhar elementos
        tela.blit(texto, texto_rect)
        tela.blit(texto2, texto2_rect)
        tela.blit(botao, botao_rect)

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return  # Iniciar o jogo
            if event.type == pygame.MOUSEBUTTONDOWN:
                if botao_rect.collidepoint(event.pos):
                    return  # Iniciar o jogo

        pygame.display.flip()

# Loop principal do jogo
jogando = True
while jogando:
    menu()
    jogo()
    pausar()

pygame.quit()