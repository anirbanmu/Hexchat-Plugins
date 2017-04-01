# Hexchat-Plugins
Hexchat plugins tested with Python 2.7.10 & HexChat 2.12.1.

### PySysInfo (system_info.py)
+ Command: `/systeminfo`
+ Dependencies:
  + Windows.
  + Python libraries: `pip install psutil`
  + External: [OpenHardwareMonitor](http://openhardwaremonitor.org/) is used to get temperature & clock frequency data (via its WMI interface). Please make sure [OpenHardwareMonitor](http://openhardwaremonitor.org/) is running before invoking the plugin. I recommend setting [OpenHardwareMonitor](http://openhardwaremonitor.org/) to automatically start up with Windows.
+ `wmic` is used instead of the WMI python libraries on pypi because HexChat seems to have some issue when they are used & it causes HexChat to hang.

### Now playing for Spotify
+ Command: `/spotify`
+ Dependencies:
  + Windows
  + Python libraries: ctypes
