FROM python:2.7

RUN apt-get -y update && apt-get install -y \
	ca-certificates curl netbase wget \
	swig python-dev libxml2-dev libxmlsec1-dev \
	build-essential libxmlsec1 

RUN mkdir /app
ADD . /app
WORKDIR /app
RUN pip install -rrequirements.txt
ENTRYPOINT ["python", "index.py"]
