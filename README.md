# Foxglove Custom Panel with Protobuf

## Overview

Largely based on [jtbandes](https://github.com/jtbandes)'s blog post [Using Protobuf Data with the Foxglove WebSocket Connection](https://foxglove.dev/blog/using-protobuf-data-with-the-foxglove-websocket-connection), this package contains example code to send protobuf messages between a websocket server and Foxglove visualization.

## Run the example

Components in this package:

* `server`: A websocket server using [Foxglove WebSocket Protocol](https://github.com/foxglove/ws-protocol)
* `extension`: Custom extension created via [foxglove/create-foxglove-extension](https://github.com/foxglove/create-foxglove-extension)
* `misc`: The proto used for this example, and an example Foxglove layout used for debugging

Test end-to-end:

1. Run the websocket server using instructions in `server/README.md`
2. Open Foxglove with a Foxglove WebSocket connection to `ws://localhost:8765`
3. Build the extension to test locally, or package & upload to your Foxglove organization (see `extension/README.md`)
4. Add the custom panel to your layout using Visualization Settings > Extensions from the top right menu

You'll see the messages published by the server on the `/server/json-messages` and `/server/protobuf-messages`
topics.

Click the layout's "Publish" button to send a client message to the server, and observe the decoded message
in the server's console logs.

The client publishes these messages to the `/client/json-messages` and `/client/protobuf-messages` topics;
once the server parses those, it forwards the parsed messages to the respective server channels for debugging.
