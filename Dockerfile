FROM ubuntu:24.04
RUN mkdir /code
ENV PATH=/code:$PATH
ENV PYTHONPATH=/code

WORKDIR /code
ADD requirements.apt .
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y && \
    xargs -a requirements.apt apt-get install -y --fix-missing && \
    apt-get upgrade -y gdal-bin \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/pythonenv/roundware-venv
RUN mkdir /pythonenv/
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python3 -m pip install pip setuptools --upgrade &&  \
    which python3  \
    && python3 --version

ADD pyproject.toml .
ADD scripts/ ./scripts
ADD roundware/ ./roundware

RUN python3 -m pip install .
RUN python3 -m roundware.manage collectstatic

ADD .coveragerc .