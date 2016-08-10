Tic Tac Toe Version 1.1 created on 10.08.2016

General Usage
This project includes the Backend for a 2 player game which is called Tic Tac Toe. Further information on the game: https://en.wikipedia.org/wiki/Tic-tac-toe

Table of contents

Installing
Quick start 
What´s included?
Which Endpoints are in tictactoe.py?
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

Instructions for playing the game

This 2player game has 9 (3x3 grid) empty fields and in each round a player can mark in one of the spaces. The aim of this game is, to have 3 out of 9 fields in one order. It does not matter if the 3 field-order is
diagonal, vertical or horizontal. For further infos please have a look at the following link: https://en.wikipedia.org/wiki/Tic-tac-toe


Which Endpoints are in tictactoe.py?

  create_player
    Path: player
    Method: POST
    Parameters: user_name, email (optional)
    Returns: Message confirming creation of the User.
    Description: Creates a new User. user_name provided must be unique.
    ConflictException: if a User with that user_name already exists.
  
  new_game
    Path: game
    Method: POST
    Parameters: 2 x user_name
    Returns: "Good Luck" - message + some further information about the new game: all the 9 available_positions, player1, player2, urlsafe_key, winner1, winner2 (both winners are set to false) and moves, player1_positions, player2_positions (will be important at a later point)
    Description: Creates new game. User can type in his user_name as player1 and player2 in order to play against herself. You need to pass the urlsafe_key to many of the upcoming endpoints.
    ConflictException: If user_name does not exist

  get_game_history
    Path: game/history/{urlsafe_game_key}
    Method: GET
    Parameters: ursafe_key
    Returns: A message, the moves in chronological order and the information that the game is not over (finished_status), if at least one of the players has made a move. Furthermore, a task is added to the taskqueue (with the name, email of the game´s player)
    Description: Verify the urlsafe_key and returns all the information which are currently important for this match
    ConflictException: if game is finished or urlsafe_key does not exist

   make_move
    Path: game/move/{urlsafe_game_key}
    Method: PUT
    Parameters: urlsafe_key, position
    Returns: the same as new_game. Here the returned value are the latest updated ones.
    Description: After verifying the urlsafe key, the player can choose a position out of the 3x3 grid. This position appears then in moves and it is mentioned in player1_positions or player1_positions (depending on whos turn it is).
    After player1 has made her move, it will be player2s turn until either one of the 2 players has 3 fields in an order or they draw.If there is a winner either winner1 or winner 2 and finished_status becomes True + the string mentiones which player is the winner and the game is finished otherwise the game has 9 rounds and there is no winner.
    ConflictException: 
    1) if there is a winner or draw, no positions can be selected 
    2) if the value is not a digit
    3) if the desired positon is not between 0-10, position can not be selected
    4) if the posititon is already used in this game, position can not be selected

  get_user_games
    Path: game/get_user_games
    Method: GET
    Parameters: user_name
    Returns: Similar to new_game and make_move. However, this time you can see a list of all the games in which currently the player is participating at (does not list finished games).
    Description: Checks in player1 and playr2 if there has been a player with such a name.
    ConflictException: If user is not in DB

  delete_game
    Path: game/delete_game
    Method: DELETE
    Parameters: urlsafe_key
    Returns: String with the relevant urlsafe_key as confirmation that game has been deleted
    Description: If the urlsafe key is correct and the game is unfinished, you can delete the game from here
    ConflictException:
    1) if urlsafe_key is wrong
    2) if game is already finished

  get_users_wins
    Path: scores/player/get_users_wins
    Method: GET
    Parameters: user_name
    Returns: String containing number of wins and name of the player
    Description: if player is in the database, all wins of a player are returned
    Besides: By calling this endpoint, the player´s win count in the
    Ranking becomes updated
    ConflictException: if user does not exist in DB

  get_user_rankings
    Path: scores/player/get_user_rankings
    Method: GET
    Parameters: -
    Returns: list of all players who are in the ranking with their name and their number of wins. The player with the most wins is on the top with his name and the number of wins.
    Description: If the get_users_wins endpoint is called then the data in get_user_rankings is updated. Why is this seperated? The user who just wants to play the game without appearing in the ranking list, can avoid this by not calling the get_user_wins endpoint. But this person has still the posibilty to check through the rankings in order to decide either to publish her wins or not.
    ConflictException: -

  incomplete_games 
    Path: games/incomplete_games
    Method: GET
    Parameters: -
    Returns: the information from Memcache (which is: incomplete games)
    Description: Checks  
    ConflictException:

Bugs and feature requests
I have not found any. If you do so, please contact me!

Creators + Contact
Name: Nojan Nourbakhsh 
Email: nojan@hotmail.de 

Lisene and Copyright
All rights reserved by Nojan Nourbakhsh. Although some parts might origin from Udacity Inc, Nojan Nourbakhsh has the license to use, modify, copy, distribute these parts of the code. Category Item Project Version 1.0 and its use are subject to a license agreement and are also subject to copyright, trademark, patent and/or other laws. For further infos, please contact Nojan Nourbakhsh.
