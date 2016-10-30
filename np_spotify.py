__module_name__ = "Now Playing Spotify"
__module_version__ = "0.1"
__module_description__ = "Displays currently playing song on Spotify"
__author__ = "Anirban Mukhopadhyay"

import xchat as XC
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
            windll.kernel32.QueryFullProcessImageNameW(process_handle, 0, pointer(exe_name), pointer(buffer_size))

            if spotify_exe_name in exe_name.value:
                window_title = create_unicode_buffer(MAX_PATH)
                windll.user32.GetWindowTextW(window, pointer(window_title), MAX_PATH)
                if window_title.value and len(window_title.value) > 3 and '-' in window_title.value:
                    return window_title.value
        finally:
            windll.kernel32.CloseHandle(process_handle)

    # Probably paused or not running then
    return None

def spotify_now_playing_cb(word, word_eol, userdata):
    now_playing = spotify_now_playing('Spotify.exe')
    XC.command((u'me 9np: %s' % ((now_playing + u' (Spotify) ') if now_playing else u'Spotify is not active or paused',)).encode('utf-8'))

XC.hook_command("spotify", spotify_now_playing_cb, help="/spotify Announces currently playing song on Spotify")
XC.prnt(__module_name__ + ' version ' + __module_version__ + ' loaded.')