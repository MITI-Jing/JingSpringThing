#!/bin/sh

OPENSSL_CMD="openssl"
SUBJECT="/CN=localhost"

$OPENSSL_CMD req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "$SUBJECT"
