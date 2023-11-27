from model import *
from player import *

import tkinter as tk
from tkinter import ttk

root = tk.Tk()

"""
Used color pallets

backgroud - #26292b
menu buttons - #0e66b2
song backgrounds - #0b3d63
TBA - #1c1c1c
selected song - #e0bb84

"""

musicDirPath = r'.\mymusic'
allSongs = Songlist("All Songs")
queue = Songlist("Queue")

def prepare_all_songs():
    allSongs.clear_list()
    scan_folder(musicDirPath, allSongs)

def play_songs_now():
    print("test")

prepare_all_songs()

root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)
height = 1000
width = 1600
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
    text=f"{allSongs.songList[0]}",
    bg="#26292b",
    fg="#FFFFFF"
)

#test.grid(row=2, column=1)

columns = ("Title", "Artist","Album","Length") # titles for the columns

tree = ttk.Treeview(window, columns=columns, show='headings') # Song list

# tree.heading("Nr.", text="Nr.")
tree.heading("Title", text="Title")
tree.heading("Artist", text="Artist")
tree.heading("Album", text="Album")
tree.heading("Length", text="Track Length")

for nr, song in enumerate(allSongs.songList, start=1):
    tree.insert('', tk.END, values=(song.return_title(), song.return_artist(), song.return_album(), str(song.convert_time()))) # inserts songs into the tree view.

tree.grid(row=1, column=1)

tree.bind('<ButtonRelease-1>', play_songs_now()) # why it broken T^T

def show_frame(frame):
    frame.tkraise()

show_frame(window)

root.resizable(False, False)
root.title("MyPyPlayer")

if __name__ == "__main__":
    root.mainloop()