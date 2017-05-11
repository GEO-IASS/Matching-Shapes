## Project Description

_Shape Battle_ is a fun multiplayer competitive game where two players play against each other and use the cubes to create interesting shapes displayed on Cozmo's face! The first person to match all the shapes wins the game. The game, apart from being pure fun, can also help kids improve their hand-eye coordination. The players can also see the score displayed on a web page with cool background music.

## Video

[https://www.youtube.com/watch?v=lpUJM2jTR1E](https://www.youtube.com/watch?v=lpUJM2jTR1E)

## Implementation Details
This demo is primarily utilizing cube's pose values to match the shape that the user creates to that displayed on Cozmo's OLED face. We have also used the ``display_oled_face_image`` to display shapes on Cozmo's oled face. The multiplayer version of the game also includes a server run on Node.js and a simple HTTP web server. 

## Instructions

There are a few dependencies on other Python libraries for the primary project: 
PIL was used to display images on Cozmo's face
Wizards of Coz Common folder found [here](https://github.com/Wizards-of-Coz/Common)

The game can be played by just one person by running the python script, but if you want to run the game in a multiplayer environment, then you would have to start a server, web server, and 2 Cozmos. To start the server follow these steps:

1. install node on your machine by visiting ``https://nodejs.org/en/`` or use ``brew install npm``
2. Open the terminal, and go to the server folder in the project. Start the server by typing ``npm start``. This should start the server on the local machine on port 5000.
3. Note down the ip for this machine by typing ``ipconfig`` on windows and ``ifconfig`` on a linux/OSX.

Once the server is on and you know the IP and port of the server, you will have to change a couple of variables in the python file as well as the web server. Update the ``SERVER_IP`` variable in the ShapeBuilder.py file to this ip and port. Open the main.js file in the Web folder and update the ip field to the server ip.

To start the local web server, go to the ``Web`` folder in the terminal, and start a local HTTP Server on port 8000. Once the web server is on, open ``localhost:8000`` in the local browser.

Run the ShapeBuilder.py script on 2 Cozmos at this point. The first Cozmo to connect will be Player 1. The game starts once Cozmo sees all three cube in front of him. The cube will flash green once it is found by Cozmo and his face will now have a shape that the player needs to create. 

## Thoughts for the Future
The current version of the game can only be played locally in the same room. This could be expanded to be an online game where two people can just connect and compete against each other. Also, currently the game does not have angled cube shapes. That could be a fun addition to the game. 
