import azure.functions as func
import json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
import logging
import requests
from .spotify_playlist_creator import SpotifyPlaylistCreator
import threading
import os

# Environment variables for the Discord bot token and public key
BOT_TOKEN = os.getenv("BOT_TOKEN")
DISCORD_PUBLIC_KEY = os.getenv("DISCORD_PUBLIC_KEY")
APPLICATION_ID = os.getenv("APPLICATION_ID")

def sync_patch(url, json_data, headers):
    """
    Send a synchronous PATCH request to a given URL with JSON data.

    Args:
        url (str): The URL to which the request is sent.
        json_data (dict): JSON data to be sent in the request.
        headers (dict): Headers to include in the request.

    Returns:
        str: Response text from the server.
    """
    response = requests.patch(url, json=json_data, headers=headers)
    return response.text
        
def async_task(interaction_token, date):
    """
    Perform a long running asynchronous task to create a Spotify playlist for a given date.

    Args:
        interaction_token (str): Interaction token for Discord.
        date (str): Date for which the playlist is created.

    Returns:
        None
    """
    
    logging.info("Running async task")
    creator = SpotifyPlaylistCreator()
    
    try:
        creator.get_data(date)
        creator.spotipy_auth()
        
        playlist_link = creator.add_songs()
        logging.info(f"Playlist link: {playlist_link}")
    except Exception as e:
        logging.error(f"An error occurred during the async task: {e}", exc_info=True)
        return
    
    # If everything is successful, send a follow up message with the result
    followup_url = f"https://discord.com/api/v10/webhooks/{APPLICATION_ID}/{interaction_token}/messages/@original"
    followup_message = {
        "content": f"Playlist created for the date: {date}. Here is the link: {playlist_link}"
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bot {BOT_TOKEN}'
    }
    response = sync_patch(followup_url, followup_message, headers)



def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Main function to handle HTTP requests and Discord commands.

    Args:
        req (func.HttpRequest): The incoming HTTP request.

    Returns:
        func.HttpResponse: Response object to be sent back.
    """

    try:
        body = req.get_body().decode()
        json_body = json.loads(body)
    except ValueError:
        return func.HttpResponse("Invalid JSON", status_code=400)

    signature = req.headers.get('X-Signature-Ed25519')
    timestamp = req.headers.get('X-Signature-Timestamp')

    if not (signature and timestamp):
        return func.HttpResponse("Bad request", status_code=400)

    try:
        public_key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(DISCORD_PUBLIC_KEY))
        public_key.verify(bytes.fromhex(signature), (timestamp + body).encode())
    except (ValueError, InvalidSignature):
        return func.HttpResponse("Invalid signature", status_code=401)

    if json_body.get('type') == 1:
        return func.HttpResponse(json.dumps({'type': 1}), status_code=200, mimetype='application/json')

    if json_body.get('type') == 2:
        data = json_body.get('data', {})
        command_name = data.get('name')
        options = {option["name"]: option["value"] for option in data.get('options', [])}   

        if command_name == 'spotify':
            logging.info("Received spotify command")
            date = options.get('date')
            interaction_token = json_body.get('token')
            
            # Perform the playlist task asynchronously
            thread = threading.Thread(target=async_task, args=(interaction_token, date))
            thread.start()
            
            # Acknowledge the command
            return func.HttpResponse(json.dumps({'type': 5}), status_code=200, mimetype='application/json')
           
    else:
        return func.HttpResponse("Invalid type", status_code=400)
