#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs.

HTTP controller handlers for memcache & task queue access

webapp2 is a lightweight Python web framework compatible 
with Google App Engines
it adds better URI routing and exception handling, a full
featured response object and a more flexible dispatching mechanism.
webapp2 also offers the package webapp2_extras with several optional
utilities: sessions, localization, internationalization, domain and
subdomain routing, secure cookies and others.
"""
import webapp2
from google.appengine.api import mail, app_identity
from tictactoe import tictactoeAPI
from models import Player


# keeps the games on the state of the art
class Updateincompletegames(webapp2.RequestHandler):
    def post(self):
        """Update game listing announcement in memcache."""
        tictactoeAPI._cache_incomplete_games()
        self.response.set_status(204)


# this will send an email to the two players of a match
class SendReminderEmail(webapp2.RequestHandler):
    def post(self):
        """Send a reminder email to each User.
        Called if user did not finish a game using a cron job"""
        app_id = app_identity.get_application_id()
        # infos: https://cloud.google.com/appengine/docs/python/appidentity/
        subject = 'Reminder - Your game is not over!'
        body1 = 'Hello {}, please make a move! Your game is not over.\
        Your opponent is {}.'.format(self.request.get('nameplayer1'),
                                     self.request.get('nameplayer2'))
        body2 = 'Hello {}, please make a move! Your game is not over.\
        Your opponent is {}.'.format(self.request.get('nameplayer2'),
                                     self.request.get('nameplayer1'))
        mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                       self.request.get('emailplayer1'),
                       subject,
                       body1)
        mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                       self.request.get('emailplayer2'),
                       subject,
                       body2)

# sets a handler for URL (/crons/set_announcement) which is also added to app.yaml
# receives requests and dispatches the appropriate handler
app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
    ('/tasks/cache_incomplete_games', Updateincompletegames),
], debug=True)
