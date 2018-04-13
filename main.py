#!/usr/bin/env python
# -*- coding: utf-8 -*

import sys, random, time, datetime, re, os
import pyglet
from pyglet.window import key, mouse
from pyglet.gl import *

#Tell pyglet where to find the media resources
pyglet.resource.path = ['resources', 'resources/sprites', 'resources/animations', 'resources/sounds']
pyglet.resource.reindex()

LOG = u""

FPS = pyglet.clock.ClockDisplay()

MAIN_BATCH = pyglet.graphics.Batch()

Z_INDEX1 = pyglet.graphics.OrderedGroup(0)
Z_INDEX2 = pyglet.graphics.OrderedGroup(1)
Z_INDEX3 = pyglet.graphics.OrderedGroup(2)
Z_INDEX4 = pyglet.graphics.OrderedGroup(3)
Z_INDEX5 = pyglet.graphics.OrderedGroup(4)
Z_INDEX6 = pyglet.graphics.OrderedGroup(5)
Z_INDEX7 = pyglet.graphics.OrderedGroup(6)
Z_INDEX8 = pyglet.graphics.OrderedGroup(7)
Z_INDEX9 = pyglet.graphics.OrderedGroup(8)
Z_INDEX10 = pyglet.graphics.OrderedGroup(9)

#Sound files
#Narrator
voice_intro = "fase1_m.wav"
voice_intro_f = "fase1_f.wav"
voice_phase1_pause = "fase1_pause_m.wav"
voice_phase1_pause_f = "fase1_pause_f.wav"
#voice_phase1_pause_v2 = "fase1_pause_v2.wav"
voice_phase2_screen = "fase2_m.wav"
voice_phase2_screen_f = "fase2_f.wav"
voice_phase1_right_1_f = "phase1_right_1_f.wav"
voice_phase1_right_1_m = "phase1_right_1_m.wav"
voice_phase1_right_2_f = "phase1_right_2_f.wav"
voice_phase1_right_2_m = "phase1_right_2_m.wav"
voice_phase1_right_3_f = "phase1_right_3_f.wav"
voice_phase1_right_3_m = "phase1_right_3_m.wav"
voice_phase1_null_1_f = "phase1_null_1_f.wav"
voice_phase1_null_1_m = "phase1_null_1_m.wav"
voice_phase1_wrong_1_f = "phase1_wrong_1_f.wav"
voice_phase1_wrong_1_m = "phase1_wrong_1_m.wav"
voice_phase1_wrong_2_f = "phase1_wrong_2_f.wav"
voice_phase1_wrong_2_m = "phase1_wrong_2_m.wav"
voice_end_thanks_f = "end_thanks_f.wav"
voice_end_thanks_m = "end_thanks_m.wav"
voice_phase1_wrong_end_of_loop_f = "wrong-phase1-end-of-loop_f.wav"
voice_phase1_wrong_end_of_loop_m = "wrong-phase1-end-of-loop_m.wav"


#music or sound effects
music_background = "forest.wav"
sound_rain = "rain_loop.wav"
sequence_end = "sequence_end.wav"
sequence_end_danger = "falling.wav"
mid_phase1_sound_start = "shiny.wav"
complete_task = "completetask_0.wav"
#voice_move_mouse = pyglet.resource.media("voice_move_mouse.mp3", streaming=False)
#voice_click_left_button = pyglet.resource.media("voice_click_left_button.mp3", streaming=False)

#FUNCTIONS
def make_sprite(file_name, x=0, y=0, batch=MAIN_BATCH, group = Z_INDEX5, dx=None, dy=None, animation=False, scale=1):
    if animation:
        load = pyglet.resource.animation(file_name)
    else:
        load = pyglet.resource.image(file_name)
    sprite = pyglet.sprite.Sprite(load, x=x, y=y, batch=batch, group=group)
    sprite.scale = scale
    if dx:
        sprite.dx=dx
    if dy:
        sprite.dy=dy
    return sprite

def play_sound_with_delay(dt, filename):
    temp_sound = pyglet.resource.media(filename , streaming=False)
    temp_player = pyglet.media.Player()
    temp_player.volume = 1
    temp_player.queue(temp_sound)
    temp_player.play()
    #return temp_player

def play_sound(filename, loop=False, volume=1):
    player = pyglet.media.Player()
    player.volume = volume
    sound = pyglet.resource.media(filename , streaming=False)
    
    if loop == True:
        looper = pyglet.media.SourceGroup(sound.audio_format, None)
        looper.loop = True
        looper.queue(sound)
        player.queue(looper)
    else:
        player.queue(sound)
    player.play()
    return player
    
def get_lines_from_file(filename):
        #strip is used to delete new line characters and white space at start and end of line
        lines = [line.strip() for line in open(filename)]
        return lines

#ended up not needing, pyglet has a clock that uses the time.time()
class Timer:
    def __init__(self):
        self.time_start = 0.0
        self.time_end = 0.0
        self.start()
             
    def start(self):
        self.time_start = time.time()
        return self.time_start
        
    def stop(self):
        self.time_end = time.time()
        stop = self.time_end - self.time_start
        return stop

def is_number(x): #determina se na string do arg existe um número
    try:
        float(x)
        return True
    except:
        return False
        
#Main Window Class
class MainWindow(pyglet.window.Window):
    def __init__(self):
        super(MainWindow, self).__init__(caption="Teste", fullscreen=True)
        
        #Constants, speed configurations
        self.CLOUDS2_DX = 30
        self.CLOUDS3_DX = 80
        self.FAIRY_DX = 750#700
        self.FAIRY_DY = 750#700
        self.FAIRY_SCALE_SPEED = 0.9#0.8
        self.WITCH_SCALE_SPEED = 0.1
        self.FAIRY_MAX_SCALE = 7#5
        self.SEED_DY = 180#400
        self.RAIN_DY = 350
        self.TREE_GROWTH_SPEED = 0.05#0.025 original / #0.09 fast
        self.RESTART_OPACITY_DOWN_SPEED = 200#250
        self.SEED_BLINK_SPEED = 200
        
        self.time_for_rain = float(WAIT_TIME)
        
        #Track log for saving data, and set CSV headers
        self.phase1_log = "seed;first_repeat_seed;first_repeat_right_or_wrong;seconds_for_input_each_seed;seconds_for_input_total;second_repeat_seed;second_repeat_right_or_wrong;seconds_for_input_each_seed;seconds_for_input_total"
        self.phase2_log = "view_order;sequence;type;type_number;user_answear;time_for_input;sequence_exist;answear_right_or_wrong"
        
        #Number of loops of phase 1. We want it to repeat 2 times before advance for phase 2
        self.phase1_max_loop = 2
        self.phase1_loop = 1
        
        #Define timer variable, for use in phase 2, to get the time the user takes to press the keys
        #self.timer = Timer()
        self.timer = pyglet.clock.Clock()
        #After all no need for the 2 variables next (time_start and time_end) since I ended up not using the Class Timer(), since pyglet has already a inner clock, used that inestead in the line above. But let it be, if one day I need to use the Class
        self.time_start = 0.0
        self.time_end = 0.0
        #Used the time_total to store the times in the mid_phase1 state of the game, for the phase1 log
        self.time_total = []
        
        #Track game current phase. I made the sates with the same name as their respective functions. List of all possible:
        #phase1_start
        #"restart_animate_fairy_stars" -> restart for new seeds phase 1: clean screen animation with fairy and stars animation
        #"animate_fairy_new_seeds" -> restart for new seeds phase 2: resets fairy position after the clean, get and creat the new seeds
        #"new_seeds_plant_animation" -> restart for new seeds phase 3: animate the new seeds goign to place
        #"watering" -> wait user to water soil with the cloud 
        #"phase1_end" -> when all seeds/sequences been showed and phase 1 ends, and we want to start phase 2 when children select sequences themselfs
        self.game_state = "phase1_start"
		
		#Define main phase of the game: phase1 = children view sequences; phase2 = children say yes or no to sequences; bot share the same functions, but some have extra mechanisms and scripts
        self.game_phase = "phase1"
        
        #SOUNDS/MUSCIC
        #List of sounds currently being played in a loop
        self.sounds_active = {}
        
        #Start music in background
        self.sounds_active["music_playing"] = play_sound(music_background, loop=True, volume=0.7)

        #Rain list made by the rain animation function when left click on the cloud, and used for calculations in the watering function for the tree grow
        self.rains = []
        #The rain is from a sprite grid, which is sliced in 10 rows and we iterate through (self.n_rains tracks this iteration) otherwise only 1 sprite would be a monotonous animation
        self.n_rains = 0
        
        #Fairy stars for animation
        self.stars = []
        
        #MOUSE
        #Change mouse to a grumpy cloud and load happy version for the change when left mouse is pressed
        self.cloud_normal = pyglet.resource.image("cloud_normal.png")
        self.cloud_happy = pyglet.resource.image("cloud_happy.png")
        cursor = pyglet.window.ImageMouseCursor(self.cloud_normal, self.cloud_normal.height/2, 0)
        self.set_mouse_cursor(cursor)
        #Track mouse position
        self.mouse_x = 0
        self.mouse_y = 0
        #And track left click
        self.left_mouse_state = False
        
        #Some sprite variables
        self.new_tree = None
        self.keyboard_mid_phase1 = None
        
        #Seed opacity status for blink animation
        self.opacity_status = "down"
        
        #RUN WORLD BACKGROUND
        self.sky()
        self.ground()
        
        #CHARACTERS
        #Narrator
        #Call function/play sounds after x seconds. Template is schedule_once(function, time to wait, args/kargs of function)
        #pyglet.clock.schedule_once(play_sound_with_delay, 1.0, voice_intro)
        
        #Start fairy Oriana
        self.fairy()

        #Load seeds
        self.sequences = get_lines_from_file("phase1_sequences.txt")
        
        #Order them randomly
        random.shuffle(self.sequences)
        #order them by lenght size e.g. seeds with 2 items first, then seeds with 3 items, etc
        self.sequences = sorted(self.sequences, key=len)
        
        #Backup phase 1 sequences, because we need in the final log to check if phase 2 answears are right or wrong
        #we use list() (or old_list[:] could do too) because list_a = list_b don't really copy, if we change the first it affects the 2nd, and give us error later, list() makes a real individual copy
        self.phase1_sequences = list(self.sequences)
        #Next seed sequence to show. PS: negative number because lists starts counting at zero, and the function that makes the seeds starts by incrementing this number, so we want to start before zero
        self.next_squence_key = -1
        
        self.seeds_current = []
        #Variables for mid_phase1
        self.empty_seeds = []
        self.input_seeds_sprites = []
        self.input_seeds_number = ""
        #track numbers of mid_phase1 repeat. we want 3 tries (2 initially but later changed to 3)
        self.mid_phase1_loop = 1
        self.mid_phase1_loop_max = 3
        
        #Var for text on screen
        self.text_show = ""
    
    def sky(self):
        clouds_index2_dx = self.CLOUDS2_DX
        clouds_index3_dx = self.CLOUDS3_DX
        sprite_width = 694
        sprite_height = 126
        self.clouds_index1 = []
        self.clouds_index2 = []
        self.clouds_index3 = []
        x=0
        #repeat images horizontally till they fill all the screen
        while x <= self.width:
            self.clouds_index1.append( make_sprite("clouds_index1.png", x=x, y=self.height-sprite_height, group=Z_INDEX1) )
            self.clouds_index2.append( make_sprite("clouds_index2.png", x=x, y=self.height-sprite_height-40, group=Z_INDEX2, dx=clouds_index2_dx) )
            self.clouds_index3.append( make_sprite("clouds_index3.png", x=x, y=self.height-sprite_height-87, group=Z_INDEX3, dx=clouds_index3_dx) )
            x += self.clouds_index3[0].width
        #Add one extra at the start, outside of the screen on the left, because of the loop animation of them moving (executed in the self.update function)
        self.clouds_index2.insert(0, make_sprite("clouds_index2.png", x=-self.clouds_index2[0].width, y=self.height-sprite_height-40, group=Z_INDEX2, dx=clouds_index2_dx) )
        self.clouds_index3.insert(0, make_sprite("clouds_index3.png", x=-self.clouds_index3[0].width, y=self.height-sprite_height-87, group=Z_INDEX3, dx=clouds_index3_dx) )

    def ground(self):
        #GROUND
        #I want the main scene to fit at least in the height 720px (because the monitor resolution 1280x720 is the one with less height of all the modern ones starting from the 1024x768), so I will try to center the main media and calculate it to fit 720px height 
        x=0
        self.ground_row1 = []
        #Originaly the grouind was random, with bones and heads of dinaussaurs randomly, but they prefered it simple with grass. To make ti random again use this list instead:
        #row1_sprite_list = ["ground_row1_col1.png", "ground_row1_col2.png", "ground_row1_col3.png", "ground_row1_col4.png", "ground_row1_col5.png"]
        row1_sprite_list = ["ground_row1_col1.png", "ground_row1_col2.png", "ground_row1_col3.png"]
        while x <= self.width:
            self.ground_row1.append( make_sprite(random.choice(row1_sprite_list), x=x, y=0, group=Z_INDEX6) )
            x += self.ground_row1[0].width
 
    def fairy(self):
        self.fairy = make_sprite("fairy.gif", y=256, group=Z_INDEX8, dx=self.FAIRY_DX, dy=self.FAIRY_DY, animation=True)
        self.fairy.y = self.height - self.fairy.height
 
    def labels(self, text="", x=500, y=500, width=0, height=0, align="left", font_name=["Lucida Sans Unicode", "Comic Sans MS", "Arial"], multiline=False, anchor_x="center", anchor_y="center", font_size=20, color=(0, 0, 0, 255), batch=MAIN_BATCH, group=Z_INDEX10):
        #Blue: color=(20, 50, 150, 255)
        return pyglet.text.Label(text,
        anchor_x=anchor_x,
        anchor_y=anchor_y,
        x=x,
        y=y,
        align=align,
        width=width,
        height=height,
        font_name=font_name,
        multiline=multiline,
        font_size=font_size,
        color=color,
        batch=batch,
        group=group)

    def phase1_start(self, dt):
        if not self.text_show:
            #texto original: Bem-vindo! Ajude a recuperar a natureza regando os cristas da fada Oriana.Use o rato para navegar a nuvem e o botão esquerdo para produzir água.
            if INTERACTION == True:
                self.text_show = self.labels(u"""Rato: move a nuvem
Botão esquerdo: produz chuva

Para iniciar pressiona enter...""", x=self.width/2, y=350, width=self.width/1.2, height=self.height/2, align="center", multiline=True)
            else:
                self.text_show = self.labels(u"""Bem-vindo!
Para iniciar pressiona enter...""", x=self.width/2, y=350, width=self.width/1.2, height=self.height/2, align="center", multiline=True)
            if SEX == "m":
                self.sounds_active["narrator"] = play_sound(voice_intro, loop=False)
            else:
                self.sounds_active["narrator"] = play_sound(voice_intro_f, loop=False)
            #self.narrator = pyglet.clock.schedule_once(play_sound_with_delay, 0.5, voice_intro)

    def restart_animate_fairy_stars(self, dt):
        #Disable mouse while animation is running
        self.set_mouse_visible(False)
        
        #Check if there is stuff from phase1_start to clean up. If there is the narrator sound in the list, it means we are comming from phase1_start function
        if "narrator" in self.sounds_active:
            self.sounds_active["narrator"].pause()
            self.sounds_active["narrator"].delete()
            del self.sounds_active["narrator"]
            
        if self.text_show:
            self.text_show.delete()
            self.text_show = ""
            
        #Animation of fairy movement
        self.fairy.x += self.fairy.dx * dt
        if self.fairy.y > self.ground_row1[0].height/6:
            self.fairy.y -= self.fairy.dy * dt
        if self.fairy.scale < self.FAIRY_MAX_SCALE:
            self.fairy.scale += self.FAIRY_SCALE_SPEED * dt
            
        #Slowly make them transparent, then delete tree, flowers and seeds from screen for a new seed sequence restart
        #Opacity down
        #if self.new_tree or self.keyboard_mid_phase1:
        #Was asked a lot of changes (no tree in mid_phase after loop 1 for instance) so for now this is a gimick that works
        if self.keyboard_mid_phase1:
            #if self.new_tree.opacity != 0 or self.keyboard_mid_phase1.opacity != 0:
            if self.keyboard_mid_phase1.opacity != 0:
                try:
                    self.new_tree.opacity = max(0, self.new_tree.opacity - (self.RESTART_OPACITY_DOWN_SPEED * dt) )
                except:
                    pass
                #create flowers animation. Disabled for the test, they prefer not many animations for now
                
                #This try except is a hack... Not optimal yes, but works. This sprite only exists when mid_phase1 is running, otherwise would give error. This code was made like a prototype, witho lots of cuts and changes along the way, but since it works, and was made by only me (and I understand) and no need to change later, no need to make it bulletproof and Object Oriented in a final version. 
                try:
                    self.keyboard_mid_phase1.opacity = max(0, self.keyboard_mid_phase1.opacity - (self.RESTART_OPACITY_DOWN_SPEED * dt) )
                except:
                    pass
                
                if INTERACTION == True:
                    #They asked for not using flowers in the normal mode, so I only use flowers in this mode
                    for flower in self.flowers:
                        flower.opacity = max(0, flower.opacity - (self.RESTART_OPACITY_DOWN_SPEED * dt) )
                
                for seed in self.seeds_current:
                    #seed.opacity = max(0, flower.opacity - (self.RESTART_OPACITY_DOWN_SPEED * dt) )
                    seed.opacity = max(0, seed.opacity - (self.RESTART_OPACITY_DOWN_SPEED * dt) )
                for seed in self.empty_seeds:
                    seed.opacity = max(0, seed.opacity - (self.RESTART_OPACITY_DOWN_SPEED * dt) )
                for seed in self.input_seeds_sprites:
                    seed.opacity = max(0, seed.opacity - (self.RESTART_OPACITY_DOWN_SPEED * dt) )
                if INTERACTION == False:
                    self.cloud_sprite.opacity = max(0, self.cloud_sprite.opacity - (self.RESTART_OPACITY_DOWN_SPEED * dt) )
                    #Turn sounds off and deletes player
                    if "rain" in self.sounds_active:
                        self.sounds_active["rain"].pause()
                        del self.sounds_active["rain"]
            #Delete when opacity is zero
            else:
                #I want to speed the game by deleting every sprite not needed anymore from memory, here I delete each individualy with pyglet delete() command. But maybe is not necessary, because next I delete the list that has all these sprites. But I do it anyway in hopes that it makes the game run faster, since it slows down a little with this many sprites animated on screen.
                #create flowers animation. Disabled for the test, they prefer not many animations for now
                if INTERACTION == True:
                    #They asked for not using flowers in the normal mode, so I only use flowers in this mode
                    for flower in self.flowers:
                        flower.delete()
                    del self.flowers[:]

                for seed in self.empty_seeds:
                    seed.delete()
                del self.empty_seeds[:]
                for seed in self.input_seeds_sprites:
                    seed.delete()
                del self.input_seeds_sprites[:]

                for seed in self.seeds_current:
                    seed.delete()
                del self.seeds_current[:]
                try:
                    self.new_tree.delete()
                    #if self.new_tree is not defined this big if block will give error, so we redifine to None
                    self.new_tree = None
                except:
                    pass
                #This try execept is a hack... Not optimal yes, but works. This sprite only exists when mid_phase1 is running, otherwise would give error. This code was made like a prototype, witho lots of cuts and changes along the way, but since it works, and was made by only me (and I understand) and no need to change later, no need to make it bulletproof and Object Oriented in a final version. 
                try:
                    self.keyboard_mid_phase1.delete()
                    self.keyboard_mid_phase1 = None
                except:
                    pass
        

        """
        #APAGAR?
        #This code is ugly, but people asked me a lot of changes and need it quick. This is because of mid_phase1, in case it is not in the 1st loop it jumps the tree growth, and we need to delete the keyboard instructions, but there is no tree, so this works in that scenario
        else:
            #This try execept is a hack... Not optimal yes, but works. This sprite only exists when mid_phase1 is running, otherwise would give error. This code was made like a prototype, witho lots of cuts and changes along the way, but since it works, and was made by only me (and I understand) and no need to change later, no need to make it bulletproof and Object Oriented in a final version. 
            try:
                self.keyboard_mid_phase1.delete()
            except:
                pass
        """        
                
        #While fairy moves, creat little stars behind
        #Load stars: each column of stars in vertical is a list, inside the list self.stars
        #Animation objective: move fairy and creat columns of stars till 50% of the screen width, then continue creating till fairy reaches out of screen but also deleting the ones behind till they all disapear
        #If starting animation and no stars in screen:
        if not self.stars:
            y = 0
            col_stars = []
            while y < self.height:
                star = make_sprite("stars.gif", x=0, group=Z_INDEX8, animation=True)
                star.y = y
                col_stars.append(star)
                y += star.height
            else:
                self.stars.append(col_stars)

        #If there are already stars, while stars summed width not reach more than half of the screen (1.6 for example; because stars start disapearing when fairy reaches half of the screen, so we need it to go the screen width plus half of it to be sure all the stars are out of the screen), create new stars when fairy is distant by the last column of stars by the width of the stars sprite
        elif self.fairy.x >= self.stars[-1][0].x + self.stars[-1][0].width + self.stars[-1][0].width and self.stars[0][0].width * len(self.stars) <= self.width * 1.6:
            y = 0
            col_stars = []
            while y < self.height:
                star = make_sprite("stars.gif", y=y, group=Z_INDEX8, animation=True)
                star.x = self.stars[-1][0].x + star.width
                col_stars.append(star)
                y += star.height
            else:
                self.stars.append(col_stars)
            #If stars occupy already half of the screen, make the first columns of stars invisible in the list of visible (we don't delete it yet, because we want it in the list of stars because of width calculations in the previous code logic
            if self.stars[0][0].width * len(self.stars) >= self.width/2:
                for stars in self.stars:
                    if stars[0].visible == True:
                        for star in stars:
                            star.visible = False
                            
                        #If last star is out of screen and animation ended, call next event animation in self.game_state
                        if stars[0].x > self.width:
                            #delete all sprites of stars from memory
                            for stars in self.stars:
                                for star in stars:
                                    star.delete()
                            #Empty list. Not: there is a difference between using 1) LIST = [] and 2) LIST[:] = [] or del LIST[:] but I think in this case it is not importante and makes no difference
                            #self.stars = []
                            #self.stars[:] = []
                            del self.stars[:]
                            #end this animation event and start the next one
                            self.game_state = "animate_fairy_new_seeds"
                        #break, because we have already found the firt visible star column of the list, don't need the others
                        break
        
    def animate_fairy_new_seeds(self, dt):
        
        #self.set_mouse_visible(False)
        if self.fairy.scale != 1:
            self.fairy.scale = 1
            self.fairy.x = -self.fairy.width
            self.fairy.y = self.height - self.fairy.height
        
        #If fairy out of position from previous animation, put it in place
        if self.fairy.x != 0:
            self.fairy.x = min(0, self.fairy.x + self.fairy.dx * dt)
        else:
            """
            if self.game_phase == "mid_phase1":
                #empty lists for next phase
                self.empty_seeds = []
                self.input_seeds_sprites = []
                self.input_seeds_number = ""
                #track numbers of mid_phase1 repeat. we want 2 tries
                self.mid_phase1_loop = 1
                #next phase start
                self.game_state = "mid_phase1"
            else:
                #And add new seeds
                self.new_seeds()
            """
            #And add new seeds
            self.new_seeds()
            
            
            
    def mid_phase1(self, dt):
        if self.empty_seeds:
            #"mid_phase1 - if self.empty_seeds"
            #check if all input was made and check if is right or wrong
            if len(self.input_seeds_sprites) == len(list(self.sequences[self.next_squence_key])):
                #done mid phase1, check results
                #if right
                if self.input_seeds_number == self.sequences[self.next_squence_key]:
                    #update log phase1
                    #self.phase1_log += self.input_seeds_number + ";True;"
                    #if first try
                    if self.mid_phase1_loop != self.mid_phase1_loop_max:
                        #update log phase1
                        #the 2nd in the csv is null because was right at first, there will not be a 2nd try, so we close it already with null
                        self.phase1_log += self.input_seeds_number + ";True;" + str(self.time_total) + ";" + str(sum(self.time_total))
                        for n in range(self.mid_phase1_loop_max - self.mid_phase1_loop):
                            self.phase1_log += ";Null;Null;0;0"
                        #reset in case it is not the first loop
                        self.mid_phase1_loop = 1
                    elif self.mid_phase1_loop == self.mid_phase1_loop_max:
                        self.phase1_log += self.input_seeds_number + ";True;" + str(self.time_total) + ";" + str(sum(self.time_total))
                        #reset self.mid_phase1_loop first to 1
                        self.mid_phase1_loop = 1
                    #Since was right skip this phase and let programme continue normally
                    #self.change_screen_sound = play_sound(sequence_end, loop=False, volume=1)
                    #Play "good choice" narrator sound
                    #Choose one from 4 randomly first
                    if SEX == "m":
                        voice_random = random.choice([voice_phase1_right_1_m, voice_phase1_right_2_m, voice_phase1_right_3_m])
                    else:
                        voice_random = random.choice([voice_phase1_right_1_f, voice_phase1_right_2_f, voice_phase1_right_3_f])
                    self.change_screen_sound = play_sound(voice_random, loop=False, volume=1)
                    self.game_phase = "phase1"
                    self.game_state = "restart_animate_fairy_stars"
                    
                #if wrong and more tries
                else:
                    #if not all tries wasted
                    if self.mid_phase1_loop != self.mid_phase1_loop_max:
                        #update log phase1
                        self.phase1_log += self.input_seeds_number + ";False;" + str(self.time_total) + ";" + str(sum(self.time_total)) + ";"
                        #increment loop
                        self.mid_phase1_loop += 1
                        """
                        #And repeat a 2nd loop, by cleaning these lists to force start over in next dt
                        self.empty_seeds = []
                        self.input_seeds_sprites = []
                        self.input_seeds_number = ""
                        """
						
                        """
						#if it is the last sequence of the blokc/loop, and it is the last try. ps: +1 because i starts at zero, but not len()
                        if len(self.sequences) == self.next_squence_key+1 and self.phase1_loop == self.phase1_max_loop:
                            if SEX == "m":
                                self.change_screen_sound = play_sound(voice_phase1_wrong_end_of_loop_m, loop=False, volume=1)
                            else:
                                self.change_screen_sound = play_sound(voice_phase1_wrong_end_of_loop_f, loop=False, volume=1)
                        #if it is not the last sequence of the loop
                        else:
                        """
                        #Play "wrong choice" narrator sound type for if 1st chance to pick
                        #Choose one from 2 randomly first
                        if SEX == "m":
                            voice_random = random.choice([voice_phase1_wrong_1_m, voice_phase1_wrong_2_m])
                        else:
                            voice_random = random.choice([voice_phase1_wrong_1_f, voice_phase1_wrong_2_f])
                        self.change_screen_sound = play_sound(voice_random, loop=False, volume=1)
                        
                    #if wrong and is last try for this sequence
                    #elif self.mid_phase1_loop == self.mid_phase1_loop_max:
                    else:
                        #if it is the last sequence of all the loops/blocks and will jump to phase 2 next
                        #self.phase1_loop == self.phase1_max_loop = if it is the very last loop, the 2nd (last) loop of phase 1
                        #len(self.sequences) == self.next_squence_key+1 = if it is the very last seed of this loop
                        if self.phase1_loop == self.phase1_max_loop and len(self.sequences) == self.next_squence_key+1:
                            #play nothing in this case
                            pass
                        #if it is the very last seed, but not the very last loop
                        elif self.phase1_loop != self.phase1_max_loop and len(self.sequences) == self.next_squence_key+1:
                            if SEX == "m":
                                self.change_screen_sound = play_sound(voice_phase1_wrong_1_m, loop=False, volume=1)
                            else:
                                self.change_screen_sound = play_sound(voice_phase1_wrong_end_of_loop_f, loop=False, volume=1)
                        #if it is the last try and wrong, but not the very last seed neither the very last loop
                        else:
                            """if SEX == "m":
                                self.change_screen_sound = play_sound(voice_phase1_wrong_end_of_loop_m, loop=False, volume=1)
                            else:
                                self.change_screen_sound = play_sound(voice_phase1_wrong_end_of_loop_f, loop=False, volume=1)
                            
                            """
                            #if SEX == "m":
                            #    self.change_screen_sound = play_sound(voice_phase1_wrong_1_m, loop=False, volume=1)
                            #else:
                            #    self.change_screen_sound = play_sound(voice_phase1_wrong_end_of_loop_f, loop=False, volume=1)
                                
                            
                            if SEX == "m":
                                self.change_screen_sound = play_sound(voice_phase1_null_1_m, loop=False, volume=1)
                            else:
                                self.change_screen_sound = play_sound(voice_phase1_null_1_f, loop=False, volume=1)
                            
                            
                            
                            
                        #update log phase1
                        self.phase1_log += self.input_seeds_number + ";False;" + str(self.time_total) + ";" + str(sum(self.time_total))
                        #And skip this, let programme continue, since we give only 2 tries
                        #reset self.mid_phase1_loop first to 1
                        self.mid_phase1_loop = 1
                        """
                        if SEX == "m":
                            null_voice = "phase1_null_1_m"
                        else:
                            null_voice = "phase1_null_1_f"
                        self.change_screen_sound = play_sound(null_voice, loop=False, volume=1)
                        """
                        #IF THE LAST CHOICE IS WRONG, YOU SAY NOTHING AFTERALL AND GO TO THE NEW SEED, SO I COMMENTED THIS OUT
                        #voice_random = random.choice([voice_phase1_wrong_1, voice_phase1_wrong_2])
                        #self.change_screen_sound = play_sound(voice_random, loop=False, volume=1)
                    
                    #restart or go to the next
                    #self.change_screen_sound = play_sound(sequence_end, loop=False, volume=1)

                    self.game_phase = "phase1"
                    self.game_state = "restart_animate_fairy_stars"
                        
                #print "\r\n"
                #print "==========================================================="
                #print self.phase1_log
                #print "==========================================================="
                
                """
                self.mid_phase1_loop += 1
                
                #we want 2 tries for mid_phase1
                #If 2 tries already, and no right results, then continue for new seed and skip this
                if self.mid_phase1_loop > 2:
                    #Let programme continue normally
                    self.game_phase = "phase1"
                    self.game_state = "restart_animate_fairy_stars"
                else:
                """    
        #If no gray empty seeds creat them first
        else:
            seed_count = len(list(self.sequences[self.next_squence_key]))
            for n in range(seed_count):
                seed = make_sprite("empty_gem.png", dy=self.SEED_DY, group=Z_INDEX8)
                seed.y = self.ground_row1[0].height - seed.height
                if self.empty_seeds:
                    seed.x = self.empty_seeds[0].x + seed.width * len(self.empty_seeds)
                else:
                    seed.x = self.width/2 - (seed_count * seed.width)/2
                self.empty_seeds.append(seed)
            self.keyboard_mid_phase1 = make_sprite("mid_phase1_keyboard.png", dy=self.SEED_DY, group=Z_INDEX10)
            self.keyboard_mid_phase1.y = self.empty_seeds[0].y + 200
            self.keyboard_mid_phase1.x = self.width/2 - (self.keyboard_mid_phase1.width)/2
            #Start the clock to get the time the child took for input
            self.timer.update_time()
            #And clean the old time older list, reseting for a new sequence input
            self.time_total[:] = []
            #Play a sound annuncng the start of this phase
            self.change_screen_sound = play_sound(mid_phase1_sound_start, loop=False, volume=1)
            
    def new_seeds(self):
        #check if game is in the mid_phase1 2nd loop, and we need to repeat the last seed for the children. If this is the case, don't creat a new seed and repeat the same as before
        if self.mid_phase1_loop > 1:
            del self.seeds_current[:]
            self.seeds_current = []
            
            #use the same seed as before (since we clreared it in the restar_fairy...etc function we need to creat it again)
            seeds = list(self.sequences[self.next_squence_key])
            
            for seed_number in seeds:
                sprite_name = "gem" + str(seed_number) + ".png"
                seed = make_sprite(sprite_name, dy=self.SEED_DY, group=Z_INDEX7)
                seed.y = self.height
                #Center the seeds in the window. If not seeds define position for the 1st, if already one calculate position based on it
                if self.seeds_current:
                    seed.x = self.seeds_current[0].x + seed.width * len(self.seeds_current)
                else:
                    seed.x = self.width/2 - (len(seeds) * seed.width)/2
                self.seeds_current.append(seed)

            self.game_state = "new_seeds_plant_animation"
        
        #otherwise creat new seed
        else:
            del self.seeds_current[:]
            self.seeds_current = []
            #Update self.next_squence_key with new key
            self.next_squence_key += 1

        
            if len(self.sequences) >= self.next_squence_key:
                #Convert each string char into a list, f.e. "157" = ["1", "5", "7"] for making the seeds sequence
                if self.game_phase == "phase1":
                    seeds = list(self.sequences[self.next_squence_key])
                    #Log
                    if self.game_phase == "phase1":
                        self.phase1_log += "\n"
                        self.phase1_log += self.sequences[self.next_squence_key] + ";"
                        #print "Phase 1 Log Add: " + self.sequences[self.next_squence_key]
                elif self.game_phase == "phase2":
                    seeds = list(self.sequences[self.next_squence_key].split(",")[0])
                
                for seed_number in seeds:
                    sprite_name = "gem" + str(seed_number) + ".png"
                    seed = make_sprite(sprite_name, dy=self.SEED_DY, group=Z_INDEX7)
                    seed.y = self.height
                    #Center the seeds in the window. If not seeds define position for the 1st, if already one calculate position based on it
                    if self.seeds_current:
                        seed.x = self.seeds_current[0].x + seed.width * len(self.seeds_current)
                    else:
                        seed.x = self.width/2 - (len(seeds) * seed.width)/2
                    self.seeds_current.append(seed)

                self.game_state = "new_seeds_plant_animation"
            else:
                if self.game_phase == "phase1":
        
                    if self.phase1_loop == self.phase1_max_loop:
                    
                        #play danger sound, not the default one in change screen. pause it and load the other
                        self.change_screen_sound.pause()
                        self.change_screen_sound.delete()
                        self.change_screen_sound = play_sound(sequence_end_danger, loop=False, volume=1)
                        
                        
                        self.game_state = "phase1_end"
                    else:
                        self.game_state = "phase1_pause"
       
                elif self.game_phase == "phase2":
                    self.game_state = "phase2_end"

                
    def phase1_pause(self, dt):
        if not self.text_show:
        
            #self.text_show = self.labels(u"""Muito bem!
#Para iniciar o loop seguinte pressiona Enter...""", x=self.width/2, y=350, width=self.width/1.2, height=self.height/2, align="center", multiline=True)


            self.phase1_loop += 1
            #shuffle seeds again for new loop
            random.shuffle(self.sequences)
            #order them by lenght size e.g. seeds with 2 items first, then seeds with 3 items, etc
            self.sequences = sorted(self.sequences, key=len)
            #restart counter for new seeds loop
            self.next_squence_key = -1
            #self.sounds_active["narrator"] = play_sound(voice_phase1_pause, loop=False)
            """
            if self.phase1_loop == 3:
                pyglet.clock.schedule_once(self.call_sound, 2.6, voice_phase1_pause_v2)
            else:
                if SEX == "m":
                    pyglet.clock.schedule_once(self.call_sound, 2.5, voice_phase1_pause)
                else:
                    pyglet.clock.schedule_once(self.call_sound, 2.5, voice_phase1_pause_f)
            #wait for enter input to go restart and go to restart_animate_fairy_stars
            """
            #if SEX == "m":
            #    pyglet.clock.schedule_once(self.call_sound, 2.5, voice_phase1_pause)
            #else:
            #    pyglet.clock.schedule_once(self.call_sound, 2.5, voice_phase1_pause_f)
                
            self.game_state = "restart_animate_fairy_stars"
            self.change_screen_sound = play_sound(sequence_end, loop=False, volume=0.7)
                    
    #We need this, because pyglet.clock.schedule_once only calls functions, and we need one here so that the call can be registered and paused later
    def call_sound(self, dt, sound):
        self.sounds_active["narrator"] = play_sound(sound, loop=False)
    
    def new_seeds_plant_animation(self, dt):
        #Move the seeds into the screen by sliding from the top of the screen
        for seed in self.seeds_current:
            if seed.y != self.ground_row1[0].height - seed.height:
                seed.y = max(self.ground_row1[0].height - seed.height, seed.y - seed.dy * dt)
            else:
                #if it is the last seed in the array, so it only runs once in the for loop, at it's end
                if seed == self.seeds_current[-1]:
                    if self.game_phase == "phase1":
                        if INTERACTION == True:
                            #Game waits for rain to drop in the seeds and grow tree
                            self.game_state = "watering"
                            #Enable mouse again
                            self.set_mouse_visible(True)
                        elif INTERACTION == False:
                            #I lost more than a week of my life because of this line... A lot of strange bugs were happening, I fixed one then a new one came, etc. This fucking function was running a lot of times and calling a lot of pyglet.clock.schedule_once that triggered later after x seconds and made a lot of conflitcts. And made everything slower the longer the wait time!! Pfff, Only later I noticed the source of all the problems, the minor bugs were only a symptom of something worst. I am pissed with this line, so I am writtign a lot for the future me to remeber the pain xD By making the game_state empty we stop the multiple calls to new_seeds_plant_animation, and the multiple pyglet.clock.schedule_once to self.change_to_watering. Now I can sleep fine again xD
                            self.game_state = ""
                            pyglet.clock.schedule_once(self.change_to_watering, self.time_for_rain)
     
                    elif self.game_phase == "phase2":
                        #Update timer, to know how long the user took to choose an option
                        #We put it here because it runs only once here
                        self.timer.update_time()
                        self.game_state = "question"
                    #TO DO APAGAR?
                    break
        """else:
            self.seed_n = 0
            for seed in self.seeds_current:
                if seed.y != self.ground_row1[0].height - seed.height:
                    seed.y = max(self.ground_row1[0].height - seed.height, seed.y - seed.dy * dt)
                else:"""
    
    #it is an isolated funcion because pyglet.clock.schedule_once only calls functions
    def change_to_watering(self, dt):
        #self.game_state = "watering"
        #If it is a normal case
        if self.mid_phase1_loop == 1 and self.game_phase != "mid_phase1":
            self.game_state = "watering"
            
        #If we are not in the 1st loop of mid_phase for inputs, in that case we don't want the tree to grow again and skip it after showing the seeds
        #NOTE: pff this part of the code is ugly and stupid! - I know, could be much better. But have few time, was asked new changes and need to give quick, no time to correct and test - dont want to change what works right now
        else:
            if self.keyboard_mid_phase1:
                pass
            else:
                #empty lists for next phase
                self.empty_seeds = []
                self.input_seeds_sprites = []
                self.input_seeds_number = ""
                self.game_phase = "mid_phase1"
                self.game_state = "mid_phase1"
    
    def question(self, dt):
        """
        try:
            if self.question_sprites:
                #This try/except is so it creats the sprits one time only, because this function runs in dt each tick
                pass
        except:
            self.question_sprites = []"""
            
        #Optimize: dt is running this function each tick, recreating these sprites again and again, but it is not a necessary processing power, if sprites already exist there is no need to creat again and wait input instead, so this can be optimized
        self.question_sprites = []
        
        #self.keyboard = make_sprite("ctrl_keys_keyboard.png",  x=self.width/2, y = 400, group=Z_INDEX8)
        #self.keyboard.x = self.keyboard.x - self.keyboard.width/2
        #self.question_sprites.append(self.keyboard)
        
        self.yes = make_sprite("yes.png",  x=self.width/2 + 350, y = 400, group=Z_INDEX8)
        #self.yes.x = self.yes.x - self.yes.width
        self.question_sprites.append(self.yes)
        
        self.no = make_sprite("no.png",  x=self.width/2 - 350, y = 400, group=Z_INDEX8)
        #subtract width because of anchor point beeing on the left
        self.no.x = self.no.x - self.no.width
        self.question_sprites.append(self.no)
    
    """
    def call_mid_phase1(self, dt):
        #empty lists for next phase
        self.empty_seeds = []
        self.input_seeds_sprites = []
        self.input_seeds_number = ""
        self.game_phase = "mid_phase1"
        self.game_state = "mid_phase1"
    """
    
    def tree_grow(self, dt):
        #If already tree, grow tree
        if self.new_tree:
            self.new_tree.scale = min(1, self.new_tree.scale + dt * self.TREE_GROWTH_SPEED)
            #Center the new scale sprite on screen
            self.new_tree.x = self.width/2 - self.new_tree.width/2
            
            #create flowers animation. Disabled for the test, they prefer not many animations for now
            """
            #new flowers while grow
            if self.new_tree.scale >= self.new_flower_each_scale * len(self.flowers):
                flower = make_sprite("flowers.gif", y=self.ground_row1[0].height, animation=True, group=Z_INDEX8)
                flower.scale = 0.2
                flower.x = self.flowers[-1].x + flower.width
                self.flowers.append(flower)
                play_sound("completetask_0.wav", loop=False, volume=1)
            """
            
            #if tree scales is 1, end and go to the next sequence/phase
            if self.new_tree.scale == 1:
                #self.change_screen_sound = play_sound(sequence_end, loop=False, volume=1)
                
                
                
                
                #jump to next phase: clearing all in screen with fairy+stars animation, for new seed if it exist
                #but first change to mid game phase for input check
                
                
                
                ####################
                #This code was added later, like prototype. Since we had a different logic in the "restart_animate_fairy_stars" function, this is a little messy (I don't delete this sprite, because the function will make checks on it and delet it later). The same with the rain sounds, I only pause them because later they will be deleted already
                if INTERACTION == False:
                    self.cloud_sprite.opacity = 0
                #Turn sounds off
                if "rain" in self.sounds_active:
                    self.sounds_active["rain"].pause()
 
                #######self.game_state = "restart_animate_fairy_stars"
                
                #start mid_phase1 after some seconds
                #pyglet.clock.schedule_once(self.call_mid_phase1, 1)

                #empty lists for next phase
                self.empty_seeds = []
                self.input_seeds_sprites = []
                self.input_seeds_number = ""
                self.game_phase = "mid_phase1"
                self.game_state = "mid_phase1"
                #############################

        #If no tree, creat sprite and plant new small tree baby :3
        else:
            #self.ground[0].height
            self.new_tree = make_sprite("tree1.png", y=self.ground_row1[0].height, group=Z_INDEX9)
            #Make the tree very small
            self.new_tree.scale = 0.01
            #Center the sprite on screen
            self.new_tree.x = self.width/2 - self.new_tree.width/2
            
            #create flowers animation. Disabled for the test, they prefer not many animations for now
            """
            #first flower
            flower = make_sprite("flowers.gif", x=0, y=self.ground_row1[0].height, animation=True, group=Z_INDEX8)
            flower.scale = 0.2
            
            #list with all flowers
            self.flowers = []
            
            self.flowers.append(flower)
            play_sound("completetask_0.wav", loop=False, volume=0.7)
            
            #calculate when new flower
            self.total_flowers = self.width / float(flower.width)
            
            #The tree stops grow when reachs 1 scale. Creat a new flower each time the tree grows this:
            self.new_flower_each_scale = 1 / self.total_flowers
            """
            
    def animate_clouds(self, dt):
        #ANIMATE CLOUDS
        #if last cloud is out of the screen, remove it out from the list and add a new one at the start: this creats the illusion of a loop inside the screen
        #PS: used the 1st "for loop" for not repeating the code
        for clouds in [self.clouds_index2, self.clouds_index3]:
            for sprite in clouds:
                if sprite.x >= self.width:
                    clouds.remove(sprite)
                    new_sprite = sprite
                    new_sprite.x = clouds[0].x - new_sprite.width
                    clouds.insert(0, new_sprite)
                #Here is the magic of movement
                sprite.x += sprite.dx * dt

    def animate_rain(self, dt):
                        
        #If INTERACTION in mode false
        if INTERACTION == False and self.game_state in ("watering"):
            self.left_mouse_state = True
            #Play Sounds
            #if "rain" not in self.sounds_active:
            #    self.sounds_active["rain"] = play_sound(sound_rain, loop=True)
    
        #This code was made originaly to work for Animation in mode True, the if above was later added for a fixed time without interaction
        if self.left_mouse_state == True and self.game_state in ("watering", "phase1_start"):
            rain_load = pyglet.resource.image("rain_day.png")
            rain_grid = pyglet.image.ImageGrid(rain_load, 10, 1)
            rain = pyglet.sprite.Sprite(rain_grid[self.n_rains], batch=MAIN_BATCH, group=Z_INDEX8)
            rain.dy = self.RAIN_DY
            if INTERACTION == False:
                self.cloud_sprite = make_sprite("watering_can.png", group=Z_INDEX9)
                self.cloud_sprite.x = self.width/2 - self.cloud_sprite.width/2
                self.cloud_sprite.y = self.height - self.cloud_sprite.height - 50
                
                rain.x = self.cloud_sprite.x + self.cloud_sprite.width/2 - rain.width/2
                rain.y = self.cloud_sprite.y - rain.height
                
            else:
                rain.x = self.mouse_x - rain.width/2
                rain.y = self.mouse_y - rain.height
                
            #Play Rain Sound
            if "rain" not in self.sounds_active:
                self.sounds_active["rain"] = play_sound(sound_rain, loop=True)
                
            self.rains.append( rain )
            #if grid ouf of index range, restart count
            if self.n_rains >= len(rain_grid)-1:
                self.n_rains = 0
            else:
                self.n_rains += 1
        
        
        #we need self.grow to check the state of the watering, if rain are inside seeds or not, for later stop de blink animation
        self.grow = False
        for rain in self.rains:
            #Delete rain sprite in case it is out of screen, otherwise it will slow down the game
            if rain.y + rain.height < 0:
                self.rains.remove(rain)
            #Make Rain transparent when under ground
            elif rain.y <= self.ground_row1[0].height:
                rain.opacity = 0
            #Here is the magic of movement for the rain
            rain.y -= rain.dy * dt
            
            #If game state is waiting for watering the seeds
            if self.game_state == "watering":
                seeds_left_x = self.seeds_current[0].x
                seeds_right_x = self.seeds_current[-1].x + self.seeds_current[-1].width
                seeds_top_y = self.seeds_current[0].y + self.seeds_current[0].height
                seeds_bottom_y = self.seeds_current[0].y
                
                #if rain.y <= seeds_top_y and rain.y >= seeds_bottom_y and rain.x + rain.width >= seeds_left_x and rain.x <= seeds_right_x:
                #The same but better code more cooler:
                #PS meaning: if rain is touching the seeds, creat tree or make it grow plus flowers, till it reaches scale 1

                if seeds_bottom_y <= rain.y <= seeds_top_y and seeds_left_x - rain.width <= rain.x <= seeds_right_x:
                    #Make seeds blink/opacity up and down when watering them
                    self.seed_blink(dt)
                    #for seed in self.seeds_current:
                        #seed.opacity = 255
                    self.tree_grow(dt)
                    #Make sefl.grow True if we find rain inside the seeds
                    self.grow = True

        #When not rainning in seeds the blink animation stops and opacity can end up in any value, like 100, 90, 0, 255, etc But we want it to be 255, to be solid and normal again if not blinking, so we make this check to turn opacity of seeds back to normal if there is no rain watering the seeds after it goes trought all possible rains.
        #Run only if there is rain droping down from cloud and the game state is "watering", otherwise we don't have seeds and gives error
        if self.rains and self.game_state == "watering":
            #If after iterating trought all rains any is inside de seeds area
            if self.grow == False:
                for seed in self.seeds_current:
                    #reset seeds opacity
                    seed.opacity = 255

    def seed_blink(self, dt):
        for seed in self.seeds_current:
            if self.opacity_status == "down":
                seed.opacity = max(0, seed.opacity - dt * self.SEED_BLINK_SPEED)
            else:
                seed.opacity = min(255, seed.opacity + dt * self.SEED_BLINK_SPEED)
        self.seeds_current
        if seed.opacity == 0:
            self.opacity_status = "up"
        if seed.opacity == 255:
            self.opacity_status = "down"
        #Note: when it stops blinking, the opacity can end up in any value. But we want it normal, solid 255 opacity when it stops blinking. But we cannot do it here, since we never when this will not be called, we did it at the end of the animate_rain() function that calls this.

    def phase1_end(self, dt):
        
		#This if is because of dt, for the code to run only once
        if not self.text_show:
        
            self.text_show = self.labels(u"""Fim da Fase 1.
Para iniciar a Fase 2 pressiona Enter...""", x=self.width/2, y=50, width=self.width/1.2, height=256, align="center", multiline=True)
            #Next we start phase2
            self.game_phase = "phase2"
            
            #Make sprites of witch
            self.witch = make_sprite("witch.png", group=Z_INDEX9, scale=0.01)
            self.witch.x = self.width/2 - self.witch.width/2
            self.witch.y = 256
                
            #Prepare the new seeds for phase 2
            #Next seed sequence to show. PS: negative number because lists starts counting at zero, and the function that makes the seeds starts by incrementing this number, so we want to start before zero
            self.next_squence_key = -1
            
            #Load new seeds
            self.sequences = get_lines_from_file("phase2_sequences.txt")
            
            #Make the seeds random
            random.shuffle(self.sequences)
            
            #Start Narrator voice with delay
            if SEX == "m":
                pyglet.clock.schedule_once(self.call_sound, 1.5, voice_phase2_screen)
                #self.narrator = pyglet.clock.schedule_once(play_sound_with_delay, 1.2, voice_phase2_screen)
            else:
                pyglet.clock.schedule_once(self.call_sound, 1.5, voice_phase2_screen_f)
                #self.narrator = pyglet.clock.schedule_once(play_sound_with_delay, 1.2, voice_phase2_screen_f)
            
            #ORIGINALLY WE WANTED RANDOOM SEEDS BUT WITH A FILTER, SO THE SAME TYPE OF SEED (GA, GB, NG, etc) WOULD NOT REPEAT. LATER WE OPTED FOR A PURE RANDOM, SO THIS CODE IS NOT IN USE, JUST BACKUP
            """
            #Make seeds order randoom, but with condition: the same type can't comeright after (f.g. GA after an GA type, or NG after a NG type)
            #first randoom the original list order
            random.shuffle(self.sequences)
            print self.sequences
            #Now group by type
            temp_list = []
            #types temp
            ga = []
            gb = []
            ng = []
            for s in self.sequences:
                seed = s.split(",")
                if seed[1] == "GA":
                    ga.append(seed)
                elif seed[1] == "GB":
                    gb.append(seed)
                elif seed[1] == "NG":
                    ng.append(seed)
                    
            #randomize the lists items order again
            random.shuffle(ga)
            random.shuffle(gb)
            random.shuffle(ng)
            
            #now reagroup by the condition of no repeat
            #temp_list = ga + gb + ng
            #Clear old list
            self.sequences = []
            #temp_last_type = []
            temp_last_type = random.choice([ga, gb, ng])
            #And insert with new seeds, accordingly to the condition, while the tem lists are not empty
            while ga or gb or ng:
                #this while is because of when a type list is empty, we don't want an empty list, so we filter with random_type != []. This is not the perfect logic, since it can loop lots of times before finding a not empty list, but since there is only 3 conditions to loop in it works and not takes much time. Later we can improve this part if needed, at the moment I don't have time to think in a better algorithm
                #this while also serves to filter the condition of not reapeating type
                random_type = []
                #aqui problema pk na 2ª itineração random_type é vazio mas temp_last_type não, não são iguais
                #OR OU AND????
                #while random_type == [] or (random_type == [] and random_type == temp_last_type):
                while random_type == []:
                    temp_type = random.choice([ga, gb, ng])
                    if temp_type != []:
                        #check if condition of no repeat is true, otherwise it will keep blank and the loop will repeat
                        if temp_type != temp_last_type:
                            random_type = temp_type
                        #later we can creat an elif here to check if is last item, in case types are not in pairs
                        #elif ga or gb or ng has only one item
                        
                    #if we have only one type left, and the numbers are not in pairs, and before we had the same type and don't have anymore different types to use (f.e. had GA before, but now only have GA's left), in this case we should make a logic to break the while and choose a type equal to the last, only if the other type lists are empty. For this is not needed because I know that the types will be in the same number each, but later for other people to use, this logic would be nice
                    #example pseudo-code:
                    #if 2 of the 3 lists types are empty:
                        #random_type = x
                        #break
                        
                if random_type[0][1] == "GA":
                    temp_last_type = ga
                elif random_type[0][1] == "GB":
                    temp_last_type = gb
                elif random_type[0][1] == "NG":
                    temp_last_type = ng

                random_item = random.choice(random_type)
                self.sequences.append(random_item)
                    
                #remove first item equal from list type
                random_type.remove(random_item)
            """
            
            #print "***************************************************"
            #print self.sequences
            
            #self.fairy_direction = "down"
            #self.temp_fairy_dy = 500
            
        #Animate witch growth
        if self.witch.height < self.height - 256:
            self.witch.scale += self.WITCH_SCALE_SPEED * dt
            self.witch.x = self.width/2 - self.witch.width/2
        
        if self.fairy.x + self.fairy.width > 0:
            self.fairy.x = self.fairy.x - 300 * dt
        
        #Initially fairy moved up and down quickly like in fear of the witch, but the authors of the project asked me to take it off. To turn it on again uncomment this code:
        #PS: self.fairy_direction = "down" and self.temp_fairy_dy = 500 above must be uncomment too, we need these variables
        """
        if self.fairy_direction == "down":
            #self.fairy.y -= self.fairy.y *dt:
            self.fairy.y = max(0, self.fairy.y - self.temp_fairy_dy * dt)
            if self.fairy.y == 0:
                self.fairy_direction = "up"
                
        elif self.fairy_direction == "up":
            #self.fairy.y -= self.fairy.y *dt:
            self.fairy.y = min(self.height - self.fairy.height, self.fairy.y + self.temp_fairy_dy * dt)
            if self.fairy.y == self.height - self.fairy.height:
                self.fairy_direction = "down"
        """
            
    
    def phase2_instructions(self,dt):
        #This if is because of dt, for the code to run only once
        if not self.text_show:
        
            self.text_show = self.labels(u"""
Pressiona Enter para iniciar...""", x=self.width/2, y=50, width=self.width/1.2, height=256, align="center", multiline=True)

            #show keyboard instructions
            self.keyboard = make_sprite("ctrl_keys_keyboard.png",  x=self.width/2, y = 400, group=Z_INDEX8)
            self.keyboard.x = self.keyboard.x - self.keyboard.width/2
        
    def phase2_end(self, dt):
        if not self.text_show:
			#play thank you message
            if SEX == "m":
                self.sounds_active["narrator"] = play_sound(voice_end_thanks_m, loop=False)
            else:
                self.sounds_active["narrator"] = play_sound(voice_end_thanks_f, loop=False)
			
            #print "---Log save start---"
            
            #slugify
            #The middle code in the NAME makes turns into a filename safe
            name = NAME.replace(" ", "_")
            name = "".join([c for c in name if re.match(r'\w', c)])
            filename = name + str(int(time.time()))
            file_path = "./Saves/" + filename + "/"
            
            #file_path_phase2 = "./Saves/" + filename + "/" + "phase2_" + filename + ".txt"
            file_path_phase2 = file_path + "phase2_" + filename + ".csv"
            file_path_phase1 = file_path + "phase1_" + filename + ".csv"
            file_path_metadata = file_path + "metadata_" + filename + ".txt"
            
            if not os.path.exists(os.path.dirname(file_path)):
                try:
                    os.makedirs(os.path.dirname(file_path))
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise

            try:
                file = open(file_path_phase2, "w")
                file.write(self.phase2_log)
                file.close()
                
                file_1 = open(file_path_phase1, "w")
                file_1.write(self.phase1_log.encode('utf8'))
                file_1.close()
                
                
                #Add screen width and height to the LOG - at start was not possible, because the first LOG data was created in console mode not fullscreen, but now inside pyglet is easier
                #first make ti global so we can acess inside the class
                global LOG
                LOG += "\r\n"
                LOG += u"Screen width: " + str(self.width)
                LOG += "\r\n"
                LOG += u"Screen height: " + str(self.height)
        
                file_2 = open(file_path_metadata, "w")
                file_2.write(LOG.encode('utf8'))
                file_2.close()
                
                print "Ficheiro criado em: " + file_path_metadata
                print "Ficheiro criado em: " + file_path_phase1
                print "Ficheiro criado em: " + file_path_phase2
                
            except:
                print "ERRO! - Save dos dados falhou!!"
            
            self.text_show = self.labels(u"""Fim da Fase 2. Teste terminado e dados gravados.
Para encerrar o programa pressiona Enter...""", x=self.width/2, y=350, width=self.width/1.2, height=self.height/2, align="center", multiline=True)
		
            """
            def exit_game(sefl, dt):
                pyglet.app.exit()
            """
            #no need, they are in the phase1_end:
            #self.fairy_direction = "down"
            #self.temp_fairy_dy = 500
            
        if self.fairy_direction == "down":
            #self.fairy.y -= self.fairy.y *dt:
            self.fairy.y = max(0, self.fairy.y - self.temp_fairy_dy * dt)
            if self.fairy.y == 0:
                self.fairy_direction = "up"
                
        elif self.fairy_direction == "up":
            #self.fairy.y -= self.fairy.y *dt:
            self.fairy.y = min(self.height - self.fairy.height, self.fairy.y + self.temp_fairy_dy * dt)
            if self.fairy.y == self.height - self.fairy.height:
                self.fairy_direction = "down"
    
    def mid_phase1_input_get(self, number):
        #Include time it took to enter input since last call
        time = self.timer.update_time()
        self.time_total.append(time)
        
        sprite_name = "gem" + str(number) + ".png"
        seed = make_sprite(sprite_name, dy=self.SEED_DY, group=Z_INDEX9)
        seed.y = self.empty_seeds[len(self.input_seeds_sprites)].y
        seed.x = self.empty_seeds[len(self.input_seeds_sprites)].x
        self.input_seeds_sprites.append(seed)
        self.input_seeds_number += str(number)
        #play this sound when key pressed
        play_sound(complete_task, loop=False, volume=1)
    
    def on_key_press(self, symbol, modifiers):
        if symbol == key.ENTER:
            if self.game_state == "phase1_start" or self.game_state == "phase1_pause":
                self.game_state = "restart_animate_fairy_stars"
                self.change_screen_sound = play_sound(sequence_end, loop=False, volume=0.7)
            elif self.game_state == "phase1_end":
                #self.game_state = "animate_fairy_new_seeds"
                #delete witch sprite
                self.witch.delete()
                #self.game_state = "restart_animate_fairy_stars"
                self.game_state = "phase2_instructions"
                #when narrator ins play_once, I can't stop it here, it stops automatically
                #self.text_show.delete()
                #self.text_show = ""
                
                #stop sound
                if "narrator" in self.sounds_active:
                    self.sounds_active["narrator"].pause()
                    self.sounds_active["narrator"].delete()
                    del self.sounds_active["narrator"]
                    
                #delet text label    
                if self.text_show:
                    self.text_show.delete()
                    self.text_show = ""
                
            elif self.game_state == "phase2_instructions":
                #delete sprite
                #for sprite in self.question_sprites:
                #    sprite.delete()
                #del self.question_sprites[:]
                self.keyboard.delete()
                self.game_state = "restart_animate_fairy_stars"
                
            elif self.game_state == "phase2_end":
                pyglet.app.exit()
                
        
        if self.game_phase == "mid_phase1":
            if symbol == key.S:
                self.mid_phase1_input_get(1)
            elif symbol == key.F:
                self.mid_phase1_input_get(2)
            elif symbol == key.H:
                self.mid_phase1_input_get(3)
            elif symbol == key.K:
                self.mid_phase1_input_get(4)
                
        
        
        """if symbol == key.DOWN:
            if window.fullscreen == True:
                self.set_fullscreen(False)
                #pyglet.app.exit()
            else:
                self.set_fullscreen(True)
        """
        
        if symbol == key.LCTRL or symbol == key.RCTRL:
            if self.game_state == "question":
                r = ""
                #update time since last update_time()
                timer = self.timer.update_time()
                #print timerr
                if symbol == key.LCTRL:
                    r = "no"
                elif symbol == key.RCTRL:
                    r = "yes"
                
                #check if answear was right or wrong
                if self.sequences[self.next_squence_key].split(",")[0] in self.phase1_sequences:
                    correct = "True"
                else:
                    correct = "False"
                
                #wrong or right answear
                if correct == "True":
                    if r == "yes":
                        answear = "True"
                    else:
                        answear = "False"
                else:
                    if r == "yes":
                        answear = "False"
                    else:
                        answear = "True"
                        
                #self.phase2_log += str(self.next_squence_key + 1) + " - Seed: " + self.sequences[self.next_squence_key][0] + " - Answer: " + r + "\r\n"
                self.phase2_log += "\n" + str(self.next_squence_key + 1) + ";" + self.sequences[self.next_squence_key].split(",")[0] + ";" + self.sequences[self.next_squence_key].split(",")[1] + ";" + self.sequences[self.next_squence_key].split(",")[2] + ";" + r + ";" + str(timer) + ";" + correct + ";" + answear
                
                #print self.phase2_log
                
                #play plim sound when CTRL pressed
                play_sound(complete_task, loop=False, volume=1)
                
                #delete sprites in the question instructions
                for sprite in self.question_sprites:
                    sprite.delete()
                del self.question_sprites[:]
                
                self.game_state = "animate_fairy_new_seeds"

        if symbol == key.F1:
            print self.phase1_log
          
        if symbol == key.F2:
            print self.phase2_log
            
        if symbol == key.F3:
            print LOG
        
        if symbol == key.ESCAPE:
            pyglet.app.exit()
            #sys.exit()
            #self.game_state = "exit_game"
            
    def on_key_release(self, symbol, modifiers):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            if INTERACTION == True:
                self.left_mouse_state = True
                #We start tracking mouse x and y here and not only in on_mouse_drag() because the user can click but not move the mouse, and we need x and y right away for the rain animation to position the rain
                self.mouse_x = x
                self.mouse_y = y
            
                #change mouse cloud to happy mode
                cursor = pyglet.window.ImageMouseCursor(self.cloud_happy, self.cloud_happy.height/2, 0)
                self.set_mouse_cursor(cursor)
            
                #Play Sounds
                if "rain" not in self.sounds_active and self.game_state in ("watering", "phase1_start"):
                    self.sounds_active["rain"] = play_sound(sound_rain, loop=True)
            
    def on_mouse_release(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            if INTERACTION == True:
                self.left_mouse_state = False
                
                #change mouse cloud to normal mode
                cursor = pyglet.window.ImageMouseCursor(self.cloud_normal, self.cloud_normal.height/2, 0)
                self.set_mouse_cursor(cursor)
                
                #Turn sounds off and deletes player
                if "rain" in self.sounds_active:
                    self.sounds_active["rain"].pause()
                    del self.sounds_active["rain"]
        
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        #keep track of mouse x and y for rain (f.e.) animations while left mouse is clicked
        if buttons == mouse.LEFT:
            self.mouse_x = x
            self.mouse_y = y
            
    def on_draw(self):
        self.clear()
        MAIN_BATCH.draw()
        #FPS.draw()
        #Set window background color rgba (note: in gl is in scale 0 to 1, inestead of 0 to 255; that is why I devide the rgb values by 255, so we get a floated value in the 0 to 1 scale
        pyglet.gl.glClearColor(241.0/255, 246.0/255, 248.0/255, 1)
        
    def update(self, dt):
        self.animate_clouds(dt)
        self.animate_rain(dt)
        
        #If there is something in the self-game_state call it's function. I made the sates with the same name as their respective functions
        if self.game_state:
            #If it exists call function dynamically instead of using a long if elif f.e.: if self.game_state == "restart_animate_fairy_stars": self.restart_animate_fairy_stars(dt) etc
            try:
                getattr(self, self.game_state)(dt)
            except:
                pass
        """
        if self.game_state == "restart_animate_fairy_stars":
            self.restart_animate_fairy_stars(dt)
        elif self.game_state == "animate_fairy_new_seeds":
            self.animate_fairy_new_seeds(dt)
        elif self.game_state ==  "new_seeds_plant_animation":
            self.new_seeds_plant_animation(dt)
        elif self.game_state ==  "watering":
            self.watering(dt)
        """    

def update(dt):
    if window:
        window.update(dt)

"""
class Seeds():
    def __init__(self):
        self.filename = "resources.txt"
        self.sequences = self.get_lines_from_file(self.filename)
        
        for seq in self.sequences:
            for char in seq:
                print char

    def get_lines_from_file(self, filename):
        #strip is used to delete new line characters and white space at start and end of line
        lines = [line.strip() for line in open(filename)]
        return lines
"""

if __name__ == '__main__':
    
    date = datetime.datetime.now()
    
    print(u"===PROGRAMA PARA TESTAR RECONHECIMENTO DE PADRÕES GRAMATICAIS===\r\n")
    print(u"-Programado por: Paulo Jorge PM | E-mail (podem contactar em caso de bugs): paulo.jorge.pm@gmail.com | Website: http://www.paulojorgepm.net")
    print(u"-Programado com: Python 2.7.12 + Pyglet 1.2.4 (é necessário suporte gráfico para OpenGL) | Licença do código: GNU GPL-3 | Imagens e som com créditos próprios, não são da minha autoria.")
    print(u"-Testado apenas em ambiente Windows (10) com monitores de resolução 1366px-768px, 1600px-900px e 1920px-1080px - baixas resoluções podem desconfigurar. Deve funcionar em ambiente Linux (no máximo com pequenos ajustes no código) Linux FTW BTW.")
    print(u"-Autoras do projeto/programado para: Ana Paula Soares (asoares@psi.uminho.pt) e Montserrat Comesaña - Escola de Psicologia, Universidade do Minho.")
    
    print(u"\r\n\r\nWelcome!\r\n->Preencha os seguintes dados referentes ao sujeito em teste antes de iniciar o programa.\r\n->Use a tecla ENTER para confirmar cada introdução\r\n")
    
    #strftime: convert from datetime to str
    LOG += "Date: " + date.strftime("%Y-%m-%d %H:%M:%S.%f")
    LOG += "\r\n"
    #decode code because command promp gives unicode errors if non ascii characters inputed
    NAME = ""
    while NAME == "":
        NAME = raw_input("Name: ").decode(sys.stdin.encoding)
        
    LOG += u"Nome: " + NAME
    LOG += "\r\n"
    
    AGE = ""
    while is_number(AGE) == False:
        AGE = raw_input("Age (only accepts numbers): ")
        
    LOG += u"Idade: " + AGE
    LOG += "\r\n"
    
    SEX = ""
    while SEX not in ["m","f"]:
        SEX = raw_input("Sexo (accepted values: m for masculine, f for feminine): ").decode(sys.stdin.encoding)
        #convert to lower case always
        SEX = SEX.lower()
        #strip whitespace from start and end just in case
        SEX = SEX.strip()  
    LOG += u"Sex: " + SEX
    LOG += "\r\n"
    
    n= ""
    while n not in ["1", "2"]:
        n = raw_input("Modo do programa: introduzir a tecla 1 para modo default (tempo fixo) ou tecla 2 para modo interativo com o rato\r\n->").decode(sys.stdin.encoding)
    if n == "2":
        INTERACTION = True
        LOG += "Mode: interactive"
    elif n == "1":
        INTERACTION = False
        LOG += "Mode: fixed"
        
    WAIT_TIME = ""
    
    while is_number(WAIT_TIME) == False:
        WAIT_TIME = raw_input("Seconds to wait before rain starts (only accepts numbers, for floats use point, not comma): ")
    
    LOG += "\r\n"
    LOG += u"Wait time: " + WAIT_TIME

    print "\r\n\r\n" + LOG
    print "\r\n"
    print u"===Start of the 1st pahse of the test==="

    enter = raw_input("\r\n=== SOFTWARE READY===\r\nPlease press any key to start...")

    #FPS delta time
    pyglet.clock.schedule_interval(update, 1/60.0)
    window = MainWindow()
    pyglet.app.run()