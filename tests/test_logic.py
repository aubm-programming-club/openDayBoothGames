import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))  # allows importing from kid_game/ and teen_game/ in later tasks

HOLE_W = 60

def is_over_hole(center_x, holes, hole_w=HOLE_W):
    return any(hx <= center_x <= hx + hole_w for hx in holes)

def reached_trigger(char_x, triggers, idx):
    if idx >= len(triggers):
        return False
    return char_x >= triggers[idx]


# --- is_over_hole ---

def test_over_hole_center():
    assert is_over_hole(230, [200, 400, 600]) is True

def test_over_hole_left_edge():
    assert is_over_hole(200, [200, 400, 600]) is True

def test_over_hole_right_edge():
    assert is_over_hole(260, [200, 400, 600]) is True

def test_not_over_hole_before():
    assert is_over_hole(199, [200, 400, 600]) is False

def test_not_over_hole_after():
    assert is_over_hole(261, [200, 400, 600]) is False

def test_over_hole_empty_list():
    assert is_over_hole(300, []) is False

def test_over_second_hole():
    assert is_over_hole(420, [200, 400, 600]) is True


# --- reached_trigger ---

def test_trigger_exact():
    assert reached_trigger(200, [200, 400, 600], 0) is True

def test_trigger_just_before():
    assert reached_trigger(199, [200, 400, 600], 0) is False

def test_trigger_past_end():
    assert reached_trigger(999, [200, 400, 600], 3) is False

def test_trigger_empty():
    assert reached_trigger(500, [], 0) is False
