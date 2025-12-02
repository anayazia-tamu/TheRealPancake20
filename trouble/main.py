"""
Trouble Game - Main Entry Point
Handles game loop and event processing
"""

import pygame
import random
import os
import pygame.gfxdraw
import math
from typing import Tuple, List, Optional, Dict
import datetime


class TroubleGame:
    """Main game controller that manages the game loop and user interactions"""

    def __init__(self):
        try:
            pygame.init()
            self.screen = pygame.display.set_mode((1200, 900))
            pygame.display.set_caption("Trouble Game")
            self.clock = pygame.time.Clock()

            self.game_state = GameState()
            self.renderer = GameRenderer(self.screen)

            self.main_menu_mode = True
            self.setup_mode = False
            self.waiting_for_peg_selection = False
            self.viewing_results = False
            self.results_data = []
            self.paused = False
            self.viewing_rules = False
        except pygame.error as e:
            print(f"Failed to initialize Pygame: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error during initialization: {e}")
            raise

    def run(self):
        """Main game loop"""
        running = True
        while running:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_events(event.pos)

            self.render()
            
            # Update dice animation
            if self.game_state.is_rolling:
                current_time = pygame.time.get_ticks()
                if current_time - self.game_state.roll_animation_start_time > self.game_state.roll_animation_duration:
                    # Animation finished
                    self.finish_roll()
                else:
                    # Update animation frame (change value every 50ms)
                    if current_time % 50 < 20: # Simple jitter
                         self.game_state.current_animation_value = random.randint(1, 6)

            # Update move animation
            if self.game_state.is_animating_move:
                try:
                    current_time = pygame.time.get_ticks()
                    if current_time - self.game_state.move_animation['start_time'] > self.game_state.move_animation['duration']:
                        self.finish_move_animation()
                except (KeyError, TypeError) as e:
                    print(f"Animation error: {e}")
                    self.game_state.is_animating_move = False

            pygame.display.flip()

        pygame.quit()

    def handle_events(self, mouse_pos):
        """Handle mouse click events"""
        if self.main_menu_mode:
            self.handle_main_menu_click(mouse_pos)
        elif self.viewing_results:
            self.handle_results_click(mouse_pos)
        elif self.viewing_rules:
            self.handle_rules_click(mouse_pos)
        elif self.setup_mode:
            self.handle_setup_click(mouse_pos)
        elif self.paused:
            self.handle_pause_menu_click(mouse_pos)
        else:
            self.handle_game_click(mouse_pos)

    def handle_main_menu_click(self, mouse_pos):
        """Handle clicks on the main menu"""
        mouse_x, mouse_y = mouse_pos
        
        # Play Game button
        play_button_rect = pygame.Rect(450, 320, 300, 80)
        if play_button_rect.collidepoint(mouse_x, mouse_y):
            self.main_menu_mode = False
            self.setup_mode = True
            return
        
        # Rules button
        rules_button_rect = pygame.Rect(450, 420, 300, 80)
        if rules_button_rect.collidepoint(mouse_x, mouse_y):
            self.main_menu_mode = False
            self.viewing_rules = True
            return
        
        # View Results button
        results_button_rect = pygame.Rect(450, 520, 300, 80)
        if results_button_rect.collidepoint(mouse_x, mouse_y):
            # Check if results directory exists
            if os.path.exists("game_results"):
                self.load_results()
                self.main_menu_mode = False
                self.viewing_results = True
            return
    
    def handle_results_click(self, mouse_pos):
        """Handle clicks on the results screen"""
        mouse_x, mouse_y = mouse_pos
        
        # Back button
        back_button_rect = pygame.Rect(450, 750, 300, 60)
        if back_button_rect.collidepoint(mouse_x, mouse_y):
            self.viewing_results = False
            self.main_menu_mode = True
            return
    
    def load_results(self):
        """Load all game results from the game_results directory"""
        self.results_data = []
        results_dir = "game_results"
        
        if not os.path.exists(results_dir):
            return
        
        # Get all result files
        files = [f for f in os.listdir(results_dir) if f.endswith('.txt')]
        files.sort(reverse=True)  # Most recent first
        
        # Load up to 10 most recent games
        for filename in files[:10]:
            filepath = os.path.join(results_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    self.results_data.append(content)
            except Exception as e:
                print(f"Error loading {filename}: {e}")
        else:
            # All files loaded successfully (or no files to load)
            if files:
                print(f"Successfully loaded {len(self.results_data)} game result(s)")

    def handle_setup_click(self, mouse_pos):
        """Handle clicks during game setup"""
        # Check which player count button was clicked
        button_y = 450
        button_spacing = 180
        start_x = 600 - (2 * button_spacing) // 2

        mouse_x, mouse_y = mouse_pos

        # Check if click is in the button area
        if 410 <= mouse_y <= 490:  # button_y ± 40
            for i in range(2, 5):  # 2, 3, 4 players
                button_x = start_x + (i - 2) * button_spacing

                # Check if click is within this button
                if button_x - 50 <= mouse_x <= button_x + 50:
                    # Initialize game with selected number of players
                    self.game_state.initialize_game(i)
                    self.setup_mode = False
                    return
            else:
                # No button was clicked in the valid y-range
                print("Click was in button area but not on any button")

    def handle_game_click(self, mouse_pos):
        """Handle clicks during gameplay"""
        # Check if pause menu button was clicked
        if self.renderer.is_pause_button_clicked(mouse_pos):
            self.paused = True
            return
        
        # Check if game is over and menu button was clicked
        if self.game_state.game_over:
            if self.renderer.is_menu_button_clicked(mouse_pos):
                # Reset to main menu
                self.main_menu_mode = True
                self.setup_mode = False
                self.waiting_for_peg_selection = False
                self.game_state = GameState()  # Create fresh game state
            return

        # Check if dice button was clicked
        if self.renderer.is_dice_button_clicked(mouse_pos):
            self.handle_dice_click()
            return

        # Check if a peg was clicked (only if waiting for peg selection)
        if self.waiting_for_peg_selection:
            peg = self.renderer.get_clicked_peg(mouse_pos, self.game_state.players)
            if peg:
                self.handle_peg_click(peg)

    def handle_dice_click(self):
        """Handle dice button clicks"""
        # Only allow dice roll if no current roll exists and not already rolling
        if self.game_state.current_roll is not None or self.game_state.is_rolling:
            return

        # Start rolling animation
        self.game_state.is_rolling = True
        self.game_state.roll_animation_start_time = pygame.time.get_ticks()
        self.game_state.message = "Rolling..."

    def finish_roll(self):
        """Complete the roll after animation"""
        self.game_state.is_rolling = False
        
        # Roll the dice
        roll = self.game_state.roll_dice()
        self.game_state.last_roll = roll
        self.game_state.message = f"Rolled a {roll}!"

        # Check if there are any valid moves
        valid_pegs = self.game_state.get_valid_pegs(roll)

        if not valid_pegs:
            # No valid moves, auto-skip turn
            self.game_state.message = f"No valid moves! {self.game_state.get_current_player().name} skips turn."
            self.game_state.advance_turn()
            self.waiting_for_peg_selection = False
        else:
            # Wait for player to select a peg
            self.waiting_for_peg_selection = True
            self.game_state.message = f"Select a peg to move"

    def handle_peg_click(self, peg):
        """Handle peg selection clicks"""
        # Check if this peg is valid for the current roll
        valid_pegs = self.game_state.get_valid_pegs(self.game_state.current_roll)

        if peg not in valid_pegs:
            # Invalid peg selection, ignore
            return

        # Calculate new position (but don't move yet)
        new_pos = self.game_state._calculate_new_position(peg, self.game_state.current_roll)
        
        if new_pos is None:
            return

        # Calculate full path for animation
        path = self.game_state.calculate_move_path(peg, self.game_state.current_roll)
        
        # Start move animation
        self.game_state.is_animating_move = True
        step_duration = 200 # ms per step
        total_duration = max(step_duration, (len(path) - 1) * step_duration)
        
        self.game_state.move_animation = {
            'peg': peg,
            'path': path,
            'start_time': pygame.time.get_ticks(),
            'duration': total_duration,
            'step_duration': step_duration
        }
        self.waiting_for_peg_selection = False # Stop input during animation

    def finish_move_animation(self):
        """Complete the move after animation"""
        try:
            self.game_state.is_animating_move = False
            anim_data = self.game_state.move_animation
            peg = anim_data['peg']
            
            # Execute the actual move logic
            move_result = self.game_state.move_peg(peg, self.game_state.current_roll)

            if not move_result["success"]:
                print(f"Move failed! Result: {move_result}")
                self.waiting_for_peg_selection = True
                self.game_state.message = "Move failed! Try again."
                return

            # Update message based on move result
            if move_result.get("captured"):
                # Message already set in move_peg
                pass
            elif move_result.get("entered_finish"):
                self.game_state.message = f"{peg.owner.name} entered the finish zone!"
            elif move_result.get("landed_on_double_trouble"):
                self.game_state.message = (
                    f"{peg.owner.name} landed on Double Trouble! Bonus roll!"
                )

            # Check win condition
            self.game_state.check_win_condition()

            if self.game_state.game_over:
                self.waiting_for_peg_selection = False
                return

            # Check if bonus roll should be granted
            if self.game_state.should_grant_bonus_roll(move_result):
                # Grant bonus roll
                if self.game_state.current_roll == 6:
                    self.game_state.message = f"Rolled a 6! Bonus roll!"
                # Reset for next roll
                self.game_state.current_roll = None
                self.waiting_for_peg_selection = False
            else:
                # No bonus roll, advance turn
                self.game_state.advance_turn()
                self.waiting_for_peg_selection = False
        except (KeyError, AttributeError) as e:
            print(f"Error finishing move animation: {e}")
            self.game_state.is_animating_move = False
            self.waiting_for_peg_selection = False

    def handle_pause_menu_click(self, mouse_pos):
        """Handle clicks on the pause menu"""
        mouse_x, mouse_y = mouse_pos
        
        # Rules button
        rules_button_rect = pygame.Rect(450, 330, 300, 70)
        if rules_button_rect.collidepoint(mouse_x, mouse_y):
            self.paused = False
            self.viewing_rules = True
            return
        
        # Back to Main Menu button
        menu_button_rect = pygame.Rect(450, 420, 300, 70)
        if menu_button_rect.collidepoint(mouse_x, mouse_y):
            self.paused = False
            self.main_menu_mode = True
            self.setup_mode = False
            self.waiting_for_peg_selection = False
            self.game_state = GameState()  # Create fresh game state
            return
        
        # Exit button
        exit_button_rect = pygame.Rect(450, 510, 300, 70)
        if exit_button_rect.collidepoint(mouse_x, mouse_y):
            pygame.quit()
            exit()
            return
    
    def handle_rules_click(self, mouse_pos):
        """Handle clicks on the rules screen"""
        mouse_x, mouse_y = mouse_pos
        
        # Back button
        back_button_rect = pygame.Rect(450, 750, 300, 60)
        if back_button_rect.collidepoint(mouse_x, mouse_y):
            self.viewing_rules = False
            # Return to main menu if we came from there, otherwise return to pause menu
            if self.main_menu_mode or self.game_state.players == []:
                self.main_menu_mode = True
            else:
                self.paused = True
            return
    
    def render(self):
        """Render the current game state"""
        try:
            mouse_pos = pygame.mouse.get_pos()
            
            if self.main_menu_mode:
                self.renderer.render_main_menu(mouse_pos)
            elif self.viewing_results:
                self.renderer.render_results_screen(self.results_data, mouse_pos)
            elif self.viewing_rules:
                self.renderer.render_rules_screen(mouse_pos)
            else:
                self.renderer.render_all(self.game_state, self.setup_mode, mouse_pos)

                # Highlight valid pegs if waiting for selection
                if self.waiting_for_peg_selection and self.game_state.current_roll is not None:
                    valid_pegs = self.game_state.get_valid_pegs(self.game_state.current_roll)
                    self.renderer.highlight_pegs(valid_pegs)
                
                # Render pause menu if paused
                if self.paused:
                    self.renderer.render_pause_menu(mouse_pos)
        except pygame.error as e:
            print(f"Rendering error: {e}")
        except Exception as e:
            print(f"Unexpected rendering error: {e}")


"""
Trouble Game - Game State and Logic
Contains all game rules, state management, and business logic
"""




class Player:
    """Represents a player in the game"""

    def __init__(self, color: str, name: str):
        self.color = color
        self.name = name
        self.pegs: List["Peg"] = []

    def get_pegs_in_home(self) -> List["Peg"]:
        """Return all pegs currently in home base"""
        return [peg for peg in self.pegs if peg.is_in_home]

    def get_pegs_on_track(self) -> List["Peg"]:
        """Return all pegs currently on the playing track"""
        return [peg for peg in self.pegs if not peg.is_in_home and not peg.is_in_finish]

    def get_pegs_in_finish(self) -> List["Peg"]:
        """Return all pegs currently in the finish zone"""
        return [peg for peg in self.pegs if peg.is_in_finish]

    def has_won(self) -> bool:
        """Check if this player has won the game"""
        return len(self.get_pegs_in_finish()) == 4


class Peg:
    """Represents a game piece belonging to a player"""

    def __init__(self, owner: Player):
        self.owner = owner
        self.position = -1  # -1 = home, 0-27 = track, 100+ = finish
        self.is_in_home = True
        self.is_in_finish = False

    def move_to(self, position: int):
        """Move this peg to a new position"""
        self.position = position

        if position == -1:
            self.is_in_home = True
            self.is_in_finish = False
        elif position >= 100:
            self.is_in_home = False
            self.is_in_finish = True
        else:
            self.is_in_home = False
            self.is_in_finish = False

    def send_home(self):
        """Send this peg back to home base"""
        self.move_to(-1)


class GameState:
    """Manages the complete game state and rules"""

    # Start positions for each player color on the main track
    START_POSITIONS = {"RED": 0, "BLUE": 7, "GREEN": 14, "YELLOW": 21}

    # Finish zone entry positions (where pegs leave the main track)
    FINISH_ENTRY_POSITIONS = {"RED": 27, "BLUE": 6, "GREEN": 13, "YELLOW": 20}

    def __init__(self):
        self.players: List[Player] = []
        self.current_player_index = 0
        self.board_occupancy: Dict[int, Peg] = {}
        self.current_roll: Optional[int] = None
        self.rolls_this_turn = 0
        self.game_over = False
        self.winner: Optional[Player] = None
        self.message = ""
        
        # Animation state
        self.is_rolling = False
        self.roll_animation_start_time = 0
        self.roll_animation_duration = 500  # ms
        self.current_animation_value = 1
        self.last_roll: Optional[int] = None
        
        self.is_animating_move = False
        self.move_animation = None # {peg, start_pos, end_pos, start_time, duration}

    def initialize_game(self, num_players: int):
        """Initialize a new game with the specified number of players"""
        if num_players < 2 or num_players > 4:
            raise ValueError("Number of players must be between 2 and 4")

        # Define player colors in order
        colors = ["RED", "BLUE", "GREEN", "YELLOW"]
        names = ["Red", "Blue", "Green", "Yellow"]

        # Create players
        self.players = []
        for i in range(num_players):
            player = Player(colors[i], names[i])
            # Create 4 pegs for each player
            for _ in range(4):
                peg = Peg(player)
                player.pegs.append(peg)
            self.players.append(player)

        # Initialize game state
        self.current_player_index = 0
        self.board_occupancy = {}
        self.current_roll = None
        self.rolls_this_turn = 0
        self.game_over = False
        self.winner = None
        self.message = f"{self.players[0].name}'s turn"
        
        self.is_rolling = False
        self.roll_animation_start_time = 0
        self.current_animation_value = 1
        self.last_roll = None
        self.is_animating_move = False
        self.move_animation = None

    def roll_dice(self) -> int:
        """Roll the dice and return the result"""
        self.current_roll = random.randint(1, 6)
        self.rolls_this_turn += 1
        return self.current_roll

    def get_valid_pegs(self, roll: int) -> List[Peg]:
        """Get all pegs that can be moved with the current roll"""
        current_player = self.get_current_player()
        valid_pegs = []

        if roll == 1:
            # Roll of 1: must move a peg from home to start
            pegs_in_home = current_player.get_pegs_in_home()
            start_pos = self.START_POSITIONS[current_player.color]

            # Check if start position is blocked by own peg
            if start_pos in self.board_occupancy:
                occupying_peg = self.board_occupancy[start_pos]
                if occupying_peg.owner == current_player:
                    # Start is blocked by own peg, no valid moves
                    return []

            # Can move any peg from home
            valid_pegs = pegs_in_home

        elif roll == 6:
            # Roll of 6: can move from home OR move a peg on track
            pegs_in_home = current_player.get_pegs_in_home()
            start_pos = self.START_POSITIONS[current_player.color]

            # Check if we can move from home
            if pegs_in_home:
                if (
                    start_pos not in self.board_occupancy
                    or self.board_occupancy[start_pos].owner != current_player
                ):
                    valid_pegs.extend(pegs_in_home)

            # Also check pegs on track
            pegs_on_track = current_player.get_pegs_on_track()
            for peg in pegs_on_track:
                new_pos = self._calculate_new_position(peg, roll)
                if new_pos is not None and self._is_valid_destination(peg, new_pos):
                    valid_pegs.append(peg)

        else:
            # Rolls 2-5: can only move pegs on track
            pegs_on_track = current_player.get_pegs_on_track()
            for peg in pegs_on_track:
                new_pos = self._calculate_new_position(peg, roll)
                if new_pos is not None and self._is_valid_destination(peg, new_pos):
                    valid_pegs.append(peg)

        return valid_pegs

    def _calculate_new_position(self, peg: Peg, roll: int) -> Optional[int]:
        """Calculate the new position for a peg after a roll"""
        current_player = peg.owner

        # If peg is in home and roll is 1 or 6, move to start
        if peg.is_in_home:
            if roll == 1 or roll == 6:
                return self.START_POSITIONS[current_player.color]
            return None

        # If peg is in finish zone, try to advance within finish
        if peg.is_in_finish:
            finish_index = peg.position - 100
            new_finish_index = finish_index + roll
            if new_finish_index < 4:
                return 100 + new_finish_index
            # Can't move past the end of finish zone
            return None

        # Calculate new position on track
        new_pos = peg.position + roll

        # Check if peg should enter finish zone
        finish_entry = self.FINISH_ENTRY_POSITIONS[current_player.color]
        start_pos = self.START_POSITIONS[current_player.color]

        # Check if we cross the finish entry point
        # Need to handle wrap-around: track goes 0-27
        if peg.position <= finish_entry < new_pos:
            # We crossed the finish entry going forward
            steps_into_finish = new_pos - finish_entry - 1
            if steps_into_finish < 4:
                return 100 + steps_into_finish
            # Overshot finish zone
            return None
        elif peg.position > finish_entry and new_pos >= 28:
            # We wrapped around - check if we would cross finish entry after wrap
            steps_after_wrap = new_pos - 28
            if start_pos <= finish_entry < start_pos + steps_after_wrap:
                # We crossed finish entry after wrapping
                steps_into_finish = start_pos + steps_after_wrap - finish_entry - 1
                if steps_into_finish < 4:
                    return 100 + steps_into_finish
                return None

        # Normal track movement (wrap around at 28)
        return new_pos % 28

    def calculate_move_path(self, peg: Peg, roll: int) -> List[int]:
        """Calculate the full path of positions for a move"""
        path = [peg.position]
        current_pos = peg.position
        current_player = peg.owner
        
        # Handle move from home
        if peg.is_in_home:
            if roll == 1 or roll == 6:
                start_pos = self.START_POSITIONS[current_player.color]
                path.append(start_pos)
            return path
            
        # Handle move from finish (shouldn't happen usually)
        if peg.is_in_finish:
            return path
            
        # Handle track movement
        steps_remaining = roll
        finish_entry = self.FINISH_ENTRY_POSITIONS[current_player.color]
        
        while steps_remaining > 0:
            # Check if entering finish
            # Logic similar to _calculate_new_position but step by step
            
            # Check if we are at finish entry and moving into finish
            if current_pos == finish_entry:
                 # Enter finish zone
                 # Find first available finish spot or just increment
                 # For animation, we can just show moving into 100, 101, etc.
                 # But we need to know which specific finish spot we end up in?
                 # Actually, let's just simulate the steps.
                 
                 # If we are at finish entry, next step is 100 (first finish spot)
                 # But wait, finish spots are 100, 101, 102, 103.
                 # If we are at entry, next is 100.
                 # If we are at 100, next is 101.
                 
                 # Let's simplify: if current is finish entry, next is 100.
                 # If current >= 100, next is current + 1.
                 
                 next_pos = 100
                 path.append(next_pos)
                 current_pos = next_pos
                 steps_remaining -= 1
                 continue
            
            if current_pos >= 100:
                next_pos = current_pos + 1
                path.append(next_pos)
                current_pos = next_pos
                steps_remaining -= 1
                continue

            # Normal track move
            next_pos = (current_pos + 1) % 28
            
            # Check if we just passed finish entry (and should have entered)
            # This is tricky step-by-step.
            # If we are at finish entry, we should go to 100, NOT (finish_entry + 1) % 28
            # UNLESS we are not the owner of that finish entry?
            # No, finish entry is specific to color.
            
            # So:
            if current_pos == finish_entry:
                 # We already handled this above?
                 # Yes, if current_pos == finish_entry, we go to 100.
                 pass
            else:
                path.append(next_pos)
                current_pos = next_pos
                steps_remaining -= 1
                
        return path

    def _is_valid_destination(self, peg: Peg, new_pos: int) -> bool:
        """Check if a destination position is valid for a peg"""
        # Check if destination is occupied by own peg
        if new_pos in self.board_occupancy:
            occupying_peg = self.board_occupancy[new_pos]
            if occupying_peg.owner == peg.owner:
                return False

        # Finish zone positions (100+) are always valid if calculated
        if new_pos >= 100:
            return True

        return True

    def move_peg(self, peg: Peg, roll: int) -> dict:
        """Move a peg and return the result of the move"""
        result = {
            "success": False,
            "captured": None,
            "entered_finish": False,
            "landed_on_double_trouble": False,
            "old_position": peg.position,
        }

        # Calculate new position
        new_pos = self._calculate_new_position(peg, roll)

        if new_pos is None or not self._is_valid_destination(peg, new_pos):
            return result

        # Remove peg from old position in board occupancy
        if peg.position >= 0 and peg.position < 100:
            if peg.position in self.board_occupancy:
                del self.board_occupancy[peg.position]

        # Check for capture before moving (only on track positions)
        if new_pos >= 0 and new_pos < 100:
            captured_peg = self.check_capture(new_pos)
            if captured_peg and captured_peg.owner != peg.owner:
                # Send opponent peg home
                captured_peg.send_home()
                result["captured"] = captured_peg
                self.message = (
                    f"{peg.owner.name} captured {captured_peg.owner.name}'s peg!"
                )

        # Move the peg
        peg.move_to(new_pos)

        # Update board occupancy for new position
        if new_pos >= 0 and new_pos < 100:
            self.board_occupancy[new_pos] = peg

        result["success"] = True
        result["new_position"] = new_pos

        # Check if entered finish zone
        if new_pos >= 100:
            result["entered_finish"] = True

        return result

    def check_capture(self, position: int) -> Optional[Peg]:
        """Check if there's an opponent peg at the given position"""
        if position in self.board_occupancy:
            return self.board_occupancy[position]
        return None

    def is_double_trouble(self, position: int) -> bool:
        """Check if the given position is a double trouble space"""
        # Double trouble spaces are at positions 3, 10, 17, 24
        return position in [3, 10, 17, 24]

    def should_grant_bonus_roll(self, move_result: dict) -> bool:
        """Determine if a bonus roll should be granted"""
        # Maximum 2 rolls per turn
        if self.rolls_this_turn >= 2:
            return False

        # Grant bonus roll if rolled a 6
        if self.current_roll == 6:
            return True

        # Grant bonus roll if landed on double trouble space
        if move_result.get("success") and move_result.get("new_position") is not None:
            new_pos = move_result["new_position"]
            if new_pos < 100 and self.is_double_trouble(new_pos):
                move_result["landed_on_double_trouble"] = True
                return True

        return False

    def advance_turn(self):
        """Advance to the next player's turn"""
        if self.game_over:
            return

        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.current_roll = None
        self.rolls_this_turn = 0
        self.message = f"{self.get_current_player().name}'s turn"

    def check_win_condition(self):
        """Check if any player has won the game"""
        for player in self.players:
            if player.has_won():
                self.game_over = True
                self.winner = player
                self.message = f"{player.name} wins!"
                self.save_game_results()
                return

    def has_valid_moves(self) -> bool:
        """Check if the current player has any valid moves for the current roll"""
        if self.current_roll is None:
            return False
        return len(self.get_valid_pegs(self.current_roll)) > 0

    def get_current_player(self) -> Player:
        """Get the current player"""
        if self.players:
            return self.players[self.current_player_index]
        return None

    def save_game_results(self):
        """Save game results to a file when the game ends"""
        if not self.game_over or not self.winner:
            return
        
        try:
            # Calculate player rankings based on pegs in finish zone
            rankings = []
            for player in self.players:
                pegs_finished = len(player.get_pegs_in_finish())
                rankings.append((player.color, pegs_finished))
            
            # Sort by pegs finished (descending)
            rankings.sort(key=lambda x: x[1], reverse=True)
            
            # Create results directory if it doesn't exist
            results_dir = "game_results"
            if not os.path.exists(results_dir):
                os.makedirs(results_dir)
            
            # Generate filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(results_dir, f"game_result_{timestamp}.txt")
            
            # Write results to file
            with open(filename, 'w') as f:
                f.write("TROUBLE GAME RESULTS\n")
                f.write("=" * 40 + "\n")
                f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Players: {len(self.players)}\n")
                f.write("\n")
                f.write("FINAL STANDINGS:\n")
                f.write("-" * 40 + "\n")
                
                for place, (color, pegs_finished) in enumerate(rankings, 1):
                    place_suffix = {1: "st", 2: "nd", 3: "rd"}.get(place, "th")
                    f.write(f"{place}{place_suffix} Place: {color} ({pegs_finished}/4 pegs finished)\n")
                
                f.write("\n")
                f.write(f"Winner: {self.winner.color}\n")
            
            print(f"Game results saved to {filename}")
        except OSError as e:
            print(f"Error saving game results: {e}")

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
# Modern Color Palette
COLORS = {"RED": (231, 76, 60), "BLUE": (52, 152, 219),"GREEN": (46, 204, 113),"YELLOW": (241, 196, 15), "BOARD_BG": (44, 62, 80), "BOARD_CIRCLE": (236, 240, 241), "TRACK": (189, 195, 199), "DOUBLE_TROUBLE": (230, 126, 34), "HIGHLIGHT": (26, 188, 156), "BLACK": (44, 62, 80), "WHITE": (255, 255, 255), "GRAY": (149, 165, 166), "SHADOW": (0, 0, 0, 100), "TEXT": (236, 240, 241)}
finish_positions = {"RED": (600, 350), "BLUE": (700, 450), "GREEN": (600, 550), "YELLOW": (500, 450)}
finish_directions = {"RED": (0, -1), "BLUE": (1, 0), "GREEN": (0, 1), "YELLOW": (-1, 0)} # Up, Right, Down, Left

class GameRenderer:
    # Handles all rendering for the Trouble game
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_large = pygame.font.SysFont("Arial Rounded MT Bold", 64)
        self.font_medium = pygame.font.SysFont("Arial Rounded MT Bold", 48)
        self.font_small = pygame.font.SysFont("Arial Rounded MT Bold", 24)
        # Fallback if system font not found
        if not self.font_large:
            self.font_large = pygame.font.Font(None, 64)
            self.font_medium = pygame.font.Font(None, 48)
            self.font_small = pygame.font.Font(None, 24)
        self.board_center = (600, 450)
        self.track_radius = 250
        self.space_positions: Dict[int, Tuple[int, int]] = {}
        # Calculate and cache board space positions
        self._calculate_space_positions()

    def render_all(self, game_state: GameState, setup_mode: bool = False, mouse_pos: Tuple[int, int] = (0, 0)):
        # Render the complete game state
        # Draw background gradient (simulated with rects for performance or just solid color)
        self.screen.fill(COLORS["BOARD_BG"])
        
        # Subtle background pattern or vignette could go here
        
        if setup_mode:
            self.render_setup_screen(mouse_pos)
        elif game_state.game_over:
            self.render_game_over_screen(game_state.winner, mouse_pos)
        else:
            self.render_board()
            self.render_track_spaces()
            self.render_home_bases(game_state.players)
            self.render_finish_zones(game_state.players)
            self.render_pegs_with_animation(game_state)
            self.render_center_dice(game_state)
            self.render_dice_button(game_state.current_roll is None and not game_state.is_rolling, game_state.current_roll, mouse_pos)
            if game_state.players:
                current_player = game_state.get_current_player()
                if current_player:
                    self.render_player_indicator(current_player)

            self.render_message(game_state.message)
            self.render_pause_button(mouse_pos)

    def _calculate_space_positions(self):
        # Calculate and cache positions for all board spaces
        # Calculate positions for 28 track spaces in a circle
        for i in range(28):
            angle = (i / 28) * 2 * math.pi - math.pi / 2  # Start at top
            x = self.board_center[0] + int(self.track_radius * math.cos(angle))
            y = self.board_center[1] + int(self.track_radius * math.sin(angle))
            self.space_positions[i] = (x, y)

    def _draw_circle_antialiased(self, surface, color, center, radius, border_color=None, border_width=0):
        # Helper to draw smooth circles
        x, y = center
        pygame.gfxdraw.aacircle(surface, x, y, radius, color)
        pygame.gfxdraw.filled_circle(surface, x, y, radius, color)
        
        if border_color and border_width > 0:
            # Draw border (simulated by drawing a slightly larger circle behind or multiple circles)
            # For simple AA border, we can just draw an AA circle outline
            for i in range(border_width):
                 pygame.gfxdraw.aacircle(surface, x, y, radius - i, border_color)

    def _draw_shadow(self, surface, center, radius, offset=(5, 5), alpha=100):
        # Draw a drop shadow
        x, y = center
        ox, oy = offset
        # Create a temporary surface for the shadow to handle alpha
        shadow_surface = pygame.Surface((radius * 2 + 10, radius * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surface, (0, 0, 0, alpha), (radius + 5, radius + 5), radius)
        surface.blit(shadow_surface, (x - radius - 5 + ox, y - radius - 5 + oy))

    def render_board(self):
        # Render the main board background
        # Draw board shadow
        self._draw_shadow(self.screen, self.board_center, self.track_radius + 40, offset=(8, 8), alpha=60)
        
        # Draw main board circle
        self._draw_circle_antialiased(self.screen, COLORS["BOARD_CIRCLE"], self.board_center, self.track_radius + 40)
        
        # Draw center circle (pop-o-matic area background)
        self._draw_circle_antialiased(self.screen, COLORS["BOARD_BG"], self.board_center, 80)
        
        # Draw a ring around the center
        pygame.gfxdraw.aacircle(self.screen, self.board_center[0], self.board_center[1], 80, COLORS["GRAY"])

    def render_center_dice(self, game_state: GameState):
        # Render the dice in the center of the board
        # Determine what value to show
        dice_value = None
        if game_state.is_rolling:
            dice_value = game_state.current_animation_value
        elif game_state.current_roll is not None:
            dice_value = game_state.current_roll
        elif game_state.last_roll is not None:
            dice_value = game_state.last_roll
            
        if dice_value is None:
            return

        cx, cy = self.board_center
        dice_size = 60
        # Draw dice background (white rounded rect)
        rect = pygame.Rect(cx - dice_size//2, cy - dice_size//2, dice_size, dice_size)
        pygame.draw.rect(self.screen, COLORS["WHITE"], rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS["GRAY"], rect, width=2, border_radius=10)
        # Draw pips
        pip_radius = 5
        pip_color = COLORS["BLACK"]
        # Helper to draw a pip
        def draw_pip(dx, dy):
            pygame.draw.circle(self.screen, pip_color, (cx + dx, cy + dy), pip_radius)
        # Pip positions relative to center
        d = 15
        if dice_value % 2 == 1: # 1, 3, 5
            draw_pip(0, 0)
        if dice_value >= 2: # 2, 3, 4, 5, 6
            draw_pip(-d, -d)
            draw_pip(d, d)
        if dice_value >= 4: # 4, 5, 6
            draw_pip(d, -d)
            draw_pip(-d, d)
        if dice_value == 6: # 6
            draw_pip(-d, 0)
            draw_pip(d, 0)

    def render_track_spaces(self):
        # Render the playing track spaces
        # Double trouble spaces
        double_trouble_positions = [3, 10, 17, 24]
        for position, (x, y) in self.space_positions.items():
            # Determine color based on whether it's a double trouble space
            if position in double_trouble_positions:
                color = COLORS["DOUBLE_TROUBLE"]
                radius = 18 # Slightly larger
            else:
                color = COLORS["WHITE"]
                radius = 15
            # Draw shadow for depth
            self._draw_shadow(self.screen, (x, y), radius, offset=(2, 2), alpha=50)
            # Draw the space
            self._draw_circle_antialiased(self.screen, color, (x, y), radius)
            # Draw border
            pygame.gfxdraw.aacircle(self.screen, x, y, radius, COLORS["GRAY"])

    def render_home_bases(self, players: List[Player]):
        """Render home bases for all players"""
        # Home base positions in corners
        home_positions = {"RED": (150, 150), "BLUE": (1050, 150), "GREEN": (1050, 750), "YELLOW": (150, 750)}
        for player in players:
            if player.color in home_positions:
                base_x, base_y = home_positions[player.color]
                # Draw base background with rounded corners
                rect = pygame.Rect(base_x - 70, base_y - 70, 140, 140)
                
                # Shadow
                shadow_rect = rect.copy()
                shadow_rect.move_ip(5, 5)
                pygame.draw.rect(self.screen, COLORS["SHADOW"], shadow_rect, border_radius=20)
                
                # Base
                pygame.draw.rect(self.screen, COLORS[player.color], rect, border_radius=20)
                
                # Inner area
                inner_rect = rect.inflate(-10, -10)
                pygame.draw.rect(self.screen, (255, 255, 255, 50), inner_rect, border_radius=15, width=2)

                # Draw 4 spots for pegs in a 2x2 grid
                for i in range(4):
                    spot_x = base_x - 30 + (i % 2) * 60
                    spot_y = base_y - 30 + (i // 2) * 60 
                    # Spot background
                    self._draw_circle_antialiased(self.screen, (0, 0, 0, 50), (spot_x, spot_y), 14)
                    self._draw_circle_antialiased(self.screen, COLORS["WHITE"], (spot_x, spot_y), 12)

    def render_finish_zones(self, players: List[Player]):
        """Render finish zones for all players"""

        for player in players:
            if player.color in finish_positions:
                start_x, start_y = finish_positions[player.color]
                dx, dy = finish_directions[player.color]
                # Draw 4 finish spaces
                for i in range(4):
                    x = start_x + dx * i * 30
                    y = start_y + dy * i * 30
                    self._draw_circle_antialiased(self.screen, COLORS[player.color], (x, y), 12)
                    pygame.gfxdraw.aacircle(self.screen, int(x), int(y), 12, COLORS["WHITE"])

    def get_screen_position_for_index(self, index: int) -> Tuple[int, int]:
        # Get screen position for a track index (0-27)
        if index in self.space_positions:
            return self.space_positions[index]
        return (0, 0)

    def get_peg_screen_position(self, peg: Peg) -> Tuple[int, int]:
        # Get the screen coordinates for a peg
        # Home base positions
        home_positions = {"RED": (150, 150), "BLUE": (1050, 150), "GREEN": (1050, 750), "YELLOW": (150, 750)}
        # Finish zone positions

        if peg.is_in_home:
            # Position in home base (2x2 grid)
            base_x, base_y = home_positions[peg.owner.color]
            pegs_in_home = peg.owner.get_pegs_in_home()
            index = pegs_in_home.index(peg) if peg in pegs_in_home else 0
            x = base_x - 30 + (index % 2) * 60
            y = base_y - 30 + (index // 2) * 60
            return (x, y)
        elif peg.is_in_finish:
            # Position in finish zone
            start_x, start_y = finish_positions[peg.owner.color]
            dx, dy = finish_directions[peg.owner.color]
            finish_index = peg.position - 100
            x = start_x + dx * finish_index * 30
            y = start_y + dy * finish_index * 30
            return (x, y)
        else:
            # Position on track
            if peg.position in self.space_positions:
                return self.space_positions[peg.position]
            return (0, 0)


    def render_pegs_with_animation(self, game_state: GameState):
        # Render all pegs, handling animation
        for player in game_state.players:
            for peg in player.pegs:
                x, y = 0, 0
                if game_state.is_animating_move and game_state.move_animation and game_state.move_animation['peg'] == peg:
                    # Calculate interpolated position along path
                    path = game_state.move_animation['path']
                    start_time = game_state.move_animation['start_time']
                    step_duration = game_state.move_animation['step_duration']
                    current_time = pygame.time.get_ticks()
                    
                    elapsed = current_time - start_time
                    total_steps = len(path) - 1
                    
                    if total_steps <= 0:
                        # Should not happen if path has at least start and end
                        x, y = self.get_peg_screen_position(peg)
                    else:
                        # Determine which step we are on
                        current_step_index = int(elapsed / step_duration)
                        
                        if current_step_index >= total_steps:
                            # Animation finished, stay at end
                            end_pos = path[-1]
                            coord = self._get_coord_for_pos(peg, end_pos)
                            x, y = coord
                        else:
                            # Interpolate between current step and next step
                            step_progress = (elapsed % step_duration) / step_duration
                            
                            start_pos = path[current_step_index]
                            end_pos = path[current_step_index + 1]
                            
                            start_coord = self._get_coord_for_pos(peg, start_pos)
                            end_coord = self._get_coord_for_pos(peg, end_pos)
                            
                            # Lerp
                            x = start_coord[0] + (end_coord[0] - start_coord[0]) * step_progress
                            y = start_coord[1] + (end_coord[1] - start_coord[1]) * step_progress
                else:
                    x, y = self.get_peg_screen_position(peg)
                # Cast to int for drawing
                ix, iy = int(x), int(y)

                # Draw peg shadow
                self._draw_shadow(self.screen, (ix, iy), 10, offset=(3, 3), alpha=80)

                # Draw peg body
                self._draw_circle_antialiased(self.screen, COLORS[player.color], (ix, iy), 12)
                
                # Draw shine/highlight on peg for 3D effect
                pygame.gfxdraw.filled_circle(self.screen, ix - 3, iy - 3, 4, (255, 255, 255, 100))
                
                # Outline
                pygame.gfxdraw.aacircle(self.screen, ix, iy, 12, (0, 0, 0))

    def _get_coord_for_pos(self, peg: Peg, pos: int) -> Tuple[int, int]:
        # Get screen coordinate for a logical position
        # Temporarily set peg position to get coordinate, then restore
        old_pos = peg.position
        old_home = peg.is_in_home
        old_finish = peg.is_in_finish
        
        peg.move_to(pos)
        coord = self.get_peg_screen_position(peg)
        
        # Restore
        peg.position = old_pos
        peg.is_in_home = old_home
        peg.is_in_finish = old_finish
        return coord

    def render_dice_button(self, enabled: bool, current_roll: Optional[int], mouse_pos: Tuple[int, int]):
        # Render the dice rolling button
        button_x = 600
        button_y = 800
        button_width = 180
        button_height = 70
        rect = pygame.Rect(button_x - button_width // 2, button_y - button_height // 2, button_width, button_height)

        # Check hover
        is_hovered = rect.collidepoint(mouse_pos) and enabled

        # Button color based on state
        if not enabled:
            button_color = COLORS["GRAY"]
            offset_y = 0
        elif is_hovered:
            button_color = (60, 220, 130) # Brighter green
            offset_y = -2 # Lift up effect
        else:
            button_color = COLORS["GREEN"]
            offset_y = 0

        # Draw shadow/sides for 3D effect
        shadow_rect = rect.copy()
        shadow_rect.move_ip(0, 5)
        pygame.draw.rect(self.screen, (30, 130, 70) if enabled else (100, 110, 110), shadow_rect, border_radius=15)

        # Draw main button face
        draw_rect = rect.copy()
        draw_rect.move_ip(0, offset_y)
        pygame.draw.rect(self.screen, button_color, draw_rect, border_radius=15)
        
        # Draw text
        if current_roll is not None:
            text = self.font_large.render(str(current_roll), True, COLORS["WHITE"])
        else:
            text = self.font_medium.render("ROLL", True, COLORS["WHITE"])

        text_rect = text.get_rect(center=(button_x, button_y + offset_y))
        self.screen.blit(text, text_rect)

    def render_player_indicator(self, current_player: Player):
        # Render indicator showing whose turn it is
        # Create a banner at the top
        banner_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 80)
        surface = pygame.Surface((SCREEN_WIDTH, 80), pygame.SRCALPHA)
        pygame.draw.rect(surface, (0, 0, 0, 100), banner_rect)
        self.screen.blit(surface, (0, 0))
        
        text = self.font_medium.render(f"{current_player.name}'s Turn", True, COLORS[current_player.color])
        text_rect = text.get_rect(center=(600, 40))
        
        # Add a glow/shadow to text
        shadow_text = self.font_medium.render(f"{current_player.name}'s Turn", True, (0, 0, 0))
        shadow_rect = shadow_text.get_rect(center=(602, 42))
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(text, text_rect)

    def render_message(self, message: str):
        # Render game status message
        if message:
            # Render below the player indicator
            text = self.font_small.render(message, True, COLORS["TEXT"])
            text_rect = text.get_rect(center=(600, 90))
            self.screen.blit(text, text_rect)

    def render_setup_screen(self, mouse_pos: Tuple[int, int]):
        # Render the game setup screen
        # Title
        title = self.font_large.render("TROUBLE", True, COLORS["YELLOW"])
        title_shadow = self.font_large.render("TROUBLE", True, (0, 0, 0))
        
        title_rect = title.get_rect(center=(600, 200))
        shadow_rect = title_shadow.get_rect(center=(604, 204))
        
        self.screen.blit(title_shadow, shadow_rect)
        self.screen.blit(title, title_rect)

        # Instructions
        instruction = self.font_medium.render("Select Number of Players", True, COLORS["TEXT"])
        instruction_rect = instruction.get_rect(center=(600, 300))
        self.screen.blit(instruction, instruction_rect)

        # Player count buttons
        button_y = 450
        button_spacing = 180
        start_x = 600 - (2 * button_spacing) // 2

        for i in range(2, 5):  # 2, 3, 4 players
            button_x = start_x + (i - 2) * button_spacing
            rect = pygame.Rect(button_x - 60, button_y - 50, 120, 100)
            is_hovered = rect.collidepoint(mouse_pos)
            offset_y = -5 if is_hovered else 0
            color = COLORS["BLUE"] if is_hovered else (41, 128, 185)
            # Shadow
            shadow_rect = rect.copy()
            shadow_rect.move_ip(0, 8)
            pygame.draw.rect(self.screen, (20, 60, 90), shadow_rect, border_radius=15)
            # Button
            draw_rect = rect.copy()
            draw_rect.move_ip(0, offset_y)
            pygame.draw.rect(self.screen, color, draw_rect, border_radius=15)
            # Text
            text = self.font_large.render(str(i), True, COLORS["WHITE"])
            text_rect = text.get_rect(center=(button_x, button_y + offset_y))
            self.screen.blit(text, text_rect)

    def render_game_over_screen(self, winner: Player, mouse_pos: Tuple[int, int] = (0, 0)):
        # Render the game over screen
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill(COLORS["BOARD_BG"])
        self.screen.blit(overlay, (0, 0))

        # Winner announcement
        title = self.font_large.render("GAME OVER!", True, COLORS["WHITE"])
        title_rect = title.get_rect(center=(600, 350))
        self.screen.blit(title, title_rect)

        if winner:
            winner_text = self.font_large.render(f"{winner.name} Wins!", True, COLORS[winner.color])
            winner_rect = winner_text.get_rect(center=(600, 450))
            self.screen.blit(winner_text, winner_rect)
        
        # Back to Menu button
        menu_button_rect = pygame.Rect(450, 600, 300, 70)
        is_menu_hovered = menu_button_rect.collidepoint(mouse_pos)
        offset_y = -3 if is_menu_hovered else 0
        menu_color = (60, 220, 130) if is_menu_hovered else COLORS["GREEN"]
        
        # Shadow
        shadow_rect = menu_button_rect.copy()
        shadow_rect.move_ip(0, 6)
        pygame.draw.rect(self.screen, (30, 130, 70), shadow_rect, border_radius=15)
        
        # Button
        draw_rect = menu_button_rect.copy()
        draw_rect.move_ip(0, offset_y)
        pygame.draw.rect(self.screen, menu_color, draw_rect, border_radius=15)
        
        # Text
        menu_text = self.font_medium.render("Back to Menu", True, COLORS["WHITE"])
        menu_text_rect = menu_text.get_rect(center=(600, 635 + offset_y))
        self.screen.blit(menu_text, menu_text_rect)

    def render_main_menu(self, mouse_pos: Tuple[int, int]):
        # Render the main menu screen
        import os
        
        # Background
        self.screen.fill(COLORS["BOARD_BG"])
        
        # Title
        title = self.font_large.render("TROUBLE", True, COLORS["YELLOW"])
        title_shadow = self.font_large.render("TROUBLE", True, (0, 0, 0))
        title_rect = title.get_rect(center=(600, 200))
        shadow_rect = title_shadow.get_rect(center=(604, 204))
        self.screen.blit(title_shadow, shadow_rect)
        self.screen.blit(title, title_rect)
        
        # Play Game button
        play_button_rect = pygame.Rect(450, 320, 300, 80)
        is_play_hovered = play_button_rect.collidepoint(mouse_pos)
        offset_y = -3 if is_play_hovered else 0
        play_color = (60, 220, 130) if is_play_hovered else COLORS["GREEN"]
        
        # Shadow
        shadow_rect = play_button_rect.copy()
        shadow_rect.move_ip(0, 6)
        pygame.draw.rect(self.screen, (30, 130, 70), shadow_rect, border_radius=15)
        
        # Button
        draw_rect = play_button_rect.copy()
        draw_rect.move_ip(0, offset_y)
        pygame.draw.rect(self.screen, play_color, draw_rect, border_radius=15)
        
        # Text
        play_text = self.font_medium.render("Play Game", True, COLORS["WHITE"])
        play_text_rect = play_text.get_rect(center=(600, 360 + offset_y))
        self.screen.blit(play_text, play_text_rect)
        
        # Rules button
        rules_button_rect = pygame.Rect(450, 420, 300, 80)
        is_rules_hovered = rules_button_rect.collidepoint(mouse_pos)
        offset_y_rules = -3 if is_rules_hovered else 0
        rules_color = (241, 196, 15) if is_rules_hovered else COLORS["YELLOW"]
        
        # Shadow
        shadow_rect = rules_button_rect.copy()
        shadow_rect.move_ip(0, 6)
        pygame.draw.rect(self.screen, (180, 140, 10), shadow_rect, border_radius=15)
        
        # Button
        draw_rect = rules_button_rect.copy()
        draw_rect.move_ip(0, offset_y_rules)
        pygame.draw.rect(self.screen, rules_color, draw_rect, border_radius=15)
        
        # Text
        rules_text = self.font_medium.render("Rules", True, COLORS["BLACK"])
        rules_text_rect = rules_text.get_rect(center=(600, 460 + offset_y_rules))
        self.screen.blit(rules_text, rules_text_rect)
        
        # View Results button
        results_button_rect = pygame.Rect(450, 520, 300, 80)
        results_exist = os.path.exists("game_results")
        is_results_hovered = results_button_rect.collidepoint(mouse_pos) and results_exist
        offset_y_results = -3 if is_results_hovered else 0
        
        if results_exist:
            results_color = (52, 152, 219) if is_results_hovered else COLORS["BLUE"]
            shadow_color = (20, 60, 90)
        else:
            results_color = COLORS["GRAY"]
            shadow_color = (100, 110, 110)
        
        # Shadow
        shadow_rect = results_button_rect.copy()
        shadow_rect.move_ip(0, 6)
        pygame.draw.rect(self.screen, shadow_color, shadow_rect, border_radius=15)
        
        # Button
        draw_rect = results_button_rect.copy()
        draw_rect.move_ip(0, offset_y_results)
        pygame.draw.rect(self.screen, results_color, draw_rect, border_radius=15)
        
        # Text
        results_text = self.font_medium.render("View Results", True, COLORS["WHITE"])
        results_text_rect = results_text.get_rect(center=(600, 560 + offset_y_results))
        self.screen.blit(results_text, results_text_rect)
        
        # Disabled message if no results
        if not results_exist:
            disabled_text = self.font_small.render("(No results available)", True, COLORS["GRAY"])
            disabled_rect = disabled_text.get_rect(center=(600, 615))
            self.screen.blit(disabled_text, disabled_rect)

    def render_results_screen(self, results_data: List[str], mouse_pos: Tuple[int, int]):
        # Render the results viewing screen
        self.screen.fill(COLORS["BOARD_BG"])
        
        # Title
        title = self.font_medium.render("Past Game Results", True, COLORS["YELLOW"])
        title_rect = title.get_rect(center=(600, 50))
        self.screen.blit(title, title_rect)
        
        # Display results
        if not results_data:
            no_results = self.font_small.render("No game results found", True, COLORS["TEXT"])
            no_results_rect = no_results.get_rect(center=(600, 400))
            self.screen.blit(no_results, no_results_rect)
        else:
            # Show most recent game
            y_offset = 120
            lines = results_data[0].split('\n')
            
            for line in lines[:20]:  # Limit to first 20 lines
                if line.strip():
                    text = self.font_small.render(line, True, COLORS["TEXT"])
                    text_rect = text.get_rect(center=(600, y_offset))
                    self.screen.blit(text, text_rect)
                    y_offset += 30
            
            # Show count of total games
            if len(results_data) > 1:
                count_text = self.font_small.render(f"Showing most recent of {len(results_data)} games", True, COLORS["GRAY"])
                count_rect = count_text.get_rect(center=(600, 680))
                self.screen.blit(count_text, count_rect)
        
        # Back button
        back_button_rect = pygame.Rect(450, 750, 300, 60)
        is_back_hovered = back_button_rect.collidepoint(mouse_pos)
        offset_y = -3 if is_back_hovered else 0
        back_color = (60, 220, 130) if is_back_hovered else COLORS["GREEN"]
        
        # Shadow
        shadow_rect = back_button_rect.copy()
        shadow_rect.move_ip(0, 5)
        pygame.draw.rect(self.screen, (30, 130, 70), shadow_rect, border_radius=15)
        
        # Button
        draw_rect = back_button_rect.copy()
        draw_rect.move_ip(0, offset_y)
        pygame.draw.rect(self.screen, back_color, draw_rect, border_radius=15)
        
        # Text
        back_text = self.font_medium.render("Back", True, COLORS["WHITE"])
        back_text_rect = back_text.get_rect(center=(600, 780 + offset_y))
        self.screen.blit(back_text, back_text_rect)

    def highlight_pegs(self, pegs: List[Peg]):
        #Highlight valid pegs for selection
        for peg in pegs:
            x, y = self.get_peg_screen_position(peg)

            # Draw pulsating highlight (could animate radius based on time if we had it)
            self._draw_circle_antialiased(self.screen, COLORS["HIGHLIGHT"], (x, y), 20)
            
            # Redraw peg on top
            self._draw_circle_antialiased(self.screen, COLORS[peg.owner.color], (x, y), 12)
            pygame.gfxdraw.aacircle(self.screen, x, y, 12, (0, 0, 0))

    def get_clicked_peg(self, mouse_pos: Tuple[int, int], players: List[Player]) -> Optional[Peg]:
        # Detect which peg was clicked
        mouse_x, mouse_y = mouse_pos
        # Check all pegs for all players
        for player in players:
            for peg in player.pegs:
                peg_x, peg_y = self.get_peg_screen_position(peg)
                # Calculate distance from mouse to peg center
                distance = ((mouse_x - peg_x) ** 2 + (mouse_y - peg_y) ** 2) ** 0.5
                # If within peg radius (12 pixels + some tolerance)
                if distance <= 20:
                    return peg
        return None

    def is_dice_button_clicked(self, mouse_pos: Tuple[int, int]) -> bool:
        # Check if the dice button was clicked
        mouse_x, mouse_y = mouse_pos

        button_x = 600
        button_y = 800
        button_width = 180
        button_height = 70

        # Check if mouse is within button bounds
        if (button_x - button_width // 2 <= mouse_x <= button_x + button_width // 2 and button_y - button_height // 2 <= mouse_y <= button_y + button_height // 2):
            return True
        return False
    
    def is_menu_button_clicked(self, mouse_pos: Tuple[int, int]) -> bool:
        # Check if the back to menu button was clicked on game over screen
        menu_button_rect = pygame.Rect(450, 600, 300, 70)
        return menu_button_rect.collidepoint(mouse_pos)
    
    def render_pause_button(self, mouse_pos: Tuple[int, int]):
        """Render the pause/menu button in the top-left corner"""
        button_x = 80
        button_y = 40
        button_size = 50
        
        rect = pygame.Rect(button_x - button_size // 2, button_y - button_size // 2, button_size, button_size)
        is_hovered = rect.collidepoint(mouse_pos)
        
        # Button color
        if is_hovered:
            button_color = (70, 80, 90)
            offset_y = -2
        else:
            button_color = (52, 73, 94)
            offset_y = 0
        
        # Shadow
        shadow_rect = rect.copy()
        shadow_rect.move_ip(0, 4)
        pygame.draw.rect(self.screen, (30, 40, 50), shadow_rect, border_radius=8)
        
        # Button
        draw_rect = rect.copy()
        draw_rect.move_ip(0, offset_y)
        pygame.draw.rect(self.screen, button_color, draw_rect, border_radius=8)
        
        # Draw three horizontal lines (hamburger menu icon)
        line_color = COLORS["WHITE"]
        line_width = 30
        line_height = 3
        line_spacing = 7
        
        for i in range(3):
            line_y = button_y + offset_y - line_spacing + i * line_spacing
            line_rect = pygame.Rect(button_x - line_width // 2, line_y - line_height // 2, line_width, line_height)
            pygame.draw.rect(self.screen, line_color, line_rect, border_radius=2)
    
    def is_pause_button_clicked(self, mouse_pos: Tuple[int, int]) -> bool:
        """Check if the pause button was clicked"""
        button_x = 80
        button_y = 40
        button_size = 50
        
        rect = pygame.Rect(button_x - button_size // 2, button_y - button_size // 2, button_size, button_size)
        return rect.collidepoint(mouse_pos)
    
    def render_pause_menu(self, mouse_pos: Tuple[int, int]):
        """Render the pause menu overlay"""
        # Create blurred/darkened overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((30, 40, 50))
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title = self.font_large.render("PAUSED", True, COLORS["WHITE"])
        title_rect = title.get_rect(center=(600, 250))
        self.screen.blit(title, title_rect)
        
        # Rules button
        rules_button_rect = pygame.Rect(450, 330, 300, 70)
        is_rules_hovered = rules_button_rect.collidepoint(mouse_pos)
        offset_y_rules = -3 if is_rules_hovered else 0
        rules_color = (241, 196, 15) if is_rules_hovered else COLORS["YELLOW"]
        
        # Shadow
        shadow_rect = rules_button_rect.copy()
        shadow_rect.move_ip(0, 5)
        pygame.draw.rect(self.screen, (180, 140, 10), shadow_rect, border_radius=15)
        
        # Button
        draw_rect = rules_button_rect.copy()
        draw_rect.move_ip(0, offset_y_rules)
        pygame.draw.rect(self.screen, rules_color, draw_rect, border_radius=15)
        
        # Text
        rules_text = self.font_medium.render("Rules", True, COLORS["BLACK"])
        rules_text_rect = rules_text.get_rect(center=(600, 365 + offset_y_rules))
        self.screen.blit(rules_text, rules_text_rect)
        
        # Back to Main Menu button
        menu_button_rect = pygame.Rect(450, 420, 300, 70)
        is_menu_hovered = menu_button_rect.collidepoint(mouse_pos)
        offset_y_menu = -3 if is_menu_hovered else 0
        menu_color = (60, 220, 130) if is_menu_hovered else COLORS["GREEN"]
        
        # Shadow
        shadow_rect = menu_button_rect.copy()
        shadow_rect.move_ip(0, 5)
        pygame.draw.rect(self.screen, (30, 130, 70), shadow_rect, border_radius=15)
        
        # Button
        draw_rect = menu_button_rect.copy()
        draw_rect.move_ip(0, offset_y_menu)
        pygame.draw.rect(self.screen, menu_color, draw_rect, border_radius=15)
        
        # Text
        menu_text = self.font_medium.render("Main Menu", True, COLORS["WHITE"])
        menu_text_rect = menu_text.get_rect(center=(600, 455 + offset_y_menu))
        self.screen.blit(menu_text, menu_text_rect)
        
        # Exit button
        exit_button_rect = pygame.Rect(450, 510, 300, 70)
        is_exit_hovered = exit_button_rect.collidepoint(mouse_pos)
        offset_y_exit = -3 if is_exit_hovered else 0
        exit_color = (231, 76, 60) if is_exit_hovered else COLORS["RED"]
        
        # Shadow
        shadow_rect = exit_button_rect.copy()
        shadow_rect.move_ip(0, 5)
        pygame.draw.rect(self.screen, (150, 40, 30), shadow_rect, border_radius=15)
        
        # Button
        draw_rect = exit_button_rect.copy()
        draw_rect.move_ip(0, offset_y_exit)
        pygame.draw.rect(self.screen, exit_color, draw_rect, border_radius=15)
        
        # Text
        exit_text = self.font_medium.render("Exit Game", True, COLORS["WHITE"])
        exit_text_rect = exit_text.get_rect(center=(600, 545 + offset_y_exit))
        self.screen.blit(exit_text, exit_text_rect)
    
    def render_rules_screen(self, mouse_pos: Tuple[int, int]):
        """Render the rules screen"""
        self.screen.fill(COLORS["BOARD_BG"])
        
        # Title
        title = self.font_large.render("HOW TO PLAY", True, COLORS["YELLOW"])
        title_rect = title.get_rect(center=(600, 50))
        self.screen.blit(title, title_rect)
        
        # Rules text
        rules = [
            "OBJECTIVE:",
            "Be the first player to move all 4 pegs around the board",
            "and into your finish zone.",
            "",
            "GAMEPLAY:",
            "• Click ROLL to roll the die",
            "• Click a highlighted peg to move it",
            "• Roll a 1 or 6 to move a peg out of home",
            "• Land on an opponent's peg to send it back home",
            "",
            "SPECIAL SPACES:",
            "• Double Trouble (orange) - Roll again!",
            "",
            "BONUS ROLLS:",
            "• Roll a 6 - Get another roll (max 2 rolls per turn)",
            "• Land on Double Trouble - Get another roll",
            "",
            "WINNING:",
            "• Move all 4 pegs into your colored finish zone",
            "• Must land exactly on the last space"
        ]
        
        y_offset = 130
        for line in rules:
            if line.startswith("OBJECTIVE:") or line.startswith("GAMEPLAY:") or \
               line.startswith("SPECIAL SPACES:") or line.startswith("BONUS ROLLS:") or \
               line.startswith("WINNING:"):
                # Section headers
                text = self.font_medium.render(line, True, COLORS["YELLOW"])
            elif line.startswith("•"):
                # Bullet points
                text = self.font_small.render(line, True, COLORS["TEXT"])
            else:
                # Regular text
                text = self.font_small.render(line, True, COLORS["WHITE"])
            
            text_rect = text.get_rect(center=(600, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 32
        
        # Back button
        back_button_rect = pygame.Rect(450, 750, 300, 60)
        is_back_hovered = back_button_rect.collidepoint(mouse_pos)
        offset_y = -3 if is_back_hovered else 0
        back_color = (60, 220, 130) if is_back_hovered else COLORS["GREEN"]
        
        # Shadow
        shadow_rect = back_button_rect.copy()
        shadow_rect.move_ip(0, 5)
        pygame.draw.rect(self.screen, (30, 130, 70), shadow_rect, border_radius=15)
        
        # Button
        draw_rect = back_button_rect.copy()
        draw_rect.move_ip(0, offset_y)
        pygame.draw.rect(self.screen, back_color, draw_rect, border_radius=15)
        
        # Text
        back_text = self.font_medium.render("Back", True, COLORS["WHITE"])
        back_text_rect = back_text.get_rect(center=(600, 780 + offset_y))
        self.screen.blit(back_text, back_text_rect)

def main():
    """Entry point for the Trouble game"""
    try:
        game = TroubleGame()
        game.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()