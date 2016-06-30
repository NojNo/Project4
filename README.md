Tic Tac Toe Version 1.0 created on 30.06.2016

General Usage
This project includes the Backend for a 2 player game which is called Tic Tac Toe. Further information on the game: https://en.wikipedia.org/wiki/Tic-tac-toe

Table of contents

Installing
Quick start 
What´s included? 
Bugs and feature requests 
Creators + Contact 
License and Copyright

Installing 

The program itself does not need to be installed. However, keep in mind the program is written in Python 2.7 on a Windows machine. The whole code was executed within a Google App Engine Launcher and the results are displayed in a browser (in my case Chrome Version 49.0.2623.112). 
Furthermore, you need a Gmail-Account in order to create a project on the Google´s Developer Console page and it might be helpful to open local versions via the Windows Run Box. 
Just execute the following line in the Run Box:
"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --incognito --user-data-dir=%TMP% --unsafely-treat-insecure-origin-as-secure="http://localhost:your-port-number" http://localhost: your-port-number /_ah/api/explorer

Quick Start:

First, set up the right settings on the Google Developers Console in order to have a Project ID.
Keep the following settings on the Credentials page in mind:

Authorized JavaScript origins:

https://poised-space-127410.appspot.com 
http://localhost:8080 
http://localhost:8000
Authorized redirect URIs: 
https://poised-space-127410.appspot.com/oauth2callback
http://localhost:8080/oauth2callback
http://localhost:8000/oauth2callback

Please insert your Project ID in app.yaml.

In order to run the program, your Application needs to be available in the Google App Engine Launcher so that you can click on “Run”.
As this project only includes the backend, you cannot see anything on the Front End. Please access the project via the API Explorer. Further information on how to use the API Explorer: https://cloud.google.com/appengine/docs/python/endpoints/test_deploy
For me the following path in the Run Box was the only way to access the API Explorer: "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --incognito --user-data-dir=%TMP% --unsafely-treat-insecure-origin-as-secure="http://localhost:8080" http://localhost:8080/_ah/api/explorer 
After entering the page, you can explore the APIs. In order to be able to execute the code within the endpoints, you need to type in your Gmail-Address and Password.
So what do you need to run the program? 
You need to set up Python + Google App Engine Launcher + Google Developer Console settings (+ a Gmail-Account) + a browser (best practice here: Chrome).
Optionally you could use the dev_appserver.py DIR for example in Git Bash.

What's included

Within the download you will find the following directories and files:

project4/
├── app.yaml
├── cron.yaml
├── design.txt
├── index.yaml
├── main.py
├── models.py
├── tictactoe.py
└── utils.py

If you run the Project in Google App Engine Launcher, you will auto-access all files.

Which Endpoints are in tictactoe.py?
 - **create_player**
    - You just need to input name and email and then this endpoint returns the player
 - **new_game**
    - checks if the 2 usernames are in the database, if this is the case,
      the players' keys are passed to a new game (via the @classmethod new_game) (which creates an instance of the class Entity "Game")
      and returns GameForm (which contains all relevant information + the urlsafe key)
 - **get_game_history**
    - checks with the help of the urlsafe key if the entity is of the right kind and if this is the case, 
      relevant information of a game are reflected. With the help of the properties moves, player1_position and
      player2_position you can see exactly what has happened in the past rounds.
    - if there is no winner/loser and the game did not finish tied, the endpoint adds a task to the task queue 
 - **make_move**
    - here the user decides on a position.
      We then check if there is already a winner, if this is not the case, the following will happen: 
      if the desired value is between 1-9 and if the value is not already used by one of the players the user places her position there. 
      Then the desired position is added to the properties moves, player1_position or player2_position and the value
      in available_position cannot be selected anymore plus is set to 0.
    - As soon as the position is placed by e.g. player1, the code checks if the list of player1_position matches any of the Tic Tac Toe winning combinations.
      If there is a match, the Property of winner1 is set to True. Parallely, the Score is updated (and can be viewed via **get_user_wins**)
    - as there is also the possibility of tie the following might happen: If the game has no winner, no setting is set to True which also means, no score is improved and no ranking position is changed. However, the game ends after 9 positions are placed.
- **get_user_games**
    - takes in a user name and, if there is a match in the database, returns a list of all relevant information for each game in which the user has participated
- **cancel_game**
    - if the urlsafe key is correct and the game is unfinished, you can delete the game from here
- **get_users_wins**
    - if player is in the database, all wins of a player are returned
    - besides: By calling this endpoint, the player´s win count in the
     Ranking becomes updated
- **get_user_rankings**
    - the Ranking is returned. The player with the most wins is on the top with his name and the number of wins.
- **incomplete_games**
    - returns the information from Memcache (which is: incomplete games)

Bugs and feature requests
I have not found any. If you do so, please contact me!

Creators + Contact
Name: Nojan Nourbakhsh 
Email: nojan@hotmail.de 
Name: Udacity 
Email: review-support@udacity.com

Lisene and Copyright
All rights reserved by Udacity Inc and Nojan Nourbakhsh. Category Item Project Version 1.0 and its use are subject to a license agreement and are also subject to copyright, trademark, patent and/or other laws. For further infos, please contact Nojan Nourbakhsh.
