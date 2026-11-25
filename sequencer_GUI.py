import tkinter as tk
from tkinter import ttk
import numpy as np
import sequence_simulator as seq
import sim_board_feed as feed
import sequencer_GUI_menu as menu_maker
import io_utils as io
import json

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
                    self.canvas.delete(obj.rect_id)

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
    for row, col in taken_coords:
        canvas_obj.switch_squares("wheat", row, col)

    colour_str = seq.tetromino_colours.get(current_result[2])
    active_coords = current_result[1]
    if active_coords and colour_str:
        for row,col in active_coords.position_indexes:
            canvas_obj.switch_squares(colour_str, row, col)

def update_slider():
    global root
    max_idx = len(root.sim_results) - 1
    if root.run_bool:
        current_iter = root.iter_slider.get()
        if current_iter < max_idx:
            root.iter_slider.set(current_iter+1)
            root.after(root.anim_delay.get(), update_slider)
        else:
            root.run_bool = False

def animate():
    global root
    if not hasattr(root, "sim_results"):
        return
    if not root.run_bool:
        root.run_bool = True
        update_slider()
    elif root.run_bool:
        root.run_bool = False

def test_callable():
    print("function call")

def parse_json():
    global root
    fp = io.get_json_file()
    with open(fp) as json_f:
        data_in = json.load(json_f)
    # data_in is dict
    data_in = [(np.asarray(x), None, None, None) for x in data_in.values()]
    root.textbox.delete(1.0, tk.END)
    root.textbox.insert(tk.END, "Using imported data")
    root.sim_results = data_in
    root.iter_slider.configure(to=len(root.sim_results)-1)
    root.iter_slider.set(0)
    update_board_canvas()


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

#####
## simulate button
root.sim_button = tk.Button(left_frame, text="Run Simulation", command=compute_simulation)
root.sim_button.grid(row=5, column=0, padx=5, pady=5, columnspan=2)

#####
## iteration slider
root.iter_slider = tk.Scale(right_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=275, label="Iteration slider", command=update_board_canvas)
root.iter_slider.pack()

#####
## play button
root.run_bool = False
root.run_button = tk.Button(left_frame, text="▶️⏸️", command=animate)
root.run_button.grid(row=6, column=0, padx=5, pady=5, columnspan=2)

#####
## animation speed
root.anim_delay = tk.IntVar(value=500) #miliseconds
root.speed_label = tk.Label(left_frame, text="Speed (ms):", fg="blue")
root.speed_label.grid(row=7, column=0, padx=5, pady=5)
root.speed_spinbox = ttk.Spinbox(left_frame, width=5, textvariable=root.anim_delay, from_=5, to=5000)
root.speed_spinbox.grid(row=7, column=1, padx=5, pady=5)

#####
## file menu
menu_structure = {"File": {"Import json": parse_json}}
menu_tracking = menu_maker.add_menu(root, **menu_structure)

### MAINLOOP ###
root.mainloop()