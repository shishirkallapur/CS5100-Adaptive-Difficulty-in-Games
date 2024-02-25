######################################################################################################
# THIS FILE IS FOR RUNNING THE PLATFORM GENERATOR AGENT ONLY. 
# THE PLATFORMS ARE RANDOM EVERY LEVEL IN THIS GAME LOOP.
# THIS GAME INSTANCE ALLOWS FOR USER INPUTS SO THE PLAYER CAN ACTUALLY PLAY USING KEYBOARD INPUTS.
# THE PLATFORM AGENT LEARNS FROM PLAYER ACTIONS.
# JUST RUN THE FILE AND IT SHOULD SHOW A PYGAME POPUP.
######################################################################################################



import pygame
import numpy as np
from DQN import *
import time
from pygame.locals import *

pygame.init()



#CONSTANT FIELDS
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 1
MAX_PLATFORMS = 10
SCROLL_THRESH = 200



#FPS
clock = pygame.time.Clock()
#define colors
WHITE = (255,255,255)
font_small = pygame.font.SysFont('Lucida Sans', 20)
font_big = pygame.font.SysFont('Lucida Sans', 24)
game_over = False
score = 0
time_taken = 0
score_data = [0]
t_score_data = [0]

aux_x = 1
aux_y = 1
aux_w = 1
action = [0,1]


#create game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('GAME')


#load images
bg_img = pygame.image.load('assets/background.png').convert_alpha()
player_img = pygame.image.load('assets/player.png').convert_alpha()
platform_img= pygame.image.load('assets/platform.png').convert_alpha()


#Create RL Agent
agent = DQNAgent()



#Rewards
def reward_from_env(curr_score,score_data,time_data, game_state):
    alpha = 0.5
    print("last 10 scores: ",score_data[-10:])
    print("current score: ",curr_score)
    if game_end_state == "GAME OVER":
        if curr_score > np.mean(score_data[-5:]):
            r1 = -alpha*(curr_score - np.mean(score_data[-5:]))
        else:
            """if curr_score > np.mean(score_data[-10:-5]):
                r1 = alpha*(abs(curr_score - np.mean(score_data[-5:])))
            else:
                r1 = -alpha*(abs(curr_score - np.mean(score_data[-10:])))"""
            r1 = -alpha*(curr_score - np.mean(score_data[-5:]))   
    else:
        print("MEAN TIME DATA: " + str(time_data))
        print("MEAN TIME DATA: " + str(np.mean(time_data[-6:-1])))
        
        if time_data[-1] > np.mean(time_data[-6:-1]):
            r1 = alpha*(time_data[-1] - np.mean(time_data[-6:-1]))
        else:
            r1 = alpha*(time_data[-1] - np.mean(time_data[-6:-1]))
        print(r1)
    """if curr_score > score_data[-1] :
        reward = -100
    else:
        reward = 50
            #LAST CHEKCPOINT CHECKING SCORES AND REWARD
            
        #reward = alpha*(abs(curr_score - np.mean(score_data[-5:])))"""
            
    return r1
            
            




class Player():
    def __init__(self, x, y):
        self.image = player_img
        self.rect = self.image.get_rect()
        self.width = 20
        self.height = 40
        self.rect.center = (x,y)
        self.vel_y = 0
        self.flip = False
        self.flag=0
        self.max_height = 0
        
        
    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
    def move(self):
        #reset vars
        dx = 0
        dy = 0
        scroll = 0
        
        #process key presses
        key = pygame.key.get_pressed()
        if key[pygame.K_a]:
            #self.rect.x -= 10
            dx = -10
            self.flip = True
            if self.flag == 0:
                self.vel_y = -20
                self.flag = 1
        if key[pygame.K_d]:
            #self.rect.x += 10
            dx = 10
            if self.flag == 0:
                self.vel_y = -20
                self.flag = 1

            
        self.vel_y += GRAVITY
        dy += self.vel_y
        #print("del y: "+str(dy))
        """if self.max_height - dy > self.max_height:
            self.max_height = self.max_height - dy"""
            
        #checkign for bounding
        if self.rect.left + dx < 0:
            dx = -self.rect.left 
            
        if self.rect.right + dx > SCREEN_WIDTH:
            dx = SCREEN_WIDTH-self.rect.right 
            
            
        #Check collision with platform
        for plat in platform_group:
            if plat.rect.colliderect(self.rect.x, self.rect.y+dy,self.width, self.height):
                """if self.rect.top > plat.rect.centery:
                    dy = 0
                    self.vel_y = 0"""
                if self.rect.bottom < plat.rect.centery:
                    if self.vel_y > 0:
                        dy = 0
                        self.vel_y = 0
                        self.flag = 0
                    
        #GROUND COLLISION
            
        #Check if level is cleared or not
        if self.rect.top <= SCROLL_THRESH:
            #if ply is jumping
            if self.vel_y < 0:
                scroll = -dy
        
        #update pos
        self.rect.x += dx
        self.rect.y += dy +scroll
        self.max_height -= dy
        
        
        
        #print(self.max_height)
        #print("Vertical posiiton: "+str(600 - self.rect.y))
        
        return scroll
        
class Platform(pygame.sprite.Sprite):
    def __init__(self,x,y,width):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(platform_img,(width,10))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    def update(self,scroll):
        self.rect.y += scroll
        
        #check if platform is off screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
            

def draw_text(text, font, col,x,y):
    img= font.render(text, True, col)
    screen.blit(img, (x,y))
    

        
#instances
player = Player(SCREEN_WIDTH//2, SCREEN_HEIGHT-150)

platform_group = pygame.sprite.Group()


    
#Create starting platform
def create_start_platform():
    platform = Platform(SCREEN_WIDTH //2 - 50, SCREEN_HEIGHT - 50, 100)
    platform_group.add(platform)
    return platform
platform = create_start_platform()
#game loop
run = True
action_taken = 0
step = 0
train_state = False
episode_time = []
start = 0
end = 0
a_name = {0:"Decrease (increase difficulty)",1:"increase (decrease difficulty)"}
game_end_state = ""





while run:
    clock.tick(FPS)
    
    
    

    
    #Taking action and executing:
    #state define
    
    #print(np.array(current_state).shape)
    if action_taken <1:
        current_state = [aux_w,aux_y]
        if np.random.random() < agent.EPSILON:
            action = np.random.randint(0, 2)
        else:
            action = np.argmax(agent.get_qs(current_state))
            print("\n\n\n"+str(agent.get_qs(current_state).shape))
            print(agent.get_qs(current_state))
            action = np.argmax(agent.get_qs(current_state))
            print(action)
            print("\n\n\n")
        action_taken += 1
        
        if action == 0:
            aux_y *= 0.9
            aux_w *= 0.9
            aux_x *= 0.9
        else:
            aux_w *= 1.1
            aux_y *= 1.1
            aux_x *= 1.1
        new_state = [aux_w,aux_y]
        #agent.replay_memory.append((current_state, action))
        
        
        
    
    
    
    if game_over == False:
        
        time_taken+=1
        start = time.time()
        scroll = player.move()

        
        #draw
        screen.blit(bg_img, (0,0))
        draw_text("aux_w: "+str(current_state[0]), font_small, WHITE, 0,0)
        draw_text("aux_y: "+str(current_state[1]), font_small, WHITE, 0,20)
        draw_text("Action: "+a_name[action], font_small, WHITE, 0,40)
        draw_text("Score: "+str(score), font_small, WHITE, 300,0)
        
        #create platforms
        if len(platform_group) < MAX_PLATFORMS:
            p_w = np.random.randint(50*aux_w,100*aux_w) #MODEL LEARNING
            p_x = np.random.randint(0,SCREEN_WIDTH - p_w) #MODEL LEARNING
            """if random.SystemRandom().random() >0.5:
                low = int(100/aux_x)
                high = int(150*aux_x)
                if low>high:
                    low = high - 20
                dell = random.SystemRandom().randint(low, high)
                if platform.rect.x - dell < 0:
                    p_x = 0
                else:
                    p_x = platform.rect.x - dell
            else:
                low = int(100/aux_x)
                high = int(150*aux_x)
                if low>high:
                    low = high - 20
                dell = random.SystemRandom().randint(low, high)
                if platform.rect.x + dell > SCREEN_WIDTH - p_w:
                    p_x = SCREEN_WIDTH - p_w
                else:
                    p_x = platform.rect.x + dell
            """
            if 50/(aux_y) > 120:
                low = 120
            else:
                low = 50/(aux_y)
            p_y = platform.rect.y - np.random.randint(low, 150) #MODEL LEARNING
            platform = Platform(p_x,p_y,p_w)
            platform_group.add(platform)
            
        
        
        #update platform
        if score<2000:
            platform_group.update(scroll)
        
        
        #update score
        if scroll >0:
            score+=scroll
    
        
        #draw player
        platform_group.draw(screen)
        player.draw()
        
        
        #GROUND CHECK
        if player.rect.top > SCREEN_HEIGHT:
            game_over = True
            end = time.time()
            train_state = True
            game_end_state = "GAME OVER"
            episode_time.append(time_taken)
            time_taken = 0
            print("Level time taken: "+str(episode_time[-1]))
        elif score >=2000:
            game_over = True
            end = time.time()
            train_state = True
            game_end_state = "Level Complete!"
            episode_time.append(time_taken)
            time_taken = 0
            print("Level time taken: "+str(episode_time[-1]))
            
        
    else:
        t_score_data.append(score)
        
        draw_text(game_end_state, font_big, WHITE, 130,200)
        draw_text("Score: " + str(score) , font_big, WHITE, 130, 250)
        #draw_text("High Score: " + str(max(t_score_data)) , font_big, WHITE, 130, 300)
        draw_text("Space to RESET", font_big, WHITE, 130,400)
        
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE]:
            
            #Training
            
            #reward definitions
            reward = reward_from_env(score,score_data,episode_time, game_end_state)
            print("REWARD for action ",a_name[action],": ",reward,"\n\n")
            score_data.append(score)
            agent.update_replay_memory((current_state,action,reward,new_state,True))
            #TRAINING
            step+=1
            error = agent.train(True, step)
            #print("\n\n",error)
            current_state = new_state
            action_taken = 0
            
            agent.EPSILON *= agent.EPSILON_DECAY
            
            #reset vars
            game_over = False
            score = 0
            scroll = 0
            player.max_height = 0
            
            #reposition player
            player.rect.center = (SCREEN_WIDTH //2 - 50, SCREEN_HEIGHT - 150)
            #reset platforms
            platform_group.empty()
            platform = create_start_platform()
    
    
    #event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            
    #update display
    pygame.display.update()
            
pygame.quit()


print("Model info: \n\n")
print(agent.EPSILON)
