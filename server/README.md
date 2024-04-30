# WebSocket server

A simple server implementation. It establishes two channels (one for JSON messages, and
another for protobuf), and publishes messages on those periodically. It also listens to
incoming client messages and prints those to console.

## Get started

Install requirements from `requirements.txt`, then run the server using `python my_server.py`
