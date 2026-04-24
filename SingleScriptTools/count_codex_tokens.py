"""
Script to count codex token usage & display per year/month for current user.

I don't use codex nor use llm for code generation,
but this is something I wanted to calculate for fun in workplace.

example output:
```
Reading sessions/rollout-yyyy-mm-ddThh-mm-ss-some-hashes.jsonl
...
Reading archived_sessions/rollout-yyyy-mm-ddThh-mm-ss-some-hashes.jsonl

Yearly Sum:
2026-02: 10,705,490 tokens (32,256 reasoning)
2026-03: 55,742,045 tokens (86,936 reasoning)
2026-04: 117,435,491 tokens (148,720 reasoning)
2026 total: 183,883,026 tokens (267,912 reasoning)


All-time total: 183,883,026 tokens (267,912 reasoning)
Today total   : 14,764,858 tokens (12,671 reasoning)
```

:Author: jupiterbjy@gmail.com
"""

import pathlib
import itertools
import json
import datetime as dt
from collections.abc import Iterator
from collections import defaultdict
from typing import TypedDict


# --- Config ---

ROOT = pathlib.Path.home() / ".codex"
SESSIONS_PATH = ROOT / "sessions"
ARCHIVED_SESSIONS_PATH = ROOT / "archived_sessions"


# --- Util ---

class _TokenUsage(TypedDict):
    input_tokens: int
    cached_input_tokens: int
    output_tokens: int
    reasoning_output_tokens: int
    total_tokens: int


class _TokenInfo(TypedDict):
    total_token_usage: _TokenUsage
    last_token_usage: _TokenUsage
    model_context_window: int


# --- Logic ---

def token_delta_gen(
    session_file: pathlib.Path
) -> Iterator[tuple[dt.datetime, int, int]]:
    """Generates (time, token count, reasoning token count) pairs
    for given session file
    """
    
    # due to unreliable `last_token_usage` we need to calc delta
    # and due to `total_tokens` not including reasoning tokens,
    # that need to be supplied separately

    last_total = 0
    last_reason_total = 0
    
    with session_file.open("rt", encoding="utf8") as fp:
        while line := fp.readline():
            data = json.loads(line)
            
            if (
                "type" not in data
                or data["type"] != "event_msg"
                or data["payload"]["type"] != "token_count"
                or not data["payload"]["info"]
            ):
                continue

            info: _TokenInfo = data["payload"]["info"]
            
            total = info["total_token_usage"]["total_tokens"]
            reason_total = info["total_token_usage"]["reasoning_output_tokens"]
            
            yield (
                dt.datetime.fromisoformat(data["timestamp"]),
                total - last_total,
                reason_total - last_reason_total,
            )
            
            last_total = total
            last_reason_total = reason_total


def total_token_delta_gen() -> Iterator[tuple[dt.datetime, int, int]]:
    """Yields (datetime, token count, reasoning token count) pairs
    for all current user's session files in home directory.
    
    Basically just wrapper for maximum lazy iteration
    """

    sessions_iter: Iterator[pathlib.Path] = itertools.chain(
        SESSIONS_PATH.glob("**/*.jsonl"),
        ARCHIVED_SESSIONS_PATH.glob("**/*.jsonl")
    )
    for session in sessions_iter:
        print("Reading", session.relative_to(ROOT))
        yield from token_delta_gen(session)


def main():
    # {year: (monthly_token, monthly_reasoning_token)}
    per_years: dict[int, tuple[dict[int, dict[int, int]], dict[int, dict[int, int]]]] = {}
    
    # accumulation pass
    for dt_time, count, reason_count in total_token_delta_gen():
        year = dt_time.year
        month = dt_time.month
        day = dt_time.day
        
        # sanity check...
        # if count < 0 or reason_count < 0:
        #     print(f"Got negative token count {count} r:{reason_count}")
        #     continue
        
        if year not in per_years:
            per_years[year] = (
                defaultdict(lambda: defaultdict(int)),
                defaultdict(lambda: defaultdict(int))
                # this is cursed but works..
            )
        
        per_years[year][0][month][day] += count
        per_years[year][1][month][day] += reason_count
    
    print("\n\nYearly Sum:")
    
    total = 0
    r_total = 0
    
    # display pass
    for year, (monthly, r_monthly) in per_years.items():
        yearly_total = 0
        yearly_r_total= 0
        
        for month in sorted(monthly):
            
            monthly_sum = sum(monthly[month].values())
            monthly_r_sum = sum(r_monthly[month].values())
            
            yearly_total += monthly_sum
            yearly_r_total += monthly_r_sum
            
            print(f"{year}-{month:02}: {monthly_sum:,} tokens ({monthly_r_sum:,} reasoning)")
        
        total += yearly_total
        r_total += yearly_r_total
        print(f"{year} total: {yearly_total:,} tokens ({yearly_r_total:,} reasoning)\n")

    print(f"\nAll-time total: {total:,} tokens ({r_total:,} reasoning)")
    
    # display today's
    today = dt.datetime.today()

    try:
        today_total = per_years[today.year][0][today.month][today.day]
        today_r_total = per_years[today.year][1][today.month][today.day]
    
    except KeyError:
        today_total = 0
        today_r_total = 0

    print(f"Today total   : {today_total:,} tokens ({today_r_total:,} reasoning)")


if __name__ == "__main__":
    main()
    input("\nPress enter to exit: ")
