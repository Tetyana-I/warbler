"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, Message, User, Follows, Likes

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

        self.user2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser",
                                    image_url=None,
                                    header_image_url=None,
                                    bio=None,
                                    location=None)

        self.user3 = User.signup(username="testuser3",
                                    email="test3@test.com",
                                    password="testuser",
                                    image_url=None,
                                    header_image_url=None,
                                    bio=None,
                                    location=None)
        db.session.commit()


    def tearDowm(self):
        """Clean up any fouled transaction."""
        db.session.rollback()


    def test_user_index(self):
        """ test list of all users """
        with self.client as client:
            resp = client.get("/users")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<p>@testuser</p>", html)
            self.assertIn("<p>@testuser2</p>", html)


    def test_user_show(self):
        """ test showing user details page """
        with self.client as client:
            resp = client.get(f"/users/{self.testuser.id}")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser", str(resp.data))
            self.assertNotIn("@testuser2", str(resp.data))


    def test_add_likes(self):
        """ test adding likes to a message """
        m = Message(text="warble to like", user_id=self.user2.id)
        db.session.add(m)
        db.session.commit()
        path = f"/users/{self.testuser.id}/add_like/{m.id}"
       
        with self.client as cl: 
            with cl.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = cl.post(path, data={'user_id': self.testuser.id, 'msg_id': m.id}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200) 
            html = resp.get_data(as_text=True)
            
            # check liked message
            self.assertIn('warble to like', html)
            
            # check added like
            self.assertIn(f'<a href="/users/{self.testuser.id}/likes">1</a>', html)


    def test_not_show_following_for_not_loggedin_user(self):
        """When you’re logged out, are you disallowed from visiting a user’s follower / following pages?"""  
        with self.client as client: 
            res = client.get(f"/users/{self.testuser.id}/following")     
            self.assertEqual(res.status_code, 302)
            self.assertEqual(res.location, "http://localhost/")

            res = client.get(f"/users/{self.testuser.id}/following", follow_redirects=True)  
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn('Access unauthorized', html)


    def test_show_following(self):
        """ test show followed users """
        
        f1 = Follows(user_being_followed_id=self.user3.id, user_following_id=self.testuser.id)
        db.session.add(f1)
        db.session.commit()
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser.id}/following")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser3", str(resp.data))
            self.assertNotIn("@testuser2", str(resp.data))



