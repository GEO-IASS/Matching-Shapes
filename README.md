# Matching-Shapes
Use the cubes to create interesting shapes displayed on Cozmo's face! It is a multi-player competitive game and the first person to match all the shapes wins the game. The game can be played by kids to improve hand-eye coordination.

The package contains node.js server scripts, a front-end web page to display the scores and the python scripts to play the game.

#Steps
* Run the server first and note the ip of the computer you are running the server on.
* In the python scripts update the "SERVER_IP" field to the correct server IP.
* In the main.js file inside Web folder, update the "ip" field to the correct server IP. 
* Run the python scripts on 2 Cozmos, the first one to connect is Player 1. 
* Run a front-end server to keep track of the scores!

# Dependencies
The modules required in addition to the `Cozmo` module are:

* pygame
* Pillow
* Common

Common is a package included in the Git repo: https://github.com/Wizards-of-Coz/Common

The other modules can be installed via pip if not already present:
`pip3 install pygame`
`pip3 install Pillow`