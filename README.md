# Spotify AI Agent

A conversational AI agent that controls your Spotify account using natural language. Built with LangChain, Google Gemini, and the Spotify Web API.

---

## Features

- Create and delete playlists
- Add and remove songs from playlists
- Get song recommendations
- Toggle playlist privacy (public/private)
- OAuth 2.0 authentication with automatic token refresh

---

## Project Structure

```
project-root/
├── main.py                  # Entry point
├── .env                     # Environment variables (not committed)
├── user_id                  # Cached Spotify user ID (auto-generated)
└── src/
    ├── __init__.py
    ├── main.py
    ├── agent.py             # LangChain agent setup and conversation loop
    ├── auth.py              # Spotify OAuth 2.0 flow
    └── utils.py             # LLM initialization
└── tools/
    ├── playlist_manipulation.py   # create, delete, toggle privacy
    ├── get_songs.py               # recommendations, song ID lookup
    └── modify_songs_in_playlist.py # add/remove songs
```

---

## Prerequisites

- Python 3.9+
- A [Spotify Developer App](https://developer.spotify.com/dashboard) with:
  - Redirect URI set to `http://127.0.0.1:8888/callback/`
  - The following scopes enabled:
    - `playlist-modify-private`
    - `playlist-modify-public`
    - `playlist-read-collaborative`
    - `playlist-read-private`
- A [Google AI Studio](https://aistudio.google.com/) API key for Gemini

---

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <your-repo-name>
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
client_id=your_spotify_client_id
client_secret=your_spotify_client_secret
GOOGLE_API_KEY=your_google_api_key
```

> **Note:** `refresh_token` will be appended automatically after first login. Do not set it manually.

### 4. Run the agent

```bash
python main.py
```

On first run, a browser window will open for Spotify login. After authorizing, the refresh token is saved to `.env` automatically — subsequent runs skip the login step.

---

## Usage

Once running, type natural language commands at the prompt:

```
You: Create a playlist called "Morning Vibes"
You: Add 5 chill lo-fi songs to Morning Vibes
You: Make Morning Vibes private
You: Delete the playlist called Morning Vibes
You: quit
```

Type `quit` to exit.

---

## Authentication Flow

1. **First run:** Opens browser → user logs into Spotify → authorization code captured via local HTTP server → exchanged for access + refresh tokens → refresh token saved to `.env`.
2. **Subsequent runs:** Refresh token is read from `.env` → new access token fetched directly, no browser required.

---

## Environment Variables Reference

| Variable         | Required | Description                             |
| ---------------- | -------- | --------------------------------------- |
| `client_id`      | Yes      | Spotify app client ID                   |
| `client_secret`  | Yes      | Spotify app client secret               |
| `GOOGLE_API_KEY` | Yes      | Google Gemini API key                   |
| `refresh_token`  | Auto     | Written automatically after first login |

---

## Known Limitations

- The agent uses `CHAT_CONVERSATIONAL_REACT_DESCRIPTION` — complex multi-step tasks may occasionally misfire tool selection. Retry with a more explicit prompt if a tool is called incorrectly.
- Token refresh does not handle expiry mid-session. If a long session returns 401 errors, restart the agent.
- `user_id` is written to a plain file in the project root, not to `.env`. Ensure this file is in `.gitignore`.

---

## .gitignore Recommendations

```
.env
user_id
__pycache__/
*.pyc
```

---

## License

MIT
