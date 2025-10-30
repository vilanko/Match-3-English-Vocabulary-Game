import pygame
import random
import sys

pygame.init()

# --- Window setup ---
WIDTH, HEIGHT = 900, 700
ROWS, COLS = 8, 8
CELL_SIZE = 70
TOP_MARGIN = 100
LEFT_MARGIN = 50
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Match 3 - English Vocabulary Edition")

FONT = pygame.font.SysFont("arial", 22)
BIG_FONT = pygame.font.SysFont("arial", 40)
SMALL_FONT = pygame.font.SysFont("arial", 18)

# --- All categories and words ---
ALL_WORDS = {
    "fruit": ["apple", "banana", "orange", "grape", "kiwi"],
    "vegetable": ["carrot", "broccoli", "spinach", "pepper", "onion"],
    "meat": ["chicken", "beef", "pork", "lamb", "bacon"],
    "fish": ["salmon", "tuna", "cod", "trout", "sardine"],
    "drink": ["water", "juice", "tea", "coffee", "milk"],
    "animal": ["cat", "dog", "elephant", "lion", "tiger"],
    "color": ["red", "blue", "green", "yellow", "purple"],
    "vehicle": ["car", "bike", "bus", "train", "airplane"],
    "clothing": ["shirt", "pants", "hat", "shoes", "coat"],
    "tool": ["hammer", "wrench", "saw", "screwdriver", "drill"],
    "sport": ["soccer", "tennis", "baseball", "basketball", "hockey"],
    "country": ["USA", "Canada", "France", "Japan", "Brazil"],
    "shape": ["circle", "square", "triangle", "rectangle", "hexagon"]
}


CATEGORY_COLORS = {
    "fruit": (255, 100, 100),
    "vegetable": (100, 220, 100),
    "meat": (255, 180, 120),
    "fish": (100, 180, 255),
    "drink": (255, 255, 120),
    "animal": (220, 170, 255),
    "color": (255, 150, 255),
    "sport": (255, 220, 100),
    "country": (150, 250, 255),
    "vehicle": (180, 180, 180)
}


# --- Helper UI functions ---
def draw_button(surface, text, rect, color, hover_color, mouse_pos):
    """Draw a button and return True if hovered."""
    x, y, w, h = rect
    hovered = x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h
    pygame.draw.rect(surface, hover_color if hovered else color, rect, border_radius=10)
    label = FONT.render(text, True, (0, 0, 0))
    surface.blit(label, label.get_rect(center=(x + w // 2, y + h // 2)))
    return hovered


# --- Tile class ---
class Tile:
    def __init__(self, row, col, categories):
        self.row = row
        self.col = col
        self.categories = categories
        self.assign_random_word()
        self.highlighted = False   # True when part of a matching line
        self.highlight_time = 0    # Time when it was highlighted


    def assign_random_word(self):
        self.category = random.choice(self.categories)
        self.word = random.choice(ALL_WORDS[self.category])
        self.color = (100, 200, 255)  # light blue for all circles


    def draw(self, surface):
        x = self.col * CELL_SIZE + CELL_SIZE // 2 + LEFT_MARGIN
        y = self.row * CELL_SIZE + CELL_SIZE // 2 + TOP_MARGIN
        pygame.draw.circle(surface, self.color, (x, y), CELL_SIZE // 2 - 3)
        text = SMALL_FONT.render(self.word, True, (0, 0, 0))
        surface.blit(text, text.get_rect(center=(x, y)))


# --- Game board class ---
class Board:
    def __init__(self, categories):
        # make sure we store a copy, not a shared reference
        self.categories = list(categories)
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self._generate_board_without_matches()
        self.remove_all_matches()

    def _generate_board_without_matches(self):
        for r in range(ROWS):
            for c in range(COLS):
                while True:
                    new_tile = Tile(r, c, self.categories)
                    self.grid[r][c] = new_tile
                    # Check if placing this tile creates a match
                    if not self._creates_match(r, c):
                        break

    def _creates_match(self, r, c):
        word_cat = self.grid[r][c].category
        # Check horizontal
        if c >= 2 and self.grid[r][c-1].category == word_cat and self.grid[r][c-2].category == word_cat:
            return True
        # Check vertical
        if r >= 2 and self.grid[r-1][c].category == word_cat and self.grid[r-2][c].category == word_cat:
            return True
        return False


    def draw(self, surface):
        for row in self.grid:
            for tile in row:
                if tile:
                    tile.draw(surface)

    def _in_bounds(self, r, c):
        return 0 <= r < ROWS and 0 <= c < COLS

    def swap(self, r1, c1, r2, c2):
        if not (self._in_bounds(r1, c1) and self._in_bounds(r2, c2)):
            return
        self.grid[r1][c1], self.grid[r2][c2] = self.grid[r2][c2], self.grid[r1][c1]
        self.grid[r1][c1].row, self.grid[r1][c1].col = r1, c1
        self.grid[r2][c2].row, self.grid[r2][c2].col = r2, c2

    def find_matches(self):
        matched = set()
        # Horizontal
        for r in range(ROWS):
            for c in range(COLS - 2):
                if (self.grid[r][c] and self.grid[r][c + 1] and self.grid[r][c + 2] and
                    self.grid[r][c].category ==
                    self.grid[r][c + 1].category ==
                    self.grid[r][c + 2].category):
                    matched.update([(r, c), (r, c + 1), (r, c + 2)])
        # Vertical
        for c in range(COLS):
            for r in range(ROWS - 2):
                if (self.grid[r][c] and self.grid[r + 1][c] and self.grid[r + 2][c] and
                    self.grid[r][c].category ==
                    self.grid[r + 1][c].category ==
                    self.grid[r + 2][c].category):
                    matched.update([(r, c), (r + 1, c), (r + 2, c)])
        
        return matched
    def remove_all_matches(self):
        while True:
            matched = self.find_matches()
            if not matched:
                break
            self.remove_and_collapse(matched)
            self.score += len(matched)

    def remove_and_collapse(self, matched):
        if not matched:
            return

        self.score += len(matched)

        # Remove matches
        for (r, c) in matched:
            self.grid[r][c] = None

        # Collapse each column
        for c in range(COLS):
            new_col = [self.grid[r][c] for r in range(ROWS) if self.grid[r][c]]
            while len(new_col) < ROWS:
                new_col.insert(0, None)
            for r in range(ROWS):
                self.grid[r][c] = new_col[r]
                if self.grid[r][c]:
                    self.grid[r][c].row = r
                    self.grid[r][c].col = c
            for r in range(ROWS):
                if self.grid[r][c] is None:
                    self.grid[r][c] = Tile(r, c, self.categories)

def add_categories_screen():
    input_boxes = []
    category_texts = [""] * 5
    word_texts = [[""] * 5 for _ in range(5)]  # 5x5 words

    # Create rectangles for categories and words
    for i in range(5):
        cat_rect = pygame.Rect(100, 50 + i*100, 150, 40)
        input_boxes.append(("cat", i, cat_rect))
        for j in range(5):
            word_rect = pygame.Rect(300 + j*120, 50 + i*100, 100, 40)
            input_boxes.append(("word", i, j, word_rect))

    active_box = None
    clock = pygame.time.Clock()

    while True:
        screen.fill((250, 250, 250))
        mouse = pygame.mouse.get_pos()
        MAX_CHARS = 12
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check which box is clicked
                active_box = None
                for box in input_boxes:
                    if box[0] == "cat":
                        if box[2].collidepoint(event.pos):
                            active_box = box
                    elif box[0] == "word":
                        if box[3].collidepoint(event.pos):
                            active_box = box
                     # green border
            elif event.type == pygame.KEYDOWN and active_box:
                if event.key == pygame.K_BACKSPACE:
                    if active_box[0] == "cat":
                        category_texts[active_box[1]] = category_texts[active_box[1]][:-1]
                    elif active_box[0] == "word":
                        i, j = active_box[1], active_box[2]
                        word_texts[i][j] = word_texts[i][j][:-1]
                elif event.key == pygame.K_RETURN:
                    active_box = None
                else:
                    char = event.unicode
                    if active_box[0] == "cat":
                        category_texts[active_box[1]] += char
                    elif active_box[0] == "word":
                        i, j = active_box[1], active_box[2]
                        if len(word_texts[i][j]) < MAX_CHARS:
                            word_texts[i][j] += char
                            

        # --- Draw input boxes ---
        for i in range(5):
            cat_rect = pygame.Rect(100, 50 + i*100, 150, 40)
            pygame.draw.rect(screen, (200, 200, 200), cat_rect, 0)
            text_surf = FONT.render(category_texts[i], True, (0, 0, 0))
            screen.blit(text_surf, (cat_rect.x + 5, cat_rect.y + 5))
            for j in range(5):
                word_rect = pygame.Rect(300 + j*120, 50 + i*100, 100, 40)
                pygame.draw.rect(screen, (220, 220, 220), word_rect, 0)
                word_surf = FONT.render(word_texts[i][j], True, (0, 0, 0))
                screen.blit(word_surf, (word_rect.x + 5, word_rect.y + 5))

        # --- Draw Save button ---
        save_rect = pygame.Rect(500, 600, 150, 50)
        draw_button(screen, "Save", save_rect, (180, 220, 255), (130, 200, 255), mouse)
        if pygame.mouse.get_pressed()[0] and save_rect.collidepoint(mouse):
            # Update ALL_WORDS
            for i in range(5):
                cat = category_texts[i].strip().lower()
                words = [w.strip().lower() for w in word_texts[i] if w.strip()]
                if cat and words:
                    ALL_WORDS[cat] = words
            # Start game with these categories
            chosen = list(category_texts[:5])
            game_screen(chosen)

        pygame.display.update()
        clock.tick(30)

# --- Game screens ---
def welcome_screen():
    while True:
        screen.fill((250, 250, 250))
        mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Play button
                if 200 <= x <= 400 and 200 <= y <= 260:
                    # Pick 5 random categories
                    chosen = random.sample(list(ALL_WORDS.keys()), 5)
                    game_screen(chosen)
                # Pick Categories button
                elif 200 <= x <= 400 and 280 <= y <= 340:
                    category_selection_screen()
                # Add Categories button
                elif 200 <= x <= 400 and 360 <= y <= 420:
                    add_categories_screen()

        # Draw buttons
        draw_button(screen, "Play", (200, 200, 200, 60), (180, 220, 255), (130, 200, 255), mouse)
        draw_button(screen, "Pick Categories", (200, 280, 200, 60), (180, 255, 180), (130, 255, 130), mouse)
        draw_button(screen, "Add Categories", (200, 360, 200, 60), (255, 180, 180), (255, 120, 120), mouse)

        pygame.display.update()


def category_selection_screen():
    chosen = []
    buttons = list(ALL_WORDS.keys())
    cols = 3  # number of columns for buttons
    button_width = 180
    button_height = 40
    x_margin = 60
    y_margin = 180
    x_spacing = 200
    y_spacing = 60

    while True:
        screen.fill((250, 250, 250))
        mouse = pygame.mouse.get_pos()

        # --- Event handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Category buttons
                for i, cat in enumerate(buttons):
                    row = i // cols
                    col = i % cols
                    x = x_margin + col * x_spacing
                    y = y_margin + row * y_spacing
                    if x <= mouse[0] <= x + button_width and y <= mouse[1] <= y + button_height:
                        if cat in chosen:
                            chosen.remove(cat)
                        elif len(chosen) < 5:
                            chosen.append(cat)
                # Play button
                if 200 <= mouse[0] <= 400 and 600 <= mouse[1] <= 660 and len(chosen) == 5:
                    game_screen(chosen)

        # --- Draw category buttons ---
        for i, cat in enumerate(buttons):
            row = i // cols
            col = i % cols
            x = x_margin + col * x_spacing
            y = y_margin + row * y_spacing
            selected = cat in chosen
            color = (100, 255, 100) if selected else (220, 220, 220)
            hover_color = (150, 255, 150) if selected else (200, 200, 200)
            draw_button(screen, cat.capitalize(), (x, y, button_width, button_height), color, hover_color, mouse)

        # --- Draw Play button ---
        can_play = len(chosen) == 5
        play_color = (180, 220, 255) if can_play else (200, 200, 200)
        draw_button(screen, "Play", (200, 600, 200, 60), play_color, (130, 200, 255), mouse)

        # --- Instruction ---
        info = SMALL_FONT.render(f"Selected: {len(chosen)}/5", True, (0, 0, 0))
        screen.blit(info, (WIDTH // 2 - info.get_width() // 2, 560))

        pygame.display.update()



def game_screen(categories):
    board = Board(categories.copy())
    selected = None
    clock = pygame.time.Clock()

    while True:
        screen.fill((250, 250, 250))
        mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return  # go back to welcome
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if y > TOP_MARGIN:
                    c = (x - LEFT_MARGIN) // CELL_SIZE
                    r = (y - TOP_MARGIN) // CELL_SIZE
                    if not board._in_bounds(r, c):
                        continue
                    if selected is None:
                        selected = (r, c)
                    else:
                        r1, c1 = selected
                        if abs(r - r1) + abs(c - c1) == 1:
                            board.swap(r, c, r1, c1)
                            matched = board.find_matches()
                            if matched:
                                while matched:
                                    board.remove_and_collapse(matched)
                                    board.score += len(matched)
                                    matched = board.find_matches()
                            else:
                            # swap back if no match
                                board.swap(r, c, r1, c1)
                        selected = None

        # Draw board
        board.draw(screen)
        score_text = FONT.render(f"Score: {board.score}", True, (0, 0, 0))
        screen.blit(score_text, (20, 20))

        pygame.display.update()
        clock.tick(30)


# --- Start the game ---
if __name__ == "__main__":
    welcome_screen()
