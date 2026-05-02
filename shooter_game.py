from pygame import *
from random import *
font.init()
import time as timer

window = display.set_mode((700, 500))
display.set_caption('Шутер')
background = transform.scale(image.load('galaxy.jpg'), (700, 500))

game = True
game_over = False  # Флаг окончания игры
bullets_num = 0
max_ammo = 5  
reload_time = 0

monsters = sprite.Group()
bullets = sprite.Group()
asteroids = sprite.Group()
score = 0
lose = 0
clock = time.Clock()
FPS = 60

font1 = font.SysFont('Arial', 36)
font2 = font.SysFont('Arial', 55)

class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, player_speed):
        super().__init__()
        self.image = transform.scale(image.load(player_image), (65, 65))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def __init__(self, player_image, player_x, player_y, player_speed):
        super().__init__(player_image, player_x, player_y, player_speed)

    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < 625:
            self.rect.x += self.speed
    
    def shoot(self):
        bullet = Bullet('bullet.png', self.rect.centerx - 7, self.rect.top, 5)
        bullets.add(bullet)
        fire.play()

class Enemy(GameSprite):
    def __init__(self, enemy_image, enemy_x, enemy_y, enemy_speed):
        super().__init__(enemy_image, enemy_x, enemy_y, enemy_speed)
        self.image = transform.scale(image.load(enemy_image), (100, 50))
    def update(self):
        self.rect.y += self.speed
        if self.rect.y >= 500:
            self.rect.y = 0
            self.rect.x = randint(0, 600)
            global lose
            lose = lose + 1

class Bullet(GameSprite):
    def __init__(self, bullet_image, bullet_x, bullet_y, bullet_speed):
        super().__init__(bullet_image, bullet_x, bullet_y, bullet_speed)
        self.image = transform.scale(image.load(bullet_image), (15, 20))
    
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()        

player = Player('rocket.png', 315, 400, 7)

for i in range(5):
    monster = Enemy('ufo.png', randint(0, 500), 0, randint(1, 2))
    monsters.add(monster)

mixer.init()
mixer.music.load('space.ogg')
fire = mixer.Sound('fire.ogg')
fire.set_volume(0.1)
mixer.music.set_volume(0.2)
mixer.music.play()

while game:
    current_time = timer.time()

    for e in event.get():
        if e.type == QUIT:
            game = False
        if e.type == KEYDOWN:
            if e.key == K_SPACE and not game_over:  # Стрелять можно только пока игра не окончена
                if reload_time == 0:
                    if bullets_num < max_ammo:
                        player.shoot()
                        bullets_num += 1
                        if bullets_num >= max_ammo:
                            reload_time = current_time + 2
                    else:
                        reload_time = current_time + 2

    if reload_time > 0 and current_time >= reload_time:
        reload_time = 0 
        bullets_num = 0

    # Проверка столкновения игрока с врагом (игра заканчивается)
    if not game_over:
        player_hits = sprite.spritecollide(player, monsters, True)
        if player_hits:
            game_over = True
            # Удаляем всех врагов и пули
            for monster in monsters:
                monster.kill()
            for bullet in bullets:
                bullet.kill()
            for asteroid in asteroids:
                asteroid.kill()

    hits_monsters = sprite.groupcollide(monsters, bullets, True, True)
    
    for hit in hits_monsters:
        score += 1
        new_monster = Enemy('ufo.png', randint(0, 600), 0, randint(1, 2))
        monsters.add(new_monster)

    window.blit(background, (0, 0))

    if reload_time > 0 and not game_over:
        remaining_time = reload_time - current_time
        if remaining_time > 0:
            rounded_time = round(remaining_time, 1)
            text_reload = font1.render('Перезарядка:' + str(rounded_time) + 'сек', 1, (255, 0, 0))
            window.blit(text_reload, (240, 425))

    # Проверка победы
    if score >= 10 and not game_over:
        game_over = True
        for monster in monsters: 
            monster.kill()
        for bullet in bullets:
            bullet.kill()
        for asteroid in asteroids:
            asteroid.kill()
        text_won = font2.render('YOU WON!', 1, (255, 255, 255))
        window.blit(text_won, (250, 225))
    # Проверка проигрыша по пропущенным врагам
    elif lose >= 5 and not game_over:
        game_over = True
        for monster in monsters: 
            monster.kill()
        for bullet in bullets:
            bullet.kill()
        for asteroid in asteroids:
            asteroid.kill()
        text_lost = font2.render('YOU LOST!', 1, (255, 255, 255))
        window.blit(text_lost, (250, 225))
    # Если игра окончена из-за столкновения
    elif game_over and score < 10 and lose < 5:
        text_lost = font2.render('YOU LOST!', 1, (255, 255, 255))
        window.blit(text_lost, (250, 225))

    text_lose = font1.render('Пропущено:' + str(lose), 1, (255, 255, 255))
    text_score = font1.render('Сбито:' + str(score), 1, (255, 255, 255))

    window.blit(text_lose, (0, 0))
    window.blit(text_score, (0, 30))

    # Обновление спрайтов только если игра не окончена
    if not game_over:
        monsters.update()
        bullets.update()
        player.update()
    else:
        monsters.draw(window)
        bullets.draw(window)

    monsters.draw(window)
    bullets.draw(window)
    player.reset()

    display.update()
    clock.tick(FPS)