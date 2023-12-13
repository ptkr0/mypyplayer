import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo

from model import *
from player import *

musicDirPath = r'.\mymusic'
allSongs = Songlist("All Songs")
queue = Songlist("Queue")

player = Player() #initializes player.py class 

def prepare_all_songs():
    allSongs.clear_list()
    scan_folder(musicDirPath, allSongs)

# for testing purposes
def button_clicked(test):
    print(test)

# we take index number of the song user clicked and we play it
# needs to be changed
def play_song(event):
    selected_iid = songTable.focus()
    
    item_index = songTable.index(selected_iid)
    player.play_song(allSongs.songList[item_index])

# root - main app window
root = tk.Tk()
root.title('MyPyPlayer')
root.geometry('1280x720+50+50')
root.resizable(False, False) # for now

columns = ("title", "artist","album","len") # titles for the columns
songTable = ttk.Treeview(root, columns=columns, show='headings') # Song list

songTable.heading("title", text="Title")
songTable.column("title", minwidth=250, width=250, stretch=0)
songTable.heading("artist", text="Artist")
songTable.column("artist", minwidth=250, width=250, stretch=0)
songTable.heading("album", text="Album")
songTable.column("album", minwidth=250, width=250, stretch=0)
songTable.heading("len", text="Track Length", anchor="e")
songTable.column("len", minwidth=100, width=100, stretch=0, anchor="e")

# filling table with music
# index number still to be added
def populate_table(event):
    prepare_all_songs() # run method that clears songList and fills it again
    songTable.delete(*songTable.get_children()) # clear table if it was filled before
    for nr, song in enumerate(allSongs.songList, start=1):
        songTable.insert('', tk.END, values=(song.return_title(), song.return_artist(), song.return_album(), str(song.convert_time()))) # inserts songs into the tree view.
    
populate_table('event')

songTable.bind('<<TreeviewSelect>>', play_song) # binding function to selecting item from the table
songTable.pack()
root.bind('<KeyPress-r>',populate_table)

# fix for blurry UI
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
finally:
    root.mainloop()