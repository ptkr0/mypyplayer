from model import *
from player import *
from rich.text import Text

from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Label, Button, ProgressBar
from textual.screen import ModalScreen
from textual.containers import Container, Horizontal, Center
from textual.binding import Binding
from textual.widget import Widget
from textual_slider import Slider

ABOUT_TEXT = r"""     
MyPyPlayer is a simple music player written in Python with the use of:
- Pygame for playing music
- eyed3 for getting metadata from tracks
- Textual for better UI
- Textual Slider for that fancy slider ( •̀ ω •́ )✧
- PyYAML for easy save/reload feature
Currently MyPyPlayer is a WIP. Hopefully one day I'll make it usable

                            _         _
                __   ___.--'_`.     .'_`--.___   __
                ( _`.'. -   'o` )   ( 'o`   - .`.'_ )
                _\.'_'      _.-'     `-._      `_`./_
                ( \`. )    //\`         '/\\    ( .'/ )
                \_`-'`---'\\__,       ,__//`---'`-'_/
                \`        `-\         /-'        '/
                `                               '   
                        Powered by MyPHPoL 2023
"""

HELP_TEXT = r"""
Welcome to MyPyPlayer - a simple music player written in Python
Use your mouse or keyboard to navigate through the menus
(mouse is more convenient, but it may cause problems)
If you don't see your music remember to put it in 'mymusic' directory in the program files
After that press 'R' to refresh table
Remember to exit program by clicking 'E' to save your current session
"""

musicDirPath = r'.\mymusic'
allSongs = Songlist("All Songs")
queue = Songlist("Queue")

def prepare_all_songs():
    allSongs.clear_list()
    scan_folder(musicDirPath, allSongs)

player = Player()

class AboutScreen(ModalScreen):

    DEFAULT_CSS = """
    AboutScreen {
        align: center middle;
    }

    AboutScreen > Container {
        width: auto;
        height: auto;
    }

    AboutScreen > Container > Label {
        margin: 1 3;
    }

    AboutScreen > Container > Horizontal {
        width: auto;
        height: auto;
    }

    AboutScreen > Container > Horizontal > Button {
        margin: 2 4;
    }
    """

    def compose(self) -> ComposeResult:
        with Container():
            yield Label(ABOUT_TEXT)
            with Horizontal():
                yield Button("Go Back", id="back", variant="success")

    @on(Button.Pressed, "#back")
    def back_to_app(self) -> None:
        self.app.pop_screen()

class ExitScreen(ModalScreen):

    DEFAULT_CSS = """
    ExitScreen {
        align: center middle;
    }

    ExitScreen > Container {
        width: auto;
        height: auto;
    }

    ExitScreen > Container > Label {
        margin: 1 3;
    }

    ExitScreen > Container > Horizontal {
        width: auto;
        height: auto;
    }

    ExitScreen > Container > Horizontal > Button {
        margin: 2 4;
    }
    """
    
    def compose(self) -> ComposeResult:
         with Container():
            yield Label("Are you sure you want to quit?")
            with Horizontal():
                yield Button("Quit", variant="error", id="quit")
                yield Button("Cancel", variant="primary", id="cancel")

    @on(Button.Pressed, "#cancel")
    def back_to_app(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#quit")
    def save_and_exit(self) -> None:
        save_to_yaml(player.volume)
        songToSave = player.return_song()
        save_to_yaml2(queue, songToSave)
        self.app.exit()

class HelpScreen(ModalScreen):

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
    }

    HelpScreen > Container {
        width: auto;
        height: auto;
    }

    HelpScreen > Container > Label {
        margin: 1 3;
    }

    HelpScreen > Container > Horizontal {
        width: auto;
        height: auto;
    }

    HelpScreen > Container > Horizontal > Button {
        margin: 2 4;
    }
    """

    def compose(self) -> ComposeResult:
        with Container():
            yield Label(HELP_TEXT)
            with Horizontal():
                yield Button("Go Back", id="back", variant="success")

    @on(Button.Pressed, "#back")
    def back_to_app(self) -> None:
        self.app.pop_screen()

class SongProgressBar(ProgressBar):

    def compose(self) -> ComposeResult:
            with Horizontal():
                with Center():
                    yield ProgressBar(show_eta=False, show_percentage=False)

    def _on_mount(self) -> None:
        self.monitor_progress = self.set_interval(0.1, self.monitor_track_progress, pause=False)

    def monitor_track_progress(self) -> None:
        if player.isPlaying:
            self.query_one(ProgressBar).update(total=player.return_length(), progress=player.return_moment())
        else:
            self.query_one(ProgressBar).update(total=None)

class Controller(Widget):

    DEFAULT_CSS = """
    Controller {
        content-align: center middle;
        height: 6;
        margin: 1;
        dock: bottom;
    }

    Controller > Horizontal > Center > Button {
        width: 1;
        border: solid white;
        background:  $surface;
    }

    Controller > Horizontal > Center > Slider {
        width: 20;
        background:  $surface  ;
        border: solid white;
    }
    """

    def compose(self) -> ComposeResult:
        with Center():
                yield SongProgressBar()
        with Horizontal():
            with Center():
                yield Button("||◁", id="toStart")
            with Center():
                yield Button("<-5s", id="minusFive")
            with Center():
                yield Button("❚❚", id="pauseResume")
            with Center():
                yield Button("+5s>", id="plusFive")
            with Center():
                yield Button("▷||", id="toEnd")
            with Center():
                yield Slider(min=0, max=100, step=1, value=int(player.volume*100), id="volumeSlider")

    @on(Button.Pressed, "#pauseResume")
    def pause_resume(self) -> None:
        player.pause_resume_song()

    @on(Button.Pressed, "#toStart")
    def to_start(self) -> None:
        player.rewind_to_start()

    @on(Button.Pressed, "#minusFive")
    def minus_five(self) -> None:
        player.skip_to(-5.0)

    @on(Button.Pressed, "#plusFive")
    def plus_five(self) -> None:
        player.skip_to(5.0)

    @on(Button.Pressed, "#toEnd")
    def to_end(self) -> None:
        player.skip_to_end()

    @on(Slider.Changed, "#volumeSlider")
    def on_slider_changed_slider(self, event: Slider.Changed) -> None:
        value = float(event.value/100)
        player.change_volume(value)

class SongInfo(Label):

    label = Label()
    def compose(self) -> ComposeResult:
        yield self.label

    def _on_mount(self) -> None:
        self.monitor_progress = self.set_interval(0.1, self.monitor_track_progress, pause=False)

    def monitor_track_progress(self):
        if not player.isPlaying:
            self.label.update("No song playing at the moment!")
            player.check_if_playing()
        elif player.isPlaying:
            self.label.update('🎵 ' + str(player))
            player.check_if_playing()

class QueueScreen(ModalScreen):

    DEFAULT_CSS = """

    DataTable {
        height: 1fr;
    }

    QueueScreen {
        content-align: center middle;
    }

    QueueScreen > Container {
        width: auto;
        height: auto;
    }

    QueueScreen > Container > DataTable {
        dock: top;
        width: auto;
        height: auto;
        margin: 2 4;
    }

    QueueScreen > Container > Horizontal > Button {
        margin: 2 4;
    }
    """
    
    def compose(self) -> ComposeResult:
        with Container():
            yield DataTable()
            with Horizontal():
                yield Button("Go back", id="back", variant="success")
                yield Button("Refresh Table", id="refresh", variant="warning")
                yield Button("Clear queue", id="clear", variant="error")

    def _on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.clear()
        table.add_columns("Title", "Artist","Album", Text("Track Length", justify='right'))
        table.fixed_columns = 1
        table.cursor_type = "row"
        table.zebra_stripes = True
        self.fill_table()

    def fill_table(self) -> None:
        table = self.query_one(DataTable)
        table.clear()
        for number, song in enumerate(queue.songList, start=1):
            label = Text(str(number))
            table.add_row(song.return_title(), song.return_artist(), song.return_album(), Text(str(song.convert_time()), justify="right"), label=label)

    @on(Button.Pressed, "#back")
    def go_back(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#clear")
    def clear_table(self) -> None:
        queue.clear_list()
        self.fill_table()

    @on(Button.Pressed, "#refresh")
    def refresh_table(self) -> None:
        self.fill_table()

class SongTable(DataTable):
    
    DEFAULT_CSS = "DataTable {height: 1fr}"
    
    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Title", "Artist","Album", Text("Track Length", justify='right'))
        table.fixed_columns = 1
        table.cursor_type = "row"
        table.zebra_stripes = True

    """thanks to splitting table creation to on_mount and fill_table i can refill table when i want"""
    def fill_table(self) -> None:
        table = self.query_one(DataTable)
        table.clear()
        for number, song in enumerate(allSongs.songList, start=1):
            label = Text(str(number))
            table.add_row(Text(str(song.return_title()), style="#f7eeed"), song.return_artist(), song.return_album(), Text(str(song.convert_time()), style="#f7eeed", justify="right"), label=label, key=song)

    """handler for selecting a row in the data table."""
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if player.isPlaying:
            queue.add_song(event.row_key.value)
            self.notify("Added to queue: "+event.row_key.value.title)
        else:
            player.play_song(event.row_key.value)
            self.notify("Started playing: "+event.row_key.value.title)
        
class MyPyPlayer(App):
    """a Textual app to play music."""

    SCREENS = {"about": AboutScreen(), "help": HelpScreen(), "queue": QueueScreen(), "exit": ExitScreen()}
    BINDINGS = [
        Binding("a", "push_screen('about')", "About The Player"), 
        Binding("h", "push_screen('help')", "Help"), 
        Binding("space", "play_resume", "Pause/Resume"),
        Binding("r", "refresh", "Refresh Music Directory"),
        Binding("q", "push_screen('queue')", "Show Queue"),
        Binding("e", "push_screen('exit')", "Exit Program")
        ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        yield SongTable()
        yield SongInfo()
        yield Controller()

    def _on_mount(self) -> None:
        self.query_one(SongTable).fill_table()
        self.monitor_progress = self.set_interval(0.1, self.monitor_track_progress, pause=False)

    """binding a footer button to an action"""
    def action_play_resume(self) -> None:
        player.pause_resume_song()

    """if song finished playing and there are still songs in the queue it will play that song aka the queue controller"""
    def monitor_track_progress(self) -> None:
        if not player.isPlaying and not queue.check_if_empty():
            player.play_song(queue.songList[0])
            queue.remove_top_song()

    def action_refresh(self) -> None:
        prepare_all_songs()
        self.query_one(SongTable).fill_table()

if __name__ == "__main__":
    prepare_all_songs()
    oldVolume = load_from_yaml()
    init_file(queue, allSongs)
    player.change_volume(oldVolume)
    app = MyPyPlayer()
    app.run()