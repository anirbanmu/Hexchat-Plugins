# Hexchat-Plugins
Hexchat plugins tested with Python 2.7.10 & HexChat 2.12.1

### PySysInfo (system_info.py)
+ Command: `/systeminfo`
+ Dependencies: `pip install psutil`
+ `wmic` is used instead of the WMI python libraries on pypi because HexChat seems to have some issue when they are issues & it causes HexChat to hang.