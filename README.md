# DECAF: Dissecting Cloud Gaming Performance

## DISCLAIMER

**The tool upload is in progress...**
Removal of disclaimer implies complete upload of tool.

## Setup

DECAF is compatible with Windows 10 operating system

First step is to download or git clone decaf from github in your C directory. It should look like C:\decaf

### Dependencies
  Please install the following:
  1. Python3: Install using MS store or PowerShell
  2. Scapy: Run the command in PowerShell `python3 -m pip install scapy`
  3. Win32api: Run the command in PowerShell `python3 -m pip install pywin32`
  4. Install FFmpeg for windows by following instructions [here](https://www.gyan.dev/ffmpeg/builds/)
  5. Install WireShark from [here](https://www.wireshark.org/download.html)

  Make sure that the WireShark is installed in direcotory C:\Program Files\Wireshark\. Otherwise, find the directory where WireShark is installed and update it in the launcher\paths.json by replacing the value of key "tshark".

### Creating required directories
  Go the C:\decaf directory and run the script create_directories.py. This will create all the required directories.

### Chromium Setup
  Download instrumented chromium from [here](https://drive.google.com/drive/folders/1kpajCHs6q7MhnPUkV23V8aOO2_cyaoPB?usp=sharing).

  Inside the C:\chromium\src\out\ that is already created, extract the downloaded chromium. The extracted files will be in folder titled _Default_.

  To run chromium, open the Windows PowerShell in administrator mode and change directory to C:\chromium\src\. Then run the command `.\out\Default\chrome.exe --no-sandbox`. This will launch chromium. Browse gaming platform such as Google Stadia and start the game say Far Cry 5.

### Launcher Setup
  Launcher runs various components of Decaf such as game bot, FFmpeg, wireshark to collect the data.
  Once the game is running in chromium, e.g., Far Cry 5 in Stadia, run the launcher.py to run to start the game bot and start collecting data. The usage is as follows:

  _Usage: python3 launcher.py platform game total_runtime_min bot_runtime_min folder_name_

  For example, if command `python3 launcher.py stadia fc5 10 8 testing` is run, it implies that fc5 will be played by game bot on stadia for 8 minutes and the it will launcher.py stop running after 10 minutes. The data collected will be stored in folder named _test_ which will be present at C:\decaf\dataset\stadia\test. The _bot_runtime_min_ can be less than or equal to _total_runtime_min_.

### Limitation
  Currently, DECAF can perform data collection for three game: Far Cry 5, Assassin's Creed Valhalla, and Crew/Crew2. It is tested for three platforms: Google Stadia, Amazon Luna, and Nvidia Geforce Now.
 

  
### Game Settings
  These game setting are required for gamebot.
  #### Far Cry 5
  Set forward movement of the character from _w_ to _mouse middle button_
  #### Assassin's Creed Valhalla
  Set forward movement of the character from _w_ to _mouse middle button_
  #### Crew/Crew2
  Enable on-screen keyboard and place it on top left of the screen
  
  
  
## Frame Prediction
To process the game recording, refer to readme.md in directory _predictor_. 



