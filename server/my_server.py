import json
import os
import ExampleMsg_pb2
from base64 import standard_b64encode

with open(
    os.path.join(os.path.dirname(ExampleMsg_pb2.__file__), "ExampleMsg.bin"), "rb"
) as schema_bin:
    schema_base64 = standard_b64encode(schema_bin.read()).decode("ascii")

import asyncio
import time
from foxglove_websocket import run_cancellable
from foxglove_websocket.server import FoxgloveServer, FoxgloveServerListener
from foxglove_websocket.types import ClientChannel, ClientChannelId


SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8765
SERVER_NAME = "Example server"


channel_ids = dict(
    server_protobuf=None,
    server_json=None,
    client_protobuf=None,
    client_json=None,
)


async def main():
    class Listener(FoxgloveServerListener):

        async def on_client_advertise(
            self, _: "FoxgloveServer", channel: ClientChannel
        ):
            # Recording the channel IDs where MessageMsg and JsonMsg were advertised, to be
            # able to forward messages to the associated server topics later.
            if channel["schemaName"] == "MessageMsg":
                channel_ids["client_protobuf"] = channel["id"]
            elif channel["schemaName"] == "JsonMsg":
                channel_ids["client_json"] = channel["id"]

        async def on_client_message(
            self, server: FoxgloveServer, channel_id: ClientChannelId, payload: bytes
        ):
            if channel_id == channel_ids["client_json"]:
                msg = json.loads(payload)
                print(
                    f"Client message on channel {channel_id}: msg={msg['msg']}, count={msg['count']}"
                )

                # Forward the message to the server's json topic
                await server.send_message(
                    channel_ids["server_json"],
                    time.time_ns(),
                    json.dumps(msg).encode("utf-8"),
                )

            if channel_id == channel_ids["client_protobuf"]:
                # The payload was sent as the string representation of an UInt32Array e.g.
                # `[10,4,121,97,121,63,16,2]`
                uint_array = [
                    int(x) for x in payload.decode("utf-8").strip("[]").split(",")
                ]

                msg = ExampleMsg_pb2.ExampleMsg()
                msg.ParseFromString(bytes(uint_array))
                print(
                    f"Client message on channel {channel_id}: msg={msg.msg}, count={msg.count}"
                )

                # Forward the message to the server's protobuf topic
                await server.send_message(
                    channel_ids["server_protobuf"],
                    time.time_ns(),
                    msg.SerializeToString(),
                )

    async with FoxgloveServer(
        SERVER_HOST,
        SERVER_PORT,
        SERVER_NAME,
        capabilities=["clientPublish"],
    ) as server:
        server.set_listener(Listener())

        channel_ids["server_protobuf"] = await server.add_channel(
            {
                "topic": "/server/protobuf-messages",
                "encoding": "protobuf",
                "schemaName": "ExampleMsg",
                "schema": schema_base64,
            }
        )

        channel_ids["server_json"] = await server.add_channel(
            {
                "topic": "/server/json-messages",
                "encoding": "json",
                "schemaName": "JsonMsg",
                "schema": json.dumps(
                    {
                        "type": "object",
                        "properties": {
                            "msg": {"type": "string"},
                            "count": {"type": "number"},
                        },
                    }
                ),
                "schemaEncoding": "jsonschema",
            }
        )

        i = 0
        while True:
            i += 1
            await asyncio.sleep(2)

            await server.send_message(
                channel_ids["server_protobuf"],
                time.time_ns(),
                ExampleMsg_pb2.ExampleMsg(
                    msg="Protobuf from server", count=i
                ).SerializeToString(),
            )

            await server.send_message(
                channel_ids["server_json"],
                time.time_ns(),
                json.dumps({"msg": "Json from server", "count": i}).encode("utf8"),
            )


if __name__ == "__main__":
    run_cancellable(main())
