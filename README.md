**<h1>Simple Discord based Spotify playlist creator</h1>**

**<h3>Introduction</h3>**
This project is a Spotify playlist creator that generates playlists based on the Billboard Hot 100 and user input. It is triggered via a Discord bot command (e.g. '/spotify &lt;date&gt;'), and utilizes Azure Functions to process the request and create the playlist. The user receives a link to a 100-song Spotify playlist corresponding to the provided date.

**<h3>Features</h3>**
**Automatic Playlist Creation**: Generates a Spotify playlist based on the Billboard Hot 100 for a given date. <br>
**Discord Bot Integration**: Users can trigger playlist creation through a Discord bot command. <br>
**Azure Functions**: Leverages Azure Functions for backend processing.

**<h3>Technologies Used</h3>**
**Python**: For scripting and backend logic.<br>
**Azure Functions**: For handling HTTP requests and serverless execution of the playlist creation process.

**<h3>Installation and Setup</h3>**

**Azure Functions Setup</h3>**: Follow Azure's documentation to set up an Azure Function App with HTTP trigger. <br>
https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python?pivots=python-mode-decorators

**<h3>Bot Setup</h3>** 
Configure your Discord bot in the Discord Developer Portal, add application command(s) to it using an IDE of your choice and finally, connect it to your Azure Functions app endpoint url.
https://discord.com/developers/docs/getting-started

**<h3>Spotify Developer Setup</h3>**
Create an App in the Spotify for Developers Dashboard for a unique client ID & client secret, and to set up a custom redirect URI
https://developer.spotify.com/

**<h3>Dependencies</h3>** 
Set up the necessary environment variables in Azure

**<h2>Usage</h2>**

**<h3>Playlist Creation</h3>**
Use the Discord bot command '/spotify &lt;date&gt;' (in DD.MM.YYYY format) to initiate the playlist creation.
![First step: initiate the playlist creation using the '/spotify &lt;date&gt;' command](https://i.imgur.com/pBzQAQL.png)
![Wait for the process to complete in just a bit](https://i.imgur.com/gbMgcWL.png)

**<h3>Receiving the Playlist</h3>**
A link to the Spotify playlist will be returned to the user, which can be opened, listened to, and saved in Spotify. <br>
![Second step: A fully functional Spotify playlist link will be returned to the user in the discord chat window](https://i.imgur.com/mTdHuIe.png) <br>
![The newly created playlist works just like any one other in Spotify and can be saved for later for instance](https://i.imgur.com/GcSfkua.png)
