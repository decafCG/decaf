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
