from tkinter import *
from numpy import matmul
from random import randint
from copy import deepcopy
from dotenv import *
from os import getenv, environ
from PIL import ImageTk

load_dotenv(find_dotenv())
BEST_SCORE = getenv("BEST_SCORE")

window = Tk()
window.title(f"Tetris | SE-2203 | Best: {int(str(BEST_SCORE))}")
window.resizable(False, False)
window.geometry("720x750+550+0")
window.config(bg="black")

CANVAS_HEIGHT = 700
CANVAS_WIDTH = 700
GAME_WIDTH = 350
GAME_HEIGHT = 700
SPACE_SIZE = 35
SHAPES = [[[1, 0], [-2, 0], [-1, 0], [0, 0]],
          [[-1, 1], [0, 1], [1, 1], [-1, 0]],
          [[-1, 1], [0, 1], [1, 1], [1, 0]],
          [[0, 0], [-1, 1], [0, 1], [-1, 0]],
          [[1, 1], [-1, 0], [0, 0], [0, 1]],
          [[-1, 1], [0, 1], [1, 1], [0, 0]],
          [[-1, 1], [0, 1], [0, 0], [1, 0]]]
COLORS = ["#00ffff",
          "#0000ff",
          "#ffa200",
          "#ffff00",
          "#ff0000",
          "Purple",
          "#00ff00"]
IMAGES = [ImageTk.PhotoImage(file="images/piecesimg/0.png"),
          ImageTk.PhotoImage(file="images/piecesimg/1.png"),
          ImageTk.PhotoImage(file="images/piecesimg/2.png"),
          ImageTk.PhotoImage(file="images/piecesimg/3.png"),
          ImageTk.PhotoImage(file="images/piecesimg/4.png"),
          ImageTk.PhotoImage(file="images/piecesimg/5.png"),
          ImageTk.PhotoImage(file="images/piecesimg/6.png")]
R = [[0, 1], [-1, 0]]

speed: int = 825
lines_deleted = 0
lvl = 1
field = []
coefficient = 1.0
score = 0
is_gameover: bool = False
is_holding: bool = False
for i in range(20):
    temp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    field.append(temp)


class Piece:

    def __init__(self):
        self.rand = randint(0, 6)
        self.shape = deepcopy(SHAPES[self.rand])
        self.coordinates = deepcopy(self.shape)
        self.blocks = []

        for i in range(4):
            self.coordinates[i][0] += 2
            x, y = self.coordinates[i]

            if self.rand == 3:
                x += 0.7
                y += 0.7
            elif self.rand == 0:
                x += 0.7
                y += 1.3
            else:
                x += 0.2
                y += 0.7
            y += 1
            x = x * SPACE_SIZE
            y = y * SPACE_SIZE

            block = prediction_canvas.create_image(x, y, image=IMAGES[self.rand])
            self.blocks.append(block)


# class Piece end

class Projection:
    def __init__(self):
        self.shape = deepcopy(piece.shape)
        self.coordinates = deepcopy(piece.coordinates)
        self.blocks = []
        for i in range(4):
            x, y = self.coordinates[i]
            x *= SPACE_SIZE
            y *= SPACE_SIZE
            x += 35 * 7
            block = tetris_canvas.create_rectangle(x + 2, y + 2, x + SPACE_SIZE - 2, y + SPACE_SIZE - 2,
                                                   outline=COLORS[piece.rand], width=1)
            self.blocks.append(block)


# class Projection end


def draw_piece():
    global piece
    for i in range(4):
        piece.coordinates[i][0] += 3
        x, y = piece.coordinates[i]
        x += 0.5
        y += 0.5
        x *= SPACE_SIZE
        y *= SPACE_SIZE
        block = tetris_canvas.create_image(x, y, image=IMAGES[piece.rand])
        piece.blocks[i] = block


def draw_hold():
    global holding
    for i in range(4):
        holding.coordinates[i][0] += 1
        x, y = holding.coordinates[i]
        if holding.rand == 3:
            x += 0.7
            y += 0.2
        elif holding.rand == 0:
            x += 0.7
            y += 0.7
        else:
            x += 0.2
            y += 0.2
        y += 1
        x = x * SPACE_SIZE + 35
        y = y * SPACE_SIZE + 20
        block = hold_canvas.create_image(x, y, image=IMAGES[holding.rand])
        holding.blocks[i] = block


def create_projection():
    index = 0
    while not collision(projection.coordinates):
        for i in range(4):
            projection.coordinates[i][1] += 1
    for square in projection.blocks:
        tetris_canvas.moveto(square, projection.coordinates[index][0] * SPACE_SIZE + 1,
                             projection.coordinates[index][1] * SPACE_SIZE + 1)
        index += 1


def move(direction):
    global coefficient, speed
    i = 0
    if direction == "Down":
        if collision(piece.coordinates):
            update_field()
            restart_piece()
            return

        for square in piece.blocks:
            tetris_canvas.move(square, 0, SPACE_SIZE)
            piece.coordinates[i][1] += 1
            i += 1


    elif direction == "Right":
        if can_move_right():
            return
        for square in piece.blocks:
            tetris_canvas.move(square, SPACE_SIZE, 0)
            piece.coordinates[i][0] += 1
            i += 1

    elif direction == "Left":
        if (can_move_left()):
            return
        for square in piece.blocks:
            tetris_canvas.move(square, -SPACE_SIZE, 0)
            piece.coordinates[i][0] -= 1
            i += 1
    projection.coordinates = deepcopy(piece.coordinates)
    coefficient += 0.01
    create_projection()


def hold():
    global holding, holded, is_holding, piece

    if not is_holding:
        remove_piece(tetris_canvas)
        holding = piece
        holded = piece
        holding.shape = SHAPES[holding.rand]
        holding.coordinates = deepcopy(holding.shape)
        restart_piece()
        is_holding = True
        draw_hold()
    else:

        if holded != piece:
            remove_piece(tetris_canvas)
            piece, holding = holding, piece
            holded = piece
            holding.shape = SHAPES[holding.rand]
            holding.coordinates = deepcopy(holding.shape)
            remove_piece(hold_canvas)
            draw_piece()
            projection.coordinates = deepcopy(piece.coordinates)
            for square in projection.blocks:
                tetris_canvas.itemconfig(square, outline=COLORS[piece.rand])
            create_projection()
            draw_hold()


def move_all():
    while not collision(piece.coordinates):
        move("Down")
        get_score("move")
        get_score("move")
    update_field()
    restart_piece()


def tick():
    global speed
    if is_gameover:
        return
    move("Down")
    window.after(speed, tick)


def remove_piece(canvas):
    global piece
    for square in piece.blocks:
        canvas.delete(square)


def collision(coordinates):
    for i in range(4):
        x, y = coordinates[i]
        if (y + 1) * 35 >= GAME_HEIGHT or field[y + 1][x] != 0:
            return True
    return False


def restart_piece():
    global piece, pieces
    pieces.pop(0)
    pieces.append(Piece())
    piece = pieces[0]

    remove_piece(prediction_canvas)
    draw_piece()
    for i in range(4):
        x, y = piece.coordinates[i]
        if field[y][x] != 0:
            game_over()
            return
    projection.coordinates = deepcopy(piece.coordinates)
    for square in projection.blocks:
        tetris_canvas.itemconfig(square, outline=COLORS[piece.rand])
    create_projection()


def can_move_right():
    for i in range(4):
        x, y = piece.coordinates[i]
        if (piece.coordinates[i][0]) >= 9 or field[y][x + 1] != 0:
            return True
    return False


def can_move_left():
    for i in range(4):
        x, y = piece.coordinates[i]
        if (piece.coordinates[i][0]) <= 0 or field[y][x - 1] != 0:
            return True
    return False


def can_rotate():
    coordinates = deepcopy(piece.coordinates)

    shape = matmul(piece.shape, R)

    coordinates = coordinates[2] + shape
    for i in range(0, 4):
        x, y = coordinates[i]

        try:
            if coordinates[i][0] < 0 or coordinates[i][0] > 9 or coordinates[i][1] > 20 or coordinates[i][1] < 0 or \
                    field[y][x] != 0:
                return False
        except IndexError:
            return False

    return True


def rotate():
    i = 1
    if can_rotate():
        piece.shape = matmul(piece.shape, R)

        piece.coordinates = piece.coordinates[2] + piece.shape
        for square in piece.blocks:
            x, y = piece.coordinates[i - 1]

            x = x * SPACE_SIZE + 1
            y = y * SPACE_SIZE + 1
            tetris_canvas.moveto(square, x, y)
            i += 1
    projection.coordinates = deepcopy(piece.coordinates)
    create_projection()
    return


def set_speed():
    global speed
    speed -= 75


def update_field():
    global coefficient, lines_deleted
    for i in range(4):
        x, y = piece.coordinates[i]
        field[y][x] = piece.blocks[i]

    lines = []
    for i in range(20):
        if 0 in field[i]:
            continue
        else:
            lines.append(i)

    if len(lines) > 0:
        global lines_deleted, lvl
        lines_deleted += len(lines)
        if lines_deleted % 10 == 0:
            lvl = lines_deleted // 10 + 1
            set_speed()
        get_score(pow(2, len(lines) - 1) * 100)
        coefficient += len(lines) / 2
        for i in range(len(lines)):
            for j in range(10):
                tetris_canvas.delete(field[lines[0]][j])
            field.pop(lines[0])
            field.insert(0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
            lines.pop(0)
        canvas_update()


def canvas_update():
    for i in range(20):
        for j in range(10):
            tetris_canvas.moveto(field[i][j], j * SPACE_SIZE + 1, i * SPACE_SIZE + 1)


def get_score(reason):
    global score, lines_deleted
    if reason == "move":
        score += 1 * coefficient
    else:
        score += reason * coefficient
    score_canvas.itemconfig(1, text=f'Score:\n{int(score)}\n\n'
                                    f'Level:\n{lvl}\n\n'
                                    f'Lines Deleted:\n{lines_deleted}')


def bind_buttons():
    window.bind('<Down>', lambda event: [move("Down"), get_score("move")])
    window.bind('<Right>', lambda event: move("Right"))
    window.bind('<MouseWheel>', lambda event: move("Down"))
    window.bind('<Left>', lambda event: move("Left"))
    window.bind('<Up>', lambda event: rotate())
    window.bind('<space>', lambda event: move_all())
    window.bind('c', lambda event: hold())


def unbind_buttons():
    window.unbind('<Down>')
    window.unbind('<Right>')
    window.unbind('<MouseWheel>')
    window.unbind('<Left>')
    window.unbind('<Up>')
    window.unbind('<space>')
    window.unbind('c')


def game_over():
    global BEST_SCORE, speed, is_gameover
    unbind_buttons()
    is_gameover = True
    tetris_canvas.delete(ALL)
    tetris_canvas.create_text(tetris_canvas.winfo_width() / 2, tetris_canvas.winfo_height() / 2,
                              font=('consolas', 70), text="GAME\nOVER", fill="red", tag="gameover")
    tetris_canvas.create_text(tetris_canvas.winfo_width() / 2, 600,
                              font=('Bahnschrift', 15),
                              text="...TETRIS...\npowered by\n\nYelnur | Karen\nShugyla | Gulzhan",
                              fill="white", tag="authors")
    if float(score) > float(BEST_SCORE):
        BEST_SCORE = score
        set_key(".env", "BEST_SCORE", str(int(BEST_SCORE)))
        window.title(f"Tetris | SE-2203 | Best: {int(BEST_SCORE)}")

# CANVASES CREATION
tetris_canvas = Canvas(window, bg="Black", height=GAME_HEIGHT, width=GAME_WIDTH,
                       highlightthickness=1, highlightbackground="white")
hold_canvas = Canvas(window, bg="Black", height=SPACE_SIZE * 4.4, width=SPACE_SIZE * 4.4,
                     highlightthickness=1, highlightbackground="white")
prediction_canvas = Canvas(window, bg="Black", height=SPACE_SIZE * 4.4, width=SPACE_SIZE * 4.4,
                           highlightthickness=1, highlightbackground="white")
score_canvas = Canvas(window, bg="Black", height=SPACE_SIZE * 4.6, width=SPACE_SIZE * 4.4,
                      highlightthickness=1, highlightbackground="white")
logo_canvas = Canvas(window, bg="Black", height=SPACE_SIZE * 4.4, width=SPACE_SIZE * 4.4,
                     highlightthickness=1, highlightbackground="white")
# CANVAS CREATION END

label = Label(window, bg="Black")

# CANVAS GRIDDING
label.grid(row=0)
hold_canvas.grid(row=1, column=1, sticky="n")
tetris_canvas.grid(row=1, column=2, padx=20)
prediction_canvas.grid(row=1, column=3, sticky="n")
score_canvas.grid(row=1, column=3, sticky="s")
logo_canvas.grid(row=1, column=1, sticky="s")
# CANVAS GRIDDING END

background_image = ImageTk.PhotoImage(file="images/background.jpg")
tetris_canvas.create_image(GAME_WIDTH / 2, GAME_HEIGHT / 2, image=background_image)

prediction_canvas.create_text(50, 12, text='Next shape:', font=('Bahnschrift', 17), fill='White', justify='center')
hold_canvas.create_text(58, 12, text='Holded shape:', font=('Bahnschrift', 17), fill='White', justify='center')
score_canvas.create_text(SPACE_SIZE * 2.2, SPACE_SIZE * 2.3, text=f'Score:\n{score}\n\n'
                                                                  f'Level:\n{lvl}\n\n'
                                                                  f'Lines Deleted:\n{lines_deleted}',
                         font=('Bahnschrift', 16), fill="White", justify="center")

pieces = []
pieces.append(Piece())
pieces.append(Piece())
piece = pieces[0]
remove_piece(prediction_canvas)
draw_piece()
projection = Projection()

create_projection()
window.after(speed, tick)
bind_buttons()

window.mainloop()  # powered by Yelnur, Karen
