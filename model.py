import os
import eyed3
from datetime import timedelta
import yaml
import random

class Song:
    def __init__(self, title, artist, length, path, album):
        self.title = title
        self.artist = artist
        self.length = round(length)
        self.path = path
        self.album = album

    def __str__(self):
        return f'{self.title:<50} {self.artist:<50} {self.convert_time()}'
    
    def __repr__(self):
        return f'Song({self.title}, {self.artist}, {self.length}, {self.path}, {self.album})'
    
    def convert_time(self):
        return timedelta(seconds=self.length)
    
    def return_title(self):
        return f'{self.title:<25}'
    
    def return_artist(self):
        return f'{self.artist:<25}'
    
    def return_album(self):
        return f'{self.album:<25}'
    
    """used when initing saved queue"""
    def is_equal(self, other):
        return self.title == other.title and self.artist == other.artist and self.length == other.length and self.album == other.album

class Songlist:
    def __init__(self, name):
        self.name = name
        self.songList = []
    
    def add_song(self, song):
        self.songList.append(song)

    def __str__(self):
        result = f'{self.name}\n'
        for i, song in enumerate(self.songList, start=0):
            result += f'{i:<3} {song}\n'
        return result
    
    def clear_list(self):
        self.songList.clear()

    def remove_top_song(self):
        self.songList.pop(0)
     
    def check_if_empty(self):
        if len(self.songList):
            return False
        return True
    
    def shuffle(self):
        random.shuffle(self.songList)

    """atm used only when initing saved queue"""
    def add_song_to_start(self, song):
        self.songList.insert(0, song)

"""scans folder for mp3 files and adds them to songlist"""
def scan_folder(path, songList):
    for file in os.listdir(path):
        if file.endswith('.mp3'):
            filePath = os.path.join(path, file)
            audio = eyed3.load(filePath)
            eyed3.log.setLevel("ERROR")
            if not audio or not audio.tag:
                continue
            artist = audio.tag.artist if audio.tag.artist else 'unknown'
            title = audio.tag.title if audio.tag.title else file
            album = audio.tag.album if audio.tag.album else ' '
            length = audio.info.time_secs
            song = Song(title, artist, length, filePath, album)
            songList.add_song(song)

"""saves volume"""
def save_to_yaml(volume):
    with open('session.yml', 'w', encoding='utf-8') as yaml_file:
        yaml.dump(volume, yaml_file, default_flow_style=False, allow_unicode=True)

"""loads saved volume"""
def load_from_yaml():
    if os.path.isfile('session.yml') and os.stat('session.yml').st_size != 0:   
        with open('session.yml', 'r', encoding='utf-8') as yaml_file:
            volume = yaml.safe_load(yaml_file)
            return volume
    return 0.5

"""saves curr song + queue"""
def save_to_yaml2(queue, currSong):
    with open('songs.yml', 'w', encoding='utf-8') as yaml_file:
        if currSong != None:
            queue.add_song_to_start(currSong)
        yaml.dump([vars(song) for song in queue.songList], yaml_file, default_flow_style=False, allow_unicode=True)

"""loads saved queue"""
def init_file(queue, allsongs):
    if os.path.isfile('songs.yml') and os.stat('songs.yml').st_size != 0:
        with open('songs.yml', 'r', encoding='utf-8') as yaml_file:
            loaded_data = yaml.safe_load(yaml_file)
            for song_data in loaded_data:
                song = Song(**song_data)
                if any(song.is_equal(song) for song in allsongs.songList):
                    queue.add_song(song)
