def to_flag(*args: list): return list(args) + list(reversed(args))
def to_color(code: int): return code >> 16, (code >> 8) & 0xFF, code & 0xFF

NR_LEDS = 40
WHITE, BLACK, TURQ = map(to_color, [0xFFFFFF, 0, 0xAAFFFF])
RED, GREEN, BLUE, CYAN, MAGENTA, YELLOW = map(to_color, [0xFF0000, 0x00FF00, 0x0000FF, 0x00FFFF, 0xFF00FF, 0xFFFF00])
COLORS = [to_flag(RED, WHITE, RED),  # austria fugging yeah
          to_flag(YELLOW, BLACK),  # austria-hungary / ancap
          to_flag(BLACK, RED, YELLOW),  # germany
          [TURQ],  # iron man generator
          [RED, YELLOW, GREEN, CYAN, BLUE, MAGENTA]]  # rbgay pride
PATH = "/sd/apps/salz/"