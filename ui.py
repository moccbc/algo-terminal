from copy import deepcopy
from card import Card, CardColor
from message import Message

TOP_LEFT_CORNER = "┌"
TOP_RIGHT_CORNER = "┐"
BOT_LEFT_CORNER = "└"
BOT_RIGHT_CORNER = "┘"
CORNERS = [TOP_LEFT_CORNER, TOP_RIGHT_CORNER, BOT_LEFT_CORNER, BOT_RIGHT_CORNER]
HORIZONTAL_EDGE = "─"
VERTICAL_EDGE = "│"

LIGHT_MAGENTA_BG = 105
WHITE_FG = 97
WHITE_BG = 107
BLACK_FG = 30 
BLACK_BG = 100
RED_BG = 41

CANVAS_HEIGHT = 18
CANVAS_WIDTH = 64
CARD_HEIGHT = 3
CARD_WIDTH = 5
CARD_TOP_ROW = 1
CARD_BOT_ROW = 14
CURSOR_TOP_ROW = CARD_TOP_ROW + CARD_HEIGHT
CURSOR_BOT_ROW = CARD_BOT_ROW - 1

class Image:
    def __init__(self, canvas = [[]]):
        self.canvas = canvas
        self.height = len(canvas)
        self.width = len(canvas[0])

    def draw(self):
        drawn_canvas = ""
        for i in range(self.height):
            for j in range(self.width):
                drawn_canvas += self.canvas[i][j]
            drawn_canvas += "\n"
        return drawn_canvas

class Ui:
    def __init__(self):
        self.canvas_height = 18
        self.canvas_width = 64
        self.canvas = self.init_grid(self.canvas_height, self.canvas_width)
        self.canvas_fg_color = WHITE_FG
        self.canvas_bg_color = LIGHT_MAGENTA_BG
        self.card_height = 3
        self.card_width = 5

    def get_board(self, top_row_cards, bot_row_cards, texts, is_player_turn, cursor_pos):
        # Remove the functional style once it is clear that all of these methods are internal
        self.clear_canvas()
        self.plot_cards(top_row_cards, CARD_TOP_ROW)
        self.plot_cards(bot_row_cards, CARD_BOT_ROW)
        self.plot_cursor(CURSOR_TOP_ROW, len(top_row_cards), cursor_pos, is_player_turn)
        self.plot_cursor(CURSOR_BOT_ROW, len(bot_row_cards), cursor_pos, not is_player_turn)
        self.plot_texts(texts)
        self.plot_canvas_frame()
        return self.draw_canvas()

    def get_default_board(self, texts):
        if not texts:
            return ""
        deck = [Card(number, color, True) for color in CardColor for number in range(12)]
        return self.get_board(deck[0:12], deck[12:], texts, True, 0)

    def draw_canvas(self):
        return Image(self.canvas).draw()

    def plot_canvas_frame(self):
        style_start = self.get_style_start(self.canvas_fg_color, self.canvas_bg_color)
        style_end = self.get_style_end()
        canvas_frame_grid = self.get_rectangle_image(
            self.canvas_height, self.canvas_width, 
            style_start, style_end
        )
        self.plot_image(canvas_frame_grid, 0, 0)

    def plot_cards(self, cards, sr):
        sc = (self.canvas_width - self.card_width*len(cards)) // 2
        is_bot_row = (sr == CARD_BOT_ROW)
        card_images = [self.get_card_image(card, is_bot_row) for card in cards]
        self.plot_images(card_images, sr, sc, 0, self.card_width)

    def plot_texts(self, texts):
        text_image = self.get_text_image(texts)
        sr = (self.canvas_height - text_image.height) // 2
        sc = (self.canvas_width - text_image.width) // 2
        self.plot_image(text_image, sr, sc)

    def plot_cursor(self, sr, hand_size, cursor_pos, show_cursor):
        if show_cursor:
            sc = self.get_cursor_column(sr, hand_size, cursor_pos)
            cursor_image = self.get_cursor_image(sr)
            self.plot_image(cursor_image, sr, sc)

    def get_cursor_column(self, sr, hand_size, cursor_pos):
        # The self.card_width // 2 is placed on the outside to account for when
        # hand_size is odd
        sc = (self.canvas_width - self.card_width*hand_size) // 2 + self.card_width // 2
        if sr == CURSOR_TOP_ROW:
            sc += self.card_width * cursor_pos
        elif sr == CURSOR_BOT_ROW:
            sc += self.card_width * (hand_size - 1)
            sc -= self.card_width * cursor_pos
        return sc

    def get_cursor_image(self, sr):
        if sr == CURSOR_TOP_ROW:
            return Image([['∧']])
        elif sr == CURSOR_BOT_ROW:
            return Image([['∨']])

    def get_text_image(self, texts):
        max_len = len(max(texts, key=len))
        texts_list = [list(text.ljust(max_len, ' ')) for text in texts]
        return Image(texts_list) 
        
    def get_card_image(self, card, is_bot_row):
        card_fg_color = WHITE_FG if card.color == CardColor.BLACK else BLACK_FG
        card_bg_color = BLACK_BG if card.color == CardColor.BLACK else WHITE_BG
        style_start = self.get_style_start(card_fg_color, card_bg_color)
        style_end = self.get_style_end() + \
            self.get_style_start(self.canvas_fg_color, self.canvas_bg_color);
        card_image = self.get_rectangle_image(
            self.card_height, self.card_width, style_start, style_end 
        )
        if card.is_revealed or is_bot_row:
            number_string = str(card.number)
            if len(number_string) < 2:
                card_image.canvas[1][2] = number_string[0]
            else:
                card_image.canvas[1][1] = number_string[0]
                card_image.canvas[1][3] = number_string[1]
        if card.is_revealed and is_bot_row:
            card_image.canvas[2][2] = "¤"

        if card.is_new:
            if is_bot_row:
                card_image.canvas[0][2] = '*'
            else:
                card_image.canvas[1][2] = '*'

        return card_image
    
    # sr, sc is where to start. dr, dc is the offset for subsequent images
    def plot_images(self, images, sr, sc, dr, dc):
        r, c = sr, sc
        for image in images:
            self._plot_image(image, r, c)
            r += dr
            c += dc

    def plot_image(self, image, sr, sc):
        self._plot_image(image, sr, sc)

    # Private helper method to plot an image onto a canvas.
    def _plot_image(self, image, sr, sc):
        for r in range(image.height):
            for c in range(image.width):
                curr_r, curr_c = sr+r, sc+c
                if (self.canvas[curr_r][curr_c] == " "):
                    self.canvas[curr_r][curr_c] = image.canvas[r][c]

    def get_style_start(self, fg_color=97, bg_color=100):
        return "\033[" + str(fg_color) + ";" + str(bg_color) + "m"

    def get_style_end(self):
        return "\033[0m"

    def get_rectangle_image(self, height, width, style_start, style_end): 
        grid = self.init_grid(height, width)
        for i in range(height):
            grid[i][0] = style_start + VERTICAL_EDGE
            grid[i][width-1] = VERTICAL_EDGE + style_end 
        for i in range(width):
            grid[0][i] = HORIZONTAL_EDGE
            grid[height-1][i] = HORIZONTAL_EDGE
        grid[0][0] = style_start + TOP_LEFT_CORNER
        grid[height-1][0] = style_start + BOT_LEFT_CORNER
        grid[0][width-1] = TOP_RIGHT_CORNER + style_end
        grid[height-1][width-1] = BOT_RIGHT_CORNER + style_end
        return Image(grid)

    def clear_canvas(self):
        self.canvas = self.init_grid(self.canvas_height, self.canvas_width)

    def init_grid(self, height, width):
        return [[" " for i in range(width)] for i in range(height)]

