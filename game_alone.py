import pygame
import random

#Ruta con imagenes y audios
SPRITES = r"C:/Users/laura_i3r1i/Downloads/python_2025/JuegoGorosito/sprites/"
SOUNDS  = r"C:/Users/laura_i3r1i/Downloads/python_2025/JuegoGorosito/sounds/"

#Ventana de display y frames 
FPS = 60
WIDTH, HEIGHT = 1200, 600

#Objetivo del juego
TARGET_KILLS = 10   

#Delimitamos nuestros personajes/objetos y los escalamos
class Actor:
    def __init__(self, image_path, pos=(0, 0), scale=1.0):
        self._base_images = [pygame.image.load(image_path).convert_alpha()]
        self.current_image_index = 0
        self.scale = scale
        self._mask = None 

#Colision con las balas
        img = self.get_current_image()
        self.rect = img.get_rect(center=pos)
        self.fps = 0
        self._anim_counter = 0

    @property
    def x(self):
        return self.rect.centerx

    @x.setter
    def x(self, v):
        self.rect.centerx = v

    @property
    def y(self):
        return self.rect.centery

    @y.setter
    def y(self, v):
        self.rect.centery = v

    @property
    def images(self):
        return self._base_images

    @images.setter
    def images(self, paths):
        self._base_images = [pygame.image.load(p).convert_alpha() for p in paths]
        self.current_image_index = 0
        self._anim_counter = 0
        self.invalidate_mask()

        img = self.get_current_image()
        self.rect = img.get_rect(center=self.rect.center)

    def animate(self):
        if self.fps <= 0 or len(self._base_images) <= 1:
            return

        self._anim_counter += 1
        frames_per_image = max(1, int(FPS / self.fps))

        if self._anim_counter >= frames_per_image:
            self._anim_counter = 0
            self.current_image_index = (self.current_image_index + 1) % len(self._base_images)
            self.invalidate_mask()
    def get_current_image(self):
        img = self._base_images[self.current_image_index]

        if self.scale != 1.0:
            w, h = img.get_size()
            img = pygame.transform.scale(img, (int(w * self.scale), int(h * self.scale)))

        return img

    def draw(self, surface):
        img = self.get_current_image()
        rect = img.get_rect(center=self.rect.center)
        self.rect = rect
        surface.blit(img, rect)
    
    def get_mask(self):
        if self._mask is None:
            img = self.get_current_image()
            self._mask = pygame.mask.from_surface(img)
        return self._mask

    def invalidate_mask(self):
        self._mask = None

#Inicio del  juego 
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BLINKILL WITH ZOMBIES")
clock = pygame.time.Clock()
running = True

#Finaliza con la cantidad de zombies muertos
game_over = False   

#Cargamos los sonidos, ajustando el volumen
PRE_MUSIC = SOUNDS + "intro.mp3"
BG_MUSIC_FILE      = SOUNDS + "bg.mp3"
BULLET_SOUND_FILE  = SOUNDS + "bullet.wav"

pygame.mixer.music.load(PRE_MUSIC)
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1)

bullet_sound = pygame.mixer.Sound(BULLET_SOUND_FILE)
bullet_sound.set_volume(0.1)

#Imagenes de fondo
background = Actor(SPRITES + "background.jpg", (WIDTH // 2, HEIGHT // 2))
journal = Actor(SPRITES + "journal_entry.png", (WIDTH // 2, HEIGHT // 2))
instructions = Actor(SPRITES + "instructions.png", (WIDTH // 2, HEIGHT // 2))

#Previo al inicio 
state = "PRE"
pre_start_time = pygame.time.get_ticks()
JOURNAL_TIME = 10000 
show_instructions = False

#Animar al jugador
player = Actor(SPRITES + "p0.png", (WIDTH // 2, HEIGHT // 2), scale=0.7)
player.images = [
    SPRITES + "p0.png",
    SPRITES + "p1.png",
    SPRITES + "p2.png",
    SPRITES + "p3.png",
    SPRITES + "p4.png",
    SPRITES + "p5.png",
    SPRITES + "p6.png",
    SPRITES + "p7.png",
]
player.fps = 8

#Contador de zombies y balas
zombies = []
bullets = []
bullet_cooldown = 0
kills = 0

#Delimitamos la cantidad de zombies que aparecen 
MAX_ZOMBIES = 3

def spawn_zombie():
    if len (zombies) >= MAX_ZOMBIES:
        return
    y = random.randint(80, HEIGHT - 80)
    z = Actor(SPRITES + "z0.gif", (-50, y), scale=0.35)
    z.images = [
        SPRITES + "z0.gif",
        SPRITES + "z1.gif",
        SPRITES + "z2.gif",
        SPRITES + "z3.gif",
        SPRITES + "z4.gif",
        SPRITES + "z5.gif",
        SPRITES + "z6.gif",
        SPRITES + "z7.gif",
    ]
    z.fps = 6
    zombies.append(z)

def spawn_bullet():
    b = Actor(SPRITES + "bullet.png", (player.x - 20, player.y), scale=0.1)
    bullets.append(b)
    if bullet_sound is not None:
        bullet_sound.play()

#Colision entre presonaje y zombies
def pixel_collide(a, b):
    offset_x = b.rect.left - a.rect.left
    offset_y = b.rect.top - a.rect.top
    return a.get_mask().overlap(b.get_mask(), (offset_x, offset_y)) is not None

#Crear algunos zombies
for _ in range(MAX_ZOMBIES):
    spawn_zombie()

#Muerte por zombies
win = False

#Loop principal - Primero las instrucciones
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        #Pantalla inicial y avanzar con tecla
        if state == "PRE" and show_instructions:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                state = "GAME"
                pygame.mixer.music.stop()
                pygame.mixer.music.load(BG_MUSIC_FILE)
                pygame.mixer.music.play(-1)

    #Pantalla previa
    if state == "PRE":
        elapsed = pygame.time.get_ticks() - pre_start_time
        if elapsed >= JOURNAL_TIME:
            show_instructions = True
        screen.fill((0, 0, 0))

        if not show_instructions:
            journal.draw(screen)
        else:
            instructions.draw(screen)

        pygame.display.flip()
        continue  

    #Iniciamos el juego
    keys = pygame.key.get_pressed()

    if not game_over:
        #Movimiento del jugador
        if keys[pygame.K_LEFT]:
            player.x -= 5
        if keys[pygame.K_RIGHT]:
            player.x += 5
        if keys[pygame.K_UP]:
            player.y -= 5
        if keys[pygame.K_DOWN]:
            player.y += 5

        #Disparo (SPACE) con pequeño cooldown
        if bullet_cooldown > 0:
            bullet_cooldown -= 1
        if keys[pygame.K_SPACE] and bullet_cooldown == 0:
            spawn_bullet()
            bullet_cooldown = 8

        player.animate()

        #Las balas salen hacia la derecha 
        for b in bullets[:]:
            b.x -= 10
            if b.x < -100:
                bullets.remove(b)

        #Los zombies vienen de la izquierda
        for z in zombies:
            z.x += 2
            z.animate()
            if z.x > WIDTH + 50:
                z.x = -50
                z.y = random.randint(80, HEIGHT - 80)
        for z in zombies:
            if pixel_collide(player, z):
                game_over = True
                pygame.mixer.music.stop()
                break

        #Colision de la bala-zombie
        for b in bullets[:]:
            for z in zombies[:]:
                if b.rect.colliderect(z.rect):
                    if b in bullets:
                        bullets.remove(b)
                    if z in zombies:
                        zombies.remove(z)
                    kills += 1
                    #Reposicion de zombies
                    if kills < TARGET_KILLS:
                        spawn_zombie()
                    else:
                        game_over = True
                        win = True
                        pygame.mixer.music.stop()
                    break

    #Dibujar en la pantalla
    background.draw(screen)
    for z in zombies:
        z.draw(screen)
    for b in bullets:
        b.draw(screen)
    player.draw(screen)

    #Contador en el centro
    font = pygame.font.SysFont(None, 48)
    text = font.render(f"Zombies killed: {kills}/{TARGET_KILLS}", True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 10))

    #Mensaje final
    if game_over:
       if win:
           end_text = font.render("Victory. Your brain remains intact.", True, (0, 255, 0))
       else:
           end_text = font.render("You died. Brain lost.", True, (255, 60, 60))

       screen.blit(end_text, (WIDTH//2 - end_text.get_width()//2, HEIGHT//2))

    pygame.display.flip()
pygame.quit()
