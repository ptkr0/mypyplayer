import os
import eyed3
from datetime import timedelta

class Song:
    def __init__(self, title, artist, length, path, album):
        self.title = title
        self.artist = artist
        self.length = round(length)
        self.path = path
        self.album = album

    def __str__(self):
        return f"{self.title:<50} {self.artist:<50} {self.convert_time()}"
    
    def __repr__(self):
        return str(self)
    
    def convert_time(self):
        return timedelta(seconds=self.length)
    
    def return_title(self):
        return f"{self.title:<25}"
    
    def return_artist(self):
        return f"{self.artist:<25}"
    
    def return_album(self):
        return f"{self.album:<25}"

class Songlist:
    def __init__(self, name):
        self.name = name
        self.songList = []
    
    def add_song(self, song):
        self.songList.append(song)

    def __str__(self):
        result = f'{self.name}\n'
        for i, song in enumerate(self.songList, start=0):
            result += f"{i:<3} {song}\n"
        return result
    
    def clear_list(self):
        self.songList.clear()

    def remove_top_song(self):
        self.songList.pop(0)
     
    def check_if_empty(self):
        if len(self.songList):
            return False
        return True

class Playlist(Songlist):
    def RemoveSong(self, song):
        if(song in self.songList):
            self.songList.remove(song)
        else:
            return -1
        
def scan_folder(path, songList):
    for file in os.listdir(path):
        if file.endswith(".mp3"):
            filePath = os.path.join(path, file)
            eyed3.log.setLevel("ERROR")
            audio = eyed3.load(filePath)
            if(audio.tag.artist == None):
                artist = "unknown"
            else:
                artist = audio.tag.artist
            if(audio.tag.title == None):
                title = file
            else:
                title = audio.tag.title
            if(audio.tag.album == None):
                album = " "
            else:
                album = audio.tag.album
            length = audio.info.time_secs
            song = Song(title, artist, length, filePath, album)
            songList.add_song(song)


