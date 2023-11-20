import contextlib 
with contextlib.redirect_stdout(None):
    from pygame import mixer
from datetime import timedelta
import os

class Player:
    def __init__(self):
        mixer.init()
        self.songFile = None
        self.isPaused = False
        self.isPlaying = False
        self.songName = None
        self.songArtist = None
        self.songAlbum = None
        self.songLength = 0
        self.volume = 0.5
        self.elapsed_time = 0 #used when seeking through the song
        mixer.music.set_volume(self.volume)

    def play_song(self, song):
        if os.path.isfile(song.path):
            self.songFile = song
            self.songName = song.title
            self.songLength = song.length
            self.songArtist = song.artist
            self.songAlbum = song.album
            self.isPlaying = True
            self.elapsed_time = 0
            mixer.music.load(song.path)
            mixer.music.play(0, 0)

    def __str__(self):
        if self.isPlaying == False and self.isPaused == False:
            return f"No song is currently playing!"
        else:
            return f"{self.songName} by: {self.songArtist} {timedelta(seconds = round(self.elapsed_time+(mixer.music.get_pos()/1000)))}/{timedelta(seconds=self.songLength)}"
        
    def return_length(self):
        if not self.isPlaying:
            return 0
        else:
            return self.songLength
        
    def return_song(self):
        return self.songFile
    
    def return_moment(self):
        if not self.isPlaying:
            return 0
        else:
            return self.elapsed_time+float(mixer.music.get_pos()/1000)

    def pause_resume_song(self):
        if not self.isPaused:
            self.isPaused = True 
            mixer.music.pause() 
        elif self.isPaused:
            self.isPaused = False
            mixer.music.unpause()
            
    """pygame automatically takes care of setting upper volume limit tho"""
    def change_volume(self, volume):
        if(volume > 1.0):
            volume = 1.0
        if(volume < 0):
            volume = 0
        self.volume = volume
        mixer.music.set_volume(volume)

    def destroy_player(self):
        mixer.music.stop()

    def check_if_playing(self):
        if mixer.music.get_busy() and not self.isPaused:
            self.isPlaying = True
        elif not mixer.music.get_busy() and not self.isPaused:
            self.songFile = None
            self.isPlaying = False
            self.songName = None
            self.songLength = 0
            self.elapsed_time = 0
            mixer.music.unload()

    def skip_to(self, number):
        if self.isPlaying:
            currentSongMoment = self.return_moment()
            self.elapsed_time = self.elapsed_time + number
            if currentSongMoment + self.elapsed_time < 0:
                self.rewind_to_start()
            else:
                currentSongMoment = currentSongMoment+number
                mixer.music.rewind()
                mixer.music.set_pos(currentSongMoment)

    """get_pos won't update if you rewind the music, since it shows time elapsed since play has started. this should work for now"""
    def rewind_to_start(self):
        if self.isPlaying:
            self.elapsed_time = 0
            mixer.music.rewind()
            mixer.music.play(0, 0)
            
    def skip_to_end(self):
        if self.isPlaying:
            mixer.music.rewind()
            mixer.music.play(0, self.songLength)