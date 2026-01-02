#!/usr/bin/env python3
"""
Test Apple Music API rate limiting
Tries 5 requests at 1 per 5 seconds to verify rate limits
"""

import json
import time
import urllib.parse
import urllib.request

# Test with 5 second delay (12 requests per minute, well under 20/min limit)
RATE_LIMIT_DELAY = 5.0

# Test albums
TEST_ALBUMS = [
    "Dookie",
    "OK Computer",
    "Rumours",
    "Born to Run",
    "Purple Rain"
]

def search_apple_music(album_name):
    """Search Apple Music API for album"""
    try:
        encoded_term = urllib.parse.quote(album_name)
        url = f"https://itunes.apple.com/search?term={encoded_term}&entity=album&limit=5"

        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

            if data.get('resultCount', 0) > 0:
                results = data.get('results', [])
                if results:
                    artist = results[0].get('artistName', 'Not found')
                    album = results[0].get('collectionName', 'Not found')
                    return (artist, album)
            return (None, None)
    except Exception as e:
        return (None, str(e))

print("🧪 Testing Apple Music API Rate Limiting")
print("=" * 50)
print(f"Test: {len(TEST_ALBUMS)} requests at 1 per {RATE_LIMIT_DELAY} seconds")
print(f"Rate: {60/RATE_LIMIT_DELAY:.0f} requests per minute")
print("=" * 50)
print()

success_count = 0
error_count = 0

for i, album in enumerate(TEST_ALBUMS, 1):
    print(f"[{i}/{len(TEST_ALBUMS)}] Testing: {album}")

    artist, result = search_apple_music(album)

    if artist:
        print(f"  ✅ SUCCESS: {artist} - {result}")
        success_count += 1
    else:
        print(f"  ❌ FAILED: {result}")
        error_count += 1

    # Don't sleep after last request
    if i < len(TEST_ALBUMS):
        print(f"  ⏳ Waiting {RATE_LIMIT_DELAY} seconds...")
        time.sleep(RATE_LIMIT_DELAY)

    print()

print("=" * 50)
print("Test Results:")
print(f"  Success: {success_count}/{len(TEST_ALBUMS)}")
print(f"  Failed: {error_count}/{len(TEST_ALBUMS)}")
print()

if success_count == len(TEST_ALBUMS):
    print("✅ All requests succeeded! Rate limit appears to be working.")
    print(f"   Safe to use {RATE_LIMIT_DELAY}s delay for full fetch.")
elif error_count > 0:
    print("⚠️  Some requests failed. Check error messages above.")
    if "403" in str(result) or "429" in str(result):
        print("   Still being rate limited. May need to:")
        print("   - Wait longer between requests")
        print("   - Try again later")
        print("   - Use different network/VPN")
else:
    print("⚠️  Mixed results. Proceed with caution.")
