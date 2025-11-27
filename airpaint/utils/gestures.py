import math

def dist(a, b):
    return math.dist([a.x, a.y], [b.x, b.y])

def fingers_up(lm):
    if lm is None:
        return 0
    tips = [8, 12, 16, 20]
    count = 0
    for tip in tips:
        if lm[tip].y < lm[tip - 2].y:
            count += 1
    return count

def pinch(lm):
    if lm is None:
        return False
    return dist(lm[4], lm[8]) < 0.045

def one_finger(lm):
    return lm is not None and fingers_up(lm) == 1

def two_fingers(lm):
    return lm is not None and fingers_up(lm) == 2

def three_fingers(lm):
    return lm is not None and fingers_up(lm) == 3

def four_fingers(lm):
    return lm is not None and fingers_up(lm) == 4