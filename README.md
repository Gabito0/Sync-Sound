# Sync & Sound

### Sync & Sound is an application that makes discovering new music more accessible, whether it features iconic artists or your favorite artists.

### If you're planning to use the website, please reach out to me to authorize your Spotify account. This is due to Spotify's API restrictions, which require manual approval of users to access the API until my application has been approved for an extended quota, allowing anyone to access my website without authorization.

[Link to website](https://syncandsound.onrender.com)

## Tech Stack

- PostgreSQL
- Flask
- Python
- JavaScript

## Setup and Dependencies

To run the project locally on your computer, please follow these steps:

1. Clone the repository to your computer by typing `git clone https://github.com/Gabito0/Sync-and-Sound.git`.

2. Create an account for [Spotify's API](https://developer.spotify.com/).

   1. Go to the [Dashboard](https://developer.spotify.com/dashboard).
   2. Click on [Create App](https://developer.spotify.com/dashboard/create).
   3. In the `Redirect URIs`, copy and paste `http://localhost:5000/callback`.
   4. After creating the app, go into your app settings and copy your client ID and client secret.

3. Add environment variables to your `.env` file.

```
CLIENT_ID='YOUR CLIENT ID'
CLIENT_SECRET='YOUR CLIENT SECRET'
SECRET_KEY='YOUR SECRET KEY'
```

4. Navigate to the project folder `Sync-and-Sound` and create a virtual environment.

```
cd Sync-and-Sound
python3 -m venv [NAME OF VIRTUAL ENVIRONMENT]
```

5. Enter the virtual environment and install the dependencies from `requirements.txt` using `pip`.

```
source venv/bin/activate
pip install -r requirements.txt
```

6. Make sure to comment out all `session['previous_page'] = 'https://syncandsound.onrender.com'` in the `update_session` function when running the app locally.

```
# session['previous_page'] = 'https://syncandsound.onrender.com'
session['previous_page'] = 'http://localhost:5000/home'
```

7. Once all dependencies have been installed, run the following command to start the application.

```
flask run
```

## Features

1. The "Home" page shows new songs from popular artists. This allows users to find new songs from iconic artists first.
   ![alt text](/imgs/home_page.png)
2. The "Local release" page shows new songs from the user's personal artists or genre. This helps users discover more music that fits their style.
   ![alt text](/imgs/local_release.png)
3. Users can save songs and go to the "My Songs" page to listen to all their saved songs.

- Saving song
  ![alt text](/imgs/saving_song.png)

- My songs page
  ![alt text](/imgs/my_songs.png)

4. Users can stream music from the website using Spotify's iframes by clicking on the song's name.
   ![alt text](/imgs/song_playing.png)

## User Flow

1. Users can create an account or sign in and then navigate to the home page, local release page, my songs page, or profile page.

## Testing

1. Logout, then login, and click accept for Spotify to access your account before testing. The reason for this is to refresh the tokens that are stored in the `.env` file for testing.

2. Make sure to comment out all `session['previous_page'] = 'https://syncandsound.onrender.com'` in the `update_session` function when running the app locally.

```
# session['previous_page'] = 'https://syncandsound.onrender.com'
session['previous_page'] = 'http://localhost:5000/home'
```

3. Comment out `validate_csrf(csrf_token)` in the `profile DELETE route`.

4. Now the application is ready for testing.
