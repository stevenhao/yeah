# GoGame

A GUI to play the ancient board game Go on your computer or across a TCP/IP connection. 

To play, first clone the respository. If you wish to play on a single computer run:
`python go_gui.py`

If you want to play on multiple computers, have one user run:
`python go_server.py [PORT] [SERVER] [BOARD SIZE]`
Then have both users connect to server by running:
`python go_client.py [PORT] [SERVER]`

# Playing with GoBot

If you wish to play against GoBot, a nnet Go AI (read about [here](https://github.com/davidzheng814/GoBot)), you must use the TCP/IP mode. To setup GoBot, read `GoBot/README.txt`. After setup, you can play against GoBot by starting up the server as normal but replacing one of the `go_client.py` programs with `gobot_client.py`. 
