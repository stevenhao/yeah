# GoGame

A GUI to play the ancient board game Go on your computer or across a TCP/IP connection. 

To play, first clone the respository. If you wish to play on a single computer run:
`python go_gui.py`

If you want to play on multiple computers, have one user run:
`python go_server.py [PORT] [SERVER] [BOARD SIZE]`
Then have both users connect to server by running:
`python go_client.py [PORT] [SERVER]`
