import pygame # Import the core Pygame library for windowing and rendering
import requests # Import requests for sending HTTP POST scores to the Flask backend
from GameLogic import CogniQuestLogic # Import the game scaling and rules logic class
import random # Import random for visual effects and mode selection
import math # Import math for sine wave generation in the synth audio
import time # Import time for delta-time and input speed checking

# --- Pygame Setup ---
pygame.init() # Initialize all imported pygame modules (font, display, etc.)
pygame.mixer.init() # Specifically initialize the mixer for audio handling
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800 # Define screen resolution (1000x800)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # Create the game window surface
pygame.display.set_caption("Cogni-Quest Elite") # Set the text in the window title bar

# --- Fonts ---
FONT_LARGE = pygame.font.Font(None, 64) # Load a large default font (size 64) for headings
FONT_MED = pygame.font.Font(None, 36) # Load a medium default font (size 36) for UI labels
FONT_SMALL = pygame.font.Font(None, 24) # Load a small default font (size 24) for subtext

# --- Themes ---
THEMES = { # Dictionary containing color palettes for the game's visual styles
    "CYBER": { # Hues of blue/navy for a hi-tech feel
        "BG": (10, 14, 23), # Dark background color
        "TILE": (30, 40, 60), # Base color for the grid tiles
        "FLASH": (0, 242, 254), # Bright cyan for sequence flashes
        "TEXT": (255, 255, 255), # Pure white for text readability
        "ACCENT": (240, 147, 251) # Neon pink for highlights
    },
    "NEON": { # Purple/magenta palette for a retro-neon look
        "BG": (20, 0, 40), # Deep purple background
        "TILE": (60, 0, 100), # Purple tiles
        "FLASH": (255, 0, 255), # Magenta flash
        "TEXT": (0, 255, 255), # Cyan text
        "ACCENT": (255, 255, 0) # Bright yellow accent
    }
}
current_theme = THEMES["CYBER"] # Initialize the game with the CYBER theme by default

# --- Particle System ---
particles = [] # List to manage active particle objects for visual 'juice'

def create_particles(pos, color): # Function to spawn a burst of particles at a specific position
    for _ in range(15): # Loop to create 15 individual particles per burst
        particles.append({ # Add a new particle dictionary to the list
            "pos": list(pos), # Initial (x, y) coordinates of the particle
            "vel": [random.uniform(-3, 3), random.uniform(-3, 3)], # Random initial velocity (x, y)
            "life": 1.0, # Initial life value (1.0 = fully alive, 0.0 = dead)
            "color": color # The RGB color of the particle (usually matches the theme flash/accent)
        })

def update_particles(): # Function to simulate particle movement and aging
    for p in particles[:]: # Iterate over a copy of the list to allow safe removal during the loop
        p["pos"][0] += p["vel"][0] # Update x position based on velocity
        p["pos"][1] += p["vel"][1] # Update y position based on velocity
        p["life"] -= 0.02 # Decrease life value each frame (aging process)
        if p["life"] <= 0: # If the particle is aged out
            particles.remove(p) # Remove it from the active list

def draw_particles(screen): # Function to render particles onto the screen surface
    for p in particles: # Loop through every active particle
        p_life = p["life"] # Get current life (used for alpha)
        p_pos = p["pos"] # Get current position
        p_color = p["color"] # Get constant color
        alpha = int(p_life * 255) # Map 0.0-1.0 life to 0-255 transparency
        s = pygame.Surface((8, 8), pygame.SRCALPHA) # Create a small surface with per-pixel alpha support
        pygame.draw.circle(s, (*p_color, alpha), (4, 4), 3) # Draw a semi-transparent colored circle
        screen.blit(s, (int(p_pos[0]-4), int(p_pos[1]-4))) # Blit the particle at its centered position

# --- Audio Setup ---
def play_sound(freq, duration=100): # Function to generate and play a synth-like sine wave beep
    try: # Begin a try block to handle potential audio device failures
        sample_rate = 44100 # CD quality sample rate (44.1kHz)
        n_samples = int(sample_rate * (duration / 1000.0)) # Total number of audio samples based on duration
        # Generates a sine wave buffer at the specified frequency
        import array # Import array module locally for high-performance sound buffer management
        buf = array.array('h', [int(16384 * math.sin(2 * math.pi * freq * i / sample_rate)) for i in range(n_samples)])
        sound = pygame.mixer.Sound(buffer=buf) # Convert the raw buffer into a Pygame Sound object
        sound.play() # Trigger the sound playback
    except Exception as e: # Catch any sound errors (e.g., driver issues)
        pass # Silently ignore sound failures

# --- Grid setup ---
GRID_SIZE = 4 # Define the number of rows and columns (constant 4x4)
TILE_SIZE = 120 # Width and height of each individual tile in pixels
GRID_START_X = (SCREEN_WIDTH - (GRID_SIZE * TILE_SIZE)) // 2 # Calculate x-offset to center the grid horizontally
GRID_START_Y = (SCREEN_HEIGHT - (GRID_SIZE * TILE_SIZE)) // 2 # Calculate y-offset to center the grid vertically
TILE_RECTS = [] # List to store pygame.Rect objects for collision and drawing
for i in range(GRID_SIZE * GRID_SIZE): # Loop 16 times to create all grid tiles
    row, col = divmod(i, GRID_SIZE) # Convert index (0-15) to 2D grid coordinates (row, col)
    rect = pygame.Rect(GRID_START_X + col * TILE_SIZE, # Calculate tile's top-left x coordinate
                       GRID_START_Y + row * TILE_SIZE, # Calculate tile's top-left y coordinate
                       TILE_SIZE, TILE_SIZE) # Set dimensions (120x120)
    TILE_RECTS.append(rect) # Store the rectangle object for later use

shake_intensity = 0 # Global variable to track screen shake amplitude (0 = no shake)

def draw_grid(screen, is_flashing=False, flashing_tile_index=-1, flash_color=None): # Primary grid rendering function
    if flash_color is None: flash_color = current_theme["FLASH"] # Default to theme's flash color if not specified
    
    # Calculate a random offset for the screen shake effect
    offset_x = random.randint(-shake_intensity, shake_intensity) # Random horizontal displacement
    offset_y = random.randint(-shake_intensity, shake_intensity) # Random vertical displacement

    for i, rect in enumerate(TILE_RECTS): # Iterate through every tile in the grid
        draw_rect = rect.move(offset_x, offset_y) # Apply the shake offset to the current tile
        color = current_theme["TILE"] # Start with the base tile color from the theme
        
        # Hover effect: light up the tile if the mouse cursor is over it
        if rect.collidepoint(pygame.mouse.get_pos()): # Check if mouse position is within the tile
            color = tuple(min(255, c + 30) for c in color) # Brighten the color slightly

        if is_flashing and i == flashing_tile_index: # If this specific tile should flash right now
            color = flash_color # Use the bright flash color
            # Draw a glowing pulse effect around the tile
            for s in range(5, 25, 5): # Create 4 expanding glow layers
                glow_rect = draw_rect.inflate(s, s) # Inflate the rectangle outward
                pygame.draw.rect(screen, (*color, 50-s*2), glow_rect, border_radius=10) # Draw faint glow
        
        pygame.draw.rect(screen, color, draw_rect, border_radius=12) # Draw the main colored tile body
        pygame.draw.rect(screen, (255, 255, 255, 30), draw_rect, 2, border_radius=12) # Draw a subtle white border
        
        # Render the tile index number in the center for player guidance
        text = FONT_SMALL.render(str(i), True, (255, 255, 255, 100)) # Create a semi-transparent text surface
        screen.blit(text, text.get_rect(center=draw_rect.center)) # Center the text and draw it on the screen

def get_clicked_tile_index(pos): # Utility function to convert mouse click coordinates to a grid index
    """Maps mouse click position to tile index."""
    for i, rect in enumerate(TILE_RECTS): # Check each tile's rectangle
        if rect.collidepoint(pos): # If the click was inside this tile
            return i # Return the index (0-15)
    return -1 # Return -1 if no tile was clicked

def main_loop(): # The core function that runs the entire game experience
    global shake_intensity, current_theme # Access global variables for modification within the loop
    game = CogniQuestLogic() # Instantiate the game logic controller
    running = True # Boolean flag to keep the game loop active
    state = "SHOWING_SEQUENCE" # Initial game state: showing the pattern to the user
    player_input = [] # List to track the tiles the player clicks during their turn
    score_submitted = False # Flag to ensure the score is only sent to the backend once per game
    
    input_start_time = 0 # Timestamp for when the player starts their input phase
    INPUT_LIMIT = 5 # Maximum allowed time (in seconds) for the player to complete their input
    
    while running: # Main game loop start
        screen.fill(current_theme["BG"]) # Clear the screen with the current theme's background color
        
        # Access global shake_intensity correctly
        global shake_intensity # Re-declare global to ensure modification access
        if shake_intensity > 0: shake_intensity -= 1 # Gradually decay the screen shake each frame
        
        # --- Handle Pygame Events ---
        for event in pygame.event.get(): # Iterate through all events captured by Pygame (clicks, keys, etc.)
            if event.type == pygame.QUIT: # If the user clicks the 'X' to close the window
                running = False # Set running to False to exit the loop
            
            if state == "AWAITING_INPUT" and event.type == pygame.MOUSEBUTTONDOWN: # During the player's turn
                clicked_tile_index = get_clicked_tile_index(event.pos) # Get which tile (if any) was clicked
                if clicked_tile_index != -1: # If a valid tile was clicked
                    player_input.append(clicked_tile_index) # Record the tile index
                    create_particles(event.pos, current_theme["FLASH"]) # Spawn visual particles at click site
                    play_sound(440 + clicked_tile_index * 20, 50) # Play a unique beep for the clicked tile
                    
                    if game.current_mode == "PREDICT": # Special logic for the one-click PREDICT mode
                        if len(player_input) == 1: # Once the user has made their single prediction
                            if game.check_player_input(player_input): # Validate with logic class
                                state = "SHOWING_SEQUENCE" # Success: go to next round
                                play_sound(880, 200) # Play a 'correct' sound
                            else: # If the prediction was wrong
                                shake_intensity = 15 # Trigger strong screen shake
                                play_sound(200, 300) # Play a 'wrong' sound
                                if game.lives <= 0: state = "GAME_OVER" # Check if out of lives
                                else: state = "SHOWING_SEQUENCE" # Still have lives: try again
                    
                    elif len(player_input) == len(game.correct_target_sequence): # For RECALL/TRANSFORM modes
                        if game.check_player_input(player_input): # Check if the full entered list is correct
                            state = "SHOWING_SEQUENCE" # Success: go to next round
                            play_sound(880, 200) # Play success sound
                        else: # If any part of the sequence was wrong
                            shake_intensity = 15 # Trigger screen shake
                            play_sound(200, 300) # Play failure sound
                            if game.lives <= 0: state = "GAME_OVER" # Check for game over
                            else: state = "SHOWING_SEQUENCE" # Regenerate sequence if lives remain

            # Power-up keys
            if event.type == pygame.KEYDOWN: # Handle keyboard presses for game utilities
                if event.key == pygame.K_1: # Key '1' for Shield power-up
                    if game.use_powerup("SHIELD"): print("SHIELD ACTIVATED!") # Use if available
                if event.key == pygame.K_2: # Key '2' for Slow-Mo power-up
                    if game.use_powerup("SLOW_MO"): print("SLOW-MO ACTIVATED!") # Use if available
                if event.key == pygame.K_t: # Key 'T' to toggle visual themes
                    current_theme = THEMES["NEON"] if current_theme == THEMES["CYBER"] else THEMES["CYBER"]

        # --- Game State Logic ---
        if state == "SHOWING_SEQUENCE": # If the game is currently in the presentation phase
            current_sequence, speed = game.generate_next_sequence() # Request a new sequence and speed from logic
            
            # Show Mode Intro: Display a temporary text overlay explaining the upcoming round
            screen.fill(current_theme["BG"]) # Clear to background
            msg = f"MODE: {game.current_mode}" # Prepare the mode name (e.g., RECALL)
            if game.current_mode == "TRANSFORM": msg += f" ({game.transformation_rule})" # Add rule if in TRANSFORM
            text = FONT_LARGE.render(msg, True, current_theme["ACCENT"]) # Render the text in accent color
            screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))) # Center on screen
            pygame.display.flip() # Update the display to show the message
            pygame.time.wait(1500) # Pause for 1.5 seconds so the player can read the mode

            # Flash sequence: The core visualization loop for the pattern
            if game.current_mode == "DOUBLE": # Special simultaneous flash for DOUBLE mode
                # Flash in pairs (t1 and t2 together)
                for i in range(0, len(current_sequence), 2): # Iterate through sequence in steps of 2
                    screen.fill(current_theme["BG"]) # Clear screen
                    t1 = current_sequence[i] # First tile of the pair
                    t2 = current_sequence[i+1] if i+1 < len(current_sequence) else t1 # Second tile (or repeat first if odd)
                    
                    draw_grid(screen, is_flashing=True, flashing_tile_index=t1) # Draw grid with t1 illuminated
                    draw_grid(screen, is_flashing=True, flashing_tile_index=t2) # Draw grid with t2 illuminated
                    
                    play_sound(440 + t1 * 20, 100) # Play beep for t1
                    play_sound(440 + t2 * 20, 100) # Play beep for t2
                    pygame.display.flip() # Update screen to show the double flash
                    pygame.time.wait(int(speed * 600)) # Wait based on current speed
                    
                    screen.fill(current_theme["BG"]) # Clear screen
                    draw_grid(screen) # Draw the empty grid (tiles off)
                    pygame.display.flip() # Update screen
                    pygame.time.wait(100) # Brief pause between flashes
            else: # Standard single-tile flash for all other modes
                # Normal single flash
                for tile_index in current_sequence: # Iterate through each index in the sequence
                    screen.fill(current_theme["BG"]) # Clear screen
                    draw_grid(screen, is_flashing=True, flashing_tile_index=tile_index) # Draw with specific tile lit
                    play_sound(440 + tile_index * 20, 100) # Play the tile's unique pitch
                    pygame.display.flip() # Update screen
                    pygame.time.wait(int(speed * 600)) # Wait based on difficulty speed
                    
                    screen.fill(current_theme["BG"]) # Clear screen
                    draw_grid(screen) # Draw default grid (all off)
                    pygame.display.flip() # Update screen
                    pygame.time.wait(100) # Small delay before the next tile
            
            state = "AWAITING_INPUT" # Transition to the player's turn
            player_input = [] # Reset player's input buffer
            input_start_time = time.time() # Start the countdown timer for input
            
        # --- UI Rendering ---
        draw_grid(screen) # Draw the main 4x4 interactive grid
        update_particles() # Advance the simulation of any active particles
        draw_particles(screen) # Render the particles on top of the grid
        
        # Stats Bar: A dark strip at the top to display game information
        pygame.draw.rect(screen, (30, 30, 40), (0, 0, SCREEN_WIDTH, 60)) # Draw horizontal bar background
        score_text = FONT_MED.render(f"SCORE: {game.score}", True, (255, 255, 255)) # Prepare score text
        lives_text = FONT_MED.render(f"LIVES: {'❤️' * game.lives}", True, (255, 100, 100)) # Prepare heart emojis for lives
        mult_text = FONT_MED.render(f"COMBO: x{game.combo_multiplier}", True, current_theme["ACCENT"]) # Prepare multiplier text
        
        screen.blit(score_text, (20, 15)) # Position score at top-left
        screen.blit(lives_text, (SCREEN_WIDTH // 2 - 50, 15)) # Position lives in the center
        screen.blit(mult_text, (SCREEN_WIDTH - 200, 15)) # Position combo multiplier at top-right

        # Power-ups bar: Instructional text at the bottom of the screen
        p_msg = f"[1] SHIELD ({game.powerups['SHIELD']})  [2] SLOW-MO ({game.powerups['SLOW_MO']})  [T] THEME"
        p_text = FONT_SMALL.render(p_msg, True, (150, 150, 150)) # Render help text in grey
        screen.blit(p_text, (20, SCREEN_HEIGHT - 30)) # Draw at the very bottom edge

        if state == "AWAITING_INPUT": # While waiting for the user to copy the pattern
            # Timer bar: A shrinking horizontal line indicating time remaining
            elapsed = time.time() - input_start_time # Calculate seconds since turn start
            timer_w = max(0, SCREEN_WIDTH - int((elapsed / INPUT_LIMIT) * SCREEN_WIDTH)) # Shrink width over time
            pygame.draw.rect(screen, current_theme["FLASH"], (0, 60, timer_w, 5)) # Draw the colored timer bar
            if elapsed > INPUT_LIMIT: # If time runs out
                game.lives -= 1 # Penalize the player
                shake_intensity = 15 # Visual feedback for failure
                state = "SHOWING_SEQUENCE" # Force a new sequence generation

        elif state == "GAME_OVER": # If the player has lost all lives
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA) # Create a full-screen surface
            overlay.fill((0, 0, 0, 200)) # Fill with semi-transparent black for a 'dimming' effect
            screen.blit(overlay, (0,0)) # Draw the overlay
            
            over_text = FONT_LARGE.render("MISSION FAILED", True, (255, 0, 0)) # Main game over heading
            final_score = FONT_MED.render(f"FINAL SCORE: {game.score}", True, (255, 255, 255)) # Display final points
            exit_text = FONT_SMALL.render("Press ESC to Exit", True, (150, 150, 150)) # Exit instructions
            
            screen.blit(over_text, over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))) # Center heading
            screen.blit(final_score, final_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))) # Center score
            screen.blit(exit_text, exit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))) # Center instruction
            
            if not score_submitted: # One-time submission to the backend
                try: # Handle potential network errors gracefully
                    # Submit with unique player name for 'Elite' version
                    requests.post('http://127.0.0.1:5000/api/submit_score', 
                                  json={'player_id': 'Elite_Agent', 'score': game.score}, 
                                  timeout=2) # Timeout after 2 seconds to prevent game hang
                    score_submitted = True # Mark as done to avoid spamming the API
                except requests.exceptions.RequestException: # If the backend is offline
                    print("Could not connect to Flask backend. Score not saved.") # Local log
                    score_submitted = True # Don't retry every frame if it fails
            
            # Check for ESC key press to quit in GAME_OVER state
            keys = pygame.key.get_pressed() # Get current state of all keyboard keys
            if keys[pygame.K_ESCAPE]: # If the Escape key is held down
                 running = False # Exit the main while loop

        pygame.display.flip() # Perform the final buffer swap to show everything to the user

    pygame.quit() # De-initialize pygame and close the window

if __name__ == '__main__': # Traditional Python entry point
   main_loop() # Start the game execution
