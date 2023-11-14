from model import *
from player import *
from pathlib import Path
from typing import Iterable
from rich.text import Text

from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable, Input, Label, DirectoryTree, Button, ProgressBar
from textual.screen import Screen, ModalScreen
from textual.containers import Container, Horizontal
from textual.binding import Binding
from textual.widget import Widget
from textual_slider import Slider

ABOUT_TEXT = """     
MyPyPlayer is a simple music player written in Python with the use of:
- pygame for playing music
- eyed3 for getting metadata from tracks
- textual for better UI
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

musicDirPath = r'.\mymusic'
allSongs = Songlist("All Songs")
queue = Songlist("Queue")

def prepare_all_songs():
    allSongs.clear_list()
    scan_folder(musicDirPath, allSongs)

player = Player()
player.change_volume(0.15)

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

class Controller(Widget):

    DEFAULT_CSS = """
    Controller {
        content-align: center middle;
        layout: vertical;
        height: 5;
        margin: 1;
        min-width: 50;
        padding: 1;
        dock: bottom;
    }
    """

    def compose(self) -> ComposeResult:
            with Horizontal():
                yield Button("||◁", id="toStart")
                yield Button("<-5s", id="minusFive")
                yield Button("❚❚", id="pauseResume")
                yield Button("+5s>", id="plusFive")
                yield Button("▷||", id="toEnd")
                yield Slider(min=0, max=10, step=1, id="volumeSlider")

    @on(Button.Pressed, "#pauseResume")
    def pause_resume(self) -> None:
        player.pause_resume_song()

    @on(Button.Pressed, "#toStart")
    def to_start(self) -> None:
        player.rewind_to_start()

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
            self.label.update(str(player)"xd")
            player.check_if_playing()

class SongTable(DataTable):
    
    DEFAULT_CSS = "DataTable {height: 1fr}"

    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.clear()
        table.add_columns("Title", "Artist", Text("Track Length", justify='right'))
        for number, song in enumerate(allSongs.songList, start=1):
            label = Text(str(number))
            table.add_row(song.return_title(), song.return_artist(), Text(str(song.convert_time()), justify="right"), label=label, key=song)
        table.fixed_columns = 1
        table.cursor_type = "row"
        table.zebra_stripes = True

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handler for selecting a row in the data table."""
        if player.isPlaying:
            queue.add_song(event.row_key.value)
            self.notify("Added to queue: "+event.row_key.value.title)
        else:
            player.play_song(event.row_key.value)
            self.notify("Started playing: "+event.row_key.value.title)

class PathScreen(ModalScreen):

    DEFAULT_CSS = """
    PathScreen {
        align: center middle;
    }

    PathScreen > Container {
        width: auto;
        height: auto;
    }
    """
    label = Label()

    def compose(self) -> ComposeResult:
        with Container():
            yield Label("Select your music folder, then press P to save it and close the window!")
            yield DirectoryTree('./')
            yield self.label

    def on_directory_tree_directory_selected( self, event: DirectoryTree.FileSelected) -> None:
        """Display currently selected directory path"""
        self.label.update(str(event.path))


    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        """Filter paths to non-hidden directories only."""
        return [p for p in paths if p.is_dir() and not p.name.startswith(".")]
        
class MyPyPlayer(App):
    """A Textual app to play music."""

    SCREENS = {"about": AboutScreen()}
    BINDINGS = [
        Binding("a", "push_screen('about')", "About The Player"), 
        Binding("space", "play_resume", "Pause/Resume")
        ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        yield SongTable()
        yield SongInfo()
        yield Controller()

    def _on_mount(self) -> None:
        self.monitor_progress = self.set_interval(0.1, self.monitor_track_progress, pause=False)

    """Binding a footer button to an action"""
    def action_play_resume(self) -> None:
        player.pause_resume_song()

    """If song finished playing and there are still songs in the queue it will play that song"""
    def monitor_track_progress(self) -> None:
        if not player.isPlaying and not queue.check_if_empty():
            player.play_song(queue.songList[0])
            queue.remove_top_song()

if __name__ == "__main__":
    prepare_all_songs()
    app = MyPyPlayer()
    app.run()
