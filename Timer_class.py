import time

class timer:
	def __init__(self, finish_time):
		self.finish_time = finish_time
		self.delta_time = 0
		self.previous_time = time.perf_counter()

	def tick(self):
		new_time = time.perf_counter()
		self.delta_time += new_time - self.previous_time
		self.previous_time = new_time

	def __bool__(self):
		return self.delta_time > self.finish_time

	def __str__(self):
		return str(self.delta_time)

	def reset(self):
		self.previous_time = time.perf_counter()
		self.delta_time = 0


