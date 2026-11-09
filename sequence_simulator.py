import numpy as np
import Thread_bot_move_sim as MS
import matplotlib.pyplot as plt
import pprint as pp
import sim_board_feed as board_gen
from sim_board_feed import trg

tetromino_keys = (
	'fw z',
	'bw z',
	'fw l',
	'bw l',
	't',
	'sq',
	'long',
)

def deter_repeats(*nums):
    ref = nums[0]
    mask = [True if n == ref else False for n in nums]
    return all(mask)

def generate_sequence(n_moves:int = 100, seed:int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    key_seq = []
    prev_two = None
    n=0
    while n < n_moves -1:
        rep_error = False
        rn = int(rng.random() * len(tetromino_keys))
        if len(key_seq) > 2:
            prev_two = key_seq[-2::]
        if prev_two is not None:
            rep_error = deter_repeats(*prev_two, rn)
        if rep_error:
            n -= 1
            continue
        n+=1
        key_seq.append(tetromino_keys[rn])
    return key_seq

def eval_board(board:np.ndarray) -> np.ndarray:
    b = board.copy()
    rem_idxs = []
    for row_idx, row in enumerate(b):
        if len(row[row == 0]) == 0:
            rem_idxs.append(row_idx)
    if len(rem_idxs) > 0:
        trimmed = np.delete(b, rem_idxs, axis=0)
        pad = np.repeat(np.zeros((1,10)), len(rem_idxs), axis=0)
        return np.insert(trimmed, 0, pad, axis=0)
    else:
        return b

if __name__ == '__main__':
    move_sim = MS.tb_move_sim()
    tetro_sequence = np.asarray(generate_sequence(n_moves = 100, seed = 2))
    trg_handler = trg.ref_grid_handler()
    curr_board = board_gen.generate_blank_board()
    print(f"simulation: 0\n{curr_board}\n")
    for n, scode in enumerate(tetro_sequence, start=1):
        if not board_gen.add_shape_to_board(curr_board, scode, trg_handler):
            print(f"simulations failed at sim number {n}")
            break
        shape_dict = trg_handler.minimised_data.get(scode)
        move_sim.new_sim_moves(curr_board, shape_dict)
        move_sim.best_move = move_sim.evaluate_moves_by_score()
        curr_board = move_sim.best_move.final_move_grid
        print(f"simulation: {n}, shape = {scode}\n{curr_board}\n")
        curr_board = eval_board(curr_board)
        print(f"after evaluation:\n{curr_board}\n")

    # write function to check the boards produced by the simulator
    # need to check if a line is cleared and update the board by removing it
    # and moving the rest of the tetromino's down

# next thing to do. handle the errors better, so evaluate adding the move to the board before sending the board to the
# sim. if it cannot be placed on the board without creating a 2 then just call it game.

