from random import randint
from pgzero.builtins import Actor, keyboard
import pgzrun

WIDTH = 800 # Setting game screen size
HEIGHT = 600
CENTER_X = WIDTH / 2
CENTER_Y = HEIGHT / 2

move_list = [] # Save the current dance sequence
display_list = [] # A sequence of dance steps for display
original_moves = [] # Keep the complete dance sequence for the second player

score_p1 = 0
score_p2 = 0
current_move = 0
count = 4
dance_length = 4 # How many moves per round

say_dance = False
show_countdown = True
moves_complete = False
game_over = False
player_turn = 1
p1_failed = False # Record whether P1 failed
p2_failed = False # Record whether P2 failed

dancer = Actor("dancer-start")# Create a character (dancer and arrow keys)
dancer.pos = CENTER_X + 5, CENTER_Y - 40

up = Actor("up")
up.pos = CENTER_X, CENTER_Y + 110
right = Actor("right")
right.pos = CENTER_X + 60, CENTER_Y + 170
down = Actor("down")
down.pos = CENTER_X, CENTER_Y + 230
left = Actor("left")
left.pos = CENTER_X - 60, CENTER_Y + 170

def draw():
    screen.clear()
    screen.blit("stage", (0, 0))
    if not game_over:
        dancer.draw()# Draw dancers and buttons
        up.draw()
        down.draw()
        right.draw()
        left.draw()
        screen.draw.text("Player 1 Score: " + str(score_p1), topleft=(10, 10), color="black") # Show score and round information
        screen.draw.text("Player 2 Score: " + str(score_p2), topleft=(10, 40), color="black")
        screen.draw.text("Player " + str(player_turn) + "'s Turn", topleft=(CENTER_X - 70, 100), color="black")
        if say_dance:# Display "Dance!" Or count down
            screen.draw.text("Dance!", color="black", topleft=(CENTER_X - 65, 150), fontsize=60)
        if show_countdown:
            screen.draw.text(str(count), color="black", topleft=(CENTER_X - 8, 150), fontsize=60)
    else:
        screen.draw.text("GAME OVER!", color="black", topleft=(CENTER_X - 130, 220), fontsize=60)# The screen of GAME OVER
        screen.draw.text("Player 1 Score: " + str(score_p1), topleft=(CENTER_X - 100, 300), color="black")
        screen.draw.text("Player 2 Score: " + str(score_p2), topleft=(CENTER_X - 100, 330), color="black")
        if p1_failed and not p2_failed: #Judge the win or lose
            screen.draw.text("Player 2 Wins!", center=(CENTER_X, 380), fontsize=60, color="black")
        elif p2_failed and not p1_failed:
            screen.draw.text("Player 1 Wins!", center=(CENTER_X, 380), fontsize=60, color="black")
        else:
            screen.draw.text("It's a tie!", center=(CENTER_X, 380), fontsize=60, color="black")

def reset_dancer():  # Reset Character Picture
    if not game_over:
        dancer.image = "dancer-start"
        up.image = "up"
        right.image = "right"
        down.image = "down"
        left.image = "left"

def update_dancer(move): #Update dancer movements and button lighting.
    if move == 0:
        up.image = "up-lit"
        dancer.image = "dancer-up"
    elif move == 1:
        right.image = "right-lit"
        dancer.image = "dancer-right"
    elif move == 2:
        down.image = "down-lit"
        dancer.image = "dancer-down"
    elif move == 3:
        left.image = "left-lit"
        dancer.image = "dancer-left"
    clock.schedule(reset_dancer, 0.5)

def display_moves():  # Show all action sequences 
    global display_list, say_dance, show_countdown
    if display_list:
        this_move = display_list.pop(0)
        update_dancer(this_move)
        clock.schedule(display_moves, 1)
    else:
        say_dance = True
        show_countdown = False

def generate_moves(): # Generate a random dance sequence
    global move_list, display_list, count, say_dance, show_countdown, original_moves
    move_list = []
    display_list = []
    count = 4
    say_dance = False
    for _ in range(dance_length):
        rand_move = randint(0, 3)
        move_list.append(rand_move)
        display_list.append(rand_move)
    original_moves = move_list.copy()
    show_countdown = True
    countdown()

def countdown(): # countdown beofre the next actions
    global count, show_countdown
    if count > 1:
        count -= 1
        clock.schedule(countdown, 1)
    else:
        show_countdown = False
        display_moves()

def next_move():  # Move on to the next step or end the round
    global current_move, moves_complete  
    if current_move < dance_length - 1:
        current_move += 1
    else:
        moves_complete = True

def on_key_up(key):
    global current_move, moves_complete, game_over
    global score_p1, score_p2, player_turn, p1_failed, p2_failed

    if game_over or not say_dance:
        return

    move = -1
    if player_turn == 1: 
        if key == keys.UP: move = 0 # the arrow keys of player1
        elif key == keys.RIGHT: move = 1
        elif key == keys.DOWN: move = 2
        elif key == keys.LEFT: move = 3
    elif player_turn == 2:
        if key == keys.W: move = 0 #the arrow keys of player2
        elif key == keys.D: move = 1
        elif key == keys.S: move = 2
        elif key == keys.A: move = 3

    if move == -1:
        return

    update_dancer(move)
    if move_list[current_move] == move:
        if player_turn == 1:
            score_p1 += 1
        else:
            score_p2 += 1
    else:
        if player_turn == 1:
            p1_failed = True
        else:
            p2_failed = True

    next_move()

def update(): # Control each round of process and turn conversion
    global current_move, moves_complete, game_over, player_turn, display_list, count, show_countdown, say_dance
    if not game_over and moves_complete:
        if player_turn == 1:
            player_turn = 2 # Change to Player 2, show the same dance steps and count down.
            current_move = 0
            display_list = original_moves.copy()
            count = 4
            show_countdown = True
            say_dance = False
            clock.schedule(countdown, 1)
        else:
            if p1_failed or p2_failed: # If one of them fails, end it; otherwise, regenerate new dance steps for Player 1.
                game_over = True
            else:
                player_turn = 1
                current_move = 0
                generate_moves()
        moves_complete = False


generate_moves()
music.play("amusementpark") #change the song 

pgzrun.go()
