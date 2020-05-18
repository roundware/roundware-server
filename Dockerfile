FROM python:3.5 as roundware
RUN mkdir /code
ENV PATH=/code:$PATH
ENV PYTHONPATH=/code
WORKDIR /code
RUN apt-get update
RUN apt-get -y install binutils libproj-dev gdal-bin ffmpeg
RUN python -m pip install --upgrade pip setuptools

ADD requirements ./requirements
ADD requirements.txt .
ADD scripts ./scripts
ADD roundware ./roundware
RUN python -m pip install -r requirements.txt

FROM roundware as roundware_dev
ADD .coveragerc .
RUN python -m pip install -r requirements/dev.txt
RUN apt-get -y install postgresql-client