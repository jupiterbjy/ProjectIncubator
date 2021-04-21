## Intro

Just a micro repo for collecting and visualizing live stream stats.

Requires google cloud API to work. Very vague, possibly not so useful docs are included in each file.

## Usage
```commandline
usage: log_stat.py [-h] [-v] [-g] [-o PATH] [-p INTERVAL] [-f INTERVAL] [-a KEY] VIDEO_ID

Records livestream details using Google Data API.

positional arguments:
  VIDEO_ID              ID of live youtube stream.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Enables debug logging.
  -g, --graph           Show plot at the end of the program.
  -o PATH, --output PATH
                        Output folder, default is script's directory.
  -p INTERVAL, --poll INTERVAL
                        Changes interval between polls. Default is 5.
  -f INTERVAL, --flush INTERVAL
                        Interval between write flush. Flushes very Nth poll. Default is 40.
  -a KEY, --api KEY     Google Data API key, can be omitted if you have it in file 'api_key' at script directory.
```

## Random ramble

Accumulated view count is increased when meeting following rules - according to [source](https://www.tubics.com/blog/what-counts-as-a-view-on-youtube/).

- A user intentionally initiates the watching of a video.
- The user watches it on the platform for at least 30 seconds

For above reason total view count is not so reliable compared to concurrent viewers. 

If total view count was reliable and unrestricted, one could estimate concurrent viewer gain/loss like this:

1. Assume view count increment directly contributes to concurrent viewer increase.
2. subtract concurrent viewer increment from view count increment, this will be estimated loss. 

For above reasons I gave up this idea.

## Data structure

Mere json!

```python
{
    # stream title. yeah.
    "stream_title": "STREAM_TITLE",

    # interval of every polling, in seconds
    "interval": 5,
    
    # List of accumulated integers from Google Data API(youtube videos api)
    "data": {
        "concurrentViewers": [...],
        "viewCount": [...],
        "likeCount": [...],
        "dislikeCount": [...]
    }
}
```


## Example data

not sure if I can just include stream name like that.

![](demo.png)
