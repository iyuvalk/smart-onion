#User interface - Basic Concept

<br />
<br />

###The problem
Since that the UI of most security systems today (SIEMs for example) is based on a ticketing system of some sort,
many security analysts are susceptible to analyst's fatigue, in this system I believe that a different concept should
be adopted.

<br>

###The new approach
The basic idea behind the UI of this system is to make it much more game-like and fun to use. It is my believe that
such a game-like user interface will help reduce the analyst's fatigue, help the HTM modules in the system classify
the data that is being sent to them - thereby improving its ability to make better predictions and detect valuable and 
relevant anomalies and reduce the false-positives to the minimum. 

The first screen the user will enter (after login) should include (at the bottom, top, left or right) a closed tab
with the current tickets created by the system and another closed tab (at the bottom, top, left or right) with the 
various health metrics of the system. In the main area of the screen an empty data-center will be displayed and to
its left a box with objects (networks, IPs, servers, workstations, devices, software, etc.) and the user will receive
points on objects that he/she classifies (i.e. moves to the correct physical and geographic location, assigns to the 
relevant organizational unit). The data entered will be sent to the HTM model of the configurator for improving its 
ability to predict the correct label for new objects that are seen by the system, each such object that system predicted
its labels will be displayed in the data-center at the location and the labeling as predicted by the system but will be 
marked with a different colour and will wait for the user's approval. Once the user approves the system prediction the 
user will also get points for approving (correcting) the prediction made by the system and the predicted data will be 
sent to the system again to re-enforce or correct its predictions for the next time. In case that multiple analysts will 
attempt to classify the same object differently the UI will conduct a "duel" in which each analyst will have to explain 
to the other analysts why he/she classified that object they way he/she did and when the other analysts will agree with 
one of the analysts he/she will receive the points for that classification and the object will be classified. In any case
of high severity tickets generated by the system and/or health issues in the system, the game will be paused and the 
relevant tab will open for all analysts, automatically minimizing the game tab.