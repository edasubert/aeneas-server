# aeneas-server
Server implementation of Aeneas forced aligner (https://github.com/readbeyond/aeneas) using FastAPI. 

## Run
Either build and run the image:
``` 
docker build -t aeneas-server:latest .
docker run -p80:80 aeneas:latest
```
Or use docker hub:
```
docker run -p80:80 eduardsubert/aeneas:latest
```

## Request
Send POST requests to `http://localhost/`.
Documentation is available at `http://localhost/docs` (the server needs to be running).

### Example request in python
```python
import requests

parameters = [
    ('language', (None, 'eng', 'application/json')),
    ('text_file_format', (None, 'plain', 'application/json')),
    ('transcript', ('transcript.txt', open('transcript.txt', 'rb'), 'text/plain')),
    ('audio', ('audio.aac', open('audio.aac', 'rb'), 'audio/aac')),
]

response = requests.post("http://localhost:80/", files=parameters)
```
