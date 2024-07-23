FROM node:14

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install

RUN apt-get update && apt-get install -y openssl

COPY . .
COPY .env .

# Don't run the script here, just make it executable
RUN chmod +x ./generate-cert.sh

# Use this as your start command
CMD ./generate-cert.sh && node server.js
