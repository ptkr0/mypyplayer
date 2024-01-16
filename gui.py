from tkinter import ttk
import customtkinter
from PIL import Image
from CTkMessagebox import CTkMessagebox

from model import *
from player import *

from os import environ
import os.path

musicDirPath = os.path.join(environ["USERPROFILE"], "Music")
allSongs = Songlist("All Songs")
queue = Songlist("Queue")

ABOUT_TEXT = r"""     
MyPyPlayer is a simple music player written in Python with the use of:
- Pygame for playing music
- eyed3 for getting metadata from tracks
- CustomTkinter for better looking UI 
- CTkMessagebox for custom messagebox (✿ ◡ ‿ ◡ )
- TTK for table widget
- PIL for image support
- PyYAML for easy save/reload feature
"""

HELP_TEXT = r"""
Welcome to MyPyPlayer - a simple music player written in Python
Use your mouse or keyboard to navigate through the menus
If you don't see your music remember to put it in 'mymusic' directory in the program files
After that press 'R' to refresh table
"""

player = Player() #initializes player.py class 

def prepare_all_songs():
    allSongs.clear_list()
    scan_folder(musicDirPath, allSongs)

"""not in the class since 2 different classes use it"""
def createTree(self):
    columns = ("nr", "title", "artist","album","len") # titles for the columns
    songTable = ttk.Treeview(self, columns=columns, show='headings') # Song list
    songTable.heading("nr", text="Nr.")
    songTable.column("nr", minwidth=50, width=50, stretch=0)
    songTable.heading("title", text="Title")
    songTable.column("title", minwidth=250, width=250, stretch=0)
    songTable.heading("artist", text="Artist")
    songTable.column("artist", minwidth=250, width=250, stretch=0)
    songTable.heading("album", text="Album")
    songTable.column("album", minwidth=250, width=250, stretch=0)
    songTable.heading("len", text="Track Length", anchor="e")
    songTable.column("len", minwidth=120, width=120, stretch=0, anchor="e")

    return songTable

# widget with progress bar and time labels
class ProgressBarFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.elapsedTime = customtkinter.CTkLabel(self, text='-:--:--' )
        self.elapsedTime.grid(row=0, column=1, padx=10, sticky='NS')
        self.pBard = customtkinter.CTkProgressBar(self, orientation="horizontal", mode="indeterminate", width=500)
        self.pBard.grid(row=0, column=3, padx=10, sticky='NS')
        self.totalTime = customtkinter.CTkLabel(self, text='-:--:--' )
        self.totalTime.grid(row=0, column=5, padx=10, sticky='NS')

class BottomButtonsFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.aboutButton = customtkinter.CTkButton(self, text='About', command=lambda: self.master.open_text_dialog(2), font=('Roboto', 19), hover=True, fg_color='gray')
        self.aboutButton.grid(row=0, column=1, padx=10)
        self.queueButton = customtkinter.CTkButton(self, text='Queue', command=lambda: self.master.open_text_dialog(3), font=('Roboto', 19), hover=True)
        self.queueButton.grid(row=0, column=3, padx=10)
        self.helpButton = customtkinter.CTkButton(self, text='Help', command=lambda: self.master.open_text_dialog(1), font=('Roboto', 19), hover=True, fg_color='gray')
        self.helpButton.grid(row=0, column=5, padx=10)

class HelpWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('Help')
        self.geometry("770x200")
        self.grid_columnconfigure((0, 1), weight=1)

        self.label = customtkinter.CTkLabel(self, text=HELP_TEXT, font=('Roboto', 19), justify='center')
        self.label.pack(padx=10, pady=5)
        self.button = customtkinter.CTkButton(self, text='Go Back', command=self.destroy, font=('Roboto', 19), hover=True)
        self.button.pack(padx=10, pady=5)

class AboutWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('About')
        self.geometry("750x300")
        self.grid_columnconfigure((0, 1), weight=1)

        self.label = customtkinter.CTkLabel(self, text=ABOUT_TEXT, font=('Roboto', 19), justify='center')
        self.label.pack(padx=10, pady=5)
        self.button = customtkinter.CTkButton(self, text='Go Back', command=self.destroy, font=('Roboto', 19), hover=True)
        self.button.pack(padx=10, pady=5)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # main app window config
        self.title('MyPyPlayer')
        self.geometry('1100x560+20+20')
        self.grid_columnconfigure((0, 9), weight=1)
        customtkinter.set_default_color_theme("green")

        # styles for the table (since CTk doesn't support treeview)
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("Treeview", background="#242424", 
                        fieldbackground="#242424", foreground="#dce4ee", borderwidth=1, font=('Roboto', 13), rowheight=22)
        style.configure("Treeview.Heading", background="#242424", foreground="#dce4ee", font=('Roboto', 13, 'bold'))

        self.tree = createTree(self) # creates the table
        self.tree.grid(row=0, column=0, padx=20, pady=20, sticky='NS', columnspan=10)
        # binding method to selecting item from the table
        self.tree.bind('<Double-1>', self.play_song)
        self.tree.bind('<KeyPress-r>',self.populate_table)
        self.label = self.createCurrSongLabel() # creates the label with current song info
        self.buttons = self.controlButtons() # creates the buttons
        self.slider = self.createVolumeSlider() # creates the volume slider
        self.slider[0].set(int(player.volume*100))
        self.progressBar = ProgressBarFrame(master=self, height=20) # creates the progress bar
        self.progressBar.grid(row=2, column=0, padx=10, pady=20, columnspan=10, sticky='NS')
        self.bottomButtons = BottomButtonsFrame(master=self, height=20)
        self.bottomButtons.grid(row=4, column=0, padx=10, pady=20, columnspan=10, sticky='NS')
        self.progressBar.pBard.start() # starts the progress bar (required for fancy animation)
        self.bind('<space>',lambda d: player.pause_resume_song())
        self.bind('<KeyPress-Left>',lambda e: self.slider[0].set(self.slider[0].get()-1))
        self.bind('<KeyPress-Right>',lambda f: self.slider[0].set(self.slider[0].get()+1))
        self.help_dialog = None
        self.about_dialog = None
        self.queue_dialog = None
        self.refresher() # starts the label refreshing method
    
    def createVolumeSlider(self):
        volumeIcon = customtkinter.CTkImage(light_image=Image.open('assets/vup.png'),
                                  size=(24, 24))
        volumeLabel = customtkinter.CTkLabel(self, image=volumeIcon, text="")
        volumeLabel.grid(row=3, column=6, padx=10, pady=20)
        volumeSlider = customtkinter.CTkSlider(self, from_=0, to=100, command=self.change_volume, width=150)
        volumeSlider.grid(row=3, column=7, padx=5, pady=20)
        
        return volumeSlider, volumeLabel, volumeIcon

    def createCurrSongLabel(self):
        currSongLabel = customtkinter.CTkLabel(self, text="No song playing at the moment!", font=('Roboto', 24))
        currSongLabel.grid(row=1, padx=10, pady=20, columnspan=10, sticky='NS')

        return currSongLabel
    
    def controlButtons(self):
        toStartButton = customtkinter.CTkButton(self, text='⏮', command=player.rewind_to_start, font=('Roboto', 24), hover=True)
        toStartButton.grid(row=3, column=1, padx=10, pady=20)

        minusFiveButton = customtkinter.CTkButton(self, text='⏪', command=lambda: player.skip_to(-5.0), font=('Roboto', 24))
        minusFiveButton.grid(row=3, column=2, padx=10, pady=20)

        pauseResumeButton = customtkinter.CTkButton(self, text='⏸', command=player.pause_resume_song, font=('Roboto', 24))
        pauseResumeButton.grid(row=3, column=3, padx=10, pady=20)

        plufFiveButton = customtkinter.CTkButton(self, text='⏩', command=lambda: player.skip_to(5.0), font=('Roboto', 24))
        plufFiveButton.grid(row=3, column=4, padx=10, pady=20)

        toEndButton = customtkinter.CTkButton(self, text='⏭', command=player.skip_to_end, font=('Roboto', 24))
        toEndButton.grid(row=3, column=5, padx=10, pady=20)

        return toStartButton, minusFiveButton, pauseResumeButton, plufFiveButton, toEndButton
    
    def refresher(self):
        player.check_if_playing()

        """spotify like volume icon changer"""
        if player.volume == 0:
            self.slider[2].configure(light_image = Image.open('assets/vmute.png'))
        elif player.volume < 0.33:
            self.slider[2].configure(light_image = Image.open('assets/vlow.png'))
        elif player.volume < 0.66:
            self.slider[2].configure(light_image = Image.open('assets/vmid.png'))
        else:
            self.slider[2].configure(light_image = Image.open('assets/vup.png'))

        if player.isPaused:
            self.buttons[2].configure(text='▶')
        else:
            self.buttons[2].configure(text='⏸')

        """if player is not playing, we disable all the buttons and turn on fancy progress bar animation"""
        if not player.isPlaying:
            self.progressBar.pBard.configure(mode='indeterminate')
            self.progressBar.pBard.start()
            self.progressBar.elapsedTime.configure(text='-:--:--')
            self.progressBar.totalTime.configure(text='-:--:--')

            for button in self.buttons[0:5]:
                if button._state == 'standard' or button._state != 'disabled': # kinda funky but it fixes the button flicker effect 
                    button.configure(state='disabled')

            self.label.configure(text="No song playing at the moment!")
            
            """else we enable the buttons and turn off the fancy animation"""
        else:
            for button in self.buttons[0:5]:
                if button._state == 'disabled':
                    button.configure(state='standard')

            self.label.configure(text='🎵 ' + str(player))
            self.progressBar.pBard.stop() # we stop the fancy animation
            self.progressBar.pBard.configure(mode='determinate') # we change the mode to determinate so we can use it as a progress bar
            self.progressBar.pBard.set(player.return_moment() / player.return_length()) # progress bar works from 0 to 1
            self.progressBar.elapsedTime.configure(text=timedelta(seconds = round(player.return_moment())))
            self.progressBar.totalTime.configure(text=timedelta(seconds = round(player.return_length())))

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
            self.on_adding_to_queue(song)
        else:
            player.play_song(song)

    def open_text_dialog(self, opt):
        if opt == 1:
            self.help_dialog = self.create_or_focus_dialog(self.help_dialog, HelpWindow)
        elif opt == 2:
            self.about_dialog = self.create_or_focus_dialog(self.about_dialog, AboutWindow)
        else:
            self.queue_dialog = self.create_or_focus_dialog(self.queue_dialog, QueueWindow)

    def create_or_focus_dialog(self, dialog, DialogClass):
        if dialog is None or not dialog.winfo_exists():
            dialog = DialogClass(self)
        else:
            dialog.focus()
        return dialog
    
    def on_closing(self):
        msg = CTkMessagebox(master=app, title="Exit?", message="Are you sure you want to quit?",
                            icon="question", option_2="Cancel", option_1="Quit", justify="center")
        response = msg.get()
        
        if response=="Quit":
            app.destroy()
            save_to_yaml(player.volume)
            songToSave = player.return_song()
            save_to_yaml2(queue, songToSave)

    def on_adding_to_queue(self, song):
        msg = CTkMessagebox(master=app, title="Song added to queue", message=f"{song}\n added to queue!",
                            icon="info", option_1="Ok", justify="center")

class QueueWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("1000x400")
        self.title('Queue')
        self.grid_columnconfigure((0, 2), weight=1)

        self.queue = createTree(self)
        self.queue.grid(row=1, column=0, padx=20, pady=20, sticky='NS', columnspan=3)
        self.goBackButton = customtkinter.CTkButton(self, text='Go Back', command=self.destroy, font=('Roboto', 19), hover=True)
        self.goBackButton.grid(row=2, column=0, sticky='S')
        self.clearQueueButton = customtkinter.CTkButton(self, text='Clear Queue', command= lambda:[queue.clear_list(), self.populate_queue()], font=('Roboto', 19), hover=True, fg_color='#c0392b', hover_color='#922b21')
        self.clearQueueButton.grid(row=2, column=1, sticky='S')
        self.shuffleQueueButton = customtkinter.CTkButton(self, text='Shuffle Queue', command= lambda:[queue.shuffle(), self.populate_queue()], font=('Roboto', 19), hover=True, fg_color='#2980b9', hover_color='#1a5276')
        self.shuffleQueueButton.grid(row=2, column=2, sticky='S')
        self.populate_queue()

    """same as populate_table but for queue (could be merged into one method in the future)"""
    def populate_queue(self):
        self.queue.delete(*self.queue.get_children()) # clears the old table
        for nr, song in enumerate(queue.songList, start=1):
            self.queue.insert('', customtkinter.END, values=(str(nr)+'.', song.return_title(), song.return_artist(), song.return_album(), str(song.convert_time()))) # inserts songs into the tree view.
        
if __name__ == '__main__':
    prepare_all_songs()
    oldVolume = load_from_yaml() #init saved volume from .yml file
    init_file(queue, allSongs) #init saved curr song + queue from .yml file
    player.change_volume(oldVolume) #change volume in the player
    app = App()
    app.populate_table(None)
    app.protocol("WM_DELETE_WINDOW", app.on_closing) # custom message box if user wants to quit
    app.mainloop()