import time

class timer:
	def __init__(self, finish_time):
		self.finish_time = finish_time
		self.delta_time = 0

	def tick(self):
		previous_time = time.perf_counter()

