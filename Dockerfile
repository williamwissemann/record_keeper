## creates an venv to build the distribution package
FROM foundation:venv as dist
ENV APPDIR /foundation/pkgs/python/pkg
WORKDIR ${APPDIR}
RUN cp -r /foundation/packages/python/backhoe/venv ${APPDIR}/venv
COPY . ${APPDIR}
RUN make python/install-dev python/dist

## build a venv we are going to use in the final image
FROM dist as venv
RUN make python/clean python/install-package

## build a final image with just the bare minimum
FROM foundation:python as final
ARG DOCKER_ENTRYPOINT
ENV DOCKER_ENTRYPOINT ${DOCKER_ENTRYPOINT}
ARG DOCKER_WORKDIR

ENV PATH="${DOCKER_WORKDIR}/venv/bin:$PATH"

WORKDIR ${DOCKER_WORKDIR}

COPY --from=venv /foundation/pkgs/python/pkg/venv ${DOCKER_WORKDIR}/venv
COPY --from=dist /foundation/pkgs/python/pkg/dist ${DOCKER_WORKDIR}/dist

COPY ./database/ /app/database/
COPY ./config/ /app/config/

RUN useradd -ms /bin/bash basic \
    && chown -R basic:basic ${DOCKER_WORKDIR}
USER basic
RUN . venv/bin/activate; python3 -m pip install dist/* \
    && rm -rf dist

ENTRYPOINT python3 ${DOCKER_ENTRYPOINT}

FROM final as debugpy
USER root
RUN . venv/bin/activate; python3 -m pip install debugpy
ENTRYPOINT . venv/bin/activate; python3 -m debugpy --listen 0.0.0.0:5678 --wait-for-client ${DOCKER_ENTRYPOINT}