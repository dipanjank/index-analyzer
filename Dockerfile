FROM python:3.8-slim

RUN apt-get update -y && apt-get upgrade -y
COPY . /srv/src/index-analyzer
RUN pip install -U pip
RUN pip install -r /srv/src/index-analyzer/requirements.txt
WORKDIR  /srv/src/index-analyzer/
CMD ["streamlit", "run", "main.py"]

