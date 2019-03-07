# record-keeper
A discord bot to keep record of Pokemon Go medals, types, best raid times, pvp (win/lose, elo) and trade preferences  

- The !help page with all features:
```
---Command List---
TRADE BOARD
Add a pokmeon to the trade board
    !want <pokemon name>
    !want <pokemon name> note:<ExampleNote>
    !want <dex number> note:<ExampleNote>
Remove a pokemon from the trade board
    !unwant <pokemon name>
    !unwant <dex number>
List trade board for a pokemon
    !tbp <pokemon or dex number>
List a user's want list
    !tbu <gamertag>
Print a copyable version of the search string
    !tbs <gamertag>

PVP
These commands will log a win/loss for 
both you and your opponent
    to log a win
    !pvp <pvp league> L:<opponents gamertag>
    to log a loss
    !pvp <pvp league> W:<opponents gamertag>
    other commands
    see !ls and !lb below

LEADERBOARD
Update a given medal
    !up <medal_name> <value>
    !up <medal_name> <value> note:<ExampleNote>
List the medal stats for a spacific user
    !ls <medal_name>
    !ls <medal_name> <gamertag>
List the leaderboards for a given medal
    !lb <medal_name>
List the uuids for a given medal
    !uuid <medal_name>
Delete a entry from a table
    !del <medal_name> <uuid>

MEDAL NAMES
To get a list of medals
    !medals 
To get a list of raid bosses
    !raid
```

## Installing:
- To build the project your going to need to run this from the root directoy
    ```
    cp ./discord_bot/RecordKeeperBot.json.template to ./discord_bot/RecordKeeperBot.json
    ```
- Then trackdown the relevant information following information on the links
    * discord_token_api_token : https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token
    * discord_channel : the name of the channel you would like the bot to interact with
    * google_api_token : https://developers.google.com/sheets/api/guides/authorizing

- Once you have the json file configured you can build the project with:
    ```
    docker-compose build
    ```
    
- To start the bot run:
    ```
    docker-compose up -d
    ```
- To make changed and rebuild:
    ```
    docker-compose down  
    docker-compose build
    docker-compose up -d
    ```

- You can check that the bot is running with:
    ```
    docker-compose ps
    ```
Look for RecordKeeperBot.sh being in state up



