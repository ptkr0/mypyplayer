from model import *
from player import *

path = r'C:\Users\Piotr\Desktop\mypyplayer'

allPlaylists = []
queue = Playlist("Queue")
allSongs = Songlist("All Songs")
scan_folder(path, allSongs)
print(allSongs)
player = Player()

print("hello world")
player.change_volume(0.15)


while True:
    x = input()
    if x == '1':
        player.pause_resume_song()
    if x == '2':
        player.play_song(allSongs.songList[1])
