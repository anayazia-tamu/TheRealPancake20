"""
Trouble Game - Main Entry Point
Handles game loop and event processing
"""

import pygame
from game_state import GameState
from renderer import GameRenderer


class TroubleGame:
    """Main game controller that manages the game loop and user interactions"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 900))
        pygame.display.set_caption("Trouble Game")
        self.clock = pygame.time.Clock()

        self.game_state = GameState()
        self.renderer = GameRenderer(self.screen)

        self.setup_mode = True
        self.waiting_for_peg_selection = False

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
            pygame.display.flip()

        pygame.quit()

    def handle_events(self, mouse_pos):
        """Handle mouse click events"""
        if self.setup_mode:
            self.handle_setup_click(mouse_pos)
        else:
            self.handle_game_click(mouse_pos)

    def handle_setup_click(self, mouse_pos):
        """Handle clicks during game setup"""
        # Check which player count button was clicked
        button_y = 450
        button_spacing = 150
        start_x = 600 - (3 * button_spacing) // 2

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

    def handle_game_click(self, mouse_pos):
        """Handle clicks during gameplay"""
        # Don't allow clicks if game is over
        if self.game_state.game_over:
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
        # Only allow dice roll if no current roll exists
        if self.game_state.current_roll is not None:
            return

        # Roll the dice
        roll = self.game_state.roll_dice()
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

        # Execute the move
        move_result = self.game_state.move_peg(peg, self.game_state.current_roll)

        if not move_result["success"]:
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

    def render(self):
        """Render the current game state"""
        self.renderer.render_all(self.game_state, self.setup_mode)

        # Highlight valid pegs if waiting for selection
        if self.waiting_for_peg_selection and self.game_state.current_roll is not None:
            valid_pegs = self.game_state.get_valid_pegs(self.game_state.current_roll)
            self.renderer.highlight_pegs(valid_pegs)


def main():
    """Entry point for the Trouble game"""
    game = TroubleGame()
    game.run()


if __name__ == "__main__":
    main()
