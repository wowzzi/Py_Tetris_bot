import tkinter as tk
from tkinter import ttk
import numpy as np
import sequence_simulator as seq
import sim_board_feed as feed

def call_sequence():
    global root
    iterations = root.iter_var.get()
    seed = root.seed_var.get()
    sequence = seq.generate_sequence(iterations, seed)
    sequence_text = "".join([f"{s}," for s in sequence])
    # sequence_text = [f"{s}," for s in sequence]
    root.textbox.delete(1.0, tk.END)
    # for t in sequence_text:
    #     root.textbox.insert(tk.END, t)
    root.textbox.insert(tk.END, sequence_text)
    root.sequence = sequence

class display_board:
    def __init__(self, master_widget, size:float | int = 30):
        self.size = size
        self.canvas_width = self.size*10
        self.canvas_height = self.size*20
        self.canvas = tk.Canvas(master_widget, width=self.canvas_width, height=self.canvas_height, bg="black")
        self.canvas.pack()
        self.xs = np.linspace(0, self.canvas_width, 11)
        self.ys = np.linspace(0, self.canvas_height, 21)
        self.mesh_grid = np.stack(np.meshgrid(self.xs[:-1], self.ys[:-1]), axis=-1)
        for x in self.xs:
            self.canvas.create_line(x, 0, x, self.canvas_height, fill="white")
        for y in self.ys:
            self.canvas.create_line(0, y, self.canvas_width, y, fill="white")
        self.squares = []
        for row_idx, arr in enumerate(self.mesh_grid):
                self.squares.append([board_sq(self, row_idx, col_idx, val, self.size) for col_idx, val in enumerate(arr)])

    def switch_squares(self, color:str, row_idx:int, col_idx:int):
        current_obj = self.squares[row_idx][col_idx]
        current_obj.draw(color)

    def clear_board(self):
        for row in self.squares:
            for obj in row:
                if hasattr(obj, "rect_id"):
                    # obj.container.delete()
                    self.canvas.delete(obj.rect_id)
                    # print(type(obj.rect_id))
                    # print(obj.rect_id)


class board_sq:
    def __init__(self, master_board, row:int, col:int, coords:np.ndarray | tuple | list, size:int | float):
        self.master_board = master_board
        self.row = row
        self.col = col
        self.coords = coords
        self.size = size

    def draw(self, color:str):
        x1, y1 = self.coords[0], self.coords[1]
        if hasattr(self, "rect_id"):
            self.master_board.canvas.delete(self.rect_id)
        self.rect_id = self.master_board.canvas.create_rectangle(x1+1, y1+1, x1 + self.size -1, y1 + self.size -1, fill=color)

def proxy_clear():
    global canvas_obj
    canvas_obj.clear_board()

def compute_simulation():
    global root
    sequence = root.textbox.get("1.0", tk.END)
    sequence = sequence.split(",")
    sequence = [x.strip() for x in sequence if x in seq.tetromino_keys]
    root.sim_results = seq.compile_simulations(sequence)
    root.iter_slider.configure(to=len(root.sim_results)-1)
    # print(root.iter_slider.get()) # current iteration setting
    root.iter_slider.set(0)
    update_board_canvas()

def update_board_canvas(*args):
    global root
    global canvas_obj
    if not hasattr(root, "sim_results"):
        return
    canvas_obj.clear_board()
    current_iter = root.iter_slider.get()
    current_result = root.sim_results[current_iter]
    np_grid = current_result[0]
    taken_coords = np.stack(np_grid.nonzero(), axis =-1)
    colour_str = seq.tetromino_colours.get(current_result[2])
    for row, col in taken_coords:
        canvas_obj.switch_squares("wheat", row, col)
    active_coords = current_result[1].position_indexes
    for row,col in active_coords:
        canvas_obj.switch_squares(colour_str, row, col)




    # so with taken coords we should use those coords to index the canvas grid and turn them orange or smthn
    # then take the coords from index 1 in result, that object has attribute position_indexes, use those to
    # change the colour of the those sqaures to a colour from the dict of colours
    # [[y,x], [y,x]]




########################
### main window root ###
########################

root = tk.Tk()
body = tk.Frame(root)
body.pack()

left_frame = tk.Frame(body)
left_frame.pack(side=tk.LEFT)

right_frame = tk.Frame(body)
right_frame.pack(side=tk.LEFT)


## Seed selector
seed_label = tk.Label(left_frame, text="Seed:")
seed_label.grid(row=0, column=0, padx=5, pady=5)

root.seed_var = tk.IntVar()
seed_spinbox = ttk.Spinbox(left_frame, width=5, textvariable = root.seed_var, from_=0, to=10000)
seed_spinbox.grid(row=0, column=1)
seed_spinbox.grid(row=0, column=1, padx=5, pady=5)
#####
## Iterations selector
iterations_label = tk.Label(left_frame, text="Iterations:")
iterations_label.grid(row=1, column=0, padx=5, pady=5)

root.iter_var = tk.IntVar(value=100)
iter_spinbox = ttk.Spinbox(left_frame, width=5, textvariable = root.iter_var, from_=1, to=10000)
iter_spinbox.grid(row=1, column=1, padx=5, pady=5)

#####
## Generate sequence button
gen_seq_button = tk.Button(left_frame, text="Generate Sequence", command=call_sequence)
gen_seq_button.grid(row=2, column=0, padx=5, pady=5, columnspan=2)

root.textbox = tk.Text(left_frame, width=20, height=20, wrap=tk.WORD)
root.textbox.grid(row=3, column=0, padx=5, pady=5, columnspan=2)

#####
## Test button for clearing coloured rects
root.clear_button = tk.Button(left_frame, text="Clear Board", command=proxy_clear)
root.clear_button.grid(row=4, column=0, padx=5, pady=5, columnspan=2)

#####
## canvas for board
canvas_obj = display_board(right_frame, 30)
# canvas_obj.switch_squares("blue", 0, 0)
# canvas_obj.switch_squares("white", 0, 1)
# canvas_obj.switch_squares("green", 0, 2)
# canvas_obj.switch_squares("red", 0, 3)
# canvas_obj.switch_squares("purple", 0, 4)
# canvas_obj.switch_squares("yellow", 0, 5)
# canvas_obj.switch_squares("orange", 0, 6)
# canvas_obj.switch_squares("orange", 0, 7)
# canvas_obj.switch_squares("orange", 0, 8)
# canvas_obj.switch_squares("orange", 0, 9)
# canvas_obj.switch_squares("orange", 19, 9)
# canvas_width = 300
# canvas_height = 600
# board_canvas = tk.Canvas(right_frame, width=canvas_width, height=canvas_height, bg="black")
# board_canvas.pack()
# xs = np.linspace(0, canvas_width, 11)
# ys = np.linspace(0, canvas_height, 21)
#
# for x in xs:
#     board_canvas.create_line(x, 0, x, canvas_height, fill="white")
# for y in ys:
#     board_canvas.create_line(0, y, canvas_width, y, fill="white")
#
# coord_mesh = np.stack(np.meshgrid(xs[:-1], ys[:-1]), axis=-1)
# print(coord_mesh.shape)
# sq = board_canvas.create_rectangle(xs[1]+1, ys[1]+1, xs[2]-1, ys[2]-1, fill="white")

#####
## simulate button
root.sim_button = tk.Button(left_frame, text="Run Simulation", command=compute_simulation)
root.sim_button.grid(row=5, column=0, padx=5, pady=5, columnspan=2)

#####
## iteration slider
# seq_len = root.textbox.get("1.0", tk.END)
# seq_len = seq_len.split(",")
# seq_len = len([x.strip() for x in seq_len if x in seq.tetromino_keys])
root.iter_slider = tk.Scale(right_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=275, label="Iteration slider", command=update_board_canvas)
root.iter_slider.pack()


### MAINLOOP ###
root.mainloop()