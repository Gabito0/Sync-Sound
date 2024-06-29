from flask_sqlalchemy import  SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

db = SQLAlchemy()

def connect_db(app):
  db.app = app
  db.init_app(app)

  # Models

class User(db.Model):
  """User's Model"""

  __tablename__ = "users"

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)

  first_name = db.Column(db.Text, nullable=False)

  last_name = db.Column(db.Text, nullable=False)

  username = db.Column(db.Text, nullable=False, unique=True)

  email = db.Column(db.Text, nullable=False, unique=True)

  password = db.Column(db.Text, nullable=False)

  songs = db.relationship('Song', secondary='users_song', backref='users')

  @classmethod
  def register(cls, first_name, last_name, username, email, password):
    """Register user w/hashed passowrd & return user"""

    hashed_pwd= bcrypt.generate_password_hash(password).decode('UTF-8')

    # turned bytestring into normal string

    user = User(
      first_name = first_name,
      last_name = last_name,
      username = username, 
      email = email,
      password = hashed_pwd
    )

    db.session.add(user)
    return user

  @classmethod
  def authenticate(cls, username, password):
    """Validate that user exists & password is correct

    Return user if valid; else return False.
    """
  
    user = cls.query.filter_by(username=username).first()

    if user:
      is_auth = bcrypt.check_password_hash(user.password, password)
      if is_auth:
        print("user authenticated")
        return user
      print("not user")
      return False
  


class Song(db.Model):
  """Song's model """
  __tablename__ = 'songs'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.Text, nullable=False)
  artist = db.Column(db.Text, nullable=False)
  song_id = db.Column(db.Text, nullable=False, unique=True)
  song_uri = db.Column(db.Text, nullable=False)

class UserSong(db.Model):
  """User song's model"""
  __tablename__ = 'users_song'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
  song_id = db.Column(db.Integer, db.ForeignKey('songs.id'))

  


  