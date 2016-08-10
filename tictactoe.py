import endpoints
from google.appengine.ext import ndb
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from models import (Player,
                    Game,
                    Score,
                    Ranking)

from models import (StringMessage,
                    NewGameForm,
                    GameForm,
                    MakeMoveForm,
                    GameForms,
                    GameForm2,
                    RankingForm,
                    RankingForms,
                    move_GameForm)

from utils import get_by_urlsafe, win_checker

# ResourceContainer
# If the request contains path or querystring arguments,
# you need to use ResourceContainer

# type in relevant infos for a Player
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))

# type in relevant infos
NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)

# now you need the urlsafe_key
GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1))

# type in a number between 1-9 (9 fields in TicTacToe)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1))

# type in a user name
GET_USER_REQUEST = endpoints.ResourceContainer(
    user_name=messages.StringField(1))

# announcement will constantly contain the following message
MEMCACHE_INCOMPLETE_GAMES = 'MOVES_REMAINING'


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
                    'A User with that name already exists in the DB! You do not need to create a new one')
        player = Player(name=request.user_name, email=request.email)
        player.put()
        return StringMessage(message='Player {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game. Tipp: You need the urlsafe_key later"""
        player1 = Player.query(Player.name == request.player1).get()
        player2 = Player.query(Player.name == request.player2).get()
        if not (player1 and player2):
            raise endpoints.NotFoundException('No user with this name in the database')
        game = Game.new_game(player1.key, player2.key)
        # player.key gives a specific entity from the kind (Player)
        # and inputs this to new_game
        return Game.to_form(game, 'Good luck playing TICTACTOE!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=move_GameForm,
                      path='game/history/{urlsafe_game_key}',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Return the current game history with the help of
        urlsafe in utils.py. Matches the strings returned by urlsafe
        """
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            if not game.winner1 == True or game.winner2 == True or len(game.moves) == 9:
                taskqueue.add(params={'nameplayer1': game.player1.get().name,
                                      'emailplayer1': game.player1.get().email,
                                      'nameplayer2': game.player2.get().name,
                                      'emailplayer2': game.player2.get().email},
                              url='/tasks/cache_incomplete_games')
            return game.move_to_form('Here we go. The history of the game')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/move/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns the current games state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.finished_status:
            raise endpoints.ForbiddenException("Game already over")
        else:
            position = request.position
            position_str = str(position)
            if position_str.isdigit():
                if position < 10 and position > 0:
                    if position not in game.moves:
                        i = len(game.moves)
                        if i % 2 == 0:
                            game.player1_position.append(position)
                            game.moves.append(position)
                            game.available_positions[position-1] = 0
                            game.put()
                            still_available = len(game.moves)
                            check = win_checker(game.player1_position)
                            if check == "Player is the champ!":
                                game.end_of_game(True, False)
                                game.put()
                                return game.to_form("Player1 is the best")
                            elif i+1 == 9:
                                game.finished_status = True
                                game.put()
                                return game.to_form("Draw")
                            else:
                                return game.to_form(check)
                        else:
                            game.player2_position.append(position)
                            game.moves.append(position)
                            game.available_positions[position-1] = 0
                            game.put()
                            still_available = len(game.moves)
                            check = win_checker(game.player2_position)
                            if check == "Player is the champ!":
                                game.end_of_game(False, True)
                                game.put()
                                return game.to_form("Player2 is the best")
                            else:
                                return game.to_form(check)
                    else:
                        raise endpoints.BadRequestException("Position is already taken")
                else:
                    raise endpoints.BadRequestException("Position must be between 1 to 9")
            else:
                raise endpoints.ForbiddenException("Please type in a number")

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
        games = Game.query(ndb.AND(Game.finished_status == False,
                                   ndb.OR(Game.player1 == player.key,
                                          Game.player2 == player.key)))
        # Ancestor query hence the key
        return GameForms(items=[game.to_form_without_message() for game in games])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/delete_game',
                      name='delete_game',
                      http_method='DELETE')
    def delete_game(self, request):
        """Via urlsafe_game_key you can delete in here"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            if game.finished_status == False:
                game.key.delete()
                return StringMessage(message='Game with the following urlsafe key is deleted: {}'.format(request.urlsafe_game_key))
            else:
                raise endpoints.NotFoundException('Game is over and cannot be deleted')
        else:
            raise endpoints.NotFoundException('Game not found! Cannot be deleted!')

    @endpoints.method(request_message=GET_USER_REQUEST,
                      response_message=StringMessage,
                      path='scores/player/get_users_wins',
                      name='get_users_wins',
                      http_method='GET')
    def get_users_wins(self, request):
        """Returns all wins of a player + prepares the ranking"""
        player = Player.query(Player.name == request.user_name).get()
        if not player:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        rankings = Ranking.query().fetch()
        members_in_ranking = []
        for ranking in rankings:
            members_in_ranking.append(ranking.player)
            if player.name in members_in_ranking:
                scores = Score.query(Score.player == player.key).count()
                players_positons = Ranking.query(Ranking.player == player.name).get()
                players_positons.number_of_wins = scores
                players_positons.put()
                return StringMessage(message="wins: {} by player:{}".format(scores, player.name))
            else:
                scores = Score.query(Score.player == player.key).count()
                get_ranked = Ranking.new_in_ranking(player.name, scores)
                return StringMessage(message="wins: {} by {}".format(scores, player.name))

    @endpoints.method(response_message=RankingForms,
                      path='scores/player/get_user_rankings',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Returns Players in descending order. The one with
        most wins is on the top"""
        rankings = Ranking.query().order(-Ranking.number_of_wins).fetch()
        return RankingForms(items=[ranking.to_form() for ranking in rankings])

    @endpoints.method(response_message=StringMessage,
                      path='games/incomplete_games',
                      name='incomplete_games',
                      http_method='GET')
    def incomplete_games(self, request):
        """Get the cached incomplete games"""
        announcement = memcache.get(MEMCACHE_INCOMPLETE_GAMES)
        if not announcement:
            announcement = ""
        return StringMessage(message=announcement)

    # create private method which relates to main.py
    @staticmethod
    def _cache_incomplete_games():
        """Populates memcache with the incomplete Games and lets you know whos turn it is"""
        games = Game.query(ndb.OR(Game.winner1 == False,
                                  Game.winner2 == False)).fetch()
        # returns a list of games
        if games:
            for game in games:
                if len(game.moves) < 9:
                    if len(game.player1_position) > len(game.player2_position):
                        announcement = 'It is {}s turn.'.format(game.player1.get().name)
                        # game.player1 returns (Player, somekey)
                        # we need the name form the instance in Player
                        memcache.set(MEMCACHE_INCOMPLETE_GAMES, announcement)
                        # you need for set -> set(some_key,some_string)
                    else:
                        announcement = 'It is {}s turn.'.format(game.player2.get().name)
                        memcache.set(MEMCACHE_INCOMPLETE_GAMES, announcement)
                else:
                    announcement = "Game is tied"
                    memcache.delete(MEMCACHE_INCOMPLETE_GAMES)
        else:
            announcement = "no games"
            memcache.delete(MEMCACHE_INCOMPLETE_GAMES)
        return announcement


# name from class in endpoints.api will be reused in here
api = endpoints.api_server([tictactoeAPI])
