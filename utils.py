"""collecting general utility functions."""

import logging
from google.appengine.ext import ndb
import endpoints

"""urlsafe = use an entity's key to obtain an encoded string suitable for 
embedding in a URL.
This produces a result like agVoZWxsb3IPCxIHQWNjb3VudBiZiwIM which can later be 
used to reconstruct the key and retrieve the original entity. NOT encrypted!!!!
Check out 
https://cloud.google.com/appengine/docs/python/ndb/
creating-entities#Python_retrieving_entities"""

# urlsafe: A urlsafe key string from GET_GAME_REQUEST
# model: The expected entity kind from models.py
def get_by_urlsafe(urlsafe, model):
    """Checks with the help of the key that the type of ndb.Model entity 
    returned is of the correct kind.
    if the key String is malformed or the entity is of the incorrect
    kind return error"""
    try:
        key = ndb.Key(urlsafe=urlsafe)
    except TypeError:
        raise endpoints.BadRequestException('Invalid Key')
    # 1. there are two ways of saying that except Exception as e: (Python 2.6.)
    # or except Exception, e:
    # e is an argument which enables us to analysis the error in more detail
    except Exception, e:
        if e.__class__.__name__ == 'ProtocolBufferDecodeError':
            raise endpoints.BadRequestException('Invalid Key')
        else:
            raise

    entity = key.get()
    if not entity:
        return None # no entity available
    if not isinstance(entity, model):
        raise ValueError('Incorrect Kind') # wrong kind
    return entity

def win_checker(player, still_available, winning_list):
    """checks if the positions in the list player match with one of the lists
     in the dictionary winning_list"""
    for w_list in winning_list:
        moves_player_compared = set(winning_list[w_list]).intersection(player)
        if len(moves_player_compared)==3:
            if len(moves_player_compared)==3:
                return "Player is the champ!"
        else:
            if still_available == 9:
                return "Tie game"
            else:
                still_to_go = 9-still_available
                return "Still %s moves left" % still_to_go

