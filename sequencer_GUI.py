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

class display_board:
    def __init__(self, master_widget, size:float | int = 30):
        self.canvas_width = size*10
        self.canvas_height = size*20
        self.canvas = tk.Canvas(master_widget, width=canvas_width, height=canvas_height, bg="black")
        self.canvas.pack()
        self.xs = np.linspace(0, canvas_width, 11)
        self.ys = np.linspace(0, canvas_height, 21)
        self.mesh_grid = np.stack(np.meshgrid(self.xs[:-1], self.ys[:-1]), axis=-1)
        for x in self.xs:
            self.canvas.create_line(x, 0, x, canvas_height, fill="white")
        for y in self.ys:
            self.canvas.create_line(0, y, canvas_width, y, fill="white")
        self.squares = []
        for row_idx, arr in enumerate(self.mesh_grid):
            for col_idx, val in enumerate(arr):
                self.squares.append(board_sq(self, row_idx, col_idx, val))

class board_sq:
    def __init__(self, master_board, row:int, col:int, coords:np.ndarray | tuple | list, size:int | float):
        self.master_board = master_board
        self.row = row
        self.col = col
        self.coords = coords
        self.size = size

    def draw(self, color:str):
        x1, y1 = self.coords[0], self.coords[1]
        if hasattr(self, "container"):
            self.container.delete()
        self.container = self.master_board.canvas.create_rectangle(x1+1, y1+1, x1 + self.size -1, y1 + self.size -1, fill=color)




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
## canvas for board
canvas_width = 300
canvas_height = 600
board_canvas = tk.Canvas(right_frame, width=canvas_width, height=canvas_height, bg="black")
board_canvas.pack()
xs = np.linspace(0, canvas_width, 11)
ys = np.linspace(0, canvas_height, 21)

for x in xs:
    board_canvas.create_line(x, 0, x, canvas_height, fill="white")
for y in ys:
    board_canvas.create_line(0, y, canvas_width, y, fill="white")

coord_mesh = np.stack(np.meshgrid(xs[:-1], ys[:-1]), axis=-1)
print(coord_mesh.shape)
sq = board_canvas.create_rectangle(xs[1]+1, ys[1]+1, xs[2]-1, ys[2]-1, fill="white")

### MAINLOOP ###
root.mainloop()