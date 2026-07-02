from PIL import Image
import mss
import numpy as np

# with mss.MSS() as sct:
# 	for n, monitor in enumerate(sct.monitors[1:], start=1):
# 		#get our raw pixel data
# 		sct_img = sct.grab(monitor)
#
# 		img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
#
# 		output = f"monitor-{n}.png"
# 		img.save(output)
# 		img.show()
# 		print(output)

with mss.MSS() as sct:
	#grab my screen pixels
	my_img = sct.grab(sct.monitors[1])

	#make a blank canvas
	blank_canvas = Image.new('RGB', my_img.size)

	#just checking what .raw gives, so turns out it gives weird hexadeicmal, but if you list it, it gets converted to
	#integers. then its in the format BGRX, blue, green, red, alpha.
	print(list(my_img.raw[:4]))

	#convert to RGB
	RGB_pixel_tuple = zip(my_img.raw[2::4],   my_img.raw[1::4], my_img.raw[::4])

	blank_canvas.putdata(list(RGB_pixel_tuple))



	np_arr = np.array(blank_canvas)
	print(np_arr.shape)
	center_x, center_y = (np_arr.shape[0]//2, np_arr.shape[1]//2)
	print(np_arr[center_x, center_y])
	np_arr[center_x, center_y] = np.array([255, 0, 0])
	img_2 = Image.fromarray(np_arr)
	img_2.show()