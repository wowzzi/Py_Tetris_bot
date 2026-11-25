import tkinter as tk

def add_menu(master_widget, **kwargs):
	# menu bar at top of master widget
    bar_menu = tk.Menu(master_widget)
    # update master_widget config to substantiate the bar menu
    master_widget.config(menu=bar_menu)
    tracking_dict = {}
    for key, value in kwargs.items():
        # each key should be substantiated as a menu item on the bar
        # each value should be dict-like with each key inside being the name of the drop-down item and the value being the command.
        menu_name = f"{key}"
        tracking_dict[menu_name] = tk.Menu(bar_menu)
        bar_menu.add_cascade(label=menu_name, menu=tracking_dict[menu_name])
        for sub_menu, _callable in value.items():
            tracking_dict[menu_name].add_command(label=sub_menu, command=_callable)
    return tracking_dict

# ok lets make a menu making system using dict-like structure as the architect of the menu implementation
# we pass kwargs as key value, but if value is dict then we substantiate a new cascade
# one rule is to keep every button as a command and not as radio or check button, unless I find a clever way to handle those exceptions
# im just thinking have we gone way out of scope? kinda fun tho