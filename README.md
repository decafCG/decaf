# DECAF: Dissecting Cloud Gaming Performance

## DISCLAIMER

DECAF project is under review at an ACM conference. We only permit the use of DECAF to the ACM conference review committee. Other than that, as long as this disclaimer is present, any other use of DECAF is strictly prohibited.  

## Setup
**The tool upload is in progress...**

DECAF is compatible with Windows 10 operating system

First step is to download or git clone decaf from github in your C directory. It should look like C:\decaf

## Dependencies
Please install the following:
1. Python3: Install using MS store or PowerShell
2. Scapy: Run the command in PowerShell `python3 -m pip install scapy`
3. Win32api: Run the command in PowerShell `python3 -m pip install pywin32`
4. Install FFmpeg for windows by following instructions [here](https://www.gyan.dev/ffmpeg/builds/)
5. Install WireShark from [here](https://www.wireshark.org/download.html)

Make sure that the WireShark is installed in direcotory _C:\Program Files\Wireshark\_. Otherwise, find the directory where WireShark is installed and update it in the _launcher\paths.json_ by replacing the value of key "tshark".

### Creating required directories
Go the _C:\decaf\_ directory and run the script create_directories.py. This will create all the required directories.

### Chromium Setup
Download instrumented chromium from [here](https://drive.google.com/drive/folders/1kpajCHs6q7MhnPUkV23V8aOO2_cyaoPB?usp=sharing).

Inside the _C:\chromium\src\out\_ that is already created, extract the downloaded chromium. The extracted files will be in folder titled _Default_.

To run chromium,  open the Windows PowerShell in administrator mode and change directory to _C:\chromium\src\_. Then run the command `.\out\Default\chrome.exe --no-sandbox`. This will launch chromium. Browse gaming platform such as Google Stadia and play the game.

### Launcher Setup
Laucher runs various components of Decaf such as game bot, FFmpeg, wireshark to collect the data.







