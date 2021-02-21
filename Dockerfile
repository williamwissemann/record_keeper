# --- BASE IMAGE ---------------------------------------------------------------

FROM ubuntu:20.04

# --- configure default environment --------------------------------------------

ENV APPDIR /usr/src/RecordKeeperBot/discord_bot
ENV DEBIAN_FRONTEND=noninteractive

# --- configure dependencies --------------------------------------------

RUN set -ex \
    && apt-get update -y -q \   
    && apt-get upgrade -y -q \
    && apt-get install -y -q \
        python3.8 python3.8-dev python3-pip \
        cron \
    # discord.py
    && pip3 install discord.py==1.* \
    # google api
    && pip3 install --upgrade \
        google-api-python-client \ 
        oauth2client \
    # cleanup
    && apt-get clean \
    && apt autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /root/.cache/pip/

# --- copy over files ----------------------------------------------------------

WORKDIR ${APPDIR}
COPY src ${APPDIR}

# --- run script ---------------------------------------------------------------
ENTRYPOINT ["./RecordKeeperBot.sh"]
