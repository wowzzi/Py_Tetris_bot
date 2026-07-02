from mss import MSS
from mss import tools
from pathlib import Path


def on_exists(fname:str) -> None:
	"""Callback example when we try to overwrite an existing screenshot."""

	file = Path(fname)
	if file.is_file():
		newfile = file.with_stem(f"{file.name}_old")
		print(f"{fname} ➡ {newfile}")
		if not newfile.is_file():
			file.rename(newfile)

with MSS() as sct:
	for filename in sct.save():
		print(filename)
		print()

	file = sct.shot(output="mon-{mon}.png", callback=on_exists)
	print(file)

	# filename = sct.shot(mon=-1, output='fullscreen.png')

	#part of the screen to cap
	monitor = {"top": 0, "left": 0, "width": 160, "height": 135}
	output = "scn-{top}x{left}_{width}x{height}.png".format(**monitor)

	#grab the data
	sct_img = sct.grab(monitor)

	#save to file
	tools.to_png(sct_img.rgb, sct_img.size, output=output)

	print(output)

	for n, mon in enumerate(sct.monitors):
		print(n, ": ", mon)
		print()

	mon = sct.monitors[2]

	monitor = {
		"top": mon["top"] +100, #100px from top,
		"left": mon["left"] +100,
		"width": mon["width"] - 500,
		"height": mon["height"] - 500,
		"mon": 2
	}

	output = "sct-monitor{mon}_{top}x{left}_{width}x{height}.png".format(**monitor)

	sct_img = sct.grab(monitor)

	tools.to_png(sct_img.rgb, sct_img.size, output=output)
	print(output)

	monitor = sct.monitors[1]

	left = monitor["left"] + int(monitor["width"] * 0.05) #should work same as *5 // 100?
	top = monitor["top"] + int(monitor["height"] * 0.05)
	right = left + 400
	lower = top + 400
	bbox = (left, top, right, lower)

	im_file = sct.grab(bbox)

	png_data = tools.to_png(im_file.rgb, im_file.size)
	print(png_data)