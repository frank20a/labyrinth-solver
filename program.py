from tkinter import *
from tkinter.ttk import OptionMenu
from functools import partial

size_x = 15
size_y = 10
box_px = 35
wall_px = 8

inf = float('inf')


def manhatan(x, y):
    return (size_x - x) + (size_y - y)


def eucledean(x, y):
    return ((size_x - x) ** 2 + (size_y - y) ** 2) ** 0.5


class Node():
    def __init__(self, x, y):
        self.visited = False
        self.x = x
        self.y = y
        self.g = inf

        self.h = 0
        self.set_h_func('eucledean')

        self.prev = None
        self.path = False
        self.current = False

    def f(self):
        return self.g + self.h

    def set_h_func(self, h_func):
        if h_func == 'manhatan': self.h = manhatan(self.x, self.y)
        if h_func == 'eucledean': self.h = eucledean(self.x, self.y)

    def __str__(self):
        return '[' + str(self.x) + ',' + str(self.y) + '] g=' + str(self.g) + ' h=' + str(self.h) + ' f=' + str(
            self.f()) + '\n'


class App(Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Window settings
        self.minsize(width=1100, height=700)
        self.maxsize(width=1100, height=700)
        self.resizable(width=False, height=False)
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.title("Labyrinth Solver - by Frank Fourlas")

        # Labyrinth
        self.reset_maze()

        # Sidebar
        sidebar = Frame(self, bg='grey')
        Button(sidebar, text='Run Algorithm', command=self.run_algorithm, height=2, font=25).pack(side=TOP, padx=10,
                                                                                                  pady=10)
        self.h_func = StringVar()
        self.h_func.trace_add('write', self.change_h_func)
        OptionMenu(sidebar, self.h_func, 'eucledean', *['eucledean', 'manhatan']).pack(side=TOP, padx=10, pady=10)
        Button(sidebar, text='Reset Maze', command=self.reset_maze, height=2, font=25).pack(side=TOP, padx=10,
                                                                                                  pady=10)
        sidebar.pack(side=LEFT, fill=Y)

        # Canvas
        self.canvas = Canvas(self, bg='#a0ff8f')
        self.canvas.bind("<Button-1>", self.canvas_click)
        self.canvas.pack(side=LEFT, expand=True, fill=BOTH)
        self.update_canvas()

        self.RUNNING = True
        self.ALGORITHM = False

    def reset_maze(self):
        self.nodes = [[Node(i, j) for j in range(size_y)] for i in range(size_x)]
        self.nodes[0][0].g = 0
        self.v_walls = [[False for j in range(size_y)] for i in range(size_x - 1)]
        self.h_walls = [[False for j in range(size_y - 1)] for i in range(size_x)]

    def soft_reset(self):
        self.nodes = [[Node(i, j) for j in range(size_y)] for i in range(size_x)]
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

    def change_h_func(self, var, indx, mode):
        h_func = self.h_func.get()
        for i in self.nodes:
            for j in i:
                j.set_h_func(h_func)

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
                print(cur)
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
                input()
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
