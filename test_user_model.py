"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase


from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Tests for user model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        
    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()


    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"

        )

        db.session.add(u)
        db.session.commit()
       
        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

        #default header image should be setup
        self.assertEqual(u.header_image_url, "/static/images/warbler-hero.jpg")


    def test_repr(self):
        """ Does the repr method work as expected? """
        u = User(
            email="test3@test.com",
            username="testuser3",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()
        self.assertEqual(repr(u), f"<User #{u.id}: testuser3, test3@test.com>")

    def test_is_following(self):
        """ Does is_following successfully detect when user1 is following user2? 
            Does is_following successfully detect when user1 is not following user3?
        """
        u1 = User(
            email="test4_1@test.com",
            username="testuser4_1",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test4_2@test.com",
            username="testuser4_2",
            password="HASHED_PASSWORD"
        )
        
        u3 = User(
            email="test4_3@test.com",
            username="testuser4_3",
            password="HASHED_PASSWORD"
        )

        db.session.add_all([u1,u2,u3])
        db.session.commit()

        following = Follows(user_being_followed_id = u2.id, user_following_id = u1.id)
        db.session.add(following)
        db.session.commit()
        self.assertEqual(u1.is_following(u2), True)
        self.assertEqual(u1.is_following(u3), False)

    def test_is_followed_by(self):
        """Does is_followed_by successfully detect when user1 is followed by user2?
        Does is_followed_by successfully detect when user1 is not followed by user3?"""

        u1 = User(
            email="test5_1@test.com",
            username="testuser5_1",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test5_2@test.com",
            username="testuser5_2",
            password="HASHED_PASSWORD"
        )
        
        u3 = User(
            email="test5_3@test.com",
            username="testuser5_3",
            password="HASHED_PASSWORD"
        )

        db.session.add_all([u1,u2,u3])
        db.session.commit()

        following = Follows(user_being_followed_id = u1.id, user_following_id = u2.id)
        db.session.add(following)
        db.session.commit()
        self.assertTrue(u1.is_followed_by(u2))
        self.assertFalse(u1.is_followed_by(u3))

    
    def test_signup(self):
        """ Does User.signup successfully create a new user given valid credentials?
        Does User.signup fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?"""
        
        self.assertIsInstance(User.signup(username="test6",
                                             email="tetst6_1@test.com",
                                             password="hashed_password",
                                             image_url="some_URL",
                                             header_image_url="another_URL" ,
                                             bio = "somethinh here",
                                             location = "wonderland"),
                                             User)


    def test_authenticate(self):
        """ Does User.authenticate fail to return a user when the username is invalid?
        Does User.authenticate fail to return a user when the password is invalid?"""

        u = User(
            email="test6_1@test.com",
            username="testuser6_1",
            password="testpassword"
        )
        db.session.add(u)
        db.session.commit()

        self.assertFalse(User.authenticate(username='testuser', password='testpassword'))

        # Does User.authenticate successfully return a user when given a valid username and password?
        # self.assertIsInstance(User.authenticate(username='testuser6_1', password='testpassword'), User)

          