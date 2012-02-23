#!/usr/bin/python
configuration_file_path = r'C:\Users\Scott\randomize_m3u.cfg'

import ConfigParser
import datetime
import os
import random
import subprocess
import sqlite3
import sys
import smtplib
import time

config = ConfigParser.ConfigParser()

if config.read(configuration_file_path):
    print 'Reading config file at {0}'.format(configuration_file_path)
    path_to_vlc = config.get('vlc','path')
    itunes_library_path = config.get('itunes','library_path')
    gmail_user = config.get('gmail','user')
    gmail_pwd = config.get('gmail','pwd')
    prowl_address = config.get('prowl','address')
else:
    print 'No config file found at {0}'.format(configuration_file_path)
    
generated_playlist_filename = 'generated_playlist.m3u'


# set defaults in case the arguments don't work or aren't given
source_playlist_path = r'C:\Users\Scott\Music\iTunes\iTunes Media\Music\morning.m3u'
playlist_minutes = 30


if len(sys.argv) > 1:
    print sys.argv
    source_playlist_path = sys.argv[1]
    print 'Source playlist: {0}'.format(source_playlist_path)
    playlist_minutes = int(sys.argv[2])
    print 'Playlist will run for {0} minutes'.format(playlist_minutes)
    print 'Sleeping for five seconds . . .'
    time.sleep(5)

source_directory = os.path.dirname(source_playlist_path)
source_playlist_name = os.path.basename(source_playlist_path)
today = datetime.datetime.now()
today_iso = today.strftime("%Y-%m-%d_%H-%M")
generated_playlist_path = os.path.join(source_directory,generated_playlist_filename)
print 'Playlist of {0} minutes will be generated from {1} at {2}'.format(playlist_minutes, source_playlist_path, generated_playlist_path)




file_reader = open(source_playlist_path, 'r')
line_at_a_time = file_reader.readlines()
file_writer = open(generated_playlist_path, 'w')

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
email_title = 'Selections from playlist {0} for {1}\n'.format(source_playlist_name,today_iso)
email_body = ''
total_minutes = 0
total_songs = 0
i = 0
while total_minutes < (playlist_minutes):
    file_writer.write('#EXTINF:' + song_list[i][1] + ',' + song_list[i][0] + '\n' + song_list[i][2] + '\n')
    total_minutes = total_minutes + (int(song_list[i][1])/60)
    song_email_line = song_list[i][0] + '\n'
    email_body += song_email_line
    i = i + 1
    total_songs = total_songs + 1
print email_body

file_writer.write('')

print 'songList contains {0} songs'.format(total_songs)

file_writer.close()
file_reader.close()

# Careful in formatting the argument strings. From the online docs:
# Windows users have to use the --option-name="value" syntax instead of the --option-name value syntax.
player_args = [path_to_vlc, '--play-and-exit', generated_playlist_path]
print 'player args are {0}'.format(player_args)
p = subprocess.Popen(player_args)