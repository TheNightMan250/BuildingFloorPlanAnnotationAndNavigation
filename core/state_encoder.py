import math
import torch


def normalize_coord(x, y, width=1.0, height=1.0):
    if width == 0:
        width = 1.0
    if height == 0:
        height = 1.0
    return x / width, y / height


def angle_between(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.degrees(math.atan2(dy, dx)) % 360.0


def encode_state(last_room, prev_room, avg_angle=0.0, pattern_count=0, grid_w=1.0, grid_h=1.0, device="cpu"):
    """
    last_room: (x,y)
    prev_room: (x,y)
    Returns tensor shape (8,)
    """
    lx, ly = last_room
    px, py = prev_room
    dx = lx - px
    dy = ly - py
    ang = angle_between((px, py), (lx, ly))
    nx, ny = normalize_coord(lx, ly, grid_w, grid_h)
    ndx, ndy = normalize_coord(dx, dy, grid_w, grid_h)
    state = torch.tensor([
        nx, ny,
        ndx, ndy,
        ang / 360.0,
        avg_angle / 360.0,
        float(pattern_count),
        grid_w if grid_w <= 1 else 1.0,
    ], dtype=torch.float32, device=device)
    return state

