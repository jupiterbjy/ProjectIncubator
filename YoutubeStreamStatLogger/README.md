## Intro

Just a micro repo for collecting and visualizing live stream stats.

Requires google cloud API to work. Very vague, possibly not so useful docs are included in each file.

Accumulated view count is increased when meeting following rules - according to [source](https://www.tubics.com/blog/what-counts-as-a-view-on-youtube/).

- A user intentionally initiates the watching of a video.
- The user watches it on the platform for at least 30 seconds

For above reason total view increase and net sum of Viewer gain may differ a bit. 

Not sure if this also works with streams, but according to plotted data I got below, it seems so.


## Data structure

Mere json!

```python
{
    # stream title. yeah.
    "stream_title": "STREAM_TITLE",

    # interval of every polling, in seconds
    "interval": 5,
    
    # Accumulated integers below
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
