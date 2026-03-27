import random
import time

class CogniQuestLogic:
    def __init__(self, grid_size=4):
        self.grid_size = grid_size
        self.tile_count = grid_size * grid_size # 16 tiles
        self.score = 0
        self.max_score = 0
        self.current_sequence = []
        self.base_speed = 1.0
        
        # New State Variables for Advanced Modes
        self.current_mode = "RECALL" # RECALL, TRANSFORM, PREDICT, MIRROR, DOUBLE
        self.correct_target_sequence = []
        self.transformation_rule = "" # Initialize as empty string instead of None
        
        # New Mechanics
        self.lives = 3
        self.combo_multiplier = 1.0
        self.consecutive_correct = 0
        self.powerups = {"SHIELD": 0, "SLOW_MO": 0, "HINT": 0}
        self.active_slow_mo = False
        self.shield_active = False
        self.last_predicted_tile = -1 # For PREDICT mode

        # Define Transformation Rules
        self.TRANSFORM_RULES = {
            "REVERSE": "Recall the sequence in reverse order.",
            "ODD_EVEN_SWAP": "Swap adjacent tile pairs (0-1, 2-3...).", 
            "TILE_SORT": "Recall tiles sorted by their number.",
            "MIRROR": "Mentally flip the grid horizontally."
        }

    def generate_next_sequence(self):
        """Generates a new sequence and determines the game mode."""
        self.score += 1
        
        sequence_length = 3 + (self.score // 2)
        
        # Determine Mode and Speed
        self.base_speed = max(0.3, 1.0 - ((self.score - 5) * 0.1))
        
        # --- Difficulty Scaling Logic (Mid-Level Game Flow) ---
        if self.score < 5:
            self.current_mode = "RECALL"
        elif 5 <= self.score < 10:
            self.current_mode = "RECALL" # Pure recall challenge, faster
        elif 10 <= self.score < 15:
            self.current_mode = "TRANSFORM"
            self.transformation_rule = random.choice(list(self.TRANSFORM_RULES.keys()))
            sequence_length = max(4, sequence_length - 1)
        elif 15 <= self.score < 20:
            self.current_mode = "MIRROR"
            sequence_length = 5
        elif 20 <= self.score < 25:
            self.current_mode = "DOUBLE" # Challenge: 2 tiles at once
            sequence_length = 8 # Will flash in pairs
        else: # Score 25+
            self.current_mode = "PREDICT"
            sequence_length = 6
        
        # Add powerups occasionally
        if self.score % 7 == 0:
            p = random.choice(list(self.powerups.keys()))
            self.powerups[p] += 1

        # Generate the Base Sequence
        if self.current_mode == "DOUBLE":
            # For DOUBLE mode, we still generate a single list but treat pairs as simultaneous
            self.current_sequence = [random.randint(0, self.tile_count - 1) for _ in range(sequence_length)]
        else:
            self.current_sequence = [random.randint(0, self.tile_count - 1) for _ in range(sequence_length)]
        
        # Adjust sequence for PREDICT mode
        if self.current_mode == "PREDICT":
            self.current_sequence = self._inject_pattern(self.current_sequence)
        
        # Calculate the target sequence based on the mode
        self.correct_target_sequence = self._apply_transformation(self.current_sequence)

        effective_speed = self.base_speed * (1.5 if self.active_slow_mo else 1.0)
        self.active_slow_mo = False # Reset after generation
        
        return self.current_sequence, effective_speed

    def use_powerup(self, p_type):
        if self.powerups.get(p_type, 0) > 0:
            self.powerups[p_type] -= 1
            if p_type == "SLOW_MO": self.active_slow_mo = True
            elif p_type == "SHIELD": self.shield_active = True
            return True
        return False

    def _inject_pattern(self, seq):
        """Creates a recognizable, *predictable* sub-pattern for PREDICT mode."""
        pattern_length = 3
        base_pattern = [random.randint(0, self.tile_count - 1) for _ in range(pattern_length)]
        
        # Repeat the pattern
        new_seq = (base_pattern * (len(seq) // pattern_length + 1))
        
        # The tile to predict is the one shifted by the current length
        self.last_predicted_tile = new_seq[len(seq)-1]
        
        return new_seq[:len(seq)-1]

    def _apply_transformation(self, seq):
        """Applies the current transformation rule to the sequence."""
        if self.current_mode == "RECALL" or self.current_mode == "PREDICT":
            # For RECALL and PREDICT (where the prediction is the 7th tile), the target is the sequence itself
            return seq
        
        if self.transformation_rule == "REVERSE":
            return list(reversed(seq))
        
        elif self.transformation_rule == "TILE_SORT":
            return sorted(seq)

        elif self.transformation_rule == "MIRROR":
            # Flip horizontally: col -> (grid_size - 1 - col)
            mirrored = []
            for t in seq:
                row, col = divmod(t, self.grid_size)
                mirrored.append(row * self.grid_size + (self.grid_size - 1 - col))
            return mirrored
        
        elif self.transformation_rule == "ODD_EVEN_SWAP":
            # Simple swap of adjacent pairs (0<->1, 2<->3...)
            return [t+1 if t%2==0 else t-1 for t in seq]
        
        return seq

    def check_player_input(self, player_input):
        """Compares the player's input with the correct target sequence."""
        
        if self.current_mode == "PREDICT":
            # For PREDICT, the player only enters ONE tile (the prediction)
            if len(player_input) != 1:
                return False # Should not happen if frontend is correct
            
            # The *correct_target_sequence* in PREDICT mode is the full pattern (A-B-C-A-B-C)
            # We check the prediction against the tile that was intentionally omitted
            predicted_tile = player_input[0]
            
            # The tile to predict is the next tile in the base pattern (A-B-C...)
            pattern_index_to_repeat = len(self.current_sequence) % 3 # assuming 3-tile pattern
            
            # Reconstruct the expected full pattern:
            # Since self.current_sequence is A-B-A-B-A, the missing tile is C.
            # A more robust implementation would store the 'base_pattern' used in _inject_pattern.
            # For simplicity here, we assume the prediction is the next expected tile in the full sequence.
            # *CRITICAL UPDATE: To correctly check prediction, the missing tile must be known.*
            
            # The missing tile was stored during generation
            is_correct = predicted_tile == self.last_predicted_tile
            
            if is_correct:
                self.consecutive_correct += 1
                self.combo_multiplier = min(5.0, self.combo_multiplier + 0.5)
                self.score += int(50 * self.combo_multiplier) # Predict is worth more
            else:
                self.lives -= 1
                self.consecutive_correct = 0
                self.combo_multiplier = 1.0
            return is_correct

        
        # --- RECALL/TRANSFORM/MIRROR Check ---
        is_correct = player_input == self.correct_target_sequence

        if is_correct:
            self.consecutive_correct += 1
            if self.consecutive_correct >= 3:
                self.combo_multiplier = min(5.0, self.combo_multiplier + 0.5)
            self.score += int(10 * self.combo_multiplier)
        else:
            if self.shield_active:
                self.shield_active = False
                print("Shield Blocked Mistake!")
                return True # Treat as correct but lose shield
            
            self.lives -= 1
            self.consecutive_correct = 0
            self.combo_multiplier = 1.0
            if self.lives < 0: self.lives = 0
            
        return is_correct
