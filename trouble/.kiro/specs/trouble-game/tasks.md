# Implementation Plan

- [x] 1. Set up project structure
  - Create main.py, game_state.py, and renderer.py files
  - Create requirements.txt with pygame>=2.5.0
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Implement core game logic in game_state.py
- [x] 2.1 Implement Peg, Player, and GameState classes
  - Create Peg class with position tracking and move methods
  - Create Player class with peg management methods
  - Create GameState class with game initialization
  - _Requirements: 1.3, 1.4, 1.5, 3.1, 3.2, 3.3, 4.1, 6.4_

- [x] 2.2 Implement dice rolling and turn management
  - Implement roll_dice() method (returns 1-6)
  - Implement get_current_player() and advance_turn() methods
  - Track rolls_this_turn counter
  - _Requirements: 2.2, 9.1, 9.2, 9.5_

- [x] 2.3 Implement move validation and execution
  - Implement board_occupancy tracking
  - Implement get_valid_pegs() for all roll types (1, 2-5, 6)
  - Implement move_peg() with position calculation and board updates
  - _Requirements: 3.1, 3.2, 3.3, 3.5, 4.3_

- [x] 2.4 Implement capture mechanics
  - Implement check_capture() method
  - Integrate capture into move_peg() to send opponent pegs home
  - _Requirements: 4.1_

- [x] 2.5 Implement finish zone logic
  - Implement finish zone entry detection (no exact count needed)
  - Implement finish zone placement (sequential positions 100-103)
  - Prevent entry to other players' finish zones
  - _Requirements: 4.4, 6.1, 6.2, 6.3_

- [x] 2.6 Implement bonus roll mechanics
  - Implement is_double_trouble() method (positions 3, 10, 17, 24)
  - Implement should_grant_bonus_roll() with 2-roll limit
  - _Requirements: 5.1, 5.2, 5.3, 10.1_

- [x] 2.7 Implement win condition and no valid moves
  - Implement check_win_condition() (4 pegs in finish)
  - Add logic to auto-skip turn when no valid moves
  - _Requirements: 6.4, 9.3_

- [x] 3. Implement rendering in renderer.py
- [x] 3.1 Create GameRenderer class and board rendering
  - Initialize pygame screen, fonts, and color constants
  - Calculate and cache board space positions
  - Implement render_board(), render_track_spaces(), render_home_bases(), render_finish_zones()
  - Visually distinguish double trouble spaces
  - _Requirements: 7.1, 10.2_

- [x] 3.2 Implement peg and UI rendering
  - Implement get_peg_screen_position() and render_pegs()
  - Implement render_dice_button() with roll display
  - Implement render_player_indicator() and render_message()
  - Implement highlight_pegs() for valid selections
  - _Requirements: 2.1, 2.4, 7.2, 7.3, 7.4, 7.5_

- [x] 3.3 Implement setup and game over screens
  - Implement render_setup_screen() for player count selection
  - Implement render_game_over_screen() with winner display
  - Implement render_all() to orchestrate all rendering
  - _Requirements: 1.1, 1.2, 6.5_

- [x] 3.4 Implement input detection
  - Implement get_clicked_peg() to detect peg clicks
  - Implement is_dice_button_clicked() to detect button clicks
  - _Requirements: 2.1, 3.4_

- [ ] 4. Implement game loop in main.py
- [x] 4.1 Create TroubleGame class and setup handling
  - Initialize GameState and GameRenderer
  - Set up pygame window and clock
  - Implement handle_setup_click() for player count selection
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 4.2 Implement game interaction handlers
  - Implement handle_dice_click() to process rolls and check for valid moves
  - Implement handle_peg_click() to execute moves, check captures, bonus rolls, and win condition
  - _Requirements: 2.1, 2.2, 3.2, 3.3, 5.1, 5.2, 9.1, 9.3_

- [x] 4.3 Implement main game loop
  - Implement handle_events() for pygame event processing
  - Implement run() method with 60 FPS game loop
  - Create main() entry point
  - _Requirements: 1.1, 2.1, 3.4_
