from model import *
from player import *
import tkinter as tk

root = tk.Tk()

"""
Used color pallets

backgroud - #26292b
menu buttons - #0e66b2
song backgrounds - #0b3d63
TBA - #1c1c1c
selected song - #e0bb84

"""

root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)
height = 500
width = 800
x = (root.winfo_screenwidth()//2)-(width//2)
y = (root.winfo_screenheight()//4)-(height//4)
root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

window = tk.Frame(root) # Song list + buttons
window2 = tk.Frame(root) # TBA

for frame in (window, window2):
    frame.grid(row=0, column=0, sticky='nsew')

window.config(background="#26292b")

test = tk.Label(
    window,
    text="Welcome to the MyPyPlayer!",
    bg="#26292b",
    fg="#FFFFFF"
)

test.grid(row=1, column=1)

def show_frame(frame):
    frame.tkraise()

show_frame(window)

root.resizable(False, False)
root.title("MyPyPlayer")
root.mainloop()