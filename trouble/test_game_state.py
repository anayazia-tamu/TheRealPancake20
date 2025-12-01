"""
Simple tests to verify core game state functionality
"""

from game_state import GameState, Player, Peg


def test_game_initialization():
    """Test that game initializes correctly with valid player counts"""
    game = GameState()

    # Test with 2 players
    game.initialize_game(2)
    assert len(game.players) == 2
    assert game.players[0].color == "RED"
    assert game.players[1].color == "BLUE"

    # Each player should have 4 pegs
    for player in game.players:
        assert len(player.pegs) == 4
        # All pegs should start in home
        assert len(player.get_pegs_in_home()) == 4
        assert len(player.get_pegs_on_track()) == 0
        assert len(player.get_pegs_in_finish()) == 0

    print("✓ Game initialization test passed")


def test_dice_rolling():
    """Test that dice rolls are in valid range"""
    game = GameState()
    game.initialize_game(2)

    # Roll dice 100 times and verify all results are 1-6
    for _ in range(100):
        roll = game.roll_dice()
        assert 1 <= roll <= 6

    print("✓ Dice rolling test passed")


def test_turn_advancement():
    """Test that turns advance correctly"""
    game = GameState()
    game.initialize_game(3)

    assert game.current_player_index == 0

    game.advance_turn()
    assert game.current_player_index == 1

    game.advance_turn()
    assert game.current_player_index == 2

    game.advance_turn()
    assert game.current_player_index == 0  # Should wrap around

    print("✓ Turn advancement test passed")


def test_peg_movement():
    """Test basic peg movement"""
    game = GameState()
    game.initialize_game(2)

    player = game.players[0]
    peg = player.pegs[0]

    # Move peg from home to start (simulating roll of 1 or 6)
    peg.move_to(0)
    assert peg.position == 0
    assert not peg.is_in_home
    assert not peg.is_in_finish

    # Move peg to finish zone
    peg.move_to(100)
    assert peg.position == 100
    assert not peg.is_in_home
    assert peg.is_in_finish

    # Send peg home
    peg.send_home()
    assert peg.position == -1
    assert peg.is_in_home
    assert not peg.is_in_finish

    print("✓ Peg movement test passed")


def test_win_condition():
    """Test that win condition is detected correctly"""
    game = GameState()
    game.initialize_game(2)

    player = game.players[0]

    # Move all 4 pegs to finish zone
    for i, peg in enumerate(player.pegs):
        peg.move_to(100 + i)

    assert player.has_won()

    game.check_win_condition()
    assert game.game_over
    assert game.winner == player

    print("✓ Win condition test passed")


def test_double_trouble_positions():
    """Test that double trouble positions are correctly identified"""
    game = GameState()
    game.initialize_game(2)

    # Double trouble spaces are at 3, 10, 17, 24
    assert game.is_double_trouble(3)
    assert game.is_double_trouble(10)
    assert game.is_double_trouble(17)
    assert game.is_double_trouble(24)

    # Other positions should not be double trouble
    assert not game.is_double_trouble(0)
    assert not game.is_double_trouble(5)
    assert not game.is_double_trouble(15)

    print("✓ Double trouble positions test passed")


def test_capture_mechanics():
    """Test that capture mechanics work correctly"""
    game = GameState()
    game.initialize_game(2)

    player1 = game.players[0]
    player2 = game.players[1]

    peg1 = player1.pegs[0]
    peg2 = player2.pegs[0]

    # Place both pegs on the track
    peg1.move_to(5)
    peg2.move_to(10)

    game.board_occupancy[5] = peg1
    game.board_occupancy[10] = peg2

    # Check that we can detect pegs at positions
    assert game.check_capture(5) == peg1
    assert game.check_capture(10) == peg2
    assert game.check_capture(15) is None

    print("✓ Capture mechanics test passed")


if __name__ == "__main__":
    test_game_initialization()
    test_dice_rolling()
    test_turn_advancement()
    test_peg_movement()
    test_win_condition()
    test_double_trouble_positions()
    test_capture_mechanics()

    print("\n✅ All tests passed!")
