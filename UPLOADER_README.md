# mbgg-sts2-uploader

Simple command-line tool to upload your Slay the Spire 2 run history to the mbgg analytics server.

## Features

✅ **Automatic discovery** - Finds your run files automatically
✅ **Smart duplicate detection** - Only uploads runs that aren't already on the server
✅ **Steam ID detection** - Automatically extracts your Steam ID from the file path
✅ **Cross-platform** - Works on macOS and Windows
✅ **Secure** - Uses access code authentication
✅ **Fast** - Checks hashes before uploading to save bandwidth

## Installation

```bash
pip install mbgg-sts2-uploader
```

That's it! No other dependencies needed.

## Usage

### Basic Upload (prompts for access code)

```bash
mbgg-sts2-upload --server https://mbgg-api.up.railway.app
```

### Upload with access code

```bash
mbgg-sts2-upload --server https://mbgg-api.up.railway.app --access-code YOUR_SECRET_CODE
```

### Dry run (see what would be uploaded)

```bash
mbgg-sts2-upload --dry-run
```

### All options

```bash
mbgg-sts2-upload --help
```

## How It Works

1. **Finds run files** - Searches your STS2 save directory for `.run` files
2. **Extracts Steam ID** - Gets your Steam ID from the directory structure
3. **Computes hashes** - Calculates SHA256 hash of each run file
4. **Checks server** - Asks server which runs it already has
5. **Uploads missing runs** - Only uploads runs that aren't already on the server

## File Locations

### macOS
```
~/Library/Application Support/SlayTheSpire2/steam/{STEAM_ID}/profile*/saves/history/*.run
```

### Windows
```
%APPDATA%/SlayTheSpire2/steam/{STEAM_ID}/profile*/saves/history/*.run
```

## Example Output

```
======================================================================
STS2 RUN UPLOADER
======================================================================
Platform:       darwin
Game directory: /Users/you/Library/Application Support/SlayTheSpire2
Server:         http://localhost:8001
----------------------------------------------------------------------

[1/5] Detecting Steam ID...
      ✓ Steam ID: 76561198032986989

[2/5] Finding run files...
      ✓ Found 97 run files

[3/5] Computing file hashes...
      ✓ Computed 97 hashes

[4/5] Checking server for existing runs...
      ✓ 10 already uploaded
      ✓ 87 need to be uploaded

[5/5] Uploading 87 runs...
      [1/87] ✓ NECROBINDER A10
      [2/87] ✓ NECROBINDER A10
      ...

======================================================================
UPLOAD COMPLETE
======================================================================
Total runs found:      97
Already on server:     10
Newly uploaded:        87
Errors:                0
======================================================================

✓ Upload successful!
  View stats at: http://localhost:8000
```

## Troubleshooting

### "Could not find Steam ID"
Make sure you've played at least one game of Slay the Spire 2.

### "No run files found"
Check that the game is installed and you have save files.

### "Access denied: Invalid access code"
Your access code is incorrect. Get the correct code from the server admin.

### "Connection refused"
Make sure the server is running and accessible.

## For Server Admins

### Setting the Access Code

The access code is configured in the backend `.env` file:

```bash
UPLOAD_ACCESS_CODE=your_secret_code_here
```

**Important:** Keep this code private! Share it only with users you want to allow uploads.

### Distributing the Uploader

You can share `sts2_uploader.py` with your friends. They just need:
1. Python 3.7+
2. `requests` library (`pip install requests`)
3. The access code (share privately)

## Security Notes

- The access code is sent in the `X-Access-Code` header
- Run data is transmitted as JSON (not binary)
- Duplicate detection prevents re-uploading the same run
- Each run is associated with the uploader's Steam ID

## Privacy

- The uploader sends your Steam ID (extracted from file path)
- Run history data (deck, relics, choices, outcomes)
- No other personal information is collected
