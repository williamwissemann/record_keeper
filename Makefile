# path to the foundation/artifacts/makefile/modules
# https://github.com/williamwissemann/foundation

# include Makefile artifacts from foundation
ARTIFACTS ?= ../../../artifacts
MAKE_MODULES = ${ARTIFACTS}/makefile/modules
-include $(MAKE_MODULES)/Makefile.*

# setup the scope of the make help
HELP_FILTER = docker/|help|python/

# python environment variable defaults
PYTHON ?= python3.9
PYTHON_PACKAGE = record_keeper

# docker environment variable defaults
DOCKER_IMAGE ?= ${PYTHON_PACKAGE}
DOCKER_TAG ?= discord
DOCKER_TARGET ?= final
DOCKER_WORKDIR ?= /app
DOCKER_ENTRYPOINT ?= ${DOCKER_WORKDIR}/venv/lib/${PYTHON}/site-packages/${PYTHON_PACKAGE}

# Adds a failback if the foundation artifacts are not in scope
%:
	@if test -d ${ARTIFACTS} || test -f ${ARTIFACTS}; then :; \
	else \
	echo "\n" \
	"This project has a missing dependency on the foundation project\n" \
	"which can be found https://github.com/williamwissemann/foundation \n" \
	"the expected file stucture should be: \n" \
	"\n" \
	"foundation \n" \
	"├───artifacts \n" \
	"├───packages \n" \
	"│   └───python \n" \
	"│       ├───backhoe \n" \
	"│       ├───utility_belt \n" \
	"|       └───>> ${PYTHON_PACKAGE} << \n" \
	; \
	fi