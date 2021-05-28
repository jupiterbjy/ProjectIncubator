import json
from discord_webhook import DiscordEmbed, DiscordWebhook


VID_TARGET = "[vid_id]"
DESC_TARGET = "[desc]"


def format_description(config_dict):
    """
    Make sure to have separators in video descriptions if you're going to use it!
    """

    start = config_dict["desc_start"]
    end = config_dict["desc_end"]

    # bake function, like how cakes bake a loaf. Meow.
    def inner(description: str) -> str:

        # if start separator is specified, check position.
        if start:
            description = description.split(start)[-1]

        # Same goes for end separator
        if end:
            description = description.split(end)[0]

        # Make sure to have one newline in both end. Can't use backslash in f-string inner block.
        description = description.strip("\n")

        return description

    return inner


def embed_closure(config_dict):
    formatter = format_description(config_dict)

    def generate_embed(video_id, description):
        embed_config = config_dict["embed"]

        dump_string = json.dumps(embed_config).replace(VID_TARGET, video_id).replace(DESC_TARGET, formatter(description))
        formatted_dict = json.loads(dump_string)

        embed = DiscordEmbed(**formatted_dict)

        return embed

    return generate_embed


def webhook_closure(webhook_url: str):
    def template(**kwargs):
        DiscordWebhook(url=webhook_url, **kwargs).execute()

    return template
