FROM python:3.9-slim

WORKDIR /app

# Install dependencies
ADD requirements.txt .
RUN apt-get update \
    && apt-get install openssh-client sshpass -y \
    && pip install -r requirements.txt

# Add the app
ADD . .

# Engage.
CMD ["behave", "--no-capture"]
