import pygame, cv2, random, os
#cv2 is for opening and playing videos, os is for reading the names of all the files inside my folder 
#cv2 treats the video file as a bunch of frames and then reads each frame and prints all of them 

class Tile(pygame.sprite.Sprite):
    def __init__(self, filename, x, y):
        super().__init__()

        self.name = filename.split('.')[0]     #split the name of the file at the dot to get just the name without the extension; [0] means the first part after splitting

        self.original_img = pygame.image.load('images/tiles/'+filename)
        self.original_img = pygame.transform.scale(self.original_img, (80, 80))

        # self.back_img = pygame.image.load('images/tiles/'+filename)
        # pygame.draw.rect(self.back_img, WHITE, self.back_img.get_rect())  #we can add a 4th parameter which will be equal to the border, but if we dont write anything then it means its a solid background 

        # self.image = self.back_img
        # self.rect = self.image.get_rect(topleft = (x,y))
        # self.shown = False    #if this is false, then it means you see a white rectangle because the image is face-down; if its true, then u see the img bcos its face up

        self.back_img = pygame.Surface((80, 80))  # Create a blank surface
        self.back_img.fill(WHITE)  # Fill it with white color

        self.image = self.back_img  # Start with the back image
        self.rect = self.image.get_rect(topleft=(x, y))  # Position the tile
        self.shown = False 

    def update(self):
        #i m gonna check if self.shown is false, then i m gonna direct the shown image to back_img otherwise i m gonna direct it to original_img
        self.image = self.original_img if self.shown else self.back_img

    def show(self):
        self.shown = True
    def hide(self):
        self.shown = False
    



#all the logic for the game will be written inside the game class and it will only take screen as the argument and nothing else 
class Game():
    def __init__(self):
        self.level = 1 
        self.level_complete = False 


        #tiles 
        self.all_tiles = [f for f in os.listdir('images/tiles/') if os.path.join('images/tiles/', f)]  #this uses os module to create an array of the name of all the images 
        
        self.img_width, self.img_height = (80,80)
        self.padding = 20
        self.margin_top = 160
        self.cols = 4
        self.rows = 2
        self.width = 800

        self.tiles_group = pygame.sprite.Group()

        #flipping and timing 
        self.flipped = []
        self.frame_count = 0 #like for how long should the unmatching tiles be displayed on screen before they are flipped back 
        self.game_block = False #if 2 tiles are flipped and those 2 images are different i want to block the game 

        #generate first level 
        self.generate_level(self.level)


        #initialize video variable
        self.is_video_playing = True
        self.get_video()

        #initialize music variable 
        self.is_music_playing = True
        self.sound_on = pygame.image.load('images/sound on.png').convert_alpha()
        self.sound_on = pygame.transform.scale(self.sound_on, (30,30))
        self.sound_off = pygame.image.load('images/sound off.png').convert_alpha()
        self.sound_off = pygame.transform.scale(self.sound_off, (30,30))
        self.music_toggle = self.sound_on
        self.music_toggle_rect = self.music_toggle.get_rect(topright= (window_width -10, 10 ))

        #load music 
        pygame.mixer.music.load('sounds/memory game sound.mp3')
        pygame.mixer.music.set_volume(.5)  #can pass anything bw 0.1 to 1
        pygame.mixer.music.play()
    
    def update(self, event_list):  #whenever i will be clicking on a tile and it flips, that will be an example of updating 
        if self.is_video_playing:
            self.success, self.img = self.cap.read()
        self.user_input(event_list)
        self.draw()

        self.check_level_complete(event_list)

    def check_level_complete(self, event_list):
        if not self.game_block:
            for event in event_list:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for tile in self.tiles_group:
                        if tile.rect.collidepoint(event.pos):
                            self.flipped.append(tile.name)
                            tile.show()
                            if len(self.flipped) == 2:
                                if self.flipped[0] != self.flipped[1]:
                                    self.game_block = True
                                else:
                                    self.flipped = []   #empty the flipped array
                                    for tile in self.tiles_group:
                                        if tile.shown:
                                            self.level_complete = True
                                        else:
                                            self.level_complete = False
                                            break
        else:
            self.frame_count += 1     #for each iteration, frame count will increase by 1, and in one minute frame count will become 60 which will be equal to fps
            if self.frame_count == FPS:
                self.frame_count = 0
                self.game_block = False

                for tile in self.tiles_group:
                    if tile.name in self.flipped:
                        tile.hide()
                self.flipped = []




    def generate_level(self, level):
        self.tiles = self.select_random_tiles(self.level)
        self.level_complete = False
        self.rows = self.level + 1
        self.cols = 4

        self.generate_tileset(self.tiles)

    def generate_tileset(self, tiles):
        #if i have more than 4 rows, it will start overlapping at the bottom margin; so whenever rows>coloumns we will  have to exchange the rows and the coloumns 
        # total_tiles = (self.level + 1) * 2
        # self.cols = int(total_tiles ** 0.5)
        # self.rows = (total_tiles + self.rows - 1) // self.rows
        self.cols = self.rows = self.cols if self.cols >= self.rows else self.rows

        # self.rows, self.cols = self.cols, self.rows

        TILES_WIDTH = (self.img_width * self.cols + self.padding * (self.cols -1))
        LEFT_MARGIN = RIGHT_MARGIN = (self.width - TILES_WIDTH) // 2
        
        self.tiles_group.empty()

        for i in range(len(tiles)):
            x = LEFT_MARGIN + ((self.img_width + self.padding) * (i % self.cols))
            y = self.margin_top + ((i // self.cols) * (self.img_height + self.padding))
  
            # x = LEFT_MARGIN + ((self.img_width + self.padding) * (i // self.rows))
            # y = self.margin_top + ((i % self.rows) * (self.img_height + self.padding))

            tile = Tile(tiles[i], x, y)
            self.tiles_group.add(tile)
    

    def select_random_tiles(self, level):
        tiles = random.sample(self.all_tiles, (self.level + self.level + 2))
        tiles_copy = tiles.copy()
        tiles.extend(tiles_copy)
        random.shuffle(tiles)
        return tiles 



    def user_input(self, event_list):   #this fn takes the event list as input which means it keeps a track of all types of keydowns/mouse-button-press
        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.music_toggle_rect.collidepoint(pygame.mouse.get_pos()):
                    if self.is_music_playing:
                        pygame.mixer.music.pause()
                        self.music_toggle = self.sound_off
                        self.is_music_playing = False
                    else:
                        pygame.mixer.music.unpause()
                        self.music_toggle = self.sound_on
                        self.is_music_playing = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.level_complete:
                    self.level += 1
                    if self.level >= 4:                        
                        running = False
                        global current_room_state_game3
                        current_room_state_game3 = 'room3'
                    else:
                        self.generate_level(self.level)
                        

    def draw(self):
        screen.fill(BLACK)

        #fonts
        title_font = pygame.font.Font('fonts/Halloween.ttf', 44)
        content_font = pygame.font.Font('fonts/HallowenInline.ttf', 24)

        #text 
        title_text = title_font.render('MEMORY  PUZZLE', True, WHITE)
        title_rect = title_text.get_rect(midtop = (window_width //2, 10))  #inside this pass that part of the rectangle as argument that u want to grab 

        level_text = content_font.render('LEVEL ' + str(self.level), True, WHITE)
        level_rect = level_text.get_rect(midtop = (window_width //2, title_rect.bottom + 3))

        info_text = content_font.render('Find 2 of each', True, WHITE)
        info_rect = info_text.get_rect(midtop = (window_width//2, level_rect.bottom + 3))

        if self.is_video_playing:
            if self.success:
                screen.blit(pygame.image.frombuffer(self.img.tobytes(), self.shape, 'BGR'), (0,0))  #those images of those frames are not being stored as images but as bytes and we need to convert those bytes to frames
            #cv2 uses Blue, Green, Red scheme instead of RGB
            else:   #what else loop does is loops the video, once all frames are exhausted, it goes back to playing it from the start
                self.get_video()



        if not self.level >= 3:
            next_text = content_font.render('Level complete. Press SPACE for next level.', True, WHITE)
        else:
            next_text = content_font.render('You solved this! Press SPACE to go back to the room.', True, WHITE)
        next_rect = next_text.get_rect(midbottom = (window_width // 2, window_height - 20))

        screen.blit(title_text, title_rect)
        screen.blit(level_text, level_rect)
        screen.blit(info_text, info_rect)
        pygame.draw.rect(screen, WHITE, (window_width - 50, 5, 45, 45))
        screen.blit(self.music_toggle, self.music_toggle_rect)

        if self.level_complete:
             screen.blit(next_text, next_rect)

        #to draw tile-set 
        self.tiles_group.draw(screen)
        self.tiles_group.update()

    def get_video(self):
        self.cap = cv2.VideoCapture('video/midnight video.mp4')
        self.success, self.img = self.cap.read()
        self.shape = self.img.shape[1::-1]

pygame.init()

window_width = 800
window_height = 600
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Memory Game")

WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255, 0, 0)

FPS = 60 
clock = pygame.time.Clock()

game = Game() #creating an object of the above class to call it later 


running = True
while running:
    event_list = pygame.event.get()
    for event in event_list:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                running = False
                pygame.mixer.music.pause()

        if event.type == pygame.QUIT:
            running = False 
                


    game.update(event_list)

    clock.tick(FPS)  #this ensures game loop will work 60 times per second 


    pygame.display.update()