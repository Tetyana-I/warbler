"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, Message, User, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None,
                                    header_image_url=None,
                                    bio=None,
                                    location=None)

        db.session.commit()

    def test_show_following_for_logged_user(self):
        """When you’re logged in, can you see the following pages for any user?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test
                being_followed_user = User(username="followed_user",
                                    email="test1@test.com",
                                    password="testuser",
                                    image_url=None,
                                    header_image_url=None,
                                    bio=None,
                                    location=None)
                db.session.add(being_followed_user)
                db.session.commit()
                f = Follows(user_being_followed_id = being_followed_user.id, user_following_id = sess[CURR_USER_KEY])
                db.session.add(f)
                db.session.commit()
                resp = c.get(f"/users/{self.testuser.id}/following")
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                # self.assertIn("<p>@{{ being_followed_user.username }}</p>", html)

    # def test_not_show_following_for_not_logged_user(self):
    #     """When you’re logged out, are you disallowed from visiting a user’s follower / following pages?"""  
    #     with app.test_client() as client: 
    #         # test redirection
    #         res = client.get(f"/users/{self.testuser.id}/following")     
    #         self.assertEqual(res.status_code, 302)
    #         self.assertEqual(res.location, "http://localhost/")
            
            
            # test redirection to correct homepage
                       
            # html = res.get_data(as_text=True)
            # self.assertEqual(res.status_code, 200)
            # self.assertIn("<h1>What's Happening?</h1>", html)




