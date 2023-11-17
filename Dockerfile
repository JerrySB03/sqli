FROM python:3.9.5-slim-buster

# Set the working directory to /app
WORKDIR /app

# Install sqlite3
RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev

COPY src/ /app/src/
COPY requirements.txt /app/

RUN /usr/local/bin/python -m pip install --upgrade pip
# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

EXPOSE 1337:80/tcp

CMD ["python", "/app/src/app.py"]