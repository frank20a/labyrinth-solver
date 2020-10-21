from tkinter import *
from tkinter.ttk import OptionMenu
from tkinter.filedialog import asksaveasfilename, askopenfile
import json

size_x = 20
size_y = 20
box_px = 30
wall_px = 8

inf = float('inf')


def manhatan(x, y, mul):
    return ((size_x - x) + (size_y - y)) * mul


def eucledean(x, y, mul):
    return (((size_x - x) ** 2 + (size_y - y) ** 2) ** 0.5) * mul


class Node():
    def __init__(self, x, y, h_func='eucledean', mul=1):
        self.visited = False
        self.x = x
        self.y = y
        self.g = inf

        self.h = 0
        self.set_h_func(h_func, mul)

        self.prev = None
        self.path = False
        self.current = False

    def f(self):
        return self.g + self.h

    def set_h_func(self, h_func, mul):
        if h_func == 'manhatan': self.h = manhatan(self.x, self.y, mul)
        if h_func == 'eucledean': self.h = eucledean(self.x, self.y, mul)

    def __str__(self):
        return '[' + str(self.x) + ',' + str(self.y) + '] g=' + str(self.g) + ' h=' + str(self.h) + ' f=' + str(
            self.f()) + '\n'


class App(Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Window settings
        self.minsize(width=1050, height=800)
        self.maxsize(width=1050, height=800)
        self.resizable(width=False, height=False)
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.title("Labyrinth Solver - by Frank Fourlas")

        # Sidebar
        sidebar = Frame(self, bg='grey')

        Button(sidebar, text='Run Algorithm', command=self.run_algorithm, height=2, font=25).pack(side=TOP, padx=10,
                                                                                                  pady=10)
        self.h_func = StringVar()
        self.h_func.set('eucledean')
        OptionMenu(sidebar, self.h_func, 'eucledean', *['eucledean', 'manhatan']).pack(side=TOP, padx=10, pady=10)

        Button(sidebar, text='Reset Maze', command=self.reset_maze, height=2, font=25).pack(side=TOP, padx=10, pady=10)

        Button(sidebar, text='Save Maze', command=self.save_maze, height=2, font=25).pack(side=TOP, padx=10, pady=10)
        Button(sidebar, text='Load Maze', command=self.load_maze, height=2, font=25).pack(side=TOP, padx=10, pady=10)

        self.display_weights = BooleanVar()
        self.display_weights.set(1)
        Checkbutton(sidebar, text='Display Weights', variable=self.display_weights).pack(side=TOP, padx=10, pady=10)

        multiplier = Frame(sidebar)
        Label(multiplier, text='h Function multiplier').pack(side=TOP, padx=10, pady=2)
        radio = Frame(multiplier)
        self.h_mul = DoubleVar()
        self.h_mul.set(1)
        Radiobutton(radio, text='1/4', variable=self.h_mul, value=0.25).pack(side=LEFT, padx=2, pady=5)
        Radiobutton(radio, text='1/2', variable=self.h_mul, value=0.5).pack(side=LEFT, padx=2, pady=5)
        Radiobutton(radio, text='1', variable=self.h_mul, value=1).pack(side=LEFT, padx=2, pady=5)
        Radiobutton(radio, text='3', variable=self.h_mul, value=3).pack(side=LEFT, padx=2, pady=5)
        Radiobutton(radio, text='15', variable=self.h_mul, value=15).pack(side=LEFT, padx=2, pady=5)
        radio.pack(side=TOP, padx=2, pady=2)
        multiplier.pack(side=TOP, padx=10, pady=10)

        sidebar.pack(side=LEFT, fill=Y)

        # Labyrinth
        self.reset_maze()

        # Canvas
        self.canvas = Canvas(self, bg='#a0ff8f')
        self.canvas.bind("<Button-1>", self.canvas_click)
        self.canvas.pack(side=LEFT, expand=True, fill=BOTH)
        self.update_canvas()

        self.RUNNING = True
        self.ALGORITHM = False

    def save_maze(self):
        filename = asksaveasfilename(defaultextension='.json', title="Save Maze As...", filetypes=(('JSON Files', '*.json'),))
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump({'v_walls': self.v_walls, 'h_walls': self.h_walls}, file)

    def load_maze(self):
        with askopenfile(mode='r', filetypes=(('JSON Files', '*.json'),)) as file:
            data = json.load(file)
            self.v_walls = data['v_walls']
            self.h_walls = data['h_walls']

    def reset_maze(self):
        self.soft_reset()
        self.v_walls = [[False for j in range(size_y)] for i in range(size_x - 1)]
        self.h_walls = [[False for j in range(size_y - 1)] for i in range(size_x)]

    def soft_reset(self):
        h_func = self.h_func.get()
        h_mul = self.h_mul.get()
        self.nodes = [[Node(i, j, h_func, h_mul) for j in range(size_y)] for i in range(size_x)]
        self.nodes[0][0].g = 0

    def canvas_click(self, event):
        x, y = event.x, event.y
        # print(x, y)
        nx = (x-wall_px)//(box_px+wall_px)
        ny = (y-wall_px)//(box_px+wall_px)

        tx = x - (nx+1)*(wall_px + box_px) > 0
        ty = y - (ny+1)*(wall_px + box_px) > 0

        try:
            if nx < 0 or ny < 0: raise IndexError

            if tx ^ ty:
                if tx:
                    if self.v_walls[nx][ny]: self.v_walls[nx][ny] = False
                    else: self.v_walls[nx][ny] = True
                else:
                    if self.h_walls[nx][ny]: self.h_walls[nx][ny] = False
                    else: self.h_walls[nx][ny] = True
        except IndexError:
            pass

        self.update_canvas()

    def next_node(self):
        temp = [min(i, key=lambda n: (n.f() if not n.visited else inf)) for i in self.nodes]
        return min(temp, key=lambda n: (n.f() if not n.visited else inf))

    def update_canvas(self):
        self.canvas.delete(ALL)

        # Print borders
        maxx = size_x * (wall_px + box_px) + wall_px
        maxy = size_y*(wall_px+box_px) + wall_px
        self.canvas.create_line(0, 0, 0, maxy, width=wall_px*2, fill='black')
        self.canvas.create_line(0, 0, maxx, 0, width=wall_px * 2, fill='black')
        self.canvas.create_line(maxx-wall_px/2, 0, maxx-wall_px/2, maxy, width=wall_px, fill='black')
        self.canvas.create_line(0, maxy-wall_px/2, maxx, maxy-wall_px/2, width=wall_px, fill='black')

        # Print squares
        weights = self.display_weights.get()
        for i in range(size_x):
            for j in range(size_y):
                if i == j == 0 or (i == size_x - 1 and j == size_y - 1) or self.nodes[i][j].path: col = 'blue'
                elif self.nodes[i][j].g == inf: col = 'white'
                elif self.nodes[i][j].visited: col = 'yellow'
                else: col = 'red'
                if self.nodes[i][j].current: col = 'green'

                x0 = wall_px + i * (wall_px + box_px)
                y0 = wall_px + j * (wall_px + box_px)
                x1 = (i + 1) * (wall_px + box_px)
                y1 = (j + 1) * (wall_px + box_px)
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=col)
                if weights and self.nodes[i][j].f() != float('inf'):
                    self.canvas.create_text(x0+4, y0+5, text='{:.4}'.format(str(self.nodes[i][j].f())), anchor=NW,
                                            font='Arial 10 bold', fill='black')

        # Print vertical walls
        for i, row in enumerate(self.v_walls):
            for j, wall in enumerate(row):
                if wall:
                    x0 = (wall_px + box_px) * (i + 1)
                    y0 = (wall_px + box_px) * j + wall_px/2
                    x1 = x0 + wall_px
                    y1 = y0 + box_px + wall_px
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill='black')

        # Print horizontal walls
        for i, row in enumerate(self.h_walls):
            for j, wall in enumerate(row):
                if wall:
                    y0 = (wall_px + box_px) * (j + 1)
                    x0 = (wall_px + box_px) * i + wall_px/2
                    x1 = x0 + box_px + wall_px
                    y1 = y0 + wall_px
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill='black')

    def run_algorithm(self):
        self.soft_reset()
        self.ALGORITHM = True

    def open(self):
        while self.RUNNING:

            # ==================== A* Algorithm ====================
            cur = self.next_node()
            if self.ALGORITHM:
                # print(cur)
                cur.visited = True

                # Calculate Top
                if not (cur.y == 0 or self.h_walls[cur.x][cur.y - 1]):      # Because the graph is a grid, distance from node to
                    if self.nodes[cur.x][cur.y - 1].g > cur.g + 1:          # node is constant and equal to 1. Therefore instead
                        self.nodes[cur.x][cur.y - 1].g = cur.g + 1          # of creating a connected, weighted graph, we can hard-
                        self.nodes[cur.x][cur.y - 1].prev = cur             # code the vertices by checking for neighbouring walls

                # Calculate Bottom
                if not (cur.y == size_y - 1 or self.h_walls[cur.x][cur.y]): # For this implementation, moving diagonally is not
                    if self.nodes[cur.x][cur.y + 1].g > cur.g + 1:          # allowed.
                        self.nodes[cur.x][cur.y + 1].g = cur.g + 1          #
                        self.nodes[cur.x][cur.y + 1].prev = cur             #

                # Calculate Left
                if not (cur.x == 0 or self.v_walls[cur.x - 1][cur.y]):      # Another change on the original A* is that we do not
                    if self.nodes[cur.x - 1][cur.y].g > cur.g + 1:          # a priority queue to store the tree boundaries. Instead
                        self.nodes[cur.x - 1][cur.y].g = cur.g + 1          # we use the next() function which returns the node that
                        self.nodes[cur.x - 1][cur.y].prev = cur             # would have been in the top of the queue

                # Calculate Right
                if not (cur.x == size_x - 1 or self.v_walls[cur.x][cur.y]): # next() works by sorting all the nodes by f (f=g+h).
                    if self.nodes[cur.x + 1][cur.y].g > cur.g + 1:          # Every node starts with an initial g value of infinite
                        self.nodes[cur.x + 1][cur.y].g = cur.g + 1          # and thus nodes that are not on the tree bound will
                        self.nodes[cur.x + 1][cur.y].prev = cur             # be returned.

                cur.current = False
                cur = self.next_node()
                cur.current = True
                if (cur.x, cur.y) == (size_x - 1, size_y - 1):
                    self.ALGORITHM = False
                    while cur.g != 0:
                        cur.path = True
                        cur = cur.prev
                # input()
            # ======================================================

            self.update_canvas()
            self.update()
        self.cleanup()

    def cleanup(self):
        pass

    def quit(self):
        self.RUNNING = False
        super().quit()
        self.destroy()


if __name__ == '__main__':
    app = App()
    app.open()
