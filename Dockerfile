FROM ubuntu:20.04 as roundware
RUN mkdir /code
ENV PATH=/code:$PATH
ENV PYTHONPATH=/code
WORKDIR /code
RUN apt-get update

ADD requirements.apt .
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive xargs -a requirements.apt apt-get install -y --fix-missing
RUN python3 -m pip install pip setuptools --upgrade
RUN which python3 && python3 --version
ADD requirements ./requirements
ADD requirements.txt .
ADD scripts ./scripts
ADD roundware ./roundware
RUN python3 -m pip install -r requirements.txt
RUN python3 -m pip install -r requirements/dev.txt
RUN python3 roundware/manage.py collectstatic

ADD .coveragerc .
