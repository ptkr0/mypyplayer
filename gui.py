from tkinter import ttk
from tkinter.messagebox import showinfo
import customtkinter

from model import *
from player import *

musicDirPath = r'.\mymusic'
allSongs = Songlist("All Songs")
queue = Songlist("Queue")

player = Player() #initializes player.py class 

def prepare_all_songs():
    allSongs.clear_list()
    scan_folder(musicDirPath, allSongs)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # root - main app window
        self.title('MyPyPlayer')
        self.geometry('1100x450+0+0')
        self.grid_columnconfigure((0, 9), weight=1)
        customtkinter.set_default_color_theme("green")

        # styles for the table (since CTk doesn't support treeview)
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("Treeview", background="#242424", 
                        fieldbackground="#242424", foreground="#dce4ee", borderwidth=1, font=('Calibri', 12))
        style.configure("Treeview.Heading", background="#242424", foreground="#dce4ee", font=('Calibri', 13, 'bold'))

        self.tree = self.createTree() # creates the table
        self.populate_table(None)
        self.label = self.createCurrSongLabel() # creates the label with current song info
        self.buttons = self.createButtons() # creates the buttons
        self.slider = self.createVolumeSlider() # creates the volume slider
        self.progressBar = self.createProgressBar() # creates the progress bar
        self.progressBar.start()
        self.refresher() # starts the label refreshing method

    def createTree(self):
        columns = ("nr", "title", "artist","album","len") # titles for the columns
        songTable = ttk.Treeview(self, columns=columns, show='headings') # Song list
        songTable.grid(row=0, column=0, padx=20, pady=20, sticky='NS', columnspan=10)

        songTable.heading("nr", text="Nr.")
        songTable.column("nr", minwidth=50, width=50, stretch=0)
        songTable.heading("title", text="Title")
        songTable.column("title", minwidth=250, width=250, stretch=0)
        songTable.heading("artist", text="Artist")
        songTable.column("artist", minwidth=250, width=250, stretch=0)
        songTable.heading("album", text="Album")
        songTable.column("album", minwidth=250, width=250, stretch=0)
        songTable.heading("len", text="Track Length", anchor="e")
        songTable.column("len", minwidth=100, width=100, stretch=0, anchor="e")

        # binding method to selecting item from the table
        songTable.bind('<Double-1>', self.play_song)
        songTable.bind('<KeyPress-r>',self.populate_table)

        return songTable
    
    def createVolumeSlider(self):
        volumeLabel = customtkinter.CTkLabel(self, text='🔈', font=('Calibri', 17))
        volumeLabel.grid(row=3, column=6, padx=5, pady=20)
        volumeSlider = customtkinter.CTkSlider(self, from_=0, to=100, command=self.change_volume, width=150)
        volumeSlider.grid(row=3, column=7, pady=20)
        volumeSlider.set(15) # starting volume
        player.change_volume(0.15) # starting volume
        volumeLabel2 = customtkinter.CTkLabel(self, text='🔊', font=('Calibri', 17))
        volumeLabel2.grid(row=3, column=8, padx=5, pady=20)
        
        return volumeSlider, volumeLabel, volumeLabel2

    def createCurrSongLabel(self):
        currSongLabel = customtkinter.CTkLabel(self, text="No song playing at the moment!", font=('Calibri', 24))
        currSongLabel.grid(row=1, padx=10, pady=20, columnspan=10, sticky='NS')

        return currSongLabel
    
    def createButtons(self):
        toStartButton = customtkinter.CTkButton(self, text='⏮', command=player.rewind_to_start, font=('Calibri', 24))
        toStartButton.grid(row=3, column=1, padx=10, pady=20)

        minusFiveButton = customtkinter.CTkButton(self, text='⏪', command=lambda: player.skip_to(-5.0), font=('Calibri', 24))
        minusFiveButton.grid(row=3, column=2, padx=10, pady=20)

        pauseResumeButton = customtkinter.CTkButton(self, text='⏸', command=player.pause_resume_song, font=('Calibri', 24))
        pauseResumeButton.grid(row=3, column=3, padx=10, pady=20)

        plufFiveButton = customtkinter.CTkButton(self, text='⏩', command=lambda: player.skip_to(5.0), font=('Calibri', 24))
        plufFiveButton.grid(row=3, column=4, padx=10, pady=20)

        toEndButton = customtkinter.CTkButton(self, text='⏭', command=player.skip_to_end, font=('Calibri', 24))
        toEndButton.grid(row=3, column=5, padx=10, pady=20)

        return toStartButton, minusFiveButton, pauseResumeButton, plufFiveButton, toEndButton
    
    def createProgressBar(self):
        progressBar =  customtkinter.CTkProgressBar(self, orientation="horizontal", mode="indeterminate", width=500)
        progressBar.grid(row=2, column=0, padx=10, pady=20, columnspan=10, sticky='NS')

        return progressBar

    def refresher(self):
        player.check_if_playing()

        if player.isPaused:
            self.buttons[2].configure(text='▶')
        else:
            self.buttons[2].configure(text='⏸')

        if not player.isPlaying:
            self.progressBar.configure(mode='indeterminate')
            self.progressBar.start()

            for button in self.buttons:
                if button._state == 'standard' or button._state != 'disabled': # kinda funky but it fixes the button flicker effect 
                    button.configure(state='disabled')

            self.label.configure(text="No song playing at the moment!")
        else:
            for button in self.buttons:
                if button._state == 'disabled':
                    button.configure(state='standard')

            self.label.configure(text='🎵 ' + str(player))
            self.progressBar.stop()
            self.progressBar.configure(mode='determinate')
            self.progressBar.set(player.return_moment() / player.return_length())

        if not player.isPlaying and not queue.check_if_empty(): # queue management 
            player.play_song(queue.songList[0])
            queue.remove_top_song()

        self.after(100, self.refresher) # calls itself every 100ms

    # a method that calls player.py method to change volume
    def change_volume(self, volume):
        player.change_volume(float(volume)/100)

    # filling table with music
    def populate_table(self, event):
        prepare_all_songs() # run method that clears songList and fills it again
        self.tree.delete(*self.tree.get_children()) # clears the old table
        for nr, song in enumerate(allSongs.songList, start=1):
            self.tree.insert('', customtkinter.END, values=(str(nr)+'.', song.return_title(), song.return_artist(), song.return_album(), str(song.convert_time()))) # inserts songs into the tree view.

    # we take index number of the song user clicked and we play it
    def play_song(self, event):
        selected_iid = self.tree.focus()
        item_index = self.tree.index(selected_iid)
        song = allSongs.songList[item_index]
        if player.isPlaying:
            queue.add_song(song)
        else:
            player.play_song(song)
        

if __name__ == '__main__':
    app = App()
    app.mainloop()