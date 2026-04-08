# mbgg-sts2-uploader

CLI tool to upload your STS run history to my analytics server (give me your
run histories pls).

## Features

**Automatic discovery** - Searches your computer and finds your run history files 
**Duplicate detection** - Only uploads runs that aren't already on the server
**Steam ID extraction** - Detects your Steam ID and sends it with the uploaded files
**Cross-platform** - macOS, Windows 
**Access Code** - Uploads have to be authorized with an access code. Ask Andrew for the code

## Installation

```bash
pip install mbgg-sts2-uploader
```

## Usage

### Recommended (prompts for access code)

```bash
mbgg-sts2-upload
```

### Upload with access code

```bash
mbgg-sts2-upload --access-code YOUR_SECRET_CODE
```

### Dry run, shows what would be uploaded

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
4. **Checks server** - Asks the server which runs it already has
5. **Uploads missing runs** - Uploads runs that aren't already on the server

## File Locations

### macOS
```
~/Library/Application Support/SlayTheSpire2/steam/{STEAM_ID}/profile*/saves/history/*.run
```

### Windows
```
%APPDATA%/SlayTheSpire2/steam/{STEAM_ID}/profile*/saves/history/*.run
```


## Troubleshooting

### "Could not find Steam ID"
Make sure you've played at least one game of Slay the Spire 2.

### "No run files found"
Check that the game is installed and you have save files.

### "Access denied: Invalid access code"
Your access code is incorrect. Ask Andrew for the code.

### "Connection refused"
Make sure the server is running and accessible.
