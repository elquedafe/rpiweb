# rpiweb

## how to clone
git clone https://github.com/ddeuterio/rpiweb.git

## directory organization
### Configuration files
config.ini --> used to dinamically instantiate different kinds of temp/hum reading sensors.
control.ini --> contains parameters needed to run the robot in tempController.py

### Statistics
dataHandler.py

### File Reader Management
fileHandler.py

### Writing data to create statistics
lecturaAuto.py --> writes in file 'lecturas.txt'

### Web related
webSensor.py --> Flask web program

static/ --> contains all the styles

templates/ --> contains all .html files and images

### apliConsola
Contains the modules related with the access to am2320 to read data from the sensor.

