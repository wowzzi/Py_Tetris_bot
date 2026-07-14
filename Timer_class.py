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

	def quick_reset(self, speed_factor = 0.5):
		"""
		Method to reset the timer on a shortened duration.
		speed_factor parameter, intended to work 0.0 < speed_factor <= 1.0
		a speed factor of 1 would be instantaneous completion of the timer.
		a speed factor of 0 would be normal execution of the timer.
		"""
		if speed_factor < 0.0:
			speed_factor = 0.0
		self.previous_time = time.perf_counter()
		self.delta_time = self.finish_time * speed_factor