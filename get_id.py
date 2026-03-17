#!/usr/bin/env python3
"""
Extract the Channel ID or Playlist ID from a YouTube URL,
and output the corresponding RSS feed link.
Usage: python get_channel_id.py
"""

import sys
import re
import urllib.request
import urllib.error
from urllib.parse import urlparse, parse_qs


RSS_BASE = "https://www.youtube.com/feeds/videos.xml"


def get_playlist_id(url: str) -> str | None:
    """Extract playlist ID directly from URL query params."""
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    playlist_id = params.get("list", [None])[0]
    if playlist_id:
        return playlist_id
    return None


def get_channel_id(url: str) -> str | None:
    """Extract channel ID from URL or by fetching the page."""

    if not url.endswith("/videos"):
        url = url+"/videos"

    # Try to extract directly from /channel/UCxxxx URL
    match = re.search(r"youtube\.com/channel/(UC[\w-]+)", url)
    if match:
        return match.group(1)

    # For /@handle, /c/, or /user/ URLs, fetch the page
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8", errors="ignore")
    except urllib.error.URLError as e:
        print(f"Error fetching URL: {e}")
        return None

    patterns = [
        r'"channelId"\s*:\s*"(UC[\w-]+)"',
        r'"externalId"\s*:\s*"(UC[\w-]+)"',
        r'<meta itemprop="channelId" content="(UC[\w-]+)"',
        r'"browseId"\s*:\s*"(UC[\w-]+)"',
    ]

    for pattern in patterns:
        match = re.search(pattern, html)
        if match:
            return match.group(1)

    return None


def main():
    url = input("Enter YouTube URL: ").strip()
    if not url.startswith("http"):
        url = "https://" + url

    # Check for playlist first
    playlist_id = get_playlist_id(url)
    if playlist_id:
        rss = f"{RSS_BASE}?playlist_id={playlist_id}"
        print(f"Playlist ID: {playlist_id}")
        print(f"RSS link: {rss}")
        return

    # Fall back to channel
    channel_id = get_channel_id(url)
    if channel_id:
        rss = f"{RSS_BASE}?channel_id={channel_id}"
        print(f"Channel ID: {channel_id}")
        print(f"RSS link: {rss}")
        return

    print("Could not extract a channel or playlist ID from that URL.")
    sys.exit(1)


if __name__ == "__main__":
    main()
