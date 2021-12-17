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
replace the complete directory paths of the respective game models. For example, replace "../fc5/" with "/home/yourdirectory/models/fc5/"
3. Create `anytitle.csv` file and place its path as value of key `"data_directories"`, in _params.json_.

Then, fill `anytitle.csv` that is created with the directory paths of data collected for each game. This file has three columns _directory,platform,game_. The entries in this file should look like as follows:

directory  | platform  | game
------------- | ------------- | ------------- | 
./data/stadia/fc5_gameplay_1/  | stadia  | fc5  | 
./data/stadia/acv_gameplay_1/  | stadia  | acv  | 
./data/luna/crew_gameplay_1/  | luna  | crew  | 


