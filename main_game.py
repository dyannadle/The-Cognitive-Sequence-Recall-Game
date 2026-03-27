import pygame
import requests # Still needed for score submission
from GameLogic import CogniQuestLogic
import random
import math
import time # Added for timer functionality

# --- Pygame Setup ---
pygame.init()
pygame.mixer.init() # Audio
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800 # Larger for more space
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cogni-Quest Elite")

# --- Fonts ---
FONT_LARGE = pygame.font.Font(None, 64)
FONT_MED = pygame.font.Font(None, 36)
FONT_SMALL = pygame.font.Font(None, 24)

# --- Themes ---
THEMES = {
    "CYBER": {
        "BG": (10, 14, 23),
        "TILE": (30, 40, 60),
        "FLASH": (0, 242, 254),
        "TEXT": (255, 255, 255),
        "ACCENT": (240, 147, 251)
    },
    "NEON": {
        "BG": (20, 0, 40),
        "TILE": (60, 0, 100),
        "FLASH": (255, 0, 255),
        "TEXT": (0, 255, 255),
        "ACCENT": (255, 255, 0)
    }
}
current_theme = THEMES["CYBER"]

# --- Particle System ---
particles = []

def create_particles(pos, color):
    for _ in range(15):
        particles.append({
            "pos": list(pos),
            "vel": [random.uniform(-3, 3), random.uniform(-3, 3)],
            "life": 1.0, # normalized life 1.0 -> 0.0
            "color": color
        })

def update_particles():
    for p in particles[:]:
        p["pos"][0] += p["vel"][0]
        p["pos"][1] += p["vel"][1]
        p["life"] -= 0.02
        if p["life"] <= 0:
            particles.remove(p)

def draw_particles(screen):
    for p in particles:
        p_life = p["life"]
        p_pos = p["pos"]
        p_color = p["color"]
        alpha = int(p_life * 255)
        s = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(s, (*p_color, alpha), (4, 4), 3)
        screen.blit(s, (int(p_pos[0]-4), int(p_pos[1]-4)))

# --- Audio Setup ---
def play_sound(freq, duration=100):
    try:
        sample_rate = 44100
        n_samples = int(sample_rate * (duration / 1000.0))
        # Use a simpler sine wave with better amplitude scaling
        import array
        buf = array.array('h', [int(16384 * math.sin(2 * math.pi * freq * i / sample_rate)) for i in range(n_samples)])
        sound = pygame.mixer.Sound(buffer=buf)
        sound.play()
    except Exception as e:
        pass 

# --- Grid setup ---
GRID_SIZE = 4
TILE_SIZE = 120
GRID_START_X = (SCREEN_WIDTH - (GRID_SIZE * TILE_SIZE)) // 2
GRID_START_Y = (SCREEN_HEIGHT - (GRID_SIZE * TILE_SIZE)) // 2
TILE_RECTS = []
for i in range(GRID_SIZE * GRID_SIZE):
    row, col = divmod(i, GRID_SIZE)
    rect = pygame.Rect(GRID_START_X + col * TILE_SIZE, 
                       GRID_START_Y + row * TILE_SIZE, 
                       TILE_SIZE, TILE_SIZE)
    TILE_RECTS.append(rect)

shake_intensity = 0

def draw_grid(screen, is_flashing=False, flashing_tile_index=-1, flash_color=None):
    if flash_color is None: flash_color = current_theme["FLASH"]
    
    offset_x = random.randint(-shake_intensity, shake_intensity)
    offset_y = random.randint(-shake_intensity, shake_intensity)

    for i, rect in enumerate(TILE_RECTS):
        draw_rect = rect.move(offset_x, offset_y)
        color = current_theme["TILE"]
        
        # Hover effect
        if rect.collidepoint(pygame.mouse.get_pos()):
            color = tuple(min(255, c + 30) for c in color)

        if is_flashing and i == flashing_tile_index:
            color = flash_color
            # Draw a glow
            for s in range(5, 25, 5):
                glow_rect = draw_rect.inflate(s, s)
                pygame.draw.rect(screen, (*color, 50-s*2), glow_rect, border_radius=10)
        
        pygame.draw.rect(screen, color, draw_rect, border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255, 30), draw_rect, 2, border_radius=12) # Subtle border
        
        text = FONT_SMALL.render(str(i), True, (255, 255, 255, 100))
        screen.blit(text, text.get_rect(center=draw_rect.center))

def get_clicked_tile_index(pos):
    """Maps mouse click position to tile index."""
    for i, rect in enumerate(TILE_RECTS):
        if rect.collidepoint(pos):
            return i
    return -1

def main_loop():
    global shake_intensity, current_theme
    game = CogniQuestLogic()
    running = True
    state = "SHOWING_SEQUENCE"
    player_input = []
    score_submitted = False
    
    input_start_time = 0
    INPUT_LIMIT = 5 # seconds
    
    while running:
        screen.fill(current_theme["BG"])
        
        # Access global shake_intensity correctly
        global shake_intensity
        if shake_intensity > 0: shake_intensity -= 1
        
        # --- Handle Pygame Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if state == "AWAITING_INPUT" and event.type == pygame.MOUSEBUTTONDOWN:
                clicked_tile_index = get_clicked_tile_index(event.pos)
                if clicked_tile_index != -1:
                    player_input.append(clicked_tile_index)
                    create_particles(event.pos, current_theme["FLASH"])
                    play_sound(440 + clicked_tile_index * 20, 50)
                    
                    if game.current_mode == "PREDICT":
                        if len(player_input) == 1:
                            if game.check_player_input(player_input):
                                state = "SHOWING_SEQUENCE"
                                play_sound(880, 200)
                            else:
                                shake_intensity = 15
                                play_sound(200, 300)
                                if game.lives <= 0: state = "GAME_OVER"
                                else: state = "SHOWING_SEQUENCE"
                    
                    elif len(player_input) == len(game.correct_target_sequence):
                        if game.check_player_input(player_input):
                            state = "SHOWING_SEQUENCE"
                            play_sound(880, 200)
                        else:
                            shake_intensity = 15
                            play_sound(200, 300)
                            if game.lives <= 0: state = "GAME_OVER"
                            else: state = "SHOWING_SEQUENCE"

            # Power-up keys
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: 
                    if game.use_powerup("SHIELD"): print("SHIELD ACTIVATED!")
                if event.key == pygame.K_2: 
                    if game.use_powerup("SLOW_MO"): print("SLOW-MO ACTIVATED!")
                if event.key == pygame.K_t: # Toggle Theme
                    current_theme = THEMES["NEON"] if current_theme == THEMES["CYBER"] else THEMES["CYBER"]

        # --- Game State Logic ---
        if state == "SHOWING_SEQUENCE":
            current_sequence, speed = game.generate_next_sequence()
            
            # Show Mode Intro
            screen.fill(current_theme["BG"])
            msg = f"MODE: {game.current_mode}"
            if game.current_mode == "TRANSFORM": msg += f" ({game.transformation_rule})"
            text = FONT_LARGE.render(msg, True, current_theme["ACCENT"])
            screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
            pygame.display.flip()
            pygame.time.wait(1500)

            # Flash sequence
            if game.current_mode == "DOUBLE":
                # Flash in pairs
                for i in range(0, len(current_sequence), 2):
                    screen.fill(current_theme["BG"])
                    t1 = current_sequence[i]
                    t2 = current_sequence[i+1] if i+1 < len(current_sequence) else t1
                    
                    draw_grid(screen, is_flashing=True, flashing_tile_index=t1)
                    draw_grid(screen, is_flashing=True, flashing_tile_index=t2)
                    
                    play_sound(440 + t1 * 20, 100)
                    play_sound(440 + t2 * 20, 100)
                    pygame.display.flip()
                    pygame.time.wait(int(speed * 600))
                    
                    screen.fill(current_theme["BG"])
                    draw_grid(screen)
                    pygame.display.flip()
                    pygame.time.wait(100)
            else:
                # Normal single flash
                for tile_index in current_sequence:
                    screen.fill(current_theme["BG"])
                    draw_grid(screen, is_flashing=True, flashing_tile_index=tile_index)
                    play_sound(440 + tile_index * 20, 100)
                    pygame.display.flip()
                    pygame.time.wait(int(speed * 600))
                    
                    screen.fill(current_theme["BG"])
                    draw_grid(screen)
                    pygame.display.flip()
                    pygame.time.wait(100)
            
            state = "AWAITING_INPUT"
            player_input = []
            input_start_time = time.time()
            
        # --- UI Rendering ---
        draw_grid(screen)
        update_particles()
        draw_particles(screen)
        
        # Stats Bar
        pygame.draw.rect(screen, (30, 30, 40), (0, 0, SCREEN_WIDTH, 60))
        score_text = FONT_MED.render(f"SCORE: {game.score}", True, (255, 255, 255))
        lives_text = FONT_MED.render(f"LIVES: {'❤️' * game.lives}", True, (255, 100, 100))
        mult_text = FONT_MED.render(f"COMBO: x{game.combo_multiplier}", True, current_theme["ACCENT"])
        
        screen.blit(score_text, (20, 15))
        screen.blit(lives_text, (SCREEN_WIDTH // 2 - 50, 15))
        screen.blit(mult_text, (SCREEN_WIDTH - 200, 15))

        # Power-ups bar
        p_msg = f"[1] SHIELD ({game.powerups['SHIELD']})  [2] SLOW-MO ({game.powerups['SLOW_MO']})  [T] THEME"
        p_text = FONT_SMALL.render(p_msg, True, (150, 150, 150))
        screen.blit(p_text, (20, SCREEN_HEIGHT - 30))

        if state == "AWAITING_INPUT":
            # Timer bar
            elapsed = time.time() - input_start_time
            timer_w = max(0, SCREEN_WIDTH - int((elapsed / INPUT_LIMIT) * SCREEN_WIDTH))
            pygame.draw.rect(screen, current_theme["FLASH"], (0, 60, timer_w, 5))
            if elapsed > INPUT_LIMIT:
                game.lives -= 1
                shake_intensity = 15
                state = "SHOWING_SEQUENCE"

        elif state == "GAME_OVER":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0,0))
            
            over_text = FONT_LARGE.render("MISSION FAILED", True, (255, 0, 0))
            final_score = FONT_MED.render(f"FINAL SCORE: {game.score}", True, (255, 255, 255))
            exit_text = FONT_SMALL.render("Press ESC to Exit", True, (150, 150, 150))
            
            screen.blit(over_text, over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)))
            screen.blit(final_score, final_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)))
            screen.blit(exit_text, exit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)))
            
            if not score_submitted:
                try:
                    # Submit with unique player name for 'Elite' version
                    requests.post('http://127.0.0.1:5000/api/submit_score', 
                                  json={'player_id': 'Elite_Agent', 'score': game.score}, 
                                  timeout=2)
                    score_submitted = True
                except requests.exceptions.RequestException:
                    print("Could not connect to Flask backend. Score not saved.")
                    score_submitted = True # Don't retry every frame if it fails
            
            # Check for ESC key press to quit in GAME_OVER state
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                 running = False

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
   main_loop()
