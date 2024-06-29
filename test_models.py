"""Test User Model"""

# run the tests with these code
# 
#  python -m unittest test_models.py

import os
from unittest import TestCase


from models import db, User, Song

os.environ['DATABASE_URL'] = "postgresql:///sync_and_sound_test"

from app import app

db.create_all()

class UserModelTestCase(TestCase):
  """Test views for user"""

  def setUp(self):
    """Create test client, add sample data"""
    db.drop_all()
    db.create_all()

    u1 = User.register('test1', 'test1', 'test1', 'test1@gmail.com', 'test111111')

    uid1 = 1111
    u1.id = uid1

    u2 = User.register('test2','test2', 'test2', 'test2@gmail.com', 'test222222')
    uid2 = 2222
    u2.id = uid2

    db.session.commit()

    u1 = User.query.get(uid1)
    u2 = User.query.get(uid2)

    song1 = Song(
      name='song1',
      artist='artist1',
      song_id='song_id1',
      song_uri='uri1'
    )
    db.session.add(song1)
    u1.songs.append(song1)
    self.song1 = song1
    db.session.commit()


    self.u1 = u1
    self.uid1 = uid1

    self.u2 = u2
    self.uid2 = uid2

    self.client = app.test_client()

  def tearDown(self):
    res = super().tearDown()
    db.session.rollback()
    return res
  

  ##
  # Test users
  # 
  def test_create_user(self):
    """Does user get created?"""

    u = User(
      first_name="test",
      last_name="test",
      username="test",
      email="test@gmail.com",
      password="testpassword" 
    )

    db.session.add(u)
    db.session.commit()

    
    user = User.query.filter_by(username='test').first()
    self.assertIsNotNone(user)
    self.assertEqual(user.email, "test@gmail.com")
    self.assertEqual(user.username, "test")

  def test_delete_user(self):
    """Delete user"""
    db.session.delete(self.u2)
    db.session.commit()

    user = User.query.get(self.uid2)
    self.assertIs(user, None)
    
  ####
  #
  # Test songs
  #
  def test_add_song(self):
    new_song = Song(
      name='song2',
      artist='artist2',
      song_id='song_id2',
      song_uri='uri2'
    )

    db.session.add(new_song)
    self.u1.songs.append(new_song)
   
    db.session.commit()
    
    self.assertEqual(len(self.u1.songs), 2)
    self.assertIn(new_song, self.u1.songs)

  def test_remove_song(self):
    """Test removing a song from a user"""

    self.u1.songs.remove(self.song1)
    db.session.commit()

    self.assertEqual(len(self.u1.songs), 0)
    self.assertNotIn(self.song1, self.u1.songs)

  











