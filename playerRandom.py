######################################################################################################
# THIS FILE IS FOR RUNNING THE PLAYER AGENT. THE PLATFORMS ARE FIXED EVERY LEVEL IN THIS GAME LOOP.
# JUST RUN THE FILE AND IT SHOULD SHOW A PYGAME POPUP.
######################################################################################################


import pygame
import numpy as np
#from DQN import *
import playerDQN as p
import time
from pygame.locals import *
from matplotlib import pyplot as plt
from PIL import Image


pygame.init()



#CONSTANT FIELDS
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 1
MAX_PLATFORMS = 10
SCROLL_THRESH = 200
NUM_STEPS = 5000
iters=0



#FPS
clock = pygame.time.Clock()


#define colors
WHITE = (255,255,255)
font_small = pygame.font.SysFont('Lucida Sans', 20)
font_big = pygame.font.SysFont('Lucida Sans', 24)
game_over = False
score = 0
prev_max_height = 0
time_taken = 0
score_data = [0]
t_score_data = [0]

"""aux_x = 1
aux_y = 1
aux_w = 1
action = [0,1]"""


action_player = [pygame.event.Event(KEYDOWN, key=K_a),pygame.event.Event(KEYDOWN, key=K_d)]

#create game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('GAME')


#load images
bg_img = pygame.image.load('assets/background.png').convert_alpha()
player_img = pygame.image.load('assets/player.png').convert_alpha()
platform_img= pygame.image.load('assets/platform.png').convert_alpha()


#Create RL Agent
#agent = DQNAgent()
agentPlayer = p.DQNAgent()



#Rewards
"""def reward_from_env(curr_score,score_data):
    alpha = 0.5
    print("last 10 scores: ",score_data[-10:])
    print("current score: ",curr_score)
    if curr_score > np.mean(score_data[-5:]):
        reward = -alpha*(curr_score - np.mean(score_data[-5:]))
    else:
        if curr_score > np.mean(score_data[-10:-5]):
            reward = alpha*(abs(curr_score - np.mean(score_data[-5:])))
        else:
            reward = -alpha*(abs(curr_score - np.mean(score_data[-10:])))
            
    if curr_score > score_data[-1] :
        reward = -100
    else:
        reward = 50
            #LAST CHEKCPOINT CHECKING SCORES AND REWARD
            
        #reward = alpha*(abs(curr_score - np.mean(score_data[-5:])))
            
    return reward"""
    
def reward_player(curr_score,prev_score, game_state):
    
    #print((curr_score,prev_score, game_state))
    #if it takes a lot of time then reward will be reduced
    if curr_score < prev_score:
        reward =  -500
    elif curr_score == prev_score:
        reward = -100
    else:
        reward =  (curr_score) * 100
    
    
    """if game_state == "GAME OVER":
        reward = -1000
    elif game_state == "Level Complete!":
        reward = 2000"""

    return reward
            

        
def get_state():
    
    """view_rect = pygame.Rect(player.rect.centerx-50,player.rect.centery-50,100,100)
    sub = screen.subsurface(view_rect)
    return sub"""
    
    pygame.image.save(screen, "buffer/screenshot.png")
    img = Image.open("buffer/screenshot.png").convert('L').resize((50,50), Image.LANCZOS)
    #img.save("buffer/vision.png")
    return np.array(img)




class Player():
    def __init__(self, x, y):
        self.image = player_img
        self.rect = self.image.get_rect()
        self.width = 20
        self.height = 40
        self.rect.center = (x,y)
        self.vel_y = 0
        self.flip = False
        self.flag = 0
        self.max_height = 0
        
        
    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
    def move(self,key):
        #reset vars
        dx = 0
        dy = 0
        scroll = 0
        
        #process key presses
        """key = pygame.key.get_pressed()
        if key[pygame.K_a]:
            #self.rect.x -= 10
            dx = -10
            self.flip = True
        if key[pygame.K_d]:
            #self.rect.x += 10
            dx = 10"""
            
        if key.key == K_a:
            #self.rect.x -= 10
            dx = -10
            self.flip = True
            if self.flag == 0:
                self.vel_y = -20
                self.flag = 1
        if key.key == K_d:
            #self.rect.x += 10
            dx = 10
            if self.flag == 0:
                self.vel_y = -20
                self.flag = 1
                
            
        self.vel_y += GRAVITY
        dy += self.vel_y
            
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
#a_name = {0:"Decrease (increase difficulty)",1:"increase (decrease difficulty)"}
#a_name = {0:"Left",1:"Rigth"}
game_end_state = ""




p_x = 0
p_y = 0
while run:
    clock.tick(FPS)
    
    
    if game_over == False:
        
        time_taken+=1
        start = time.time()
        

        
        #Taking action using explore exploit by player

        
        #draw
        screen.blit(bg_img, (0,0))
        """draw_text("aux_w: "+str(current_state[0]), font_small, WHITE, 0,0)
        draw_text("aux_y: "+str(current_state[1]), font_small, WHITE, 0,20)
        draw_text("Action: "+a_name[action], font_small, WHITE, 0,40)"""
        draw_text("Score: "+str(score), font_small, WHITE, 200,0)
        
        #create platforms
        if len(platform_group) < MAX_PLATFORMS:
            """p_w = np.random.randint(50,100) #MODEL LEARNING
            p_x = np.random.randint(0,SCREEN_WIDTH - p_w) #MODEL LEARNING
            p_y = platform.rect.y - np.random.randint(50, 150) #MODEL LEARNING"""
            p_x = 75
            p_y = platform.rect.y - 70
            p_w = 50
            """p_x = SCREEN_WIDTH - 100 + np.random.randint(5)
            p_y = platform.rect.y - 100
            p_w = 50"""
            platform = Platform(p_x,p_y,p_w)
            platform_group.add(platform)
            
            
        """state_maker = 0
        player_state = []
        plats=[]
        for i in platform_group:
            plats.append((i.rect.centerx,i.rect.centery))

        
        player_state.append(player.rect.centerx)
        player_state.append(player.rect.centery)
        flag = 0
        for i in plats:
            if i[1] < player.rect.centery:
                player_state.append(i[0])
                player_state.append(i[1])
                flag = 1
                break
        if flag == 0:
            player_state.append(plats[-1][0])
            player_state.append(plats[-1][1])
        print("Player STate: "+str(player_state))
        
        
        #current_state = np.array(player_state)"""
        
        current_state =get_state()
        
        
        
        
        
        if np.random.random() <= agentPlayer.EPSILON:
            action = np.random.randint(0, 2)
        else:
            #action = np.argmax(agentPlayer.get_qs(current_state),axis=1)[0]
            #print(agentPlayer.get_qs(current_state).shape)
            action = np.argmax(agentPlayer.get_qs(current_state))
        pygame.event.post(action_player[action])
        
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                scroll = player.move(event)
        

        
        
        #update platform
        if score<2000:
            platform_group.update(scroll)
        
        
        #update score
        if scroll >0:
            score+=scroll

    
        
        #draw player
        platform_group.draw(screen)
        player.draw()
        
        
        
        
        player_state_next =get_state()
        reward = reward_player(player.max_height,prev_max_height,game_end_state)
        prev_max_height = player.max_height
        #GROUND CHECK
        if player.rect.top > SCREEN_HEIGHT:
            game_over = True
            end = time.time()
            train_state = True
            game_end_state = "GAME OVER"
            episode_time.append(time_taken)
            time_taken = 0
            print("Level time taken: "+str(episode_time[-1]))
            
            
            agentPlayer.update_replay_memory((current_state,action,reward,player_state_next,True))
        elif score >=2000:
            game_over = True
            end = time.time()
            train_state = True
            game_end_state = "Level Complete!"
            episode_time.append(time_taken)
            time_taken = 0
            print("Level time taken: "+str(episode_time[-1]))

            agentPlayer.update_replay_memory((current_state,action,reward,player_state_next,True))
        elif time_taken>=1000:
            game_over = True
            end = time.time()
            train_state = True
            game_end_state = "GAME OVER"
            episode_time.append(time_taken)
            time_taken = 0
            print("Level time taken: "+str(episode_time[-1]))
            
        agentPlayer.update_replay_memory((current_state,action,reward,player_state_next,False))
            
            
        """player_state_next = []
        plats=[]
        for i in platform_group:
            temp = []
            plats.append((i.rect.centerx,i.rect.centery))  
        player_state_next.append(player.rect.centerx)
        player_state_next.append(player.rect.centery)
        flag = 0
        for i in plats:
            if i[1] < player.rect.centery:
                player_state_next.append(i[0])
                player_state_next.append(i[1])
                flag == 1
                break
            
        if flag == 0:
            player_state.append(plats[-1][0])
            player_state.append(plats[-1][1])"""
            

        
        
        
        
        #print("\n\n\nSARSA "+ str((current_state,action,reward,player_state_next,True)))
        #agentPlayer.update_replay_memory((current_state,action,reward,player_state_next,False))
        
        
        
        
            
        
    else:
        p_x = 0
        p_y = 0
        t_score_data.append(score)
        
        draw_text(game_end_state, font_big, WHITE, 130,200)
        draw_text("Score: " + str(score) , font_big, WHITE, 130, 250)
        #draw_text("High Score: " + str(max(t_score_data)) , font_big, WHITE, 130, 300)
        draw_text("Space to RESET", font_big, WHITE, 130,400)
    

        key = pygame.key.get_pressed()
        #if key[pygame.K_SPACE]:
            
        #TRAINING
    
        
        
        score_data.append(score)
        
        
        #TRAINING
        step+=1
        error = agentPlayer.train(True, step)
        #print("\n\n",error)
        current_state = player_state_next
        action_taken = 0
        
        agentPlayer.EPSILON *= agentPlayer.EPSILON_DECAY
        if agentPlayer.EPSILON <0.2:
            agentPlayer.EPSILON = 0.2
        #agentPlayer.EPSILON -= (iters/NUM_STEPS)
        """#Training
        
        #reward definitions
        reward = reward_from_env(score,score_data)
        print("REWARD for action ",a_name[action],": ",reward,"\n\n")
        score_data.append(score)
        agent.update_replay_memory((current_state,action,reward,new_state,True))
        
        
        #TRAINING THE PLATFORM
        step+=1
        error = agent.train(True, step)
        current_state = new_state
        action_taken = 0
        
        agent.EPSILON *= agent.EPSILON_DECAY"""
        
        #reset vars
        game_over = False
        score = 0
        scroll = 0
        game_end_state = ""
        
        #reposition player
        player.rect.center = (SCREEN_WIDTH //2 - 50, SCREEN_HEIGHT - 150)
        #reset platforms
        platform_group.empty()
        platform = create_start_platform()
        print("\n\n\n ITERATION: "+str(iters+1))
        if iters<NUM_STEPS:
            iters+=1
        else:
            run=False
        
    
    #event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            
    #update display
    pygame.display.update()
    
            
pygame.quit()

plt.figure()
plt.plot(t_score_data)
plt.show()
