from pytchat import LiveChat
import time
import json
import pprint
import pathlib


# chat_id = "LLw58K_VVwE"
chat_id = input("Stream ID:")

members = set()


def callback(chat_data):
    for chat in chat_data.items:
        json_data: dict = json.loads(chat.json())
        members.add(json_data["author"]["name"])
        pprint.pprint(members)


livechat = LiveChat(chat_id, callback=callback, direct_mode=True)


while livechat.is_alive():
    time.sleep(3)

livechat.raise_for_status()

if members:
    save_file = pathlib.Path(__file__).parent.joinpath(chat_id + ".json")
    save_file.write_text(json.dumps(members, indent=2), "utf8")
