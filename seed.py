from app import app
from models import User, db, Song

# Drop all tables and recreate them
db.drop_all()
db.create_all()

# Create a new Song instance
s1 = Song(name='nadie mas', artist='nsqk', song_id ='dasd', song_uri='lol')
s2 = Song(name='bad', artist='nsqk', song_id='sada', song_uri='lo')

# Register a new user with a hashed password
u1 = User.register(first_name='user1', last_name='user1last',username='user1',email='user1@gmail.com', password='user1')
u1.first_name = 'user1'
u1.last_name = 'lastnam1'
u1.email = 'email1'

# Establish the relationship
u1.songs.append(s1)
u1.songs.append(s2)

# Add instances to the session and commit
db.session.add(s1)
db.session.add(u1)
db.session.commit()


