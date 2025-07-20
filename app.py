import os
import logging
from flask import Flask, render_template, request, redirect, url_for, session, flash
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Spotify API configuration
SPOTIPY_CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.environ.get("SPOTIPY_REDIRECT_URI", "https://5a2b6c95-1b4a-4f1c-9b24-1ceafa5dc2ad-00-2vvbioulhir05.spock.replit.dev/callback")

# Spotify OAuth scopes
SCOPE = "user-top-read playlist-modify-private playlist-modify-public"

def get_spotify_oauth():
    """Create SpotifyOAuth instance"""
    return SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SCOPE
    )

def get_time_range_display(time_range):
    """Convert time range parameter to display text"""
    time_range_map = {
        'short_term': 'Last 4 Weeks',
        'medium_term': 'Last 6 Months',
        'long_term': 'All Time'
    }
    return time_range_map.get(time_range, 'Unknown')

@app.route('/')
def index():
    """Landing page with time range selection"""
    return render_template('index.html')

@app.route('/login')
def login():
    """Initiate Spotify OAuth login"""
    time_range = request.args.get('time_range')
    if not time_range or time_range not in ['short_term', 'medium_term', 'long_term']:
        flash('Invalid time range selected', 'error')
        return redirect(url_for('index'))
    
    # Store time range in session
    session['time_range'] = time_range
    
    # Check if required environment variables are set
    if not SPOTIPY_CLIENT_ID or not SPOTIPY_CLIENT_SECRET:
        flash('Spotify API credentials not configured. Please check environment variables.', 'error')
        return render_template('error.html', 
                             error_message='Spotify API credentials not configured',
                             error_details='SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables must be set.')
    
    try:
        sp_oauth = get_spotify_oauth()
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    except Exception as e:
        logging.error(f"Error during OAuth setup: {str(e)}")
        flash('Error setting up Spotify authentication', 'error')
        return render_template('error.html', 
                             error_message='Authentication Error',
                             error_details=f'Failed to initiate Spotify login: {str(e)}')

@app.route('/callback')
def callback():
    """Handle Spotify OAuth callback"""
    try:
        sp_oauth = get_spotify_oauth()
        code = request.args.get('code')
        error = request.args.get('error')
        
        if error:
            flash(f'Spotify authorization error: {error}', 'error')
            return redirect(url_for('index'))
        
        if not code:
            flash('No authorization code received from Spotify', 'error')
            return redirect(url_for('index'))
        
        # Get access token
        token_info = sp_oauth.get_access_token(code)
        if not token_info:
            flash('Failed to get access token from Spotify', 'error')
            return redirect(url_for('index'))
        
        # Create Spotify client
        sp = spotipy.Spotify(auth=token_info['access_token'])
        
        # Get time range from session
        time_range = session.get('time_range', 'medium_term')
        
        # Get user info
        user_info = sp.current_user()
        user_id = user_info['id']
        display_name = user_info.get('display_name', user_id)
        
        # Get top tracks
        logging.info(f"Fetching top tracks for time range: {time_range}")
        top_tracks = sp.current_user_top_tracks(limit=50, time_range=time_range)
        
        if not top_tracks['items']:
            flash('No top tracks found for the selected time period', 'warning')
            return render_template('error.html', 
                                 error_message='No Data Available',
                                 error_details='No top tracks found for the selected time period. Try listening to more music on Spotify!')
        
        # Create playlist name
        time_display = get_time_range_display(time_range)
        playlist_name = f"Top 50 - {time_display}"
        
        # Check if playlist already exists
        playlists = sp.current_user_playlists(limit=50)
        existing_playlist = None
        
        for playlist in playlists['items']:
            if playlist['name'] == playlist_name and playlist['owner']['id'] == user_id:
                existing_playlist = playlist
                break
        
        # Create or update playlist
        if existing_playlist:
            playlist_id = existing_playlist['id']
            # Clear existing tracks
            sp.playlist_replace_items(playlist_id, [])
            logging.info(f"Updated existing playlist: {playlist_name}")
        else:
            # Create new playlist
            new_playlist = sp.user_playlist_create(
                user_id, 
                playlist_name, 
                public=False,
                description=f"Your top 50 tracks from {time_display.lower()} - Generated by Top 50 Playlist Generator"
            )
            playlist_id = new_playlist['id']
            logging.info(f"Created new playlist: {playlist_name}")
        
        # Add tracks to playlist
        track_uris = [track['uri'] for track in top_tracks['items']]
        sp.playlist_add_items(playlist_id, track_uris)
        
        # Get playlist info for confirmation
        playlist_info = sp.playlist(playlist_id)
        playlist_url = playlist_info['external_urls']['spotify']
        
        # Prepare track list for display
        tracks_display = []
        for track in top_tracks['items']:
            artists = ', '.join([artist['name'] for artist in track['artists']])
            tracks_display.append({
                'name': track['name'],
                'artists': artists,
                'album': track['album']['name'],
                'external_url': track['external_urls']['spotify']
            })
        
        return render_template('confirmation.html',
                             playlist_name=playlist_name,
                             playlist_url=playlist_url,
                             tracks=tracks_display,
                             time_display=time_display,
                             user_name=display_name,
                             track_count=len(tracks_display))
        
    except spotipy.exceptions.SpotifyException as e:
        logging.error(f"Spotify API error: {str(e)}")
        error_msg = f"Spotify API Error: {str(e)}"
        if "insufficient client scope" in str(e).lower():
            error_msg = "Insufficient permissions. Please make sure the app has the required scopes."
        return render_template('error.html', 
                             error_message='Spotify API Error',
                             error_details=error_msg)
    
    except Exception as e:
        logging.error(f"Unexpected error in callback: {str(e)}")
        return render_template('error.html', 
                             error_message='Unexpected Error',
                             error_details=f'An unexpected error occurred: {str(e)}')

@app.route('/privacy')
def privacy():
    """Privacy policy page"""
    return render_template('error.html', 
                         error_message='Privacy Policy',
                         error_details='This app only accesses your Spotify listening data to generate playlists. No data is stored or shared with third parties.')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
