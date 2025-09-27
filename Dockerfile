# declare what image to use
FROM python:3.13.4-slim-bullseye


# for running file
# docker build -f Dockerfile -t pyapp .
# docker run -it pyapp


# for uploading to docker repo 
# docker build -f Dockerfile -t adityaalok/py-test:latest .
# docker push adityaalok/py-test:latest

# python -m http.server 8000  // python cmd for web server
# docker run -it -p 8000:8000 pyapp
CMD ["python", "-m", "http.server", "8000"]