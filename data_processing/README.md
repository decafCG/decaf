# Data Processing

The data processing environment setup is tested for Ubuntu 20.04, thus, it is recommended for conflict free setup of environment.

## Environment Setup

### Dependencies
Running data processing requires following:
1. Machine/VM with Ubuntu 
2. Python3
3. Python packages: numpy, tensorflow, keras, shutil, json, PIL, pytesseract
4. FFmpeg

### Setup

The convinent way to setup environment is to use Anaconda. Install Anaconda from the instruction on the link [here](https://www.digitalocean.com/community/tutorials/how-to-install-the-anaconda-python-distribution-on-ubuntu-20-04).

Once Anaconda is installed, follow the following instructions to install all the packages:

`conda create --name decaf python=3 tensorflow-gpu keras pandas numpy psutil ffmpeg pillow`

Enter `yes` to create an environment `decaf` with the required packages

Run `conda activate decaf`

Run `pip install pytesseract`

At this point the environment is setup to process the data collected using chromium and laucher.


## Process Chromium Logs and Game Recordings

The python3 script `data_processing.py` processes both chromium logs and the game recordings. 

First, lets set paths in _params.json_ as follows:
1. Download the trained model for FarCry5, Assassin's Creed Valhala, Crew, and Crew2 from the [here](https://drive.google.com/drive/folders/1-RP1jfTfvcsI65LvE0vgnH1CxwkP629B?usp=sharing) and place the in some directory.
2. In _params.json_, in 
```json
"models" : {
	"fc5": "../fc5/",
	"crew": "../crew",
	"crew2": "../crew2",
	"acv": "../acv"		
}
```
replace the complete directory paths of the respective game models. For example, replace "../fc5/" with "/home/yourdirectory/models/fc5/".

3. Create `anytitle.csv` file and place its path as value of key `"data_directories"`, in _params.json_.

The purpose of `anytitle.csv` is to provide the directory paths of all the collected data in one place. The script `data_processing.py` will read all the paths from this file and process all of them in one execution. Fill `anytitle.csv` with the directory paths of data collected for each game. This file has three columns _directory,platform,game_. The entries in this file should look like as follows:

directory  | platform  | game
------------- | ------------- | ------------- | 
./data/stadia/fc5_gameplay_1/  | stadia  | fc5  | 
./data/stadia/fc5_gameplay_2/  | stadia  | fc5  | 
./data/stadia/acv_gameplay_1/  | stadia  | acv  | 
./data/luna/crew_gameplay_1/  | luna  | crew  | 


Now, run the `python3 data_processing.py` to processing chromium logs and game recordings in all the directories provided in `anytitle.csv`.

### How `data_processing.py` Works?

This processing script has three key function that process the data. These functions are explained below.

#### Chromium Log Processing
To process the chromium logs, there are two functions `process_videoReceiveStream_log` and `process_rtcStatsCollector_log`.

`process_videoReceiveStream_log` parses the chromium log file (videoReceiveStream.txt) that contains the data from the 'videoReceiveStream' module of the chromium. It generates the two `.json` files: 1) `parsed_videoReceiveStream.json`, which contains the metrics in `.json` format so that analysis can be performed on them, and 2) `vrs_summary_stats.json`, which provide the summary statistics of the metrics in the log file.

`process_rtcStatsCollector_log` parses the chromium log file (rtcStatsCollector.txt) that contains the data on network RTT. It generates three `.json` files: 1) `parsed_rtcStatsCollector.json`, which contains the metrics in `.json` format, 2) `current_rtt.json`, which contains rtt list ('rtts') and timestamp list ('ts') representing the RTT collected over duration of the experiment and summary statistics of RTT, and 3) `packet_loss_stats.json`, which contains the timestamp list ('ts') and packet losses ('packetsLost') representing packets lost over duration of experiment.


#### Game Recording Processing

Function `process_game_recording` processes the game recording. It perform the following operations:
1. Crop the video according to "video_crop_param" of the respective games that are provided in _param.json_.
2. Convert cropped and original video into frames.
3. Run machine learning models on cropped frames and identify the action frames. Then, it generates  `predicted_files.json` that contains file names of all the action frames.
4. The filenames in `predicted_files.json` are then used to fetch the uncropped frame and decode the appended timestamp from it. These timestamps are saved in `frame_timestamps.json`, which can be used along with the `bot_log.csv` to find game delay. The process is described in the [paper](https://dl.acm.org/doi/10.1145/3491043).
