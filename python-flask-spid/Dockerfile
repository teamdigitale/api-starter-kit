FROM python:2.7

RUN apt-get -y update && apt-get install -y \
	ca-certificates curl netbase wget \
	swig python-dev libxml2-dev libxmlsec1-dev \
	build-essential libxmlsec1 

RUN mkdir /app
WORKDIR /app
# Add requirements.txt before rest of repo for caching
ADD requirements.txt /app
RUN pip install -rrequirements.txt

ADD . /app/
ENTRYPOINT ["python", "index.py"]
