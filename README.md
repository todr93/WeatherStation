# WeatherStation
WeatherStation is an app which get the weather info from OpenWeather API.
Its main purpose is generating of an image for RaspberryPi with e-Paper screen.

## Requirements
App is compatible with Python 3.7 to Python 3.12. \
All required modules are in requirements.txt file.

## Usage
It can be used in two modes:
- screen mode with RaspberryPi and e-Paper screen, 
- test mode (save image on the local disk and show it).

### Windows
1. Clone repository by "git clone https://github.com/todr93/WeatherStation".
1. Use "createEnvironment.bat" to create virtual environment and install all required modules.
1. Use "runTestMode.bat" to run application in test mode.

### Linux
1. Clone repository by "git clone https://github.com/todr93/WeatherStation".
1. Make scripts executables:  
    - "chmod +x createEnvironment.sh",
    - "chmod +x runTestMode.sh".
1. Use "createEnvironment.sh" to create virtual environment and install all required modules.
1. Use "runTestMode.sh" to run application in test mode.