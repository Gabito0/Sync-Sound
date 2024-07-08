from flask import Flask, redirect, request, jsonify, session, render_template, url_for, g, flash
from werkzeug.exceptions import NotFound
from functools import wraps
import requests
import urllib.parse
from datetime import datetime
from models import connect_db, db, User, Song
from forms import SignUpForm, SignInForm, UserEditForm
from sqlalchemy.exc import IntegrityError
from flask_wtf.csrf import validate_csrf
from wtforms import ValidationError
from dotenv import load_dotenv
import os
load_dotenv()

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL', 'postgresql:///sync_and_sound_beta')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.secret_key = os.getenv('SECRET_KEY')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET= os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:5000/callback')


AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

connect_db(app)

def update_db(songs):
  """
  Updates the song details in the database.

  :param songs: List of song objects to be updated.
  """
  for song in songs:
    song_id = song.song_id
    
    # If song_id is a string that looks like a list (e.g., "['1ViErUfDfWkXPXTsjj3kyh']"), strip the brackets and quotes
    if isinstance(song_id, str) and song_id.startswith('[') and song_id.endswith(']'):
      song_id = song_id[1:-1].strip("'")

    # Prepare headers for the API request
    headers = {'Authorization': f"Bearer {session['access_token']}"}

    # Make the API request to get track details
    resp = requests.get(API_BASE_URL + 'tracks' + f"/{song_id}", headers=headers)

    # Check if the API request was successful
    if resp.status_code == 200:
      track = resp.json()

      # Extract artist names and join them into a single string
      artists = track['artists']
      artist_string = ", ".join([artist['name'] for artist in artists])

      # Update the song object with the new details
      song.name = track['name']
      song.song_id = track['id']
      song.song_uri = track['uri']
      song.artist = artist_string

    else:
      # Raise a NotFound exception to trigger the 404 error handler
      raise NotFound(f"Failed to fetch track details for song ID: {song_id}")

def update_env_file(file_path, new_variables):
  """
  Updates variables in a .env file. Overwrites existing keys and adds new ones if they don't exist.
  This is used for testing purposes.
  """
  try:
    # Read the existing content and split into lines.
    with open(file_path, 'r') as file:
      lines = file.readlines()
    
    # Create a dictionary of current environment variables.
    env_vars = {}
    for line in lines:
      if '=' in line:
        key, value = line.strip().split('=', 1)
        env_vars[key] = value

    # Update the dictionary with new variables.
    env_vars.update(new_variables)

    # Write the updated content back to the file.
    with open(file_path, 'w') as file:
      for key, value in env_vars.items():
        file.write(f'{key}={value}\n')
  except Exception as e:
    print(f"An error occurred: {e}")

def is_token_expire():
  """
  Checks if spotify token is expired.
  """
  if datetime.now().timestamp() > session['expires_at']:
    return True

@app.before_request
def update_sesssions():
# def add_user_to_g():
  """
  This is run before any request to update the global and previous_page 
  sessions.
  """
  
  referrer = request.referrer
  # if there's a referrer set it in the session otherwise set it to home route.
  if referrer:
    session['previous_page'] = referrer
  else:
    session['previous_page'] = 'https://syncandsound.onrender.com'
    # session['previous_page'] = 'http://localhost:5000/home' 
  
  if session['previous_page']:
    # if none of the selected routes are in the session['previous_page],
    # set session['previous_page'] to home route.
    if 'home' not in session['previous_page'] and 'local-release' not in session['previous_page'] and 'my-songs' not in session['previous_page']:
      session['previous_page'] = 'https://syncandsound.onrender.com'
      # session['previous_page'] = 'http://localhost:5000/home' 

  if CURR_USER_KEY in session:
    # if CURR_USER_KEY exist in the session, search the user in the db
    # and set that user as the global.user session.
    g.user = User.query.get(session[CURR_USER_KEY])

  else:
    # if not in the session set global user as none.
    g.user = None

def initialize_user_session(user): 
  """ 
    Adds the user to the session before going to the next route.
  """
  session[CURR_USER_KEY] = user.id
  g.user = user

def clear_sessions():
  """
  Clears all sessions
  """

  if CURR_USER_KEY in session:
    del session[CURR_USER_KEY]
  session.clear()
  g.user = None
   
def requires_auth(func):
  @wraps(func)
  def decorated_views(*args, **kwargs):
    if not g.user:
      flash('Please sign in!', "danger")
      return redirect(url_for('sign_in'))
    if 'access_token' not in session:
      # this connects to the Spotify API
      return redirect(url_for('connect_spotify'))
    if is_token_expire():
      return redirect(url_for('refresh_token'))
    return func(*args, **kwargs)
  return decorated_views

def get_spotify_playlist_tracks(playlist_name):
  """
  Gets tracks from a specified Spotify playlist.
  """
  headers = {'Authorization': f"Bearer {session['access_token']}"}
  params = {'q': playlist_name, 'type': 'playlist'}

  playlist_resp = requests.get(API_BASE_URL + 'search', params=params, headers=headers)
  if playlist_resp.status_code == 200:
    try:
      data = playlist_resp.json()
      for playlist in data.get('playlists', {}).get('items', []):
        # check if one of the playlists is equal to the playlist_name and is from Spotify.
        if playlist_name.lower() in playlist['name'].lower() and playlist['owner']['display_name'] == 'Spotify':
          playlist_id = playlist['id']
          playlist_params = {
            'fields': 'items(track(artists(name),name,id,uri))'
          }
          # make a request to get all the songs from the playlist_id.
          new_release_resp = requests.get(API_BASE_URL + f"playlists/{playlist_id}/tracks", params=playlist_params, headers=headers)
          break
      
      if new_release_resp.status_code == 200:
        try:
          tracks = new_release_resp.json()
          song_artist_uri_id_dict = {}
          # iterate each track
          for track in tracks['items']:
            # should check if the track is None or not
            if track['track'] is not None:
              song_name = track['track']['name']
              artists = [artist['name'] for artist in track['track']['artists']]
              uri = track['track']['uri']
              song_id = track['track']['id']
              # add song_name to the song_artist_uri_id_dict with values set, [], uri.
              if song_name not in song_artist_uri_id_dict:
                song_artist_uri_id_dict[song_name] = (set(), [], uri)
              # add artist to set, since it shows the same artist more than once.
              song_artist_uri_id_dict[song_name][0].update(artists)
              # adds song_id if not song_artist_uri_id_dict[song_name][1]
              if song_id not in song_artist_uri_id_dict[song_name][1]:
                song_artist_uri_id_dict[song_name][1].append(song_id)
          return song_artist_uri_id_dict
        except ValueError as e:
          print("Getting playlist tracks failed:", e)
          raise NotFound(description="Playlist not found")
      else:
        print("Error:", new_release_resp)
        raise NotFound(description="Playlist not found")
    except ValueError as e:
      print('Request failed to grab playlist name:', e)
      raise NotFound(description="Playlist not found")
  else:
    print("Error:", playlist_resp.status_code)
    raise NotFound(description="Playlist not found")

#################### signing in/up routes ####################
@app.route('/sign-up', methods=["GET", "POST"])
def sign_up():
  """Handle user signup
  Create new user and add to DB. Redirect to home page.

  If form not valid, present form.

  if there already is a user with that username : flash message and re-represent form
  """

  form = SignUpForm()

  if form.validate_on_submit():
    try:
      user = User.register(
        first_name = form.first_name.data,
        last_name = form.last_name.data,
        username = form.username.data,
        email = form.email.data,
        password = form.password.data
      )
      db.session.commit()


    except IntegrityError:
      flash("Username already taken!", "danger")
      return render_template('sign-up.html', form=form)
    
    # add user to global session
    initialize_user_session(user) # change to initialize_user_session

    return redirect(url_for('index'))
  
  else:
  
    return render_template('sign-up.html', form=form)   
       
@app.route('/sign-in', methods=["GET", "POST"])  
def sign_in():
  """Signs in user if credentials are valid."""

  form = SignInForm()

  if form.validate_on_submit():
    user = User.authenticate(
      form.username.data,
      form.password.data
    )

    if user:
      # change to initialize_user_session
      initialize_user_session(user)
      return redirect(url_for('home_page'))

    flash("Invalid credentials!", "danger")

  return render_template('sign-in.html', form=form)

#################### spofity api routes ####################
@app.route('/connect-spotify') 
def connect_spotify():
  """
  Connects to user's spotify account.
  """
  # scopes  user-read-private user-read-email playlist-read-private
  scope ='user-read-private'
  params = {
    'client_id': CLIENT_ID,
    'response_type': 'code',
    'scope': scope,
    'redirect_uri': REDIRECT_URI,
    'show_dialog': True
  }

  auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

  return redirect(auth_url)

@app.route('/callback')
def callback():
  """
  Grabs token and refresh token.
  """
  if 'error' in request.args:
    clear_sessions()
    return redirect(url_for("sign_in"))
  if 'code' in request.args:
    req_body = {
      'code': request.args['code'],
      'grant_type': 'authorization_code',
      'redirect_uri': REDIRECT_URI,
      'client_id': CLIENT_ID,
      'client_secret': CLIENT_SECRET
    }

    response = requests.post(TOKEN_URL, data=req_body)

    token_info = response.json()
    # updates session for each token
    session['access_token'] = token_info['access_token']
    session['refresh_token'] = token_info['refresh_token']
    session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
    # updates the tokens in the .env for testing purposes
    update_env_file('.env', {'TEST_ACCESS_TOKEN': session['access_token'], 'TEST_REFRESH_TOKEN': session['refresh_token'], 'TEST_EXPIRES_AT' : session['expires_at']})
    return redirect(session.get('previous_page', url_for('home_page')))
  
@app.route('/refresh_token')
def refresh_token():
  """
  Grabs a new token if the previous token is expired.
  """
  if 'refresh_token' not in session:
    return redirect(url_for('connect_spotify'))
  
  if datetime.now().timestamp() > session['expires_at']:
    req_body = {
      'grant_type': 'refresh_token',
      'refresh_token': session['refresh_token'],
      'client_id': CLIENT_ID,
      'client_secret': CLIENT_SECRET
    }

    response = requests.post(TOKEN_URL, data=req_body)
    new_token_info = response.json()

    # changes sessions for 'access_token' and 'expires_at' to new token and expiration time.
    session['access_token'] = new_token_info['access_token']
    session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']
    return redirect(url_for('home_page'))

#################### music routes ####################
@app.route('/')
@requires_auth
def index():
  """Redirect to home_page if sessions are still valid"""
  return redirect(url_for('home_page'))  

@app.route('/home')
@requires_auth
def home_page():
  """
  Shows new songs from  popular artists
  """  
  song_data = get_spotify_playlist_tracks('New Music Friday')
  user_songs = g.user.songs
  # shows songs that been saved by the user
  songs_uri = [song.song_uri for song in user_songs]
  return render_template('home.html', song_artist_uri_id_dict=song_data, songs_uri=songs_uri)

@app.route('/local-release')
@requires_auth
def get_local_release():
  """
  Shows new songs that are aligned to user's personal genre.
  """
  song_data = get_spotify_playlist_tracks('Release Radar')
  user_songs = g.user.songs
  # shows songs that been saved by the user
  songs_uri = [song.song_uri for song in user_songs]
  return render_template('local-release.html', song_artist_uri_id_dict=song_data, songs_uri=songs_uri)

@app.route('/logout')
def logout():
  """Logout user and clears all sessions"""
  clear_sessions()
  flash("Successfully logged out!", "success")
  return redirect(url_for('sign_in'))

#################### save/remove songs routes #################### 
@app.route('/my-songs')
@requires_auth
def show_user_like_songs():
  """
  Shows user's saved songs.
  """
  user = g.user
  songs = user.songs
  update_db(songs)
  db.session.commit()
  
  return render_template('users-songs.html', user=user)

@app.route('/save-song', methods=['POST'])
@requires_auth
def save_song():
  """
  Add song to user's liked songs
  """
  user = g.user
  artists = request.form['artist']
  # remove anything that is not letters
  artists = artists.strip("{}").replace("'","")
  song_uri = request.form['song_uri']
  song = Song.query.filter(Song.song_uri==song_uri).first()

  # check if songs is in db
  if song:
    user.songs.append(song)
    # if not added to db
  else:
    new_song = Song(
      name=request.form['song_name'],
      artist=artists,
      song_id=request.form['song_id'],
      song_uri=song_uri
    )
    # append song to user
    user.songs.append(new_song)

  db.session.commit()

  return redirect(session.get('previous_page', url_for('home_page')))

@app.route('/remove-song', methods=['POST'])
@requires_auth
def remove_song():
  """"
  Removes song from user's liked songs
  """
  # check if the song exists
  song = Song.query.filter(Song.song_uri==request.form['song_uri']).first()
  user_songs = g.user.songs
  # adds all songs except for the selected song to user's songs
  g.user.songs = [like for like in user_songs if like != song]

  db.session.commit()

  return redirect(session.get('previous_page', url_for('home_page')))

#################### user's profile route ####################
@app.route('/profile', methods=["GET", "PUT", "DELETE"])
@requires_auth

def profile():
  """
  Retrieve, update, or delete the user's data.

  - GET: Retrieve the user's data.
  - PUT: Update the user's data and return a 200 status code.
  - DELETE: Delete the user's data and return a 200 status code.

  A JavaScript file is responsible for redirecting to the designated routes for PUT and DELETE requests.
  """

  user = g.user
  if request.method == 'PUT':
    data = request.get_json()
    form = UserEditForm(data=data, obj=user)
    if form.validate():
      if User.authenticate(user.username, form.password.data):
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data

        db.session.commit()
        # returns a 'success=true' and the script.js is in charge of redirecting to profile route.
        return jsonify(success=True, message="Profile updated successfully"), 200
      else:
        return jsonify(success=False, message="Incorrect password"), 401
    else:
      errors = form.errors
      print("Validation errors:", errors)
      return jsonify(success=False, message="Validation failed"), 400

  elif request.method == 'DELETE':
    try:
      # Validate CSRF token
      csrf_token = request.headers.get('X-CSRFToken')

      # Please comment out 'validate_csrf' when running test
      validate_csrf(csrf_token)
    except ValidationError as e:
      return jsonify(success=False, message=str(e)), 400

    db.session.delete(user)
    db.session.commit()
    logout()
    flash("User Deleted!", "success")
    # returns a 'success=true' and the script.js is in charge of redirecting to sign-in route.
    return jsonify(success=True), 200

  form = UserEditForm(obj=user)

  return render_template('profile.html', form=form)

#################### Error handler route ####################
@app.errorhandler(404)
def handle_error(e):
  """
  Handle 404 errors by rendering the 404 error page.

  Any unknown route will be directed to this handler.
  """
  return render_template('404.html', e=e)


