# Strava Integration for Apple Music Album Data

This script fetches running data from the Strava API and matches it with your Apple Music album listening timestamps.

## Prerequisites

1. **Strava API Access**
   - Go to https://www.strava.com/settings/api
   - Note your **Client ID** (you'll need this to run the script)
   - Your Client Secret, Access Token, and Refresh Token are already configured in the script

2. **Python Requirements**
   ```bash
   pip install requests
   ```

## Usage

### Test Mode (Recommended First Run)

Test mode processes only a small subset of albums and makes limited API requests without saving:

```bash
python3 fetch_strava_data.py --test --client-id YOUR_CLIENT_ID
```

This will:
- Process only the first 10 albums
- Make at most 5 API requests
- Not modify the data.json file
- Show you what would be matched

### Full Run

Once you've verified test mode works, run the full script:

```bash
python3 fetch_strava_data.py --client-id YOUR_CLIENT_ID
```

Or without specifying client ID (it will prompt you):

```bash
python3 fetch_strava_data.py
```

### Command Line Options

- `--test` - Enable test mode (process subset, don't save)
- `--test-limit N` - Process N albums in test mode (default: 10)
- `--client-id ID` - Provide Strava Client ID (otherwise will prompt)

## Rate Limits

Strava API has the following limits:
- **100 requests per 15 minutes**
- **1,000 requests per day**

The script:
- Tracks API request count
- Waits 1 second between requests
- Shows warnings when approaching limits
- Supports a max request limit for testing

## What Data is Added

For each album matched with a Strava run, the following fields are added:

- `strava_activity_id` - Unique ID of the Strava activity
- `strava_activity_name` - Name of the run
- `strava_activity_type` - Type (Run, VirtualRun, etc.)
- `strava_start_date` - When the run started
- `strava_distance_miles` - Distance in miles
- `strava_distance_meters` - Distance in meters
- `strava_moving_time_seconds` - Time spent moving
- `strava_elapsed_time_seconds` - Total elapsed time
- `strava_pace_per_mile` - Pace in min/mile format (e.g., "8:30")
- `strava_elevation_gain_meters` - Total elevation gain
- `strava_average_speed_mps` - Average speed (meters per second)
- `strava_max_speed_mps` - Max speed (meters per second)
- `strava_average_heartrate` - Average heart rate (if available)
- `strava_max_heartrate` - Max heart rate (if available)
- `strava_average_cadence` - Average cadence (if available)
- `strava_suffer_score` - Strava suffer score (if available)
- `strava_has_heartrate` - Whether heart rate data is available

## Matching Algorithm

The script matches albums to Strava runs by:
1. Comparing the album's `first_listen` timestamp with run start times
2. Finding runs within a 60-minute window (±30 minutes)
3. Selecting the closest match if multiple runs are found

## Token Refresh

The script automatically refreshes your access token if it has expired. After running, it will display your new tokens:

```
New tokens (save these for future use):
  Access Token: [new token]
  Refresh Token: [new token]
```

**Important:** Save these new tokens if you plan to run the script again in the future.

## Example Output

```
Loading data from apple-music-watch-viewer/public/data.json...
  Loaded 467 albums

⚠ TEST MODE: Processing only first 10 albums

Initializing Strava client...

Fetching Strava activities between:
  2023-02-18T16:00:14.130000+00:00 and 2025-11-11T14:45:32.619000+00:00

Fetching Strava activities...
  Fetching page 1... (Request 1)
    Got 200 activities

Total API requests made: 1
  Fetched 200 total activities
  Found 185 running activities

Matching albums with Strava activities...
  ✓ Matched 'Arms Down' with Strava run:
    Morning Run - 5.2 mi @ 8:45/mi

Matched 8 out of 10 albums with Strava activities

⚠ TEST MODE: Not saving data (would save to apple-music-watch-viewer/public/data.json)
Run without --test flag to save changes
```

## Troubleshooting

### "401 Unauthorized" Error
Your access token has expired. The script should automatically refresh it. If it doesn't work, check that your refresh token is correct.

### No Matches Found
- Verify that your Strava activities overlap with your album listening times
- Check that activities are marked as "Run" type in Strava
- The matching window is ±30 minutes - if runs started more than 30 minutes before/after the album, they won't match

### Rate Limit Errors
If you hit the rate limit:
- Wait 15 minutes before trying again
- Use `--test` mode to test with fewer requests
- The script automatically waits 1 second between requests to help avoid limits
