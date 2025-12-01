"""
Trouble Game - Game State and Logic
Contains all game rules, state management, and business logic
"""

from typing import List, Optional, Dict
import random


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

        # If peg is in finish zone, can't move
        if peg.is_in_finish:
            return None

        # Calculate new position on track
        new_pos = peg.position + roll

        # Check if peg should enter finish zone
        finish_entry = self.FINISH_ENTRY_POSITIONS[current_player.color]

        # Determine if we've passed or reached the finish entry
        # Handle wrap-around: if new_pos >= 28, we've wrapped around the board
        if new_pos > finish_entry or new_pos >= 28:
            # Check if we actually crossed the finish entry point
            # This happens when: current position <= finish_entry < new position (before wrap)
            if peg.position <= finish_entry:
                # We're approaching from before the entry point
                if new_pos > finish_entry:
                    # Enter finish zone - no exact count needed
                    # Place in next available finish position
                    finish_pegs = current_player.get_pegs_in_finish()
                    finish_index = len(finish_pegs)

                    if finish_index < 4:
                        return 100 + finish_index
                    # All finish spots taken (shouldn't happen in normal play)
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
