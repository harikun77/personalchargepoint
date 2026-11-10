# Work Chargers

Mobile PWA + Python API on Vercel for favorite ChargePoint stations.

## Deploy
1. Push this folder to a GitHub repo (private recommended).
2. Import the repo in Vercel (free Hobby plan).
3. Add environment variables:
   - `CP_USERNAME`, `CP_PASSWORD`: your ChargePoint login
   - `APP_PASSCODE`: a passcode you choose (entered once in the app)
   - `FAVORITE_STATION_IDS`: comma-separated station IDs
4. Open the Vercel URL on your phone, then Share > Add to Home Screen.

## Known unknowns
`python-chargepoint` method names (`get_station`, `join_waitlist`) are unverified.
If the app shows "not available", the library version lacks that call.
