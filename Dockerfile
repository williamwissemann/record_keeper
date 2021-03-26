FROM foundation:artifact as art_box 

FROM ubuntu:20.04 as test_box
ARG DOCKER_ENTRYPOINT
ENV DOCKER_ENTRYPOINT ${DOCKER_ENTRYPOINT}
ENTRYPOINT echo ${DOCKER_ENTRYPOINT}

## builds a base image for future steps to use
FROM ubuntu:20.04 as base
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y -q \   
    && apt-get upgrade -y -q \
    && apt-get install -y -q \
        python3.8 \
        python3-venv \
    && apt-get clean \
    && apt autoremove -y \
    && rm -rf /var/lib/apt/lists/* 

## creates an venv to build the distribution pacakge
FROM base as dist_box
ENV DEBIAN_FRONTEND=noninteractive
ENV APPDIR /foundation/pkgs/pkg
WORKDIR ${APPDIR}
COPY --from=art_box /artifacts /foundation/artifacts
COPY . ${APPDIR}
RUN apt-get update -y -q \
    && apt-get install -y -q \
        python3-pip \
        git
RUN make python/install-dev python/dist

## build a the vinal venv we are going too use
FROM dist_box as venv_box
WORKDIR /foundation/pkgs/pkg
RUN make python/clean
RUN make python/install-package

## build a final image with just the bare minimum
FROM base as final
ARG DOCKER_ENTRYPOINT
ENV DOCKER_ENTRYPOINT ${DOCKER_ENTRYPOINT}
ARG DOCKER_WORKDIR

ENV PATH="${DOCKER_WORKDIR}/venv/bin:$PATH"

WORKDIR ${DOCKER_WORKDIR}

COPY --from=venv_box /foundation/pkgs/pkg/venv ${DOCKER_WORKDIR}/venv
COPY --from=dist_box /foundation/pkgs/pkg/dist ${DOCKER_WORKDIR}/dist

RUN useradd -ms /bin/bash basic \
    && chown -R basic:basic ${DOCKER_WORKDIR}
USER basic
RUN . venv/bin/activate; python3 -m pip install dist/* \
    && rm -rf dist

ENTRYPOINT python3 ${DOCKER_ENTRYPOINT}
