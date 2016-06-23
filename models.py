"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods."""

import random
from protorpc import messages
from google.appengine.ext import ndb

class Player(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()

# what does stringmessage do
# if I want to display a message like 'User {} created!' I need this class
class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)

class possible_wins(ndb.Model):
    win1 = ndb.IntegerProperty(repeated=True)

# whats the score is missing. I need end of game
class Game(ndb.Model):
    """Game object"""
    player1 = ndb.KeyProperty(required=True, kind='Player')
    player2 = ndb.KeyProperty(required=True, kind='Player')
    winner1 = ndb.BooleanProperty(required=True, default=False)
    winner2 = ndb.BooleanProperty(required=True, default=False)
    available_positions = ndb.IntegerProperty(repeated=True)
    player1_position = ndb.IntegerProperty(repeated=True)
    player2_position = ndb.IntegerProperty(repeated=True)
    moves = ndb.IntegerProperty(repeated=True)

    @classmethod
    def new_game(cls, player1, player2):
        """Creates and returns a new game"""
        game = Game(player1=player1,
                    player2=player2,
                    winner1=False,
                    winner2=False,
                    available_positions=[1,2,3,4,5,6,7,8,9],
                    player1_position=[],
                    player2_position=[],
                    moves=[])
        game.put()
        return game

    def to_form2(self):
        """Returns a GameForm representation of the Game"""
        form = GameForm2()
        form.player1 = self.player1.get().name # why user.get().name because user is object. we need the name attribute of this object
        form.player2 = self.player2.get().name
        form.winner1 = self.winner1
        form.winner2 = self.winner2
        form.available_positions = self.available_positions
        form.player1_position = self.player1_position
        form.player2_position = self.player2_position
        form.moves = self.moves
        return form

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe() # auto -generated
        form.player1 = self.player1.get().name # why user.get().name because user is object. we need the name attribute of this object
        form.player2 = self.player2.get().name
        form.winner1 = self.winner1
        form.winner2 = self.winner2
        form.message = message # message is the input of the function and is set in tictactoe.py
        form.available_positions = self.available_positions
        form.player1_position = self.player1_position
        form.player2_position = self.player2_position
        form.moves = self.moves
        return form

    def end_of_game(self, player1=False, player2=False):
        self.winner1 = player1
        self.winner2 = player2
        self.put()
        """score = Score(player=self.player1.get().name, date=str(self.date))
        score.put()"""


    """def end_of_game2(self, won=False):
        self.winner2 = True
        self.put()
        score = Score(player=self.player2.get().name, won=self.won,
                      date=str(self.date))
        score.put()"""

class NewGameForm(messages.Message):
    """Used to create a new game"""
    player1 = messages.StringField(1, required=True)
    player2 = messages.StringField(2, required=True)

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    player1 = messages.StringField(1, required=True)
    player2 = messages.StringField(2, required=True)
    winner1 = messages.BooleanField(3, required=True)
    winner2 = messages.BooleanField(4, required=True)
    urlsafe_key = messages.StringField(5, required=True)
    message = messages.StringField(6, required=True)
    available_positions = messages.IntegerField(7, repeated = True)
    player1_position = messages.IntegerField(8, repeated = True)
    player2_position = messages.IntegerField(9, repeated = True)
    moves = messages.IntegerField(10, repeated = True)

class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    position = messages.IntegerField(1, required=True)

class GameForm2(messages.Message):
    """GameForm for outbound game state information"""
    player1 = messages.StringField(1, required=True)
    player2 = messages.StringField(2, required=True)
    winner1 = messages.BooleanField(3, required=True)
    winner2 = messages.BooleanField(4, required=True)
    available_positions = messages.IntegerField(5, repeated = True)
    player1_position = messages.IntegerField(6, repeated = True)
    player2_position = messages.IntegerField(7, repeated = True)
    moves = messages.IntegerField(8, repeated = True)

class GameForms(messages.Message):
    """Return multiple GameForms"""
    items = messages.MessageField(GameForm2, 1, repeated = True)


"""class Score(ndb.Model):
    Score object
    player = ndb.KeyProperty(required=True, kind='Player')
    date = ndb.DateProperty(required=True)

    def to_form(self):
        return ScoreForm(player=self.user.get().name, date=str(self.date))

class ScoreForm(messages.Message):
    ScoreForm for outbound Score information
    player = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)

class ScoreForms(messages.Message):
    Return multiple ScoreForms
    items = messages.MessageField(ScoreForm, 1, repeated=True)
   # player2_position = messages.MessageField(2, repeated=True)
   # moves = messages.MessageField(3, repeated=True)"""