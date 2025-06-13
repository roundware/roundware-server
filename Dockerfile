FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

ENV PATH=/code:$PATH
ENV PYTHONPATH=/code

WORKDIR /code
RUN apt-get update && apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    add-apt-repository ppa:ubuntugis/ppa && \
    apt-get update && \
    apt-get install -y \
    binutils \
    ffmpeg \
    gdal-bin \
    git \
    libgdal-dev \
    libproj-dev \
    mediainfo \
    pacpl \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3.11-distutils \
    python3-gdal \
    python3-fiona \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/pythonenv/roundware-venv
RUN mkdir -p /pythonenv/ && \
    python3.11 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python3 -m pip install --no-cache-dir pip setuptools --upgrade

COPY pyproject.toml .
COPY scripts/ ./scripts
COPY roundware/ ./roundware

# Create symlinks for GDAL and Fiona
RUN ln -s /usr/lib/python3/dist-packages/GDAL* $VIRTUAL_ENV/lib/python3.11/site-packages/ && \
    ln -s /usr/lib/python3/dist-packages/fiona* $VIRTUAL_ENV/lib/python3.11/site-packages/

RUN python3 -m pip install .
RUN python3 -m roundware.manage collectstatic --noinput

COPY .coveragerc .