# Trouble Game Design Document

## Overview

The Trouble game will be implemented in Python using Pygame as the primary UI framework. Pygame provides excellent support for 2D graphics, animations, and event handling, making it ideal for a board game implementation. The architecture will follow a Model-View-Controller (MVC) pattern to separate game logic from presentation, ensuring maintainability and testability.

The game will support 2-4 players on a single device, with smooth animations for dice rolling and piece movements. The UI will be intuitive with clear visual feedback for valid moves, current player turns, and game state changes.

## Architecture

### Simplified File Structure

The game will be organized into 3 main files:

1.**main.py** - Entry point, game loop, and event handling

2.**game_state.py** - Game state, rules, and logic (Player, Peg, GameState classes)

3.**renderer.py** - All rendering and visual display

### High-Level Architecture

```

┌──────────────────────────────────────────┐

│            main.py (Game Loop)           │

│  - Event handling (mouse clicks)         │

│  - Game control flow                     │

│  - Main game loop                        │

└──────────────────────────────────────────┘

         │                    │

         ▼                    ▼

┌─────────────────┐  ┌─────────────────────┐

│  game_state.py  │  │    renderer.py      │

│  - GameState    │  │  - GameRenderer     │

│  - Player       │  │  (handles all       │

│  - Peg          │  │   drawing)          │

│  (all logic)    │  │                     │

└─────────────────┘  └─────────────────────┘

```

## Components and Interfaces

### 1. game_state.py

**Purpose**: All game logic, state management, and rules in one file

```python

class Player:

    - color: str

    - pegs: List[Peg]

    - name: str


    + get_pegs_in_home() -> List[Peg]

    + get_pegs_on_track() -> List[Peg]

    + get_pegs_in_finish() -> List[Peg]

    + has_won() -> bool


class Peg:

    - owner: Player

    - position: int (track position, -1for home, 100+ for finish)

    - is_in_home: bool

    - is_in_finish: bool


    + move_to(position: int) -> None

    + send_home() -> None


class GameState:

    - players: List[Player]

    - current_player_index: int

    - board_occupancy: Dict[int, Peg]  # track position -> peg

    - current_roll: Optional[int]

    - rolls_this_turn: int

    - game_over: bool

    - winner: Optional[Player]

    - message: str


    + initialize_game(num_players: int) -> None

    + roll_dice() -> int

    + get_valid_pegs(roll: int) -> List[Peg]

    + move_peg(peg: Peg, roll: int) -> dict  # returns move result

    + check_capture(position: int) -> Optional[Peg]

    + is_double_trouble(position: int) -> bool

    + should_grant_bonus_roll(move_result: dict) -> bool

    + advance_turn() -> None

    + check_win_condition() -> None

    + get_current_player() -> Player

```

### 2. renderer.py

**Purpose**: All rendering logic combined into one class

**Constants** (defined at top of file):

```python

SCREEN_WIDTH = 1200

SCREEN_HEIGHT = 900

COLORS = {

'RED': (220, 50, 50),

'BLUE': (50, 120, 220),

'GREEN': (50, 200, 80),

'YELLOW': (240, 220, 50),

'BOARD_BG': (240, 230, 210),

'TRACK': (255, 255, 255),

'DOUBLE_TROUBLE': (255, 200, 50),

'HIGHLIGHT': (100, 255, 100)

}

```

```python

class GameRenderer:

    - screen: pygame.Surface

    - font_large: pygame.font.Font

    - font_small: pygame.font.Font

    - board_center: Tuple[int, int]

    - track_radius: int

    - space_positions: Dict[int, Tuple[int, int]]  # cached positions


    + render_all(game_state: GameState) -> None

    + render_board() -> None

    + render_track_spaces() -> None

    + render_home_bases(players: List[Player]) -> None

    + render_finish_zones(players: List[Player]) -> None

    + render_pegs(players: List[Player]) -> None

    + render_dice_button(enabled: bool, current_roll: Optional[int]) -> None

    + render_player_indicator(current_player: Player) -> None

    + render_message(message: str) -> None

    + render_setup_screen() -> None

    + render_game_over_screen(winner: Player) -> None

    + highlight_pegs(pegs: List[Peg]) -> None

    + get_peg_screen_position(peg: Peg) -> Tuple[int, int]

    + get_clicked_peg(mouse_pos: Tuple[int, int], players: List[Player]) -> Optional[Peg]

    + is_dice_button_clicked(mouse_pos: Tuple[int, int]) -> bool

```

### 3. main.py

**Purpose**: Entry point, game loop, and event handling

```python

class TroubleGame:

    - game_state: GameState

    - renderer: GameRenderer

    - screen: pygame.Surface

    - clock: pygame.time.Clock

    - setup_mode: bool

    - waiting_for_peg_selection: bool


    + run() -> None

    + handle_events() -> None

    + handle_setup_click(mouse_pos: Tuple[int, int]) -> None

    + handle_game_click(mouse_pos: Tuple[int, int]) -> None

    + handle_dice_click() -> None

    + handle_peg_click(peg: Peg) -> None

    + render() -> None


defmain():

    game = TroubleGame()

    game.run()

```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Game initialization creates valid state
*For any* valid player count (2-4), initializing a game should produce a game state where: (a) the number of players matches the requested count, (b) each player has a unique color, and (c) all pegs for all players start in their home base
**Validates: Requirements 1.3, 1.4, 1.5**

### Property 2: Dice rolls are in valid range
*For any* dice roll, the result should be an integer between 1 and 6 inclusive
**Validates: Requirements 2.2**

### Property 3: Valid moves for mid-range rolls
*For any* peg currently on the playing track and any roll value in the range [2, 5], moving that peg by the rolled number of spaces should be a valid move (assuming the destination is not blocked by the player's own peg)
**Validates: Requirements 3.2**

### Property 4: Invalid moves are rejected
*For any* game state, attempting to make an illegal move (such as moving a peg not on track with rolls 2-5, or moving from home base when start space is blocked by own peg) should be rejected and leave the game state unchanged
**Validates: Requirements 3.5**

### Property 5: Capture sends opponent home
*For any* game state where a peg lands on a space occupied by an opponent's peg on the playing track, the opponent's peg should be sent back to home base (position = -1, is_in_home = true)
**Validates: Requirements 4.1**

### Property 6: Cannot land on own peg
*For any* game state and any move, a peg should not be able to land on a space occupied by another peg belonging to the same player
**Validates: Requirements 4.3**

### Property 7: Finish zone exclusivity
*For any* peg attempting to enter a finish zone, the move should only be valid if the finish zone belongs to that peg's owner
**Validates: Requirements 4.4**

### Property 8: Double trouble grants bonus roll
*For any* game state where a peg lands on a double trouble space (positions 3, 10, 17, 24), the player should be granted an additional roll (unless they've already rolled twice this turn)
**Validates: Requirements 5.2**

### Property 9: Maximum two rolls per turn
*For any* turn, the number of consecutive rolls should never exceed 2, regardless of how many bonus roll conditions are triggered
**Validates: Requirements 5.3**

### Property 10: Finish zone entry without exact count
*For any* peg at or past the finish zone entry point for its player, the peg should be allowed to enter the finish zone without requiring an exact roll count
**Validates: Requirements 6.1**

### Property 11: Finish zone placement order
*For any* player's finish zone, pegs should be placed in sequential order (positions 100, 101, 102, 103) based on arrival order
**Validates: Requirements 6.2**

### Property 12: Finish zone count accuracy
*For any* game state, the tracked count of pegs in each player's finish zone should equal the actual number of that player's pegs with positions in range [100, 103]
**Validates: Requirements 6.3**

### Property 13: Win condition triggers correctly
*For any* player, when that player has exactly 4 pegs in the finish zone, the game should declare that player as the winner and set game_over to true
**Validates: Requirements 6.4**

### Property 14: Turn advances without bonus
*For any* game state where a move is completed and no bonus roll conditions are met, the current player index should advance to the next player
**Validates: Requirements 9.1**

### Property 15: Turn order cycles correctly
*For any* sequence of turn advancements, the current player index should cycle through players in order (0 → 1 → 2 → ... → n-1 → 0)
**Validates: Requirements 9.2**

### Property 16: No valid moves skips turn
*For any* game state where the current player has no valid moves for their roll, the turn should automatically advance to the next player
**Validates: Requirements 9.3**

### Property 17: Game over stops turn progression
*For any* game state where game_over is true, attempting to advance the turn should not change the current player index
**Validates: Requirements 9.5**

## Data Models

### Position System

The board uses a simple integer-based position system:

-**-1**: Peg is in home base

-**0-27**: Peg is on the main track

-**100-103**: Peg is in finish zone (100 + finish_index)

Each player has a designated start position on the track, and the finish zone entry is calculated based on the player's color.

### Board Layout

-**Main Track**: 28 spaces in a circular path

-**Start Spaces**: Each player has a designated start space on the main track

- Red: position 0
- Blue: position 7
- Green: position 14
- Yellow: position 21

-**Double Trouble Spaces**: Positioned at indices 3, 10, 17, 24 (evenly distributed)

-**Home Bases**: 4 spaces per player (off the main track)

-**Finish Zones**: 4 spaces per player leading to the center

### Coordinate System

The board will be rendered with:

- Center point at (600, 450)
- Track spaces arranged in a circle with radius 250 pixels
- Home bases in the four corners
- Finish zones extending from track toward center
- Dice button in the bottom center area

## Error Handling

### Invalid Move Handling

```python

class InvalidMoveError(Exception):

pass


class GameStateError(Exception):

pass

```

**Error Scenarios**:

1.**Blocked Start Space**: Display message "Your start space is blocked by your own peg"

2.**No Valid Moves**: Display message "No valid moves available" and auto-skip turn

3.**Invalid Peg Selection**: Highlight only valid pegs, ignore clicks on invalid pegs

4.**Animation Interruption**: Queue moves, don't allow new actions during animations

### Validation Flow

```

User Action → Input Handler → Rules Engine Validation → Execute or Reject

                                        ↓

                                  Show Error Message (if invalid)

```

## Testing Strategy

### Unit Tests

1.**Rules Engine Tests**:

- Test valid move generation for each roll value (1-6)
- Test capture mechanics
- Test bonus roll conditions
- Test win condition detection
- Test blocked start space scenarios

2.**Game State Tests**:

- Test turn progression
- Test player initialization
- Test peg state transitions
- Test board position calculations

3.**Position System Tests**:

- Test track wrapping
- Test finish zone entry
- Test start space identification

### Integration Tests

1.**Complete Turn Flow**:

- Roll dice → Select peg → Move peg → Check captures → Check bonus roll → End turn

2.**Special Scenarios**:

- Roll 1 effect on all opponents
- Roll 6 with multiple options
- Landing on double trouble space
- Entering finish zone
- Winning the game

### Manual Testing

1.**UI/UX Testing**:

- Verify all animations are smooth
- Test responsiveness of buttons and peg selection
- Verify visual clarity of game state
- Test with 2, 3, and 4 players

2.**Edge Cases**:

- All pegs in home
- All pegs in finish
- Multiple pegs on same track section
- Rapid clicking during animations

## Implementation Notes

### Game Loop Structure

```python

defrun():

    running = True

while running:

        clock.tick(60)


# Handle events

for event in pygame.event.get():

if event.type == pygame.QUIT:

                running = False

elif event.type == pygame.MOUSEBUTTONDOWN:

                handle_click(event.pos)


# Render

        renderer.render_all(game_state)

        pygame.display.flip()


    pygame.quit()

```

### Performance Considerations

- Cache board space positions on initialization
- Pre-calculate screen coordinates for all board positions
- Use simple immediate-mode rendering (redraw everything each frame)
- Target 60 FPS for smooth display

## Dependencies

```

pygame>=2.5.0

```

Pygame is the only external dependency required. It provides:

- Window management and rendering
- Event handling (mouse, keyboard)
- Drawing primitives (circles, rectangles, lines)
- Font rendering
- Time management for animations
