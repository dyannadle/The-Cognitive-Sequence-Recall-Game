import random # Import the random module for generating sequences and selecting rules
import time # Import the time module for potential time-based logic

class CogniQuestLogic: # Define the main logic class for the Cogni-Quest game
    def __init__(self, grid_size=4): # Initialize the game logic with a default grid size of 4x4
        self.grid_size = grid_size # Store the grid size (4)
        self.tile_count = grid_size * grid_size # Calculate total number of tiles (16)
        self.score = 0 # Initialize player's current score to zero
        self.max_score = 0 # Variable to track the player's highest score in the session
        self.current_sequence = [] # List to store the current sequence of tile indices to flash
        self.base_speed = 1.0 # Initial time (in seconds) between tile flashes
        
        # New State Variables for Advanced Modes
        self.current_mode = "RECALL" # Current game mode (RECALL, TRANSFORM, PREDICT, MIRROR, DOUBLE)
        self.correct_target_sequence = [] # The actual sequence the player must input to win the round
        self.transformation_rule = "" # Initialize as empty string; stores the current active rule
        
        # New Mechanics
        self.lives = 3 # Player starts with 3 lives
        self.combo_multiplier = 1.0 # Multiplier for the score, increases with consecutive successes
        self.consecutive_correct = 0 # Counts how many rounds have been won in a row
        self.powerups = {"SHIELD": 0, "SLOW_MO": 0, "HINT": 0} # Dictionary to track available power-up counts
        self.active_slow_mo = False # Flag to indicate if the slow-motion power-up is active for this round
        self.shield_active = False # Flag to indicate if the shield power-up is shielding the player
        self.last_predicted_tile = -1 # Stores the omitted tile for the PREDICT mode checking

        # Define Transformation Rules
        self.TRANSFORM_RULES = { # Dictionary mapping rule keys to human-readable instructions
            "REVERSE": "Recall the sequence in reverse order.", # Rule to input the sequence backwards
            "ODD_EVEN_SWAP": "Swap adjacent tile pairs (0-1, 2-3...).", # Rule to swap pairs (0 and 1, 2 and 3, etc.)
            "TILE_SORT": "Recall tiles sorted by their number.", # Rule to input tiles from lowest to highest index
            "MIRROR": "Mentally flip the grid horizontally." # Rule to flip the column index of each tile
        }

    def generate_next_sequence(self): # Method to set up the next round of the game
        """Generates a new sequence and determines the game mode."""
        self.score += 1 # Increment score/round counter (used for difficulty scaling)
        
        sequence_length = 3 + (self.score // 2) # Length increases every 2 points scored
        
        # Determine Mode and Speed
        self.base_speed = max(0.3, 1.0 - ((self.score - 5) * 0.1)) # Speed gets faster as score increases
        
        # --- Difficulty Scaling Logic (Mid-Level Game Flow) ---
        if self.score < 5: # For low scores (under 5)
            self.current_mode = "RECALL" # Use simple RECALL mode
        elif 5 <= self.score < 10: # For scores between 5 and 9
            self.current_mode = "RECALL" # Still RECALL, but base_speed is faster
        elif 10 <= self.score < 15: # For scores between 10 and 14
            self.current_mode = "TRANSFORM" # Introduce TRANSFORM mode
            self.transformation_rule = random.choice(list(self.TRANSFORM_RULES.keys())) # Pick a random rule
            sequence_length = max(4, sequence_length - 1) # Shorten sequence slightly to balance difficulty
        elif 15 <= self.score < 20: # For scores between 15 and 19
            self.current_mode = "MIRROR" # Introduce MIRROR mode specifically
            sequence_length = 5 # Set fixed length for this specific challenge
        elif 20 <= self.score < 25: # For scores between 20 and 24
            self.current_mode = "DOUBLE" # Introduce DOUBLE mode (flashes in pairs)
            sequence_length = 8 # Total tiles shown (8 tiles = 4 simultaneous pairs)
        else: # For scores 25 and above
            self.current_mode = "PREDICT" # Introduce the final PREDICT mode
            sequence_length = 6 # Sequence length for pattern recognition

        # Add powerups occasionally
        if self.score % 7 == 0: # Every 7 rounds won
            p = random.choice(list(self.powerups.keys())) # Choose a random power-up type
            self.powerups[p] += 1 # Increment the count for that power-up

        # Generate the Base Sequence
        if self.current_mode == "DOUBLE": # If in double flash mode
            # For DOUBLE mode, we still generate a single list but treat pairs as simultaneous
            self.current_sequence = [random.randint(0, self.tile_count - 1) for _ in range(sequence_length)] # Random tiles
        else: # For all other modes
            self.current_sequence = [random.randint(0, self.tile_count - 1) for _ in range(sequence_length)] # Random tiles
        
        # Adjust sequence for PREDICT mode
        if self.current_mode == "PREDICT": # If the mode is PREDICT
            self.current_sequence = self._inject_pattern(self.current_sequence) # Generate a pattern and remove last tile
        
        # Calculate the target sequence based on the mode
        self.correct_target_sequence = self._apply_transformation(self.current_sequence) # Transform if needed

        effective_speed = self.base_speed * (1.5 if self.active_slow_mo else 1.0) # Apply slow-mo effect to speed
        self.active_slow_mo = False # Reset the power-up flag after it has been used for this generation
        
        return self.current_sequence, effective_speed # Return the sequence to show and the flash speed

    def use_powerup(self, p_type): # Method to activate an acquired power-up
        if self.powerups.get(p_type, 0) > 0: # Check if the player has at least one of this type
            self.powerups[p_type] -= 1 # Consume one power-up
            if p_type == "SLOW_MO": self.active_slow_mo = True # Flag for round generation
            elif p_type == "SHIELD": self.shield_active = True # Flag for input checking
            return True # Return True to indicate success
        return False # Return False if the power-up was not available

    def _inject_pattern(self, seq): # Internal method to create repetitive patterns for PREDICT mode
        """Creates a recognizable, *predictable* sub-pattern for PREDICT mode."""
        pattern_length = 3 # Use a 3-tile base pattern (e.g., A-B-C)
        base_pattern = [random.randint(0, self.tile_count - 1) for _ in range(pattern_length)] # Random 3 tiles
        
        # Repeat the pattern to fill the required sequence length plus overflow
        new_seq = (base_pattern * (len(seq) // pattern_length + 1)) 
        
        # The tile to predict is the one that would naturally come next in the pattern
        self.last_predicted_tile = new_seq[len(seq)-1]
        
        return new_seq[:len(seq)-1] # Return the sequence with the last tile removed for display

    def _apply_transformation(self, seq): # Internal method to calculate what the user should actually enter
        """Applies the current transformation rule to the sequence."""
        if self.current_mode == "RECALL" or self.current_mode == "PREDICT" or self.current_mode == "DOUBLE": # Simple modes
            # For RECALL, PREDICT, and DOUBLE, the required input matches what was shown (mostly)
            return seq # No mental math required for the base sequence
        
        if self.transformation_rule == "REVERSE": # If rule is REVERSE
            return list(reversed(seq)) # Return the sequence backwards
        
        elif self.transformation_rule == "TILE_SORT": # If rule is TILE_SORT
            return sorted(seq) # Return the indices in numerical order (0 to 15)

        elif self.transformation_rule == "MIRROR": # If rule is MIRROR
            # Flip horizontally: calculate new col as (3 - old_col)
            mirrored = [] # Initialize empty list for result
            for t in seq: # For each tile index in the sequence
                row, col = divmod(t, self.grid_size) # Extract row and column (e.g., 5 -> row 1, col 1)
                mirrored.append(row * self.grid_size + (self.grid_size - 1 - col)) # Append flipped version
            return mirrored # Return the list of mirrored tiles
        
        elif self.transformation_rule == "ODD_EVEN_SWAP": # If rule is ODD_EVEN_SWAP
            # Simple swap of adjacent pairs (0<->1, 2<->3...)
            return [t+1 if t%2==0 else t-1 for t in seq] # Apply bitwise-like swap to each tile index
        
        return seq # Fallback to returning original sequence if no rule matches

    def check_player_input(self, player_input): # Main method to validate the user's clicks
        """Compares the player's input with the correct target sequence."""
        
        if self.current_mode == "PREDICT": # Special handling for PREDICT mode (single click check)
            # For PREDICT, the player only enters ONE tile (the prediction)
            if len(player_input) != 1: # Sanity check for the frontend input
                return False # If not exactly one click, it's an error
            
            predicted_tile = player_input[0] # Get the single tile the player clicked
            
            # The missing tile was stored during generation
            is_correct = predicted_tile == self.last_predicted_tile # Compare with hidden predicted tile
            
            if is_correct: # If prediction was correct
                self.consecutive_correct += 1 # Increment streak
                self.combo_multiplier = min(5.0, self.combo_multiplier + 0.5) # Increase combo up to 5x
                self.score += int(50 * self.combo_multiplier) # Add large bonus score
            else: # If prediction was wrong
                self.lives -= 1 # Deduct a life
                self.consecutive_correct = 0 # Reset streak
                self.combo_multiplier = 1.0 # Reset multiplier
            return is_correct # Return result of the single-tile check
        
        # --- RECALL/TRANSFORM/MIRROR Check ---
        is_correct = player_input == self.correct_target_sequence # Check if entire list matches target

        if is_correct: # If the whole sequence was correct
            self.consecutive_correct += 1 # Increment success streak
            if self.consecutive_correct >= 3: # After 3 perfect rounds
                self.combo_multiplier = min(5.0, self.combo_multiplier + 0.5) # Increase multiplier
            self.score += int(10 * self.combo_multiplier) # Add points multiplied by current combo
        else: # If the sequence was incorrect
            if self.shield_active: # Check if SHIELD power-up was active
                self.shield_active = False # Consume the shield
                print("Shield Blocked Mistake!") # Visual/Console feedback
                return True # Treat this failure as a 'pass' for the player
            
            self.lives -= 1 # Deduct a life for the error
            self.consecutive_correct = 0 # Reset the success streak
            self.combo_multiplier = 1.0 # Reset points multiplier to base
            if self.lives < 0: self.lives = 0 # Ensure lives don't go negative
            
        return is_correct # Return whether the input was initially correct or not
