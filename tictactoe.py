import endpoints
import logging
from google.appengine.ext import ndb
from protorpc import remote, messages, message_types
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import Player, StringMessage, Game#, Score
from models import NewGameForm, GameForm, MakeMoveForm, \
GameForms, GameForm2#, ScoreForm, ScoreForms

from utils import get_by_urlsafe, win_checker, win_checker_test

#ResourceContainer
# If the request contains path or querystring arguments, you need to use ResourceContainer

USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1))

MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1))

GET_USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1))

MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'

@endpoints.api(name='tic_tac_toe', version='v1')

class tictactoeAPI(remote.Service):
    """Game API"""

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='player',
                      name='create_Player',
                      http_method='POST')
    def create_Player(self, request):
        """Create a User. Requires a unique username"""
        query_player = Player.query(Player.name == request.user_name).get()
        # somehow the if statement cannot be:
        # if query_player1 == True and query_player2 == True
        if query_player:
            raise endpoints.ConflictException(
                    'A User with that name already exists in the DB! You do not need\
                    to create a new one')
        player = Player(name=request.user_name, email=request.email)
        player.put()
        return StringMessage(message='Player {} created!'.format(
                request.user_name))
        """Old mit  prozent '%(d %(d' % (1, 2) --> ohne ( bei d
           New '{} {}'.format(1, 2)
           Also wird user_name aus request in die {} eingesetzt"""

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        player1 = Player.query(Player.name == request.player1).get()
        player2 = Player.query(Player.name == request.player2).get()
        if not (player1 and player2):
          raise endpoints.NotFoundException(
            'No user with this name in the database')
        game = Game.new_game(player1.key, player2.key)
        # user.key because we decided to use the KeyProperty as fieldtype
        return Game.to_form(game, 'Good luck playing TICTACTOE!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Return the current game history with the help of
        urlsafe in utils.py. Matches the strings returned by urlsafe
        """
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            if not game.winner1 == True or game.winner2 == True or len(game.moves) ==9:
              taskqueue.add(url='/tasks/cache_incomplete_games')
            return game.to_form('Here we go. The history of the game')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.winner1:
            return game.to_form('Game already over!')
        if game.winner2:
            return game.to_form('Game already over!')
        else:
            position = request.position
            if position<10 and position>0:
              if position not in game.moves:
                winning_list = {"win1": [1,2,3], "win2": [1,5,9], "win3": [1,4,7], 
                                "win4": [2,5,8], "win5": [3,5,7], "win6": [3,6,9],
                                "win7": [4,5,6], "win3": [7,8,9]}
                i = len(game.moves)
                if i%2==0:
                    game.player1_position.append(position)
                    game.moves.append(position)
                    game.available_positions[position-1] = 0
                    game.put()
                    still_available = len(game.moves)
                    check = win_checker(game.player1_position, still_available, winning_list)
                    if check == "Player is the champ!":
                      game.end_of_game(True,False)
                      return game.to_form("Player1 is the best")
                    else:
                      return game.to_form(check)
                else:
                    game.player2_position.append(position)
                    game.moves.append(position)
                    game.available_positions[position-1] = 0
                    game.put()
                    still_available = len(game.moves)
                    check = win_checker(game.player2_position, still_available, winning_list)
                    if check == "Player is the champ!":
                      game.end_of_game(False,True)
                      return game.to_form("Player2 is the best")
                    else:
                      return game.to_form(check)
              else:
                raise endpoints.BadRequestException("Position is already taken")
            else:
              raise endpoints.BadRequestException("Position must be between 1 to 9")

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=StringMessage,
                      path='game/test',
                      name='test',
                      http_method='PUT')
    def test(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.winner1:
            return game.to_form('Game already over!')
        if game.winner2:
            return game.to_form('Game already over!')
        else:
            position = request.position
            if position<10 and position>0:
              if position not in game.moves:
                i = len(game.moves)
                if i%2==0:
                    game.player1_position.append(position)
                    game.moves.append(position)
                    game.available_positions[position-1] = 0
                    game.put()
                    still_available = len(game.moves)
                    check = win_checker_test(game.player1_position)
                    check2 = win_checker_test(game.player2_position)
                    return StringMessage(message='bla bla bla player1_position {} player2_position {} still_available {} check_if_player1_won {} check_if_player1_won {} created! Moves {}'.format(game.player1_position, game.player2_position, still_available, check, check2, game.moves))

                else:
                    game.player2_position.append(position)
                    game.moves.append(position)
                    game.available_positions[position-1] = 0
                    game.put()
                    still_available = len(game.moves)
                    check = win_checker_test(game.player1_position)
                    check2 = win_checker_test(game.player2_position)
                    return StringMessage(message='player1_position {} player2_position {} still_available {} check_if_player1_won {} check_if_player1_won {} created! Moves {}'.format(game.player1_position, game.player2_position, still_available, check, check2, game.moves))
              else:
                raise endpoints.BadRequestException("Position is already taken")
            else:
              raise endpoints.BadRequestException("Position must be between 1 to 9")


    @endpoints.method(request_message=GET_USER_REQUEST,
                      response_message=GameForms,
                      path='game/get_user_games',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Return all Player's active games"""
        player = Player.query(Player.name == request.user_name).get()
        if not player:
            raise endpoints.BadRequestException('User not found!')
        games = Game.query(ndb.OR(Game.player1 == player.key,
                                  Game.player2 == player.key)) #Ancestor query hence the key
        return GameForms(items=[game.to_form2() for game in games])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/cancel_game',
                      name='cancel_game',
                      http_method='POST')
    def cancel_game(self, request):
        """Via urlsafe_game_key you can delete in here"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
          if game.moves < 9 or game.winner1 == False or game.winner2 == False:
            game.key.delete()
            return StringMessage(message='Game with the following urlsafe key is deleted: {}'.format(request.urlsafe_game_key))
          else:
            raise endpoints.NotFoundException('Game is over and cannot be deleted')
        else:
          raise endpoints.NotFoundException('Game not found! Cannot be deleted!')

    """@endpoints.method(request_message=GET_USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/player/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        Returns all of an individual User's scores
        player = Player.query(Player.name == request.user_name).get()
        if not player:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        scores = Score.query(Score.player == player.key)
        return ScoreForms(items=[score.to_form() for score in scores])"""

    @endpoints.method(response_message=StringMessage,
                      path='games/incomplete_games',
                      name='incomplete_games',
                      http_method='GET')
    def incomplete_games(self, request):
        """Get the cached incomplete games"""
        announcement = memcache.get(MEMCACHE_MOVES_REMAINING)
        if not announcement:
            announcement = ""
        return StringMessage(message=announcement)

    # create private method
    @staticmethod
    def _cache_incomplete_games():
        """Populates memcache with the incomplete Games"""
        games = Game.query(ndb.OR(Game.winner1 == False,
                                  Game.winner2 == False)).fetch()
        # returns a list of games
        if games:
          for game in games:
            if len(game.moves)<9:
              if len(game.player1_position)>len(game.player2_position):
                announcement = 'It is {} turn.'.format(game.player1.get().name) 
                #game.player1 returns (Player, somekey) - we need the name form the instance in Player
                memcache.set(MEMCACHE_MOVES_REMAINING, announcement)
              else:
                announcement = 'It is {} turn.'.format(game.player2.get().name)
                memcache.set(MEMCACHE_MOVES_REMAINING, announcement)
            else:
                announcement = "Game is tied"
                memcache.delete(MEMCACHE_ANNOUNCEMENTS_KEY)
        else:
          announcement = ""
          memcache.delete(MEMCACHE_ANNOUNCEMENTS_KEY)
        return announcement



# name from class in endpoints.api will be reused in here
api = endpoints.api_server([tictactoeAPI])

