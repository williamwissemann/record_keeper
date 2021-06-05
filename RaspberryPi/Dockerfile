FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

ENV APPDIR /app
WORKDIR ${APPDIR}

COPY dist/ ${APPDIR}/dist

RUN apt-get update -y -q \
    && apt-get upgrade -y -q \
    && apt-get install -y -q \
        python3.9 \
        python3-dev \
        python3-venv \
        libffi-dev \
        rustc \
    && python3.9 -m venv venv \
    && . venv/bin/activate; python -m pip install pip --upgrade \
    && . venv/bin/activate; pip install dist/* \
    && rm -rf ${APPDIR}/dist

ENV PATH="/app/venv/bin:$PATH"

ENTRYPOINT [ "python3",  "/app/venv/lib/python3.9/site-packages/record_keeper"]

