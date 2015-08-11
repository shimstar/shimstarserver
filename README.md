# shimstarserver

This is the server part of my spaceship game.

##installation

Shimstar use the panda engine (http://www.panda3d.org/). Install SDK to be able to launch shimstar server.
Panda3d comes with their own python in installation (python 2.7 32bits).
Shimstar is using Mysql Database (5.6). Install MysqlDb python package (python 2.7 32 bits).

## Configuration

Architecture of shimstar server based on same source is the following:

- A main server
    - take connection to the game
    - gives ip for the right zone
    - manage station topics
      - Buy/sell items
      - install items
      - ...
    - manage death
    - ...
- X zone servers
    - Manage zone game (npc, players move, player's fire, physics,...)
    
### Main server

Configuration for main server is about database configuration
  - Modify dbconnector.py (host, user, password, database)
  
### Zone Server

Configuration for zone server is about network configuration
  - modify configzone.py :
    - C_ID_ZONE : contains the id the zone server will load and run
    - C_IP_ZONE : contains the ip of the computer running the zoneserver
    - C_IP_MAINSERVER : contains the ip of the computer running main server
