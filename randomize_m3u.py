#!/usr/bin/python
"""
Given an m3u playlist as exported from iTunes, create a new randomized list of a specified duration and play it in VLC Media Player
"""

import ConfigParser
import datetime
import gmailer
import os
import random
import subprocess
import sqlite3
import sys
import datetime

CONFIGURATION_FILE = 'randomize_m3u.cfg'
DATABASE_FILE = 'randomize_m3u.db'
GENERATED_PLAYLIST_FILENAME = 'randomize_m3u_generated_playlist.m3u'

config = ConfigParser.ConfigParser()

if config.read(CONFIGURATION_FILE):
    print 'Reading config file at {0}'.format(CONFIGURATION_FILE)
    PATH_TO_VLC = config.get('vlc','path')
    ORIGINAL_ITUNES_MUSIC_DIRECTORY = config.get('itunes','original_itunes_music_directory')
    GMAIL_USER = config.get('gmail','user')
    GMAIL_PASSWORD = config.get('gmail','pwd')
    PROWL_ADDRESS = config.get('prowl','address')
else:
    print 'No config file found at {0}'.format(CONFIGURATION_FILE)


if len(sys.argv) > 1:
    print sys.argv
    SOURCE_PLAYLIST_PATH = sys.argv[1]
    PLAYLIST_MINUTES = int(sys.argv[2])

class PlayistRandomizer():
    """Class to generate a random playlist"""
    
    def __init__(self, full_path_to_source_playist, number_of_minutes_in_new_playlist, generated_playlist_name, original_itunes_music_directory):
        """ Create an instance of the PlaylistRandomizer class """
        self.source_playlist_path = full_path_to_source_playist
        self.source_playlist_name = os.path.basename(full_path_to_source_playist)
        self.music_directory = os.path.dirname(full_path_to_source_playist)
        self.original_itunes_music_directory = original_itunes_music_directory
        self.number_of_minutes_in_new_playlist = number_of_minutes_in_new_playlist
        self.generated_playlist_name = generated_playlist_name
        self.generated_playlist_path = os.path.join(self.music_directory,generated_playlist_name)
        now = datetime.datetime.now()
        self.now_iso = now.strftime("%Y-%m-%d_%H-%M")
        self.file_reader = open(full_path_to_source_playist, 'r')
        self.line_at_a_time = self.file_reader.readlines()
        self.file_writer = open(self.generated_playlist_path, 'w')        

    def generate_playlist(self, source_playlist_path, GENERATED_PLAYLIST_FILENAME, playlist_minutes, DATABASE_FILE, GMAIL_USER, PROWL_ADDRESS, GMAIL_PASSWORD, PATH_TO_VLC):
        """ """
        source_playlist_name = os.path.basename(source_playlist_path)
        today = datetime.datetime.now()
        print 'Playlist of {0} minutes will be generated from {1} at {2}'.format(playlist_minutes, source_playlist_path, generated_playlist_path)
    
        
    
        song_list = []
        for m3u_line in line_at_a_time:
            if m3u_line[0:7] == '#EXTM3U':
                print 'Found the first line'
            elif m3u_line[0:8] == '#EXTINF:':
                just_data = m3u_line.replace('#EXTINF:','')
                split_m3u_line = just_data.split(',', 1) # limit the splits to one in case the title string contains a comma
                track_seconds = split_m3u_line[0].replace('\n','')
                track_title = split_m3u_line[1].replace('\n','')
            else:
                track_path_with_line_ending = m3u_line
                track_path = track_path_with_line_ending.replace('\n','')
                song_list.append([track_title, track_seconds, track_path])
                track_seconds = ''
                track_title = ''
                track_path = ''
    
        random.shuffle(song_list)
    
        file_writer.write('#EXTM3U\n')
        email_title = 'Selections from playlist {0} for {1}\n'.format(source_playlist_name,now_iso)
        email_body = ''
        total_minutes = 0
        total_songs = 0
        i = 0
    
        connection = None
        connection = sqlite3.connect(DATABASE_FILE)
        cur = connection.cursor()  
        cur.execute('CREATE TABLE IF NOT EXISTS plays (id INTEGER PRIMARY KEY, title TEXT, path TEXT, playlist TEXT, date TEXT)')
    
        while total_minutes < (playlist_minutes):
            file_writer.write('#EXTINF:' + song_list[i][1] + ',' + song_list[i][0] + '\n' + song_list[i][2] + '\n')
            title = song_list[i][0].replace("'","")
            path = song_list[i][2].replace("'","")
            sql = "INSERT INTO plays (title, path, playlist, date) VALUES ('{0}', '{1}', '{2}', '{3}');".format(title,path,source_playlist_name, now_iso)
            print sql
            cur.execute(sql)
            total_minutes = total_minutes + (int(song_list[i][1])/60)
            song_email_line = song_list[i][0] + '\n'
            email_body += song_email_line
            i = i + 1
            total_songs = total_songs + 1
        print email_body
    
        file_writer.write('')
    
        print 'songList contains {0} songs'.format(total_songs)
    
        gmailer.mail(PROWL_ADDRESS, email_title, email_body, GMAIL_USER, GMAIL_PASSWORD)
    
        connection.commit()
        file_writer.close()
        file_reader.close()
        connection.close()
    
        # Careful in formatting the argument strings. From the online docs:
        # Windows users have to use the --option-name="value" syntax instead of the --option-name value syntax.
        player_args = [PATH_TO_VLC, '--play-and-exit', generated_playlist_path]
        print 'player args are {0}'.format(player_args)
        p = subprocess.Popen(player_args)

if __name__ == "__main__":
    randomizer = PlayistRandomizer(SOURCE_PLAYLIST_PATH, PLAYLIST_MINUTES, GENERATED_PLAYLIST_FILENAME, ORIGINAL_ITUNES_MUSIC_DIRECTORY)
    print randomizer
    print randomizer.source_playlist_path
    print randomizer.source_playlist_name
    print randomizer.music_directory