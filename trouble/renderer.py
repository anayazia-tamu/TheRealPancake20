"""
Trouble Game - Rendering and Display
Handles all visual rendering and UI display
"""

import pygame
from typing import Tuple, List, Optional, Dict
from game_state import GameState, Player, Peg


# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900

# Color definitions
COLORS = {
    "RED": (220, 50, 50),
    "BLUE": (50, 120, 220),
    "GREEN": (50, 200, 80),
    "YELLOW": (240, 220, 50),
    "BOARD_BG": (240, 230, 210),
    "TRACK": (255, 255, 255),
    "DOUBLE_TROUBLE": (255, 200, 50),
    "HIGHLIGHT": (100, 255, 100),
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "GRAY": (128, 128, 128),
}


class GameRenderer:
    """Handles all rendering for the Trouble game"""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)

        self.board_center = (600, 450)
        self.track_radius = 250
        self.space_positions: Dict[int, Tuple[int, int]] = {}

        # Calculate and cache board space positions
        self._calculate_space_positions()

    def render_all(self, game_state: GameState, setup_mode: bool = False):
        """Render the complete game state"""
        self.screen.fill(COLORS["BOARD_BG"])

        if setup_mode:
            self.render_setup_screen()
        elif game_state.game_over:
            self.render_game_over_screen(game_state.winner)
        else:
            self.render_board()
            self.render_track_spaces()
            self.render_home_bases(game_state.players)
            self.render_finish_zones(game_state.players)
            self.render_pegs(game_state.players)
            self.render_dice_button(
                game_state.current_roll is None, game_state.current_roll
            )

            if game_state.players:
                current_player = game_state.get_current_player()
                if current_player:
                    self.render_player_indicator(current_player)

            self.render_message(game_state.message)

    def _calculate_space_positions(self):
        """Calculate and cache positions for all board spaces"""
        import math

        # Calculate positions for 28 track spaces in a circle
        for i in range(28):
            angle = (i / 28) * 2 * math.pi - math.pi / 2  # Start at top
            x = self.board_center[0] + int(self.track_radius * math.cos(angle))
            y = self.board_center[1] + int(self.track_radius * math.sin(angle))
            self.space_positions[i] = (x, y)

    def render_board(self):
        """Render the main board background"""
        # Draw a large circle for the board
        pygame.draw.circle(
            self.screen, COLORS["TRACK"], self.board_center, self.track_radius + 30, 0
        )

        # Draw center circle
        pygame.draw.circle(self.screen, COLORS["BOARD_BG"], self.board_center, 80, 0)

    def render_track_spaces(self):
        """Render the playing track spaces"""
        # Double trouble spaces
        double_trouble_positions = [3, 10, 17, 24]

        for position, (x, y) in self.space_positions.items():
            # Determine color based on whether it's a double trouble space
            if position in double_trouble_positions:
                color = COLORS["DOUBLE_TROUBLE"]
            else:
                color = COLORS["WHITE"]

            # Draw the space
            pygame.draw.circle(self.screen, color, (x, y), 15, 0)
            pygame.draw.circle(self.screen, COLORS["BLACK"], (x, y), 15, 2)

            # Draw position number for debugging (optional)
            # text = self.font_small.render(str(position), True, COLORS["BLACK"])
            # self.screen.blit(text, (x - 10, y - 10))

    def render_home_bases(self, players: List[Player]):
        """Render home bases for all players"""
        # Home base positions in corners
        home_positions = {
            "RED": (150, 150),
            "BLUE": (1050, 150),
            "GREEN": (1050, 750),
            "YELLOW": (150, 750),
        }

        for player in players:
            if player.color in home_positions:
                base_x, base_y = home_positions[player.color]

                # Draw home base background
                pygame.draw.rect(
                    self.screen,
                    COLORS[player.color],
                    (base_x - 60, base_y - 60, 120, 120),
                    0,
                )
                pygame.draw.rect(
                    self.screen,
                    COLORS["BLACK"],
                    (base_x - 60, base_y - 60, 120, 120),
                    3,
                )

                # Draw 4 spots for pegs in a 2x2 grid
                for i in range(4):
                    spot_x = base_x - 30 + (i % 2) * 60
                    spot_y = base_y - 30 + (i // 2) * 60
                    pygame.draw.circle(
                        self.screen, COLORS["WHITE"], (spot_x, spot_y), 12, 2
                    )

    def render_finish_zones(self, players: List[Player]):
        """Render finish zones for all players"""
        # Finish zone positions extending toward center
        finish_positions = {
            "RED": (600, 350),
            "BLUE": (700, 450),
            "GREEN": (600, 550),
            "YELLOW": (500, 450),
        }

        # Direction vectors for finish zones
        finish_directions = {
            "RED": (0, -1),  # Up
            "BLUE": (1, 0),  # Right
            "GREEN": (0, 1),  # Down
            "YELLOW": (-1, 0),  # Left
        }

        for player in players:
            if player.color in finish_positions:
                start_x, start_y = finish_positions[player.color]
                dx, dy = finish_directions[player.color]

                # Draw 4 finish spaces
                for i in range(4):
                    x = start_x + dx * i * 30
                    y = start_y + dy * i * 30

                    pygame.draw.circle(self.screen, COLORS[player.color], (x, y), 12, 0)
                    pygame.draw.circle(self.screen, COLORS["BLACK"], (x, y), 12, 2)

    def get_peg_screen_position(self, peg: Peg) -> Tuple[int, int]:
        """Get the screen coordinates for a peg"""
        # Home base positions
        home_positions = {
            "RED": (150, 150),
            "BLUE": (1050, 150),
            "GREEN": (1050, 750),
            "YELLOW": (150, 750),
        }

        # Finish zone positions
        finish_positions = {
            "RED": (600, 350),
            "BLUE": (700, 450),
            "GREEN": (600, 550),
            "YELLOW": (500, 450),
        }

        finish_directions = {
            "RED": (0, -1),
            "BLUE": (1, 0),
            "GREEN": (0, 1),
            "YELLOW": (-1, 0),
        }

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

    def render_pegs(self, players: List[Player]):
        """Render all pegs on the board"""
        for player in players:
            for peg in player.pegs:
                x, y = self.get_peg_screen_position(peg)

                # Draw peg
                pygame.draw.circle(self.screen, COLORS[player.color], (x, y), 10, 0)
                pygame.draw.circle(self.screen, COLORS["BLACK"], (x, y), 10, 2)

    def render_dice_button(self, enabled: bool, current_roll: Optional[int]):
        """Render the dice rolling button"""
        button_x = 600
        button_y = 800
        button_width = 150
        button_height = 60

        # Button color based on state
        if enabled:
            button_color = COLORS["GREEN"]
        else:
            button_color = COLORS["GRAY"]

        # Draw button
        pygame.draw.rect(
            self.screen,
            button_color,
            (
                button_x - button_width // 2,
                button_y - button_height // 2,
                button_width,
                button_height,
            ),
            0,
            10,
        )
        pygame.draw.rect(
            self.screen,
            COLORS["BLACK"],
            (
                button_x - button_width // 2,
                button_y - button_height // 2,
                button_width,
                button_height,
            ),
            3,
            10,
        )

        # Draw text
        if current_roll is not None:
            text = self.font_large.render(str(current_roll), True, COLORS["BLACK"])
        else:
            text = self.font_small.render("ROLL", True, COLORS["BLACK"])

        text_rect = text.get_rect(center=(button_x, button_y))
        self.screen.blit(text, text_rect)

    def render_player_indicator(self, current_player: Player):
        """Render indicator showing whose turn it is"""
        text = self.font_small.render(
            f"{current_player.name}'s Turn", True, COLORS[current_player.color]
        )
        text_rect = text.get_rect(center=(600, 50))
        self.screen.blit(text, text_rect)

    def render_message(self, message: str):
        """Render game status message"""
        if message:
            text = self.font_small.render(message, True, COLORS["BLACK"])
            text_rect = text.get_rect(center=(600, 100))
            self.screen.blit(text, text_rect)

    def render_setup_screen(self):
        """Render the game setup screen"""
        # Title
        title = self.font_large.render("TROUBLE", True, COLORS["BLACK"])
        title_rect = title.get_rect(center=(600, 200))
        self.screen.blit(title, title_rect)

        # Instructions
        instruction = self.font_small.render(
            "Select Number of Players", True, COLORS["BLACK"]
        )
        instruction_rect = instruction.get_rect(center=(600, 300))
        self.screen.blit(instruction, instruction_rect)

        # Player count buttons
        button_y = 450
        button_spacing = 150
        start_x = 600 - (3 * button_spacing) // 2

        for i in range(2, 5):  # 2, 3, 4 players
            button_x = start_x + (i - 2) * button_spacing

            # Draw button
            pygame.draw.rect(
                self.screen,
                COLORS["BLUE"],
                (button_x - 50, button_y - 40, 100, 80),
                0,
                10,
            )
            pygame.draw.rect(
                self.screen,
                COLORS["BLACK"],
                (button_x - 50, button_y - 40, 100, 80),
                3,
                10,
            )

            # Draw text
            text = self.font_large.render(str(i), True, COLORS["WHITE"])
            text_rect = text.get_rect(center=(button_x, button_y))
            self.screen.blit(text, text_rect)

    def render_game_over_screen(self, winner: Player):
        """Render the game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(COLORS["WHITE"])
        self.screen.blit(overlay, (0, 0))

        # Winner announcement
        title = self.font_large.render("GAME OVER!", True, COLORS["BLACK"])
        title_rect = title.get_rect(center=(600, 350))
        self.screen.blit(title, title_rect)

        if winner:
            winner_text = self.font_large.render(
                f"{winner.name} Wins!", True, COLORS[winner.color]
            )
            winner_rect = winner_text.get_rect(center=(600, 450))
            self.screen.blit(winner_text, winner_rect)

    def highlight_pegs(self, pegs: List[Peg]):
        """Highlight valid pegs for selection"""
        for peg in pegs:
            x, y = self.get_peg_screen_position(peg)

            # Draw highlight circle around peg
            pygame.draw.circle(self.screen, COLORS["HIGHLIGHT"], (x, y), 15, 3)

    def get_clicked_peg(
        self, mouse_pos: Tuple[int, int], players: List[Player]
    ) -> Optional[Peg]:
        """Detect which peg was clicked"""
        mouse_x, mouse_y = mouse_pos

        # Check all pegs for all players
        for player in players:
            for peg in player.pegs:
                peg_x, peg_y = self.get_peg_screen_position(peg)

                # Calculate distance from mouse to peg center
                distance = ((mouse_x - peg_x) ** 2 + (mouse_y - peg_y) ** 2) ** 0.5

                # If within peg radius (10 pixels + some tolerance)
                if distance <= 15:
                    return peg

        return None

    def is_dice_button_clicked(self, mouse_pos: Tuple[int, int]) -> bool:
        """Check if the dice button was clicked"""
        mouse_x, mouse_y = mouse_pos

        button_x = 600
        button_y = 800
        button_width = 150
        button_height = 60

        # Check if mouse is within button bounds
        if (
            button_x - button_width // 2 <= mouse_x <= button_x + button_width // 2
            and button_y - button_height // 2
            <= mouse_y
            <= button_y + button_height // 2
        ):
            return True

        return False
