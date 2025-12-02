# Trouble Game - Rendering and Display
# Handles all visual rendering and UI display
import pygame
import pygame.gfxdraw
import math
from typing import Tuple, List, Optional, Dict
from game_state import GameState, Player, Peg
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
        # Finish zone positions extending toward center
        #finish_positions = {"RED": (600, 350), "BLUE": (700, 450), "GREEN": (600, 550), "YELLOW": (500, 450)}
        # Direction vectors for finish zones
        #finish_directions = {"RED": (0, -1), "BLUE": (1, 0), "GREEN": (0, 1), "YELLOW": (-1, 0)} # Up, Right, Down, Left

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
        #finish_positions = {"RED": (600, 350), "BLUE": (700, 450), "GREEN": (600, 550), "YELLOW": (500, 450)}

        #finish_directions = {"RED": (0, -1), "BLUE": (1, 0), "GREEN": (0, 1), "YELLOW": (-1, 0)} # Up, Right, Down, Left

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
        # Render all pegs on the board
        for player in players:
            for peg in player.pegs:
                # Check if this peg is currently animating
                is_animating = False
                # We need to access the game state to check animation, but render_pegs only takes players list.
                # Ideally we should pass game_state or handle this differently.
                # For now, let's assume we can't easily access game_state here without changing signature.
                # Wait, render_pegs is called from render_all which has game_state.
                # Let's update render_pegs signature in a separate step or just do it here if we can see the caller.
                # The caller is render_all(self, game_state...).
                # So we should update render_pegs to take game_state instead of players, or pass animation info.
                pass

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
        play_button_rect = pygame.Rect(450, 350, 300, 80)
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
        play_text_rect = play_text.get_rect(center=(600, 390 + offset_y))
        self.screen.blit(play_text, play_text_rect)
        
        # View Results button
        results_button_rect = pygame.Rect(450, 470, 300, 80)
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
        results_text_rect = results_text.get_rect(center=(600, 510 + offset_y_results))
        self.screen.blit(results_text, results_text_rect)
        
        # Disabled message if no results
        if not results_exist:
            disabled_text = self.font_small.render("(No results available)", True, COLORS["GRAY"])
            disabled_rect = disabled_text.get_rect(center=(600, 565))
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
        """Render the pause/menu button in the top-right corner"""
        button_x = 1120
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
        button_x = 1120
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
        
        # Back to Main Menu button
        menu_button_rect = pygame.Rect(450, 380, 300, 70)
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
        menu_text_rect = menu_text.get_rect(center=(600, 415 + offset_y_menu))
        self.screen.blit(menu_text, menu_text_rect)
        
        # Exit button
        exit_button_rect = pygame.Rect(450, 480, 300, 70)
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
        exit_text_rect = exit_text.get_rect(center=(600, 515 + offset_y_exit))
        self.screen.blit(exit_text, exit_text_rect)
