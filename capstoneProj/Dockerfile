FROM python:3.9-slim
EXPOSE 8080

ADD v2.py  ./app/newProg.py
COPY requirements.txt requirements.txt
COPY inspectData/testfile.txt .app/inspectData/testfile.txt
RUN pip3 install -r requirements.txt 
RUN apt-get update &&  apt-get install -y \
	build-essential \
	curl \
	software-properties-common \
	git \
	&& rm -rf /var/lib/apt/lists/* \
	streamlit

HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

ENTRYPOINT ["streamlit", "run", "newProg.py", "--server.port=8080","--server.address=0.0.0.0"]
WORKDIR /app

