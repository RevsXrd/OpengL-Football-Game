from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math

# Window dimensions
W_Width, W_Height = 800, 600

# Game variables
player1_x, player1_y = -300, -200
player2_x, player2_y = 300, -200
ball_x, ball_y = 0, 0
ball_dx, ball_dy = -4, 3
player1_speed = 15
player2_speed = 15
ball_size = 15
player_radius = 30

ground_level = -250
g = 1  # Gravity
jump_speed = 20
player1_dy = 0
player2_dy = 0

# Player stamina
Player1_Stamina = 5
Player2_Stamina = 5
max_stamina = 5

# Scores
score1 = 0
score2 = 0

# Last Scorer
Last_Scorer = None

# Celebration variables
celebration_timer = 0
celebration_duration = 60  # Frames

# Game duration in seconds
game_duration = 60  # 1 minute
game_timer = game_duration * 60  # Converted to frames (60 FPS)
game_over = False

# Ability variables
ability_x, ability_y = 0, 400
ability_radius = 15
ability_fall_speed = 5
ability_active = False
boost_duration = 2000  # 2 seconds in milliseconds
boost_speed = 30
player1_boosted = False
player2_boosted = False
spawn_interval = 5000

# Weather variables
weather_active = True
weather_duration = 10000  # Increased to 10 seconds in milliseconds
weather_speed_modifier = 0.5  # Reduce speed by 50%

# Wind variables
wind_active = True  # Wind starts as inactive
wind_strength = 2    # Strength of the wind
wind_direction = 1
wind_duration = 4000  # Increased to 4 seconds in milliseconds

# Hard kick variables
hard_kick_x, hard_kick_y = 0, 400
hard_kick_radius = 15
hard_kick_fall_speed = 5
hard_kick_active = False
hard_kick_duration = 2000  # 2 seconds in milliseconds
player1_hard_kick = False
player2_hard_kick = False
hard_kick_spawn_interval = 6000  # 6 seconds

number_patterns = {
    "0": [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
          (1, 0), (1, 4),
          (2, 0), (2, 1), (2, 2), (2, 3), (2, 4)],
    "1": [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4)],
    "2": [(0, 0), (0, 2), (0, 3), (0, 4),
          (1, 0), (1, 2), (1, 4),
          (2, 0), (2, 1), (2, 2), (2, 4)],
    "3": [(0, 0), (0, 2), (0, 4),
          (1, 0), (1, 2), (1, 4),
          (2, 0), (2, 1), (2, 2), (2, 3), (2, 4)],
    "4": [(0, 0), (0, 1), (0, 2),
          (1, 2),
          (2, 0), (2, 1), (2, 2), (2, 3), (2, 4)],
    "5": [(0, 0), (0, 1), (0, 2), (0, 4),
          (1, 0), (1, 2), (1, 4),
          (2, 0), (2, 2), (2, 3), (2, 4)],
    "6": [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
          (1, 0), (1, 2), (1, 4),
          (2, 0), (2, 2), (2, 3), (2, 4)],
    "7": [(0, 0), (0, 1), (0, 2),
          (1, 0),
          (2, 0), (2, 1), (2, 2), (2, 3), (2, 4)],
    "8": [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
          (1, 0), (1, 2), (1, 4),
          (2, 0), (2, 1), (2, 2), (2, 3), (2, 4)],
    "9": [(0, 0), (0, 1), (0, 2),
          (1, 0), (1, 2),
          (2, 0), (2, 1), (2, 2), (2, 3), (2, 4)],
}

# Key states
keys = {}

def draw_line_midpoint(x1, y1, x2, y2, color=(1.0, 1.0, 1.0)):
    glColor3f(*color)
    glBegin(GL_POINTS)

    dx = x2 - x1
    dy = y2 - y1
    d = 2 * dy - dx  # Initial decision parameter
    x, y = x1, y1

    # Adjust for different octants
    if abs(dy) <= abs(dx):  # Slope <= 1
        if x1 > x2:  # Ensure left-to-right drawing
            x, y = x2, y2
            x2, y2 = x1, y1
            dx = -dx
            dy = -dy

        while x <= x2:
            glVertex2f(x, y)
            if d > 0:
                y += 1 if dy > 0 else -1
                d += 2 * (dy - dx)
            else:
                d += 2 * dy
            x += 1
    else:  # Slope > 1
        if y1 > y2:  # Ensure bottom-to-top drawing
            x, y = x2, y2
            x2, y2 = x1, y1
            dx = -dx
            dy = -dy

        while y <= y2:
            glVertex2f(x, y)
            if d > 0:
                x += 1 if dx > 0 else -1
                d += 2 * (dx - dy)
            else:
                d += 2 * dx
            y += 1

    glEnd()

# Function to draw a circle
def draw_circle(x, y, radius, color):
    glColor3f(*color)

    # Midpoint Circle Algorithm
    dx = 1 - radius  # Initial decision parameter
    x0, y0 = 0, radius  # Start at the topmost point of the circle
    points = []

    while x0 <= y0:
        # Add points for the eight symmetric positions
        points.extend([
            (x + x0, y + y0), (x - x0, y + y0), (x + x0, y - y0), (x - x0, y - y0),
            (x + y0, y + x0), (x - y0, y + x0), (x + y0, y - x0), (x - y0, y - x0)
        ])

        # Update decision parameter
        if dx < 0:
            dx += 2 * x0 + 3
        else:
            dx += 2 * (x0 - y0) + 5
            y0 -= 1

        x0 += 1

    # Draw the points using GL_POINTS
    glBegin(GL_POINTS)
    for point in points:
        glVertex2f(*point)
    glEnd()

# Function to display scores
def draw_number_with_points(x, y, number, scale=10):
    glColor3f(1.0, 1.0, 1.0)
    glPointSize(5)
    glBegin(GL_POINTS)
    for digit in str(number):
        if digit not in number_patterns:
            continue
        for (dx, dy) in number_patterns[digit]:
            glVertex2f(x + dx * scale, y - dy * scale)
        x += scale * 4  # Add spacing for next digit
    glEnd()

# Function to draw text on the screen
def draw_text(x, y, text):
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ctypes.c_int(ord(ch)))

def draw_stamina1(x, y, stamina, max_stamina):
    glColor3f(0.0, 0.0, 1.0)
    glPointSize(5)
    glBegin(GL_POINTS)
    for i in range(int(stamina)):
        glVertex2f(x + i * 10, y)
    glEnd()
def draw_stamina2(x, y, stamina, max_stamina):
    glColor3f(1.0,0.0, 0.0)
    glPointSize(5)
    glBegin(GL_POINTS)
    for i in range(int(stamina)):
        glVertex2f(x + i * 10, y)
    glEnd()

# Display function
def display():
    global player1_x, player1_y, player2_x, player2_y, ball_x, ball_y, score1, score2, game_over, Player1_Stamina, Player2_Stamina, game_timer, celebration_timer, Last_Scorer

    glClear(GL_COLOR_BUFFER_BIT)

    # Draw ground
    draw_line_midpoint(-W_Width // 2, ground_level, W_Width // 2, ground_level, color=(0.5, 1.0, 0.5))


    # Draw players
    draw_circle(player1_x, player1_y, player_radius, (0.0, 0.0, 1.0))
    draw_circle(player2_x, player2_y, player_radius, (1.0, 0.0, 0.0))

    # Draw ball
    draw_circle(ball_x, ball_y, ball_size, (1.0, 1.0, 0.0))

    # Draw scores using points
    draw_number_with_points(-100, W_Height // 2 - 50, score1, scale=10)
    draw_number_with_points(50, W_Height // 2 - 50, score2, scale=10)
    draw_weather_effect()
    draw_wind_effect()
    draw_ability()
    draw_hard_kick()

    # Check for game over
    if game_over:
        glColor3f(1.0, 1.0, 1.0)
        draw_text(-100, 50, "Game Over!")
        draw_text(-120, 0, f"Player 1: {score1} | Player 2: {score2}")
        if score1 > score2:
            draw_text(-100, -50, "Player 1 Wins!")
        elif score2 > score1:
            draw_text(-100, -50, "Player 2 Wins!")
        else:
            draw_text(-100, -50, "It's a Tie!")
        glutSwapBuffers()
        return

    # Draw stamina as pixels
    draw_stamina1(-W_Width // 2 + 20, W_Height // 2 - 20, Player1_Stamina, max_stamina)
    draw_stamina2(W_Width // 2 - 100, W_Height // 2 - 20, Player2_Stamina, max_stamina)

    # Draw remaining time
    remaining_time = game_timer // 60  # Convert frames to seconds
    draw_text(-50, W_Height // 2 - 150, f"Time Left: {remaining_time}s")

    # Draw celebration message
    if celebration_timer > 0:
        if Last_Scorer == "Player2":
            draw_text(-50, 0, "Player2 Scores!")
        elif Last_Scorer == "Player1":
            draw_text(-50, 0, "Player1 Scores!")

    glutSwapBuffers()

# Update function
def update(value):
    global ball_x, ball_y, ball_dx, ball_dy, player1_x, player1_y, player2_x, player2_y
    global player1_dy, player2_dy, score1, score2, ability_y, ability_active, player1_boosted, player2_boosted
    global player1_speed, player2_speed, ability_fall_speed, wind_active, wind_strength, wind_direction
    global Player1_Stamina, Player2_Stamina, game_timer, game_over, celebration_timer, Last_Scorer
    global hard_kick_y, hard_kick_active, player1_hard_kick, player2_hard_kick

    if game_over:
        return

    # Update game timer
    game_timer -= 1
    if game_timer <= 0:
        game_over = True
        glutPostRedisplay()
        return

    # Apply gravity
    player1_dy -= g
    player2_dy -= g
    ball_dy -= g

    # Update player speed based on weather and boost
    effective_speed1 = player1_speed * (weather_speed_modifier if weather_active else 1)
    effective_speed2 = player2_speed * (weather_speed_modifier if weather_active else 1)

    # Update player 1 position
    player1_y += player1_dy
    if player1_y - player_radius <= ground_level:
        player1_y = ground_level + player_radius
        player1_dy = 0

    # Update player 2 position
    player2_y += player2_dy
    if player2_y - player_radius <= ground_level:
        player2_y = ground_level + player_radius
        player2_dy = 0

    # Update ball position
    ball_x += ball_dx
    ball_y += ball_dy

    # Ball collisions with ground
    if ball_y - ball_size <= ground_level:
        ball_y = ground_level + ball_size
        ball_dy = -ball_dy * 0.8  # Dampen the bounce

    # Ball collisions with players
    if check_collision(player1_x, player1_y, ball_x, ball_y, player_radius + ball_size):
        if ball_y > player1_y:  # Ball hits upper half of player 1
            ball_dy = abs(ball_dy) * (5 if player1_hard_kick else 1)
        else:  # Ball hits lower half of player 1
            ball_dy = -abs(ball_dy) * (5 if player1_hard_kick else 1)
        ball_dx = abs(ball_dx) * (5 if player1_hard_kick else 1)


    # Ball collisions with walls
    if ball_x - ball_size <= -W_Width // 2 or ball_x + ball_size >= W_Width // 2:
        ball_dx = -ball_dx

    # Player 1 movement
    if keys.get(b'w') and player1_y == ground_level + player_radius and Player1_Stamina > 0:
        player1_dy = jump_speed
        Player1_Stamina -= 1
    if keys.get(b'a'):
        player1_x -= effective_speed1
    if keys.get(b'd'):
        player1_x += effective_speed1

    # Player 2 movement
    if keys.get(b'i') and player2_y == ground_level + player_radius and Player2_Stamina > 0:
        player2_dy = jump_speed
        Player2_Stamina -= 1
    if keys.get(b'j'):
        player2_x -= effective_speed2
    if keys.get(b'l'):
        player2_x += effective_speed2

    # Constrain players within boundaries
    player1_x = max(-W_Width // 2 + player_radius, min(player1_x, W_Width // 2 - player_radius))
    player2_x = max(-W_Width // 2 + player_radius, min(player2_x, W_Width // 2 - player_radius))

    # Ball collisions with players
    if check_collision(player1_x, player1_y, ball_x, ball_y, player_radius + ball_size):
        ball_dx = abs(ball_dx) * (5 if player1_hard_kick else 1)
        ball_dy = jump_speed   # Harder hit
    if check_collision(player2_x, player2_y, ball_x, ball_y, player_radius + ball_size):
        ball_dx = -abs(ball_dx) * (5 if player2_hard_kick else 1)
        ball_dy = jump_speed

    # Check for goals
    if ball_x - ball_size <= -W_Width // 2:
        score2 += 1
        reset_ball()
        celebration_timer = celebration_duration
        Last_Scorer = "Player2"

    if ball_x + ball_size >= W_Width // 2:
        score1 += 1
        reset_ball()
        celebration_timer = celebration_duration
        Last_Scorer = "Player1"

    # Reduce celebration timer
    if celebration_timer > 0:
        celebration_timer -= 1

    # Regenerate stamina
    Player1_Stamina = min(Player1_Stamina + 0.005, max_stamina)
    Player2_Stamina = min(Player2_Stamina + 0.005, max_stamina)

    if wind_active:
        ball_dx += wind_direction * wind_strength * 0.1

    # Ability falls
    if ability_active:
        ability_y -= ability_fall_speed  # Fall speed
        if ability_y - ability_radius <= ground_level:
            ability_active = False

    if hard_kick_active:
        hard_kick_y -= hard_kick_fall_speed
        if hard_kick_y - hard_kick_radius <= ground_level:
            hard_kick_active = False

    if hard_kick_active:
        if check_collision(player1_x, player1_y, hard_kick_x, hard_kick_y, player_radius + hard_kick_radius):
            hard_kick_active = False
            player1_hard_kick = True
            glutTimerFunc(hard_kick_duration, reset_hard_kick, 1)
        elif check_collision(player2_x, player2_y, hard_kick_x, hard_kick_y, player_radius + hard_kick_radius):
            hard_kick_active = False
            player2_hard_kick = True
            glutTimerFunc(hard_kick_duration, reset_hard_kick, 2)

    # Check for player collision with the ability
    if ability_active:
        if check_collision(player1_x, player1_y, ability_x, ability_y, player_radius + ability_radius):
            ability_active = False
            player1_boosted = True
            player1_speed = boost_speed
            glutTimerFunc(boost_duration, reset_speed, 1)
        elif check_collision(player2_x, player2_y, ability_x, ability_y, player_radius + ability_radius):
            ability_active = False
            player2_boosted = True
            player2_speed = boost_speed
            glutTimerFunc(boost_duration, reset_speed, 2)

    # Trigger a redraw
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

def draw_weather_effect():
    if weather_active:
        glPushAttrib(GL_POINT_BIT)  # Save current point size
        glPointSize(1)  # Set point size to 1 for smaller wind pixels
        for _ in range(50):  # Draw random rain particles
            x = random.randint(-W_Width // 2, W_Width // 2)
            y = random.randint(-W_Height // 2, W_Height // 2)
            draw_line_midpoint(x, y, x, y - 10, color=(0.5, 0.5, 1.0))
        glPopAttrib()

def draw_wind_effect():
    if wind_active:
        glPushAttrib(GL_POINT_BIT)  # Save current point size
        glPointSize(0.1)  # Set point size to 1 for smaller wind pixels
        for _ in range(20):  # Draw lines to represent wind
            if wind_direction == 1:
                x_start = random.randint(-W_Width // 2, W_Width // 2 - 50)
                y_start = random.randint(-W_Height // 2, W_Height // 2)
                draw_line_midpoint(x_start, y_start, x_start + 50, y_start, color=(1.0, 1.0, 0.8))
            else:
                x_start = random.randint(-W_Width // 2 + 50, W_Width // 2)
                y_start = random.randint(-W_Height // 2, W_Height // 2)
                draw_line_midpoint(x_start, y_start, x_start - 50, y_start, color=(1.0, 1.0, 0.8))
        glPopAttrib()  # Restore previous point size

def toggle_wind(value):
    global wind_active, wind_direction
    wind_active = not wind_active
    wind_direction = random.choice([-1, 1])  # Randomize direction
    glutTimerFunc(wind_duration, toggle_wind, 0)  # Schedule wind deactivation


def draw_ability():
    if ability_active:
        draw_circle(ability_x, ability_y, ability_radius, (0.0, 1.0, 0.0))

def draw_hard_kick():
    if hard_kick_active:
        draw_circle(hard_kick_x, hard_kick_y, hard_kick_radius, (1.0, 0.0, 1.0))

def check_collision(x1, y1, x2, y2, combined_radius):
    distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
    return distance <= combined_radius

def toggle_weather():
    global weather_active
    weather_active = not weather_active  # Toggle weather state

def reset_ball():
    global ball_x, ball_y, ball_dx, ball_dy
    ball_x, ball_y = 0, 0
    ball_dx = random.choice([-4, 4])
    ball_dy = random.choice([-3, 3])

def spawn_ability(value):
    global ability_x, ability_y, ability_active
    if not ability_active:  # Only spawn a new ability if none is active
        ability_x = random.randint(-W_Width // 2 + ability_radius, W_Width // 2 - ability_radius)
        ability_y = W_Height // 2  # Start from the top
        ability_active = True

    glutTimerFunc(spawn_interval, spawn_ability, 0)  # Schedule the next spawn

def spawn_hard_kick(value):
    global hard_kick_x, hard_kick_y, hard_kick_active
    if not hard_kick_active:
        hard_kick_x = random.randint(-W_Width // 2 + hard_kick_radius, W_Width // 2 - hard_kick_radius)
        hard_kick_y = W_Height // 2
        hard_kick_active = True

    glutTimerFunc(hard_kick_spawn_interval, spawn_hard_kick, 0)

def reset_speed(player):
    global player1_boosted, player2_boosted, player1_speed, player2_speed
    if player == 1:
        player1_boosted = False
        player1_speed = 15  # Reset player 1's speed
    elif player == 2:
        player2_boosted = False
        player2_speed = 15  # Reset player 2's speed

def reset_hard_kick(player):
    global player1_hard_kick, player2_hard_kick
    if player == 1:
        player1_hard_kick = False
    elif player == 2:
        player2_hard_kick = False

def keyboard(key, x, y):
    global weather_active
    keys[key] = True
    if key == b'r':
        weather_active = not weather_active  # Toggle rain
        glutPostRedisplay()  # Update the display

def keyboard_up(key, x, y):
    keys[key] = False

def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-W_Width // 2, W_Width // 2, -W_Height // 2, W_Height // 2, -1, 1)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(W_Width, W_Height)
    glutCreateWindow(b"Head Soccer with Weather Effect")

    init()

    glutTimerFunc(spawn_interval, spawn_ability, 0)
    glutTimerFunc(hard_kick_spawn_interval, spawn_hard_kick, 0)
    glutTimerFunc(0, toggle_wind, 0)

    glutDisplayFunc(display)
    glutTimerFunc(16, update, 0)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)

    glutMainLoop()

if __name__ == "__main__":
    main()