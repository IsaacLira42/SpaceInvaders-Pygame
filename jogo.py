import pygame
from pygame.locals import *
import random

pygame.init()

musica_de_fundo = pygame.mixer.music.load('music_and_sounds/musica_jogo.mp3')
pygame.mixer.music.play(-1)

som_laser = pygame.mixer.Sound('music_and_sounds/som_laser.wav')
som_laser.set_volume(0.8)

som_explosao = pygame.mixer.Sound('music_and_sounds/som_explosion.wav')
som_explosao.set_volume(0.8)

# Variáveis e propriedades da tela
largura = 600
altura = 700
screen = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Invasores Espaciais")

# Variáveis do jogo
linhas = 3
colunas = 5
alienigena_cooldown = 1000
ultimo_tiro_alien = pygame.time.get_ticks()

# cores
red = (255, 0, 0)
green = (0, 255, 0)

# Frames
FPS = 60
relogio = pygame.time.Clock()

# Carregar imagem
BG = pygame.image.load("img/backgrounds/espaco_bg.png")
def draw_bg():
    screen.blit(BG, (0,0))

# Texto
fonte = pygame.font.Font(None, 30)  # None usa a fonte padrão, e 36 é o tamanho


# Classe da nave espacial
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/naves/jogador/0.png")
        self.image = pygame.transform.scale(self.image, (self.image.get_width()*0.4, self.image.get_height()*0.4))
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.vida_inicial = health
        self.vida_restante = health
        self.ultimo_tiro = pygame.time.get_ticks()
    
    def update(self):
        # Velocidade
        velocidade = 5

        # Tempo entre cada disparo
        COOLDOWN = 800 # MILISEGUNDOS

        # Detectar teclas pressionadas
        key = pygame.key.get_pressed()
        if (key[pygame.K_LEFT] or key[pygame.K_a]) and self.rect.left > 0:
            self.rect.x -= velocidade
        if (key[pygame.K_RIGHT] or key[pygame.K_d]) and self.rect.right < largura:
            self.rect.x += velocidade

        tempo_atual = pygame.time.get_ticks()
        # Atirar
        if key[pygame.K_SPACE] and tempo_atual - self.ultimo_tiro > COOLDOWN:
            som_laser.play()
            bullet_group.add(Bullets(self.rect.centerx, self.rect.top))
            self.ultimo_tiro = tempo_atual

        # Atualizar Mask
        self.mask = pygame.mask.from_surface(self.image)

        # Barra de vida
        pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom+12), self.rect.width, 5))
        if self.vida_restante > 0:
            pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom+12), int(self.rect.width * (self.vida_restante / self.vida_inicial)), 5))
        elif self.vida_restante <= 0:
            exp = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(exp)
            self.kill()

# Classe da Bala
class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/bullets/2.png")
        self.image = pygame.transform.scale(self.image, (self.image.get_width()*0.25, self.image.get_height()*0.25))
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]

    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()
        # Colisões
        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            som_explosao.play()
            exp = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(exp)

# Classe dos inimigos
class Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/naves/aliens/" + str(random.randint(0, 4)) +".png")
        self.image = pygame.transform.scale(self.image, (self.image.get_width()*0.25, self.image.get_height()*0.25))
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.move_counter = 0
        self.move_direction = 1

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 75:
            self.move_direction *= -1
            self.move_counter *= self.move_direction

# Classe da Bala dos aliens
class Alien_Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/bullets/1.png")
        self.image = pygame.transform.scale(self.image, (self.image.get_width()*0.25, self.image.get_height()*0.25))
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]

    def update(self):
        self.rect.y += 2
        if self.rect.top > altura:
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            # Reduz a vida da spaçonave
            self.kill()
            som_explosao.play()
            spaceship.vida_restante -= 1
            exp = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(exp)

# Classe das explosoes
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1,6):
            img = pygame.image.load(f"img/explosions/exp{num}.png")
            if size == 1:
                img = pygame.transform.scale(img, (20,20))
            if size == 2:
                img = pygame.transform.scale(img, (40,40))
            if size == 3:
                img = pygame.transform.scale(img, (160,160))
            # Adicionando imagem na lista
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.counter = 0
    
    def update(self):
        velocidade_da_explosao = 3
        # Atualizar animação da explosão
        self.counter += 1

        if self.counter >= velocidade_da_explosao and self.index < len(self.images) -1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        # Se a animação for completa, deletar a explosão
        if self.index >= len(self.images) - 1 and self.counter >= velocidade_da_explosao:
            self.kill()

# Grupos de sprites
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

def mensagem():
    global run, pause  # Agora vamos controlar a pausa do jogo
    if len(alien_group) == 0:
        mensagem = fonte.render("Você ganhou! Pressione 'R' para reiniciar.", True, (255,255,255))
        screen.blit(mensagem, (largura//2 - 200, 400))  # Ajuste para centralizar
        pause = True  # Congela o jogo
    if spaceship.vida_restante <= 0:
        mensagem = fonte.render("Game Over! Pressione 'R' para reiniciar.", True, (255,255,255))
        screen.blit(mensagem, (largura//2 - 200, 400))  # Ajuste para centralizar
        pause = True  # Congela o jogo

def reiniciar_jogo():
    global spaceship, alien_group, bullet_group, alien_bullet_group, explosion_group
    spaceship.kill()
    spaceship = Spaceship(largura // 2, altura - 70, 5)
    spaceship_group.add(spaceship)

    bullet_group.empty()
    alien_bullet_group.empty()
    explosion_group.empty()

    alien_group.empty()
    creat_aliens()

def creat_aliens():
    # Gerar aliens
    for row in range(linhas):
        for item in range(colunas):
            alien = Aliens(100 + item * 100,  50 + row * 70)
            alien_group.add(alien)

creat_aliens()

# Crier Jogador
spaceship = Spaceship(largura//2, altura-70, 5)
spaceship_group.add(spaceship)

pause = False

run = True
while run:
    relogio.tick(FPS)
    draw_bg()

    if not pause:
        # criar balas alienigenas aleatoriamente
        tempo_atual = pygame.time.get_ticks()
        # Atirar
        if tempo_atual - ultimo_tiro_alien > alienigena_cooldown and len(alien_bullet_group) < 8 and len(alien_group) > 0:
            attacking_alien = random.choice(alien_group.sprites())
            Alien_bullet = Alien_Bullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom)
            alien_bullet_group.add(Alien_bullet)
            ultimo_tiro_alien = tempo_atual
            som_laser.play()
            
        # Atualizar Nave espacial
        spaceship.update()

        # Atualizar grupos
        bullet_group.update()
        alien_group.update()
        alien_bullet_group.update()
        explosion_group.update()

        # Desenhar grupos
        spaceship_group.draw(screen)
        bullet_group.draw(screen)
        alien_group.draw(screen)
        alien_bullet_group.draw(screen)
        explosion_group.draw(screen)

    mensagem()

    # Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            run = False
        if pause and evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_r:
                pause = False
                reiniciar_jogo()

    pygame.display.update()
pygame.quit()