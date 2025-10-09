import pygame
import requests # Still needed for score submission
from GameLogic import CogniQuestLogic 

# --- Pygame Setup (Same as before) ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cogni-Quest Advanced")

FONT_LARGE = pygame.font.Font(None, 48)
FONT_SMALL = pygame.font.Font(None, 24)

# Colors and Grid setup (Same as before)
TILE_COLORS = [(255,0,0), (0,255,0), (0,0,255), (255,255,0)] # Example colors
GRID_SIZE = 4
TILE_SIZE = 100
GRID_START_X = (SCREEN_WIDTH - (GRID_SIZE * TILE_SIZE)) // 2
GRID_START_Y = (SCREEN_HEIGHT - (GRID_SIZE * TILE_SIZE)) // 2
TILE_RECTS = []
for i in range(GRID_SIZE * GRID_SIZE):
    row, col = divmod(i, GRID_SIZE)
    rect = pygame.Rect(GRID_START_X + col * TILE_SIZE, 
                       GRID_START_Y + row * TILE_SIZE, 
                       TILE_SIZE, TILE_SIZE)
    TILE_RECTS.append(rect)

def draw_grid(screen, is_flashing=False, flashing_tile_index=-1, flash_color=(255,255,255)):
    """Draws the 4x4 grid."""
    for i, rect in enumerate(TILE_RECTS):
        color = TILE_COLORS[i % len(TILE_COLORS)]
        
        if is_flashing and i == flashing_tile_index:
            color = flash_color # Use a bright color when flashing
        
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (50, 50, 50), rect, 3) # Border
        
        # Display tile index for 'TILE_SORT' visibility
        text = FONT_SMALL.render(str(i), True, (0, 0, 0))
        screen.blit(text, text.get_rect(center=rect.center))

def show_sequence(screen, sequence, speed):
    """Flashes the sequence."""
    for tile_index in sequence:
        draw_grid(screen, is_flashing=True, flashing_tile_index=tile_index)
        pygame.display.flip()
        pygame.time.wait(int(speed * 1000))
        draw_grid(screen) # Turn the tile off
        pygame.display.flip()
        pygame.time.wait(200) 

def get_clicked_tile_index(pos):
    """Maps mouse click position to tile index."""
    for i, rect in enumerate(TILE_RECTS):
        if rect.collidepoint(pos):
            return i
    return -1

def main_loop():
    game = CogniQuestLogic()
    running = True
    state = "SHOWING_SEQUENCE" # SHOWING_SEQUENCE, AWAITING_INPUT, GAME_OVER
    player_input = []
    
    while running:
        # --- Handle Pygame Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if state == "AWAITING_INPUT" and event.type == pygame.MOUSEBUTTONDOWN:
                clicked_tile_index = get_clicked_tile_index(event.pos)
                
                if clicked_tile_index != -1:
                    player_input.append(clicked_tile_index)
                    
                    # --- Check Input based on Mode ---
                    
                    if game.current_mode == "PREDICT":
                        # In PREDICT mode, only one click is allowed
                        if len(player_input) == 1:
                            if game.check_player_input(player_input):
                                state = "SHOWING_SEQUENCE"
                                print(f"Prediction Correct! Score: {game.score}")
                            else:
                                state = "GAME_OVER"
                                print(f"Prediction Failed! Final Score: {game.score}")
                    
                    elif len(player_input) == len(game.correct_target_sequence):
                        # RECALL or TRANSFORM full sequence entered
                        if game.check_player_input(player_input):
                            state = "SHOWING_SEQUENCE"
                            print(f"Sequence Correct! Score: {game.score}")
                        else:
                            state = "GAME_OVER"
                            print(f"Sequence Failed! Final Score: {game.score}")
                    
        # --- Game State Logic ---
        if state == "SHOWING_SEQUENCE":
            current_sequence, speed = game.generate_next_sequence()
            
            # Display instructions before the flash
            screen.fill((0, 0, 0))
            instruction_text = ""
            if game.current_mode == "RECALL":
                instruction_text = "Watch the sequence and repeat it."
            elif game.current_mode == "TRANSFORM":
                instruction_text = f"RULE: {game.TRANSFORM_RULES[game.transformation_rule]}"
            elif game.current_mode == "PREDICT":
                instruction_text = "Watch the pattern and PREDICT the NEXT tile."
                
            text = FONT_LARGE.render(instruction_text, True, (255, 255, 255))
            screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, 50)))
            draw_grid(screen)
            pygame.display.flip()
            pygame.time.wait(2000) # Give 2 seconds to read the rule

            # Show the sequence (only part of it in PREDICT mode)
            show_sequence(screen, current_sequence, speed)
            
            # Transition to input state
            state = "AWAITING_INPUT"
            player_input = []
            
        # --- Drawing and Updates ---
        screen.fill((0, 0, 0)) 
        draw_grid(screen) 
        
        # Display current game information
        mode_text = FONT_SMALL.render(f"MODE: {game.current_mode}", True, (0, 255, 255))
        score_text = FONT_LARGE.render(f"SCORE: {game.score}", True, (255, 255, 255))
        
        screen.blit(mode_text, (10, 10))
        screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 10, 10))

        # Re-display instructions during input phase
        if state == "AWAITING_INPUT":
            if game.current_mode == "TRANSFORM":
                 rule_text = FONT_SMALL.render(f"Rule: {game.TRANSFORM_RULES[game.transformation_rule]}", True, (255, 100, 100))
                 screen.blit(rule_text, rule_text.get_rect(center=(SCREEN_WIDTH // 2, 50)))
            elif game.current_mode == "PREDICT":
                 predict_text = FONT_LARGE.render("CLICK YOUR PREDICTION NOW!", True, (255, 200, 0))
                 screen.blit(predict_text, predict_text.get_rect(center=(SCREEN_WIDTH // 2, 50)))
            else:
                 input_prompt = FONT_SMALL.render(f"Enter Tile {len(player_input) + 1} of {len(game.correct_target_sequence)}", True, (255, 255, 255))
                 screen.blit(input_prompt, input_prompt.get_rect(center=(SCREEN_WIDTH // 2, 50)))

        elif state == "GAME_OVER":
            over_text = FONT_LARGE.render("GAME OVER! Press ESC to Exit.", True, (255, 0, 0))
            score_final = FONT_LARGE.render(f"FINAL SCORE: {game.score}", True, (255, 255, 255))
            screen.blit(over_text, over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)))
            screen.blit(score_final, score_final.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)))
            
            # Check for ESC key press to quit in GAME_OVER state
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                 running = False
            
            # Submit score to Flask backend (uncomment when running backend)
            # requests.post('http://localhost:5000/api/submit_score', json={'player_id': 'Player1', 'score': game.score})

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
   main_loop()
