import numpy as np

class tetris_square:
	def __init__(self, row, col, value, bg_value):
		self.index = np.array([row, col])
		self.px_mean = value
		self.bg_value = bg_value

		self.is_accounted_for = False

		self.is_top_border = False
		self.is_bottom_border = False
		self.is_left_border = False
		self.is_right_border = False

		self.is_static = True
		self.is_bg = True



		self.neighbour_idx = {
			'above': self.index + [-1, 0],
			'below': self.index + [1, 0],
			'left': self.index + [0, -1],
			'right': self.index + [0, 1],
			'topl': self.index + [-1, -1],
			'topr': self.index + [-1, 1],
			'botl': self.index + [1, -1],
			'botr': self.index + [1, 1]
		}
		self.neighbour_objx = {
			'above': None,
			'below': None,
			'left': None,
			'right': None,
			'topl': None,
			'topr': None,
			'botl': None,
			'botr': None,
		}
		self._check_if_bg()

	def get_neighbours(self, input_grid: np.ndarray):
		height_lim = len(input_grid)-1
		print(height_lim)
		width_lim = len(input_grid[0])-1
		print(width_lim)
		for key, coord in self.neighbour_idx.items():
			row = coord[0]
			col = coord[1]
			print(f"row: {row}, col: {col}")
			do_asignment = True
			if coord[0] <0:
				self.is_top_border = True
				do_asignment = False
			if coord[0] > height_lim:
				self.is_bottom_border = True
				do_asignment = False
			if coord[1] <0:
				self.is_left_border = True
				do_asignment = False
			if coord[1] > width_lim:
				self.is_right_border = True
				do_asignment = False

			if do_asignment:
				print("doing asignement")
				self.neighbour_objx[key] = input_grid[row][col]

	def update_val(self, new_mean_px):
		if new_mean_px < 0:
			new_mean_px = 0
		elif new_mean_px > 255:
			new_mean_px = 255
		self.px_mean = new_mean_px
		self._check_if_bg()

	def accounted_for(self, set_to: bool = True):
		self.is_accounted_for = set_to

	def _check_if_bg(self):
		if self.px_mean - self.bg_value <=2:
			self.is_bg = True
			self.is_static = True
			self.accounted_for()
		else:
			self.is_bg = False
			self.is_static = False
			self.accounted_for(set_to=False)

	def return_active_neighbours(self):
		non_bg_obj_neighbours = []
		above = self.neighbour_objx.get("above")
		below = self.neighbour_objx.get("below")
		left =  self.neighbour_objx.get("left")
		right =  self.neighbour_objx.get("right")

		if above is not None:
			if not above.is_bg:
				non_bg_obj_neighbours.append(above)
		if below is not None:
			if not below.is_bg:
				non_bg_obj_neighbours.append(below)
		if left is not None:
			if not left.is_bg:
				non_bg_obj_neighbours.append(left)
		if right is not None:
			if not right.is_bg:
				non_bg_obj_neighbours.append(right)

		return non_bg_obj_neighbours






