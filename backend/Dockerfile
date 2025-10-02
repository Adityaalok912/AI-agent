# declare what image to use
FROM python:3.13.4-slim-bullseye

# host.docker.internal -> loalhost
# curl -X POST -d '{"message": "hello duniya"}'  -H "Content-Type: application/json" http://host.docker.internal:8080/api/chats/
RUN apt-get update && apt-get install -y curl

#create python virtual environment
#isolate our python app and install from system-level python
RUN python -m venv /opt/venv/
ENV PATH=/opt/venv/bin:$PATH


WORKDIR /app

#COPY local_folder container_folder
COPY requirements.txt /tmp/requirements.txt

#RUN within container while building
RUN pip install -r /tmp/requirements.txt

COPY ./src .


CMD ["python", "-m", "http.server", "8000"]