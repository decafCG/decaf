# DECAF: Dissecting Cloud Gaming Performance

## DISCLAIMER

DECAF project is under review at an ACM conference. We only permit the use of DECAF to the ACM conference review committee. Other than that, as long as this disclaimer is present, any other use of DECAF is strictly prohibited.  

## Setup
The tool upload is in progress...

DECAF is compatible with Windows 10 Operating System

### Chromium Setup
Download instrumented chromium from [here](https://drive.google.com/drive/folders/1kpajCHs6q7MhnPUkV23V8aOO2_cyaoPB?usp=sharing).

In the C directory of your computer, create two folders:
1) C:/chromium_dataset/
2) C:/chromium/src/out/


Inside the ‘out’ folder, extract the downloaded chromium. The extracted files will be in folder titled ‘Default’.

To run chromium,  open the terminal Windows PowerShell in administrator mode and change directory to C:/chromium/src/. Then run following command:

./out/Default/chrome.exe --no-sandbox

This will launch chromium. Browse gaming platform such as Google Stadia and play the game.

I think you should use an
`<addr>` element here instead.





