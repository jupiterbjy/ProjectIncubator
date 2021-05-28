Bot to get stream notifications using Google Data API v3 + Twitch API.

Built for one specific use-case: YouTube & Twitch simultaneous streaming condition. 

```commandline
usage: TwitchAPIMethod.py [-h] [-p CONFIG_PATH] [-i INTERVAL] twitch_channel_name client_id client_secret api url

positional arguments:
  twitch_channel_name   Twitch channel name
  client_id             Twitch Application ID
  client_secret         Twitch Application Secret
  api                   Google Data API key
  url                   Discord webhook url

optional arguments:
  -h, --help            show this help message and exit
  -p CONFIG_PATH, --path CONFIG_PATH
                        Path to configuration json file. Default path is 'configuration.json' adjacent to this script
  -i INTERVAL, --interval INTERVAL
                        interval between checks in seconds. Default is 1.
```

Do note that too low interval will cause quota to exceed.

---

## Configuration file

If you're lazy like me and don't want to pass path parameter, create `configuration.json` with structure below next to script's path.

Currently, only supports 2 variable. You can use this anywhere in dictionary. This is possible because dictionary is dumped
into strings then json serialized back - a dumb, crude way.

- *[desc]* - part where description is formatted in.
- *[vid_id]* - part where YouTube video ID is formatted, mostly for completing link.

### Structure
```json
{
  "content": "<Content part of discord message>",
  "embed": {
    "title": "<Title part of discord embed>",
    "description": "<description part of discord embed>",
    "color": "<Hex color code of embed>",
    "image": {
      "url": "<Image part of discord embed>"
    },
    "thumbnail": {
      "url": "<Thumbnail part of discord embed>"
    },
    "fields": [
      {
        "name": "<Title of embed field 1>",
        "value": "<Value part of embed field 1>"
      }
    ]
  },
  "desc_start": "<Splitter string to distinguish header in YouTube description.>",
  "desc_end": "<Splitter string to distinguish footer in YouTube description>",
  "channels": ["<Youtube channel id 1>"]
}
```

- "channels" - Useful when streamer uses more than one YouTube channel with one twitch channel.

### Example configuration
```json
{
  "content": "<@&812458585522962513>",
  "embed": {
    "title": "#live",
    "description": "[desc]",
    "color": "18ffff",
    "image": {
      "url": "https://i.ytimg.com/vi/[vid_id]/mqdefault.jpg"
    },
    "thumbnail": {
      "url": "https://cdn.discordapp.com/attachments/783069235999014912/840531297499480084/ezgif.com-gif-maker.gif"
    },
    "fields": [
      {
        "name": "Youtube",
        "value": "https://youtu.be/[vid_id]"
      },
      {
        "name": "Twitch",
        "value": "https://cyannyan.com/twitch"
      }
    ]
  },
  "desc_start": "",
  "desc_end": "────",
  "channels": ["UC9wbdkwvYVSgKtOZ3Oov98g", "UC9waeFu44i5NwB7x48Tq6Bw"]
}
```

Will generates this.

![image](https://user-images.githubusercontent.com/26041217/120014990-b51b9380-c01d-11eb-893f-c95916035fe5.png)

This just unpacks `embed` dictionary over initializer of module `discord_webhook`'s class `DiscordEmbed`, so if
you know what that class accepts it you could edit and add it configuration file.
