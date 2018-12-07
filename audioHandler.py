import subprocess

def playRob():
	path = "audio/rob.mp3"
	return_code = subprocess.call(["mpg123", path])