Bot to test stream notifications using Google Data API v3. Far from completion.

```commandline
usage: discord_bot.py [-h] -a KEY -u URL [-i INTERVAL] [-e] [-I] (-c ID | -t VID_ID)

optional arguments:
  -h, --help            show this help message and exit
  -a KEY, --api KEY     Google Data API key
  -u URL, --url URL     Discord webhook url.
  -i INTERVAL, --interval INTERVAL
                        Check interval in minutes. If omitted, will be set to 5.
  -e, --exclude-live    Excludes check for already live streams. This reduces Quota usages roughly by a bit short on
                        half.
  -I, --ignore-error    Ignore HTTP Errors including quota check.This will still fail to get data from Youtube, but
                        script won't stop.
  -c ID, --channel-id ID
                        Youtube channel's ID.
  -t VID_ID, --test VID_ID
                        Test output with youtube video id
```

Do note that too low interval will cause quota to exceed.
Default configuration with 5 minutes interval will be somewhat short to cover full 24 hours.

---

Don't forget to edit file `configuration.json` to user's taste, if you're brave enough to use this wacky script.

- format: Format of discord live notification message.
- start: Keyword just before *actual* description part in description of the video. Leave it empty to disable starting string check.
- end: Keyword just after *actual* description part in description of the video. Leave it empty to disable end string check.

```json
{
  "format": "#live\n\n{}\n\n[Youtube]https://youtu.be/{}",
  "start": "",
  "end": "────"
}

```
