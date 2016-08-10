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
        return None
        # no entity available
    if not isinstance(entity, model):
        raise ValueError('Incorrect Kind')
        # wrong kind
    return entity
    # correct kind


def win_checker(win):
    """checks if the user is a winner of not"""
    if set(win).issuperset(set([1,2,3])) or set(win).issuperset(set([1,5,9])) or set(win).issuperset(set([1,4,7])) or set(win).issuperset(set([2,5,8])) or set(win).issuperset(set([3,5,7])) or set(win).issuperset(set([3,6,9])) or set(win).issuperset(set([4,5,6])) or set(win).issuperset(set([7,8,9])):
        return "Player is the champ!"
    else:
        return "Your current positions: {}!".format(win)
