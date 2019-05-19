# --- BASE IMAGE ---------------------------------------------------------------

FROM ubuntu:18.04

# --- configure default environment --------------------------------------------

ENV DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true

# --- configure dependencies --------------------------------------------

RUN set -ex \
    && apt-get update -y -q \   
    && apt-get upgrade -y -q \
    && apt-get install python3-pip -y -q \
    && apt-get install cron \
    # discord.py
    && pip3 install discord.py==1.* \
    # google api
    && pip3 install --upgrade google-api-python-client \
    && pip3 install --upgrade oauth2client 

# --- copy over files ----------------------------------------------------------

COPY discord_bot /usr/src/RecordKeeperBot/discord_bot
WORKDIR /usr/src/RecordKeeperBot/discord_bot

# --- run script ---------------------------------------------------------------
ENTRYPOINT ["./RecordKeeperBot.sh"]


