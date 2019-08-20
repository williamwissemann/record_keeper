# Record-Keeper
A discord bot to keep track of Pokemon Go medals, types, best raid times, pvp (win/lose, elo) and trade preferences etc.

## Installing:
- To build the project your going to need to run this from the root directoy
    ```
    cp ./discord_bot/RecordKeeperBot.json.template to ./discord_bot/RecordKeeperBot.json
    ```
- Then trackdown the relevant information following information on the links
    * discord_token_api_token : https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token
    * google_api_token (optional) : https://developers.google.com/sheets/api/guides/authorizing

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

- ADVANCED: docker run
    ```    
    docker run \
    -v <record-keeper-path>/Database/:/usr/src/RecordKeeperBot/database/ \
    -v <record-keeper-path>/discord_bot:/usr/src/RecordKeeperBot/discord_bot/ \
    -it <image_id> bash
    ```

## SETUP:
Once inviting the the bot to a discord, the server admin needs to activaite a listiner to get the commands to work. Instructions can be found via !setup

- The !setup page with all features:
```
Setup
run these commands in channels you would like to modify
Add a listener to channel
    !activate <listener>
Remove a listener from a channel
    !deactivate  <listener>
View all listener for a channel
    !active
available listeners
 - help: activiates !help
 - training-wheels: activiates error messages on bad commands
 - record-keeper: a record keeper for medals
 - trade-keeper: a trading want manager
 - friend-keeper: an ultra friends for pvp
 - battle-keeper: an elo based leaderbaord
 - iv-ranker: a pokemon rater
 - message-cleanup: cleans up bot messages on a timer
 - deletable-data: activiates commands for delete bad entries
 - dice: activiates !roll <sides>
---------------------------------------------
```

## HELP:

- The !help page with all commands:

```
COMMAND LIST
DM the bot !help for a completed list of supported commands
---------------------------------------------
RECORD KEEPER
    Update a given medal
        !up <medal> <value>
        !up <medal> <value> note:<ExampleNote>
        WARNING: a note can't contain spaces
    List the medal stats for a spacific user
        !ls <medal>
        !ls <medal> <discord_id>
    List the leaderboards for a given medal
        !lb <medal>
---------------------------------------------
DELETING
    Delete entry via UUID
        !del <medal> <uuid>
    List the uuids for a given medal
        !uuid <medal>
    NOTE: Only entries made in the last 30 minutes can be deleted
---------------------------------------------
FRIEND-KEEPER
    Add a friend
        !add-friend <discord_id>
        !auf <discord_id>
    Remove a friend
        !remove-friend <discord_id>
        !ruf <discord_id>
    List friends
        !friends
    Notify friends
        !ping-friends <message>
        !ltb <message>
    toggle status
        !online
        !offline
---------------------------------------------
BATTLE-KEEPER
    These commands will log a win/loss for 
    both you and your opponent
    To log a loss
        !pvp <league> L:<discord_id>
    To log a win
        !pvp <league> W:<discord_id>
    To log a tie
        !pvp <league> T:<discord_id>
        other commands
    List the battle logs
        !ls <league>
        !ls <league> <discord_id>
    List the elo leaderboard for a league
        !lb <league>
---------------------------------------------
TRADE-BOARD
    Add a pokmeon to the trade board
        !want <pokemon>
        !want <pokemon> note:<ExampleNote>
        !want <dex number> note:<ExampleNote>
    Remove a pokemon from the trade board
        !unwant <pokemon>
        !unwant <dex#>
    List trade board for a pokemon
        !tbp <pokemon or dex number>
    List a user's wants
        !tbu <discord_id>
    Print a copyable version of a users search string
        !tbs <discord_id>
---------------------------------------------
IV-RANKER
    Rank a pokemon for great league
        !rankgreat <pokemon> <ATK> <DEF> <HP> <filter>
        !rankg <dex#> <ATK> <DEF> <HP> <filter>
    Rank a pokemon for great ultra
        !rankultra <pokemon> <ATK> <DEF> <HP> <filter>
        !ranku <dex#> <ATK> <DEF> <HP> <filter>
    Rank a pokemon for great master
        !rankmaster <pokemon> <ATK> <DEF> <HP> <filter>
        !rankm <dex#> <ATK> <DEF> <HP> <filter>
    FILTERS: wild (default), wb (weather boosted),
        best (best-friends), raid, lucky 
---------------------------------------------
```




