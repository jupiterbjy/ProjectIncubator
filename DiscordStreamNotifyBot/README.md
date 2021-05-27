Bot to test stream notifications using Google Data API v3. A bit far from polished.

```commandline
usage: discord_bot.py [-h] [-p CONFIG_PATH] [-i INTERVAL] [-c NUM] [-I] [-v]
                      api url

positional arguments:
  api                   Google Data API key.
  url                   Discord webhook url.

optional arguments:
  -h, --help            show this help message and exit
  -p CONFIG_PATH, --path CONFIG_PATH
                        Path to configuration json file.
  -i INTERVAL, --interval INTERVAL
                        interval between checks in seconds. Default is 60.
  -c NUM, --count NUM   Number of videos to fetch from each channel. Default
                        is 3.
  -I, --ignore-error    Ignore HTTP Errors including quota check.This will
                        still fail to get data from Youtube, but script won't
                        stop.
  -v, --verbose         Enables debugging message.
```

Do note that too low interval will cause quota to exceed.

---

Don't forget to edit file `configuration.json` to user's taste, if you're brave enough to use this wacky script.

- format: Format of discord live notification message.
- start: Keyword just before *actual* description part in description of the video. Leave it empty to disable starting string check.
- end: Keyword just after *actual* description part in description of the video. Leave it empty to disable end string check.
- channels: List of channels to check. Useful when one streamer has sub-channel for copyrighted content streams.

```json
{
  "format": "#live\n\n{}\n\n[Youtube]https://youtu.be/{}",
  "start": "",
  "end": "",
  "channels": ["Channel 1 id", "Channel 2 id"]
}

```
