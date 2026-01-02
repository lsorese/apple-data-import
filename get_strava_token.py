#!/usr/bin/env python3
"""
Helper script to get new Strava access tokens via OAuth flow.

This script will:
1. Generate an authorization URL
2. Wait for you to authorize the app
3. Exchange the authorization code for access/refresh tokens
"""

import sys

CLIENT_ID = "193286"
CLIENT_SECRET = "7c0564b4ea0552314ed091a0f1c0d2da8d50730c"

def main():
    print("=== Strava Token Generator ===\n")

    # Step 1: Generate authorization URL
    auth_url = (
        f"https://www.strava.com/oauth/authorize?"
        f"client_id={CLIENT_ID}&"
        f"response_type=code&"
        f"redirect_uri=http://localhost&"
        f"approval_prompt=force&"
        f"scope=activity:read_all"
    )

    print("Step 1: Open this URL in your browser:\n")
    print(auth_url)
    print("\n")

    print("Step 2: After authorizing, you'll be redirected to a URL like:")
    print("http://localhost/?state=&code=XXXXXXXXXXXXX&scope=read,activity:read_all")
    print("\n")

    # Step 2: Get authorization code
    code = input("Paste the 'code' value from the URL here: ").strip()

    if not code:
        print("Error: No code provided")
        sys.exit(1)

    # Step 3: Exchange code for tokens
    print("\nExchanging code for tokens...")

    import requests

    url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code"
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()

        data = response.json()

        print("\n✓ Success! Here are your new tokens:\n")
        print(f"Access Token:  {data['access_token']}")
        print(f"Refresh Token: {data['refresh_token']}")
        print(f"Expires At:    {data['expires_at']}")

        print("\n\nUpdate these values in fetch_strava_data.py:")
        print(f'ACCESS_TOKEN = "{data["access_token"]}"')
        print(f'REFRESH_TOKEN = "{data["refresh_token"]}"')

    except requests.exceptions.RequestException as e:
        print(f"\n✗ Error: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        sys.exit(1)

if __name__ == '__main__':
    main()
