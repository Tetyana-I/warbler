"Meesage model tests."""

# run these tests like:
#    python -m unittest test_message_model.py

import os
from unittest import TestCase

from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()


class MessageModelTestCase(TestCase):
    """Test model for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        
    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()


    def test_message_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()
       

        m = Message(
            text = "My test message",
            user_id = u.id
        )

        db.session.add(m)
        db.session.commit()


        self.assertEqual(m.text, "My test message")

        #user "u" should have one message
        self.assertEqual(len(u.messages), 1)


