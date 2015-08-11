# shimstarserver

This is the server part of my spaceship game.

##installation

Shimstar use the panda engine (http://www.panda3d.org/). Install SDK to be able to launch shimstar server.
Panda3d comes with their own python in installation (python 2.7 32bits).
Shimstar is using Mysql Database (5.6). Install MysqlDb python package (python 2.7 32 bits).
An real SQL database, is stored into sql directory (shimstar.sql). You can use it for your test.

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


## Code Construction

main.py will instantiate a TCP network object, which will listen tcp communication and process each task required.

mainzone.py will instantiate a TCP network object, and a zone object processing physics, and event in the zone.
mainzone is a multithread process (one for network, one for physics).

### directory tree

config\behaviour will contains for each zone, the different npc behaviour you need when you instantiate a new npc. It is xml description of the behaviour.
config\npc is handled by code, it is where it will instantiate behaviour (idnpc.xml) for each npc.

models : contains all models necessary for run physics on server
shimstar : root package for code source
shimstar\bdd : database stuff + checkconsistency allowing to clean all orphans object
shimstar\core : constantes + manage server state
shimstar\items : all items in shimstar are described as child of the class item (ships, weapons, ...)
shimstar\network\ : stuff for main server running network (messaging + dispatch)
network : defining classes use by network class
npc : classes managing npc, attitude and behaviour...
user: user classses (character)
world/zone : zone is managing event into zone + player & npc's movement & physics. Station and asteroid here too
zoneserver : stuff to run zone networking
sql : stored the actual database structure and datas
