import webbrowser
import urllib.parse
from dotenv import load_dotenv
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import requests
import base64

load_dotenv()
client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
redirect_uri = "http://127.0.0.1:8888/callback/"
scopes = "playlist-modify-private playlist-modify-public playlist-read-collaborative playlist-read-private"
access_token = None


def get_auth_code():
    """
    Initiates the Spotify OAuth 2.0 authorization flow.

    Opens a browser window for the user to log in and authorize the app.
    Starts a local HTTP server to capture the authorization code from the redirect.
    Returns:
        str: The authorization code if successful, otherwise None.
    """
    auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode({
    "client_id": client_id,
    "response_type": "code",
    "redirect_uri": redirect_uri,
    "scope": scopes
    })
    class CallbackHandler(BaseHTTPRequestHandler):
        auth_code = None
        def do_GET(self):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            if "code" in params:
                CallbackHandler.auth_code = params["code"][0]
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"You can close this window now.")
            else:
                self.send_response(400)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"Missing authorization code.")

    server = HTTPServer(("127.0.0.1", 8888), CallbackHandler)
    print("Waiting for Spotify redirect...")
    webbrowser.open(auth_url)
    print("Go to the URL above and log in.")
    try:
        server.handle_request()
    except Exception as e:
        print("Error while waiting for redirect:", e)
    finally:
        server.server_close()

    if CallbackHandler.auth_code is None:
        print("Authorization failed or was canceled.")
    print(CallbackHandler.auth_code)
    return CallbackHandler.auth_code

def get_tokens(auth_code):
    """
    Exchanges the authorization code for access and refresh tokens.

    Args:
        auth_code (str): The authorization code obtained from Spotify.

    Returns:
        dict: A dictionary containing access_token, refresh_token, and other token info.
    """
    # validate credentials
    if not client_id or not client_secret:
        raise EnvironmentError("client_id or client_secret not set in environment (.env)")

    cid = client_id.strip()
    csecret = client_secret.strip()

    url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{cid}:{csecret}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": redirect_uri
    }

    r = requests.post(url, headers=headers, data=data, timeout=10)
    if r.status_code != 200:
        # surface body for debugging (invalid_client, invalid_grant, redirect_uri_mismatch, etc.)
        raise RuntimeError(f"Token request failed ({r.status_code}): {r.text}")
    return r.json()

def refresh_access_token(refresh_token):
    """
    Refreshes the Spotify access token using a refresh token.

    Args:
        refresh_token (str): The refresh token obtained from Spotify.

    Returns:
        str: The new access token.
    """
    url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {"Authorization": f"Basic {auth_header}"}
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    r = requests.post(url, headers=headers, data=data)
    r.raise_for_status()
    return r.json()['access_token']

def write_refresh_token_to_env(refresh_token):
    """
    Writes the refresh token to the .env file.
    """
    env_path = ".env"
    with open(env_path, "a") as env_file:
        env_file.write(f"\nrefresh_token={refresh_token}\n")

def main_auth():
    global access_token
    refresh_token = os.getenv("refresh_token")
    if refresh_token:
        access_token = refresh_access_token(refresh_token)
        print("Welcome! Access token refreshed!")
    else:
        print("No refresh token found. Starting authentication flow...")
        auth_code = get_auth_code()
        if auth_code:
            tokens = get_tokens(auth_code)
            access_token = tokens.get("access_token")
            refresh_token= tokens.get("refresh_token")
            if refresh_token:
                write_refresh_token_to_env(refresh_token)
                access_token = refresh_access_token(refresh_token)


        else:
            print("Authentication failed.")
    
    headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
    }
    
    r = requests.get("https://api.spotify.com/v1/me", headers=headers)
    r.raise_for_status()
    user_id = r.json()["id"]

    with open("user_id", "w") as f:
        f.write(user_id)

    return(access_token)

def retrieve_access_token():
    return(access_token)
