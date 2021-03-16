# --- BASE IMAGE ---------------------------------------

FROM ubuntu:20.04 as base
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y -q \   
    && apt-get upgrade -y -q \
    && apt-get install -y -q \
        python3.8 \
        python3-venv \
    && apt-get clean \
    && apt autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /root/.cache/pip/

# --- stage the venv --------------------
FROM base as stage
ENV DEBIAN_FRONTEND=noninteractive
ENV APPDIR /app
WORKDIR ${APPDIR}
COPY . ${APPDIR}

RUN apt-get update -y -q \   
    && apt-get upgrade -y -q \
    && apt-get install -y -q \
        python3.8 \
        python3-pip \
        python3-venv \
        git \
    && make install-dev dist \
    && make clean install

# --- build a image with bare minimum --------------------
FROM base as final
ENV APPDIR /app
WORKDIR ${APPDIR}

ENV PATH="/app/venv/bin:$PATH"

COPY --from=stage ${APPDIR}/venv ${APPDIR}/venv
COPY --from=stage ${APPDIR}/dist ${APPDIR}/dist

RUN . venv/bin/activate; pip install dist/* \
    && rm -rf ${APPDIR}/dist

ENTRYPOINT [ "python3",  "/app/venv/lib/python3.8/site-packages/record_keeper/app.py"]
