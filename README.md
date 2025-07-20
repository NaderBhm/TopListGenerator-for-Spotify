<h1 align="center">
  <a href="https://5a2b6c95-1b4a-4f1c-9b24-1ceafa5dc2ad-00-2vvbioulhir05.spock.replit.dev" target="_blank" style="text-decoration: none; color: #1DB954;">
    🎵 Try the App !
  </a>
</h1>


# Spotify Top 50 Playlist Generator

Generate a personalized Spotify playlist with your top 50 most listened tracks for different time ranges — Last 4 Weeks, Last 6 Months, or All Time.

This Flask web app uses the Spotify Web API and Spotipy library to authenticate users, fetch their top tracks, and create or update private playlists on their Spotify account.

---

## Features

- OAuth2 login with Spotify for secure authentication.
- Select your preferred time range:  
  - Last 4 Weeks  
  - Last 6 Months  
  - All Time
- Fetch top 50 tracks for the selected time range.
- Create or update a private Spotify playlist with those tracks.
- View the playlist and track details in the app.
- Clear and informative error handling with user-friendly messages.
- Privacy-first approach: the app only accesses your Spotify data temporarily and never stores it.

---

## Prerequisites

- Python 3.7 or later
- Spotify Developer account and a created Spotify app

---

## Getting Started

### 1. Clone the repository

git clone https://github.com/NaderBhm/spotify-top50-generator.git
cd spotify-top50-generator

### 2. Create a Spotify app
* Go to the Spotify Developer Dashboard
* Create a new app

* Add your redirect URI (e.g., https://yourdomain.com/callback or your local dev URL)
This must exactly match the SPOTIPY_REDIRECT_URI environment variable.

### 3. Setup environment variables
Create a .env file or set these environment variables in your system:

SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=https://yourdomain.com/callback
SESSION_SECRET=random_secret_key_for_sessions
SESSION_SECRET can be any random string (for example, generated via openssl rand -hex 16).

### 4. Install dependencies
pip install -r requirements.txt
### 5. Run the app

python app.py
Open your browser and go to http://localhost:5000

## Usage
On the homepage, select your preferred time range.

You will be redirected to Spotify for login and permission authorization.

After login, the app will generate your top 50 playlist based on your listening history.

You can open the playlist directly on Spotify and share or edit it.

## Troubleshooting
Invalid Redirect URI error:
Make sure the redirect URI configured in your Spotify Developer Dashboard exactly matches the one in your app's environment variable SPOTIPY_REDIRECT_URI.

Insufficient client scope:
Ensure your Spotify app has these scopes enabled:

user-top-read

playlist-modify-private

playlist-modify-public

Environment variables not set:
The app will not work unless SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET are properly set.

## License
This project is licensed under the MIT License.

## Author
Made by NADER BEN HAJ MESSAOUD
GitHub: https://github.com/NaderBhm

## Privacy
This app only accesses your Spotify listening data temporarily to generate playlists. No user data is stored or shared with third parties.
