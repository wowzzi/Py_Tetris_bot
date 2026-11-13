import numpy as np
import pprint as pp
import Tetromino_ref_grids as trg

def generate_blank_board():
    return np.zeros((20,10), dtype=np.int8)

def add_shape_to_board(game_board:np.ndarray, shape_key:str, ref_grid_obj) -> bool:
    tmo_dict = ref_grid_obj.minimised_data.get(shape_key)
    tmos = tmo_dict.values()
    r = []
    for tmo in tmos:
        height = tmo.shape[0]
        width = tmo.shape[1]
        new_board = game_board.copy().astype(np.uint8)
        start_x = 4-(width//2)
        end_x = start_x + width
        new_board[0:height, start_x:end_x] += tmo.astype(np.uint8)
        if len(new_board[new_board==2]) == 0:
            r.append(True)
        else:
            r.append(False)

    return any(r)

if __name__ == "__main__":
    trg_handler = trg.ref_grid_handler()
    board = generate_blank_board()
    next_board = add_shape_to_board(board, "t", trg_handler)
    print(next_board)