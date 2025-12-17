# Nuxified - Custom Discord Selfbot

A comprehensive, self-hosted Discord selfbot written in Python, designed for personal use with extensive utility features and AI integration. The bot provides text manipulation, media downloading, NSFW content fetching, automated responses, and more.

[Wiki here.](https://github.com/hexxedspider/nuxified/wiki)

## Key Features

- **AI Integration**: AI replies (once you set up the [free] OpenRouter API key) that activates on pings (DMS ONLY, SERVER PINGS DO NOT COUNT). Custom personality that you get to pick, and you can save presets for different styles.
- **Many Commands**: 150+ commands right off rip!
- **Locked commands**: Some commands (nux ownercmds) are locked to owner only.
- **Status Cycler**: It will change your status from a preset one (mine by default, you can swap it out at any point).

## Setup

pip requirements lol what'd you expect
```pip install -r requirements.txt```

### Notes
Use Python 3.11.9 or another compatible version (there is a python library - audioop-lts - to make 3.12+ versions work!)
pip for installing dependencies
discord account (no shit) and user token (i can try making a tool for this if you have trouble!)

### Using it
1. Clone or download the repository
2. Install dependencies (listed above)
3. Rename the .envv to .env
    3.1. add user id's to allowed (yourself excluded) if you want other people to use the commands - optional.
    3.2. put your user token to run nuxified.
    3.3. add the openrouter api key (that you can get for free, all models i used and have listed are entirely free) to use the ai reply - optional.
    3.4. add other api keys that you might want to use - optional.

### Running the Bot

what do you think?
```python nuxified.py```
or, if you want to modify the code yourself and have it restart the script,
```python w.py```
additonally, if you want to use a graphical interface instead of just an IDE and tapping files, use the launcher.py (either by a command or double tapping the file).

### Optional Setup
- Place font files (.otf/.ttf) in the `dmfonts/` directory, or keep the ones I put.
- Use ```nux watch {server id}``` if you want to track all messages (within reason, you cannot save messages you don't have access to) sent in it, auto creates the directory.

## Usage

All commands start with `nux ` prefix. Only three use `all`, but that's personal use more than anything (all scripts running with this, e.g. copying the script and running in tandem with different tokens, will make them all use the command if in the same place).

## Disclaimer

Discord selfbots violate their ToS. Use at your own risk. Never share your Discord token or account credentials. By using this script, you always run the risk of having your account locked, warned, suspended, or outright terminated. USE AT YOUR OWN RISK. If you get banned or catch a violation, that's on you - not me.

## Configuration

- `config.pkl` - Main config (watched guilds, cleaner settings, autoreplies, etc.).
- `ai_config.pkl` - AI personality and presets.
- `logs/` directory for message logging.
