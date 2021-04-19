FROM python:3.9-buster

ENV PYTHONIOENCODING=UTF-8

RUN apt-get update -y && apt-get upgrade -y \
    && apt-get install -y ffmpeg espeak libespeak-dev

COPY . /app

WORKDIR /app

# numpy needs to be installed first
RUN pip install numpy && pip install -r requirements.txt 

RUN useradd -ms /bin/bash user \
    && chown -R user /app
USER user

EXPOSE 80

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
