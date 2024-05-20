# discord-message-logger-bot

### Description

This bot is designed to keep a complete log of selected chats. It saves all messages and attachments

Its features:
- Saving the entire message history when adding a channel.
- Background saving of sent messages. 
- Addition of history in case of bot disconnection.

#### Prerequisites
- Python 3.8+ installed on your system.
- Discord.py library installed.
- SQLAlchemy library installed.
- Aiohttp library insalled
- Configobj libraary installed
  
### Quick Setup
1. Clone this repository.
2. Create a new app on the Discord developer portal.
3. Set up bot permissions on the Discord Developer Portal.
4. Create a key.txt file and paste your Discord bot token inside it.
5. *Not required, but recommended.* Set the GUILD_ID of your server in config.ini.
6. Run the bot script:
   ##### python main.py
7. Invite the bot to your Discord server using the OAuth2 URL generated from the Discord Developer Portal.

### Commands
Add a channel to tracking:
#### //?add @CHANNEL

Remove a channel from tracking:
#### //?del @CHANNEL

Set the limit of message history that the bot will read to update all modified messages after the bot is loaded.
Default = 100
#### //?cfgsetlim NUMBER

Set the personal status of the bot:
#### //?cfgsetstatus STATUS
