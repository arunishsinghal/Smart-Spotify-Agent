from langchain.agents import initialize_agent, AgentType, Tool
import os
from dotenv import load_dotenv
from langchain.schema import SystemMessage
from tools.playlist_manipulation import create_playlist,delete_playlist,toggle_playlist_privacy
from tools.get_songs import get_recommendations,recommendation_desc,get_spotify_song_id
from tools.modify_songs_in_playlist import add_songs_to_playlist,delete_songs_from_playlist
# from langchain_community.utilities import SerpAPIWrapper

load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY")
# search = SerpAPIWrapper()

def run_spotify_agent(llm):
    
    tools = [
        Tool(name="Create Playlist", func=create_playlist, description="Creates a playlist with specified name Input: 'name'"),
        Tool(name = "Delete playlist",func =delete_playlist, description = "Deletes a playlist with specified name Input: 'name'" ),
        Tool(name="Get Recommendations", func=get_recommendations, description=recommendation_desc),
        #Tool(name="Song Search",func=search.run,description="Use this to search for songs based on a query (like 'top 10 chill songs'). Returns song names."),
        Tool(name="Get song IDs",func=get_spotify_song_id,description="Returns the spotify Song IDs from the song names.Input: ['Song 1', 'Song2', 'Song3',]"),
        Tool(name = "Add songs to playlist",func=add_songs_to_playlist,description="Adds spotify Song IDs to playlist, Input: [SongID_1,SongID_2,...,'playlist_name']"),
        Tool(name = "Delete songs from playlist",func=delete_songs_from_playlist,description="Deletes spotify Song IDs from playlist, Input: [SongID_1,SongID_2,...,'playlist_name']"),
        Tool(name = "Toggle playlist privacy",func = toggle_playlist_privacy, description="Toggles the privacy setting of a playlist with a specified name. Input: 'name'"),
    ]

    system_message = SystemMessage(
        content=(
            "You are a helpful Spotify assistant. "
            "Always use the right tool based on the user query and the tool description "
            "If the request is incomplete, politely ask for the missing values. "
            "Return the result of the Action (Success/Failure)"
        )
    )


    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent_type=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        agent_kwargs={"system_message": system_message},
    )


    print("🤖 Agent ready! Type 'quit' to exit.\n")

    while True:
        query = input("You: ")
        if query.lower().strip() == "quit":
            print("Bot: Goodbye 👋")
            break

        try:
            response = agent.invoke({"input": query})   
            print("Bot:", response["output"])
        except Exception as e:
            print("Bot: (error handled)", str(e))
