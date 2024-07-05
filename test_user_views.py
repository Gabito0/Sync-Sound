"""User view test"""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py
# 
# if test fails:
# 1. Run the app and log in (if already login, logout).
# 2. Stop the running app.
# 3. Run the tests again.

import os
from unittest import TestCase
from unittest.mock import patch
from dotenv import load_dotenv
load_dotenv()

from models import db, connect_db, User, Song


os.environ['DATABASE_URL'] = "postgresql:///sync_and_sound_test"
access_token = os.getenv('TEST_ACCESS_TOKEN')
refresh_token = os.getenv('TEST_REFRESH_TOKEN')
expire_at = os.getenv('TEST_EXPIRES_AT')
expire_at = float(expire_at)
print("checkingfloat", type(expire_at))



print("this is the access toekn",access_token)

from app import app, CURR_USER_KEY


db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users and songs"""

    def setUp(self):
        """Create test client, add sample data"""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        # Create a sample user to use in tests
        self.testuser = User.register(
            first_name="test",
            last_name="user",
            username="testuser",
            email="test@test.com",
            password="password1111"
        )
        self.testuser_id = 1234
        self.testuser.id = self.testuser_id
        
        self.testsong = Song(
        name="Test Song",
        artist="Test Artist",
        song_id="testsongid",
        song_uri="testsonguri"
        )
        db.session.add(self.testsong)
        db.session.commit()

        self.testuser.songs.append(self.testsong)
        db.session.commit()

    def tearDown(self):
        """Clean up any fouled transaction"""
        res = super().tearDown()
        db.session.rollback()
        return res

    def login_and_set_session(self):
        with self.client.session_transaction() as sess:
            sess[CURR_USER_KEY] = self.testuser.id
            sess['access_token'] = access_token
            sess['refresh_token'] = refresh_token
            sess['expires_at'] = expire_at

    def test_home_page(self):
        """Can a user go to home page?"""
        with self.client as client:
            self.login_and_set_session()
            resp = client.get('/home', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("Song", html)

    def test_local_release_page(self):
        """Can user go to local release page?"""
        with self.client as client:
            self.login_and_set_session()
            resp = client.get('local-release', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("Artist", html)
    
    def test_my_songs_route(self):
        """Does uses save song route works?"""
        with self.client as client:
            self.login_and_set_session()
            resp = client.get('/my-songs', follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertIn("My Songs", html)
        

    def test_sign_up_user(self):
        """can user create account?"""
        with self.client as client:
            data = {
                "first_name": "New",
                "last_name": "User",
                "username": "newuser",
                "email": "newuser@test.com",
                "password": "password11",
            }
            with client.session_transaction() as sess:
                sess['access_token'] = access_token
                sess['refresh_token'] = refresh_token
                sess['expires_at'] = expire_at
            resp = client.post('sign-up', data=data, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            # check if user is the in db
            user = User.query.filter_by(username="newuser").first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, "newuser@test.com")

    def test_logout_user(self):
        """Does logout route works?"""
        with self.client as client:
            self.login_and_set_session()
            resp = client.get('/logout', follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertIn("Sign In", html)
    

    def test_save_song(self):
        """Does save songs works?"""
        with self.client as client:
            data = {
                "artist": "test_artist",
                "song_uri": "test_uri",
                "song_name": "test_name",
                "song_id": "test_song_id"
            }
            self.login_and_set_session()
            resp = client.post('/save-song', data=data, follow_redirects=True)
            html= resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            song = Song.query.filter_by(song_id="test_song_id").first()
            self.assertIsNotNone(song)

    def test_remove_song(self):
        """Does remove song work?"""
        with self.client as client:
            data = {
                "song_uri":"testsonguri"
            }
            self.login_and_set_session()
            resp = client.post('/remove-song', data=data, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            user = User.query.get(self.testuser_id)
            user_songs = user.songs
            self.assertNotIn(self.testsong, user_songs)

    def test_show_profile(self):
        """Does user info loads?"""
        with self.client as client:
            self.login_and_set_session()
            resp = client.get('/profile', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("test@test.com", html)

    def test_update_profile(self):
        """Does profile PUT works?"""
        with self.client as client:
            data={
                "first_name": "changed name",
                "last_name": "user",
                "email": "test@test.com",
                "password": "password1111"
            }
            self.login_and_set_session()
            resp = client.put('/profile', json=data, follow_redirects=True)
            self.assertEqual(resp.status_code,200)
            
            user = User.query.get(self.testuser_id)
            self.assertEqual(user.first_name, "changed name")

    def test_delete_user(self):
        """
        Does profile DELETE works?
        Please comment out `validate_csrf(csrf_token)` in the delete route.
        """
        with self.client as client:
            self.login_and_set_session()
            headers ={"X-CSRFToken": "mock-token"}
            resp = client.delete('/profile',headers=headers,follow_redirects=True)  # Corrected URL
            self.assertEqual(resp.status_code, 200)
            user = User.query.get(self.testuser_id)
            self.assertIsNone(user)
            html = resp.get_data(as_text=True)
            self.assertIn('"success":true', html)
