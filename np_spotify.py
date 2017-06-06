__module_name__ = "Now Playing Spotify"
__module_version__ = "0.1"
__module_description__ = "Displays currently playing song on Spotify"
__author__ = "Anirban Mukhopadhyay"

import xchat as XC
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from ctypes import *
from ctypes.wintypes import *

def spotify_now_playing(spotify_exe_name):
    ENUM_WINDOWS_CB = WINFUNCTYPE(BOOL, HWND, LPARAM)

    window_processes = {}

    def enum_windows_cb(hwnd, lparam):
        pid = DWORD()
        windll.user32.GetWindowThreadProcessId(hwnd, pointer(pid))
        window_processes[hwnd] = pid
        return True

    windll.user32.EnumWindows(ENUM_WINDOWS_CB(enum_windows_cb), 0)

    for window, process in window_processes.iteritems():
        try:
            process_handle = windll.kernel32.OpenProcess(0x1000, False, process)

            exe_name = create_unicode_buffer(MAX_PATH)
            buffer_size = DWORD(MAX_PATH)
            windll.kernel32.QueryFullProcessImageNameW(HANDLE(process_handle), 0, pointer(exe_name), pointer(buffer_size))

            if spotify_exe_name in exe_name.value:
                window_title = create_unicode_buffer(MAX_PATH)
                windll.user32.GetWindowTextW(window, pointer(window_title), MAX_PATH)
                if window_title.value and len(window_title.value) > 3 and '-' in window_title.value:
                    return window_title.value
        finally:
            windll.kernel32.CloseHandle(process_handle)

    # Probably paused or not running then
    return None

def get_spotify_info(track):
    if track is None:
        return None

    client_credentials_manager = SpotifyClientCredentials(client_id='5496075e0db74e0ab6d03586b21a2830', client_secret='0036ce7987814eaa8ac61080c3650253')
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    results = sp.search(q=track, limit=1, type='track')

    tracks = results.get('tracks')
    if tracks:
        items = tracks.get('items')
        if items:
            return items[0]

    return None

def spotify_now_playing_cb(word, word_eol, userdata):
    now_playing = spotify_now_playing('Spotify.exe')
    message = u'me 9np: %s' % ((now_playing + u' (Spotify)') if now_playing else u'Spotify is not active or paused',)

    spotify_info = get_spotify_info(now_playing)
    if spotify_info:
        message = message + u' [ ' + spotify_info['external_urls']['spotify'] + u' ]' + ' [ ' + spotify_info['uri'] + ' ]'
    XC.command(message.encode('utf-8'))

XC.hook_command("spotify", spotify_now_playing_cb, help="/spotify Announces currently playing song on Spotify")
XC.prnt(__module_name__ + ' version ' + __module_version__ + ' loaded.')