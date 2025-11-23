# this is the main fork of the script, i will try to keep it updated with the latest changes.
# i might end up actually forking the repo on github with just specific utils.
# the folder (excluded, .gitignore) other_accounts is just this script but pasted with other names and what not, branded to those accounts.
# it's in a seperate folder since they don't really matter to me, hence why i don't keep them updated, and dont bother trying to update them... not that you'd know anyway.

import discord, asyncio, random, aiohttp, datetime, io, qrcode, requests, base64, math, yt_dlp, os, logging, re, psutil, platform, subprocess, sys, json, hashlib, urllib.parse, uuid
from gtts import gTTS
from redgifs import API as RedGifsAPI
from pyfiglet import figlet_format
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
import barcode
from barcode.writer import ImageWriter
from googletrans import Translator
import scipy.signal as sp_signal
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import xml.etree.ElementTree as ET
import pickle

logging.getLogger('discord.gateway').setLevel(logging.WARNING)
logging.getLogger('discord.http').setLevel(logging.WARNING)
logging.getLogger('discord.client').setLevel(logging.WARNING)

XGD_API_KEY = "25ff18ddf60a188f5f2b412db909b8f9"
STEAM_API_BASE = "https://api.steampowered.com"

zalgo_up = [chr(i) for i in range(0x0300, 0x036F)]
flip_map = str.maketrans(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890",
    "ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz∀𐐒ƆᗡƎℲ⅁HIſʞ˥WՈΌԀΌᴚS⊥ՈΛMX⅄Z⇂ᄅƐㄣϛ9ㄥ860"
)
load_dotenv()
ALLOWED_USER_IDS = set(int(x) for x in os.getenv('allowed', '').split(',') if x.strip())
TOKEN = os.getenv('nuxified')
STEAM_API_KEY = os.getenv('STEAM_API_KEY')

VERSION = "4.0.0"

nsfw_categories = {
"ass": ["Ass", "SexyAss", "pawgtastic", "bigasses", "assgirls", "BigAss", "booty_queens", "hugeasses", "AssPillow", "OiledAss"],
"boobs": ["Boobs", "Stacked", "BustyPetite", "YummyBoobs", "BigBoobsGW", "Boobies", "KnockoutBoobs", "BoobsAndTities", "TittyDrop", "EbonyBoobs", "BigBoobsSEX", "Titties", "PerfectTits", "massivetits", "boobbounce"],
"hentai": ["hentai", "HENTAI_GIF", "animebooty", "Hentai_AnimeNSFW", "CuddlesAndHentai", "Hentai__videos", "CumHentai", "thick_hentai", "HypnoHentai", "HentaiCumsluts", "Tomboy_Hentai", "NSFWskyrim"],
"milf": ["milf", "MILFs", "MilfPawg", "maturemilf", "youngerMILFS", "MommyMaterial", "MommyHeaven", "Mommy_tits", "JustMommy", "mommy_capts", "AnimeMILFS", "MommyMilfs"],
"thighs": ["Thighs", "thickthighs", "thigh", "ThighFucking", "Thigh_Gap", "ThiccThighsSaveLives", "thighhighs", "thighdeology", "thighzone", "thighsupemacy", "thighjob_NSFW", "Thighjobhentai", "thighhighhentai"],
"goth": ["BigEmoTitties", "GothPussy", "GothWhoress", "gothsluts", "goth_girls", "bigtiddygothgf", "GothChicks", "GothBlowjobs", "gothgirlsgw", "EmoGirlsFuck", "goth_babes", "BIGTITTYGOTHGF", "Hentai_Goth", "GothGirlsGlazed", "GothGoddess", "GothFuckdolls", "BigBootyGoTHICCgf", "GothGirlMommy", "altgonewild"],
"bwomen": ["Ebony", "BlackGirlsCentral", "BlackHentai", "BlackPornMatters", "HotBlackChicks", "BlackTitties", "BlackGirlsKissing", "BlackGirlPics", "blackchickswhitedicks", "BlackChicksWorld", "blackchicks4whitedick", "BlackChicksPorn", "BrownChicksWhiteDicks"],
"rreverse": ["FMRP", "ReverseGangBangz", "HentaiReverseRape2", "ReverseFreeUse"],
"femdom": ["Femdom", "FemdomFetish", "SensualFemdom", "gentlefemdom", "femdomraw", "FemdomCreampie", "femdomhentai", "femdom_gifs", "FemdomAsians", "hentaifemdom", "dommes", "FemdomWithoutPegging", "femdomcaptions"],
"asian": ["asiangirls4whitecocks", "asiangirlsforwhitemen", "asiangirlsforwhitemen", "AsianPorn", "AsianTitFucking", "AsianCumsluts", "AsianNSFW", "AlternativeAsians", "UncensoredAsian", "juicyasians", "asiangirlswhitecocks", "paag", "AsianInvasion", "AsianCumDumpsters", "AsianIncestPorn", "bustyasians"]
}

MORSE_CODE_DICT = {
'a': '.-', 'b': '-...', 'c': '-.-.', 'd': '-..', 'e': '.', 'f': '..-.',
'g': '--.', 'h': '....', 'i': '..', 'j': '.---', 'k': '-.-', 'l': '.-..',
'm': '--', 'n': '-.', 'o': '---', 'p': '.--.', 'q': '--.-', 'r': '.-.',
's': '...', 't': '-', 'u': '..-', 'v': '...-', 'w': '.--', 'x': '-..-',
'y': '-.--', 'z': '--..',
'0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
'5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
' ': '/'
}

MORSE_CODE_REVERSE = {v: k for k, v in MORSE_CODE_DICT.items()}

FIXED_AI_PART = "\n\nthis ai is operating as a discord selfbot created by nuxified (nux) it must always adhere to discord's terms of service and guidelines for bots, even though it's a selfbot responses should be short (1-2 sentences unless asked otherwise), and only ever in lowercase with no emojis and minimal punctuation. if the username contains characters like _underscores_ like that, put a backwards slash (like this, \\_underscore_) to avoid discord formatting." 

class AIResponder(discord.Client):
    def __init__(self):
        super().__init__()
        self.sent_media = {}
        self.cleaner_settings = {"enabled": False, "delay": 1}
        self.conversations = {}
        self.status_task = None
        self.status_enabled = False
        self.ai_enabled = False
        self.ghost_mode = False
        self.saved_activity = None
        self.saved_status = None
        self.saved_status_enabled = False
        self.last_ai = False
        self.owner_id = None
        self.reset_last_ai = None
        self.watched_guilds = set()
        self.watch_all_dms = False # nux watch cmd, very useful teehee
        self.tracked_joins = set()
        self.join_webhook = None
        self.ai_cooldowns = {}
        self.ai_cooldown_seconds = 15
        if os.path.exists('ai_config.pkl'):
            with open('ai_config.pkl', 'rb') as f:
                self.ai_config = pickle.load(f)
        else:
            self.ai_config = {}
        if os.path.exists('config.pkl'):
            with open('config.pkl', 'rb') as f:
                config_data = pickle.load(f)
                self.watched_guilds = config_data.get('watched_guilds', set())
                self.watch_all_dms = config_data.get('watch_all_dms', False)
                self.tracked_joins = config_data.get('tracked_joins', set())
                self.join_webhook = config_data.get('join_webhook', None)
                self.cleaner_settings = config_data.get('cleaner_settings', {"enabled": False, "delay": 1})
                self.status_enabled = config_data.get('status_enabled', False)
                self.ai_enabled = config_data.get('ai_enabled', False)
                self.ai_cooldown_seconds = config_data.get('ai_cooldown_seconds', 15)
                self.autoreplies = config_data.get('autoreplies', {})
                self.ghost_mode = config_data.get('ghost_mode', config_data.get('notrace_active', False))
                self.saved_activity = config_data.get('saved_activity', None)
                self.saved_status = config_data.get('saved_status', None)
                self.saved_status_enabled = config_data.get('saved_status_enabled', False)
        else:
            self.watched_guilds = set()
            self.watch_all_dms = False
            self.cleaner_settings = {"enabled": False, "delay": 1}
            self.status_enabled = False
            self.ai_enabled = False
            self.ai_cooldown_seconds = 15
            self.autoreplies = {}
            self.ghost_mode = False
            self.saved_activity = None
            self.saved_status = None
            self.saved_status_enabled = False
        self.cdm_tasks = {}
        self.api = RedGifsAPI()
        self.af_api = "https://api.alexflipnote.dev"
        self.autoowod_task = None
        self.autoowod_time = None
        self.autoowod_channel = None
        self.voice_watch_enabled = set()
        autoowod_channel_id = config_data.get('autoowod_channel_id', None)
        if autoowod_channel_id:
            self.autoowod_channel = self.get_channel(autoowod_channel_id)
        self.autoowod_time = config_data.get('autoowod_time', None)
        self.voice_watch_enabled = set(config_data.get('voice_watch_enabled', set()))
        self.autoreact_rules = config_data.get('autoreact_rules', [])
        self.weather_ip_enabled = config_data.get('weather_ip_enabled', False)
        unique = os.getenv('TOKEN', '') or str(os.getpid())
        seed = int(hashlib.sha256(unique.encode()).hexdigest(), 16) % (10**8)
        self.rand = random.Random(seed)
        self.help_categories = {
            "text tools": {
                "nux define <word>": "official dictionary definition",
                "nux udefine <word>": "urban dictionary definition",
                "nux zalgo <text>": "turn text into glitched text",
                "nux flip <text>": "flip your text upside-down",
                "nux ascii <text>": "turn your text into ascii art",
                "nux mock <text>": "alternate your text casing",
                "nux emc|dmc <text>": "encode/decode morse code",
                "nux base64 encode/decode <text>": "encode or decode base64",
                "nux rot <encode|decode> <text>": "converts text into rot13",
                "nux rvowel <text>": "removes vowels from the given text",
                "nux piglatin <encode|decode> <text>": "converts text into piglatin",
                "nux hash <algorithm> <text>": "hashes text using md5, sha1, sha256, or sha512",
                "nux wordcount <text>": "counts words in the provided text",
                "nux charfreq <text>": "displays the frequency of each character in the text",
                "nux anagram <text>": "rearranges letters to create an anagram",
                "nux uuid": "generates a unique identifier"
            },
            "media": {
                "nux qr <text/url>": "generate a qr code",
                "nux tts <text>": "convert text to speech (sends mp3)",
                "nux dlmedia <url> <audio|video>": "download videos or audio from youtube, tiktok, pinterest, twitter (fuck x), instagram, and reddit (more websites supported soon)",
                "nux pornhub <white> - <orange>": "make a image with your text in the pornhub logo style",
                "nux didyoumean <search> - <dym>": "make a google result image that has the <search> text in the text bar, and <dym> being the blue text that would correct you",
                "nux facts <text>": "make an image with the fact book from ed, edd n eddy using your text",
                "nux scroll <text>": "make an image with the scroll meme format",
                "nux freq <freq hz> <waveform>": "sends back an audio file with the requested hz and waveform, useful for clean frequencies",
                "nux font <fontname> <text>": "renders text using a specific font from dmfonts"
            },
            "fun": {
                "nux dadjoke": "sends a random dad joke",
                "nux echo <text>": "i repeat what you say",
                "nux fakenitro": "sends a fake nitro gift",
                "nux achievement <text>": "send a fake minecraft achievement with your text and a random icon",
                "nux cuddle <@person>": "sends a cuddling gif with both of you (you and the person you mentioned) pinged",
                "nux weather <location>": "fetches current weather for the given location",
                "nux translate <from_lang> <to_lang> <text>": "translates text between languages (e.g., en to fr)",
                "nux lyrics <artist> - <song>": "fetches lyrics for the specified song",
                "nux rhyme <word>": "find words that rhyme with the given word",
                "nux synonym <word>": "find synonyms for the given word",
                "nux barcode <text>": "generate a barcode for the given text",
                "nux nasaapod": "fetch NASA's Astronomy Picture of the Day",
                "nux steamprofile <steamid/vanity>": "generate steam profile card image with info",
                "nux osu": "get a link to osu! user profile"
            },
            "utilities": {
                "nux id": "show your user id and info",
                "nux dumpdm": "dump recent dm history to a file",
                "nux shorten": "shorten urls using a url shortener",
                "nux calc": "evaluate math expressions",
                "nux cdm": "deletes some of my messages in this dm",
                "nux burstcdm": "deletes 5 of my recent messages in this dm",
                "nux help": "show this help message",
                "nux uptime": "show how long the bot has been running",
                "nux inviteinfo <url>": "shows the info on a discord invite",
                "nux uinfo <@person>": "extract as much info as i can from the mentioned person.",
                "nux roleinfo <@role>": "extract as much info as i can from the mentioned role.",
                "nux ping": "returns my ping in milliseconds (ms)",
                "nux usercount": "displays member count in the server (online/idle/dnd/offline)",
                "nux iplookup <ip>": "look up information about an ip address",
                "nux serverinfo": "shows detailed information about the current server",
                "nux channelinfo": "shows information about the current channel",
                "nux emojis": "lists all custom emojis in the server",
                "nux avatar <@user>": "shows a user's avatar in full size",
                "nux banner <@user>": "shows a user's banner if they have one",
                "nux stats": "shows bot statistics and system information",
                "nux bug": "report a bug to the developer",
                "nux repo": "show the GitHub repository link",
                "nux update": "check for script updates on GitHub",
                "nux joinwh <url>": "set webhook url for join notifications",
                "nux trackjoins <guild_id | list>": "toggle or list join tracking for guilds",
                "nux watch <guild_id | dm | list>": "toggle message logging for a server or all dms, or list watched servers",
                "nux spacedhelp": "show a more spaced out version of the help message",
                "nux statustoggle": "toggles the bot's rotating status messages on or off",
                "nux ghost": "toggles entirely traceless mode",
                "nux ai memory <user_id>": "shows ai conversation history with user",
                "nux learn <phrase> | <response>": "teaches custom ai responses",
                "nux autoowod start <channel_id> <HH:MM>": "automatically does 'owo daily' at scheduled UTC time with variation",
                "nux voicewatch <guild_id | list>": "toggle voice channel logging for a guild",
                "nux autoreact": "automatically reacts to messages in channels based on keywords"
            },
            "restricted / misc commands you dont have access to, or don't fit in the categories": {
                "nux ocmds": "sends a message with commands only the owner can use",
                "nux hhelp": "sends a message with the proper usage for nsfw commands it seems like literally every thing like what i am has something nsfw attached so i joined in"
            }
        }
        self.nsfwhelp_categories = {
            "neko.life": {
                "nux hentai": "drawn nsfw",
                "nux thighs": "the best thing to ever exist",
                "nux ass": "the 1stnd best thing to ever exist",
                "nux boobs": "what do you think",
                "nux pussy": "do i need to explain",
                "nux pgif": "porn gif, pgif, yk?",
                "nux neko": "cat-girl related",
            },
            "reddit based": {
                "nux nsfw <ass>": "idk what to write for this one i started at the bottom of this list and worked my way up",
                "nux nsfw <boobs>": "barbeque sauce on my titties",
                "nux nsfw <hentai>": "animated porn simple",
                "nux nsfw <milf>": "i'm old enough to be your mom please please please",
                "nux nsfw <thighs>": "so soft n squishy",
                "nux nsfw <goth>": "goth women are one of the best things to ever happen",
                "nux nsfw <bwomen>": "black women also one of the best things to ever happen",
                "nux nsfw <rreverse>": "for when you're the one that wants to be used",
                "nux nsfw <femdom>": "we all need a little of women telling us what to do",
                "nux nsfw <asian>": "for when you need actually lowkey i dont have anything to put here",
                "nux nsfw usage": "for all catergories, do nux nsfw <catergory> <number>, and it will attempt to pull that many posts, and if it can't, it'll send what it did end up grabbing",
            },
            "redgif": {
                "nux redgif <search> <number>": "similiar to the reddit one (nux nsfw) but uses redgif instead"
            },
            "rule34.xxx": {
                "nux rule34 <search> <number>": "again, similar to reddit but pulls from a different source"
            },
            "misc": {
                "existing": "use nux nsfwlist to see the options",
            }
        }
        self.commands = {
        "all ping": self.cmd_aping,
        "all tdm": self.cmd_targetdm,
        "all spam": self.cmd_targetdmspam,
        "nux id": self.cmd_id,
        "nux serverinfo": self.cmd_serverinfo,
        "nux channelinfo": self.cmd_channelinfo,
        "nux emojis": self.cmd_emojis,
        "nux kiss": self.cmd_kiss,
        "nux cf": self.cmd_coinflip,
        "nux avatar": self.cmd_avatar,
        "nux banner": self.cmd_banner,
        "nux wiki": self.cmd_wiki,
        "nux github": self.cmd_github,
        "nux stats": self.cmd_stats,
        "nux bug": self.cmd_bug,
        "nux repo": self.cmd_repo,
        "nux update": self.cmd_update,
        "nux dumpdm": self.cmd_dumpdm,
        "nux help": self.cmd_help,
        "nux define": self.cmd_define,
        "nux udefine": self.cmd_udefine,
        "nux uptime": self.cmd_uptime,
        "nux qr": self.cmd_qr,
        "nux tts": self.cmd_tts,
        "nux ascii": self.cmd_ascii,
        "nux hentai": self.cmd_hentai,
        "nux thighs": self.cmd_thighs,
        "nux ass": self.cmd_ass,
        "nux boobs": self.cmd_boobs,
        "nux pussy": self.cmd_pussy,
        "nux neko": self.cmd_neko,
        "nux hug": self.cmd_hug,
        "nux pat": self.cmd_pat,
        "nux slap": self.cmd_slap,
        "nux nickname": self.cmd_nickname,
        "nux emc": self.cmd_emc,
        "nux dmc": self.cmd_dmc,
        "nux fakenitro": self.cmd_fakenitro,
        "nux achievement": self.cmd_achievement,
        "nux pgif": self.cmd_pgif,
        "nux zalgo": self.cmd_zalgo,
        "nux flip": self.cmd_flip,
        "nux base64": self.cmd_base64,
        "nux hash": self.cmd_hash,
        "nux wordcount": self.cmd_wordcount,
        "nux charfreq": self.cmd_charfreq,
        "nux shorten": self.cmd_shorten,
        "nux mock": self.cmd_mock,
        "nux dadjoke": self.cmd_dadjoke,
        "nux inviteinfo": self.cmd_inviteinfo,
        "nux uinfo": self.cmd_userinfo,
        "nux ocmds": self.cmd_ownercmds,
        "nux nsfwlist": self.cmd_nsfwlist,
        "nux nsfw": self.cmd_nsfw,
        "nux hhelp": self.cmd_nsfwhelp,
        "nux spacedhelp": self.cmd_spacedhelp,
        "nux facts": self.cmd_facts,
        "nux scroll": self.cmd_scroll,
        "nux pornhub": self.cmd_pornhub,
        "nux freq": self.cmd_waveform,
        "nux rule34": self.cmd_rule34,
        "nux piglatin": self.cmd_piglatin,
        "nux rot": self.cmd_rot13,
        "nux rvowel": self.cmd_removevowels,
        "nux ping": self.cmd_ping,
        "nux roleinfo": self.cmd_roleinfo,
        "nux leaveguild": self.cmd_leaveguild,
        "nux eval": self.cmd_eval,
        "nux restart": self.cmd_restart,
        "nux simulate": self.cmd_simulate,
        "nux print": self.cmd_print,
        "nux fexample": self.cmd_fexample,
        "nux translate": self.cmd_translate,
        "nux lyrics": self.cmd_lyrics,
        "nux usercount": self.cmd_usercount,
        "nux iplookup": self.cmd_iplookup,
        "nux nhentai": self.cmd_nsfw_nhentai,
        "nux autoreply": self.cmd_autoreply,
        "nux watch": self.cmd_watch,
        "nux weather": self.cmd_weather,
        "nux weatherip": self.cmd_weatherip_toggle,
        "nux guilds": self.cmd_guilds,
        "nux didyoumean": self.cmd_didyoumean,
        "nux calc": self.cmd_calc,
        "nux cleaner": self.cmd_cleaner,
        "nux cdm": self.cmd_cleardmsent,
        "nux cuddle": self.cmd_cuddle,
        "nux insane": self.cmd_loser,
        "nux font": self.cmd_font,
        "nux statustoggle": self.cmd_statustoggle,
        "nux ghost": self.cmd_ghost,
        "nux burstcdm": self.cmd_burstcdm,
        "nux dlmedia": self.cmd_dlmedia,
        "nux echo": self.cmd_echo,
        "nux ai preset": self.cmd_ai_preset,
        "nux anagram": self.cmd_anagram,
        "nux uuid": self.cmd_uuid,
        "nux joinwh": self.cmd_setjoinwebhook,
        "nux trackjoins": self.cmd_trackjoins,
        "nux ai memory": self.cmd_ai_memory,
        "nux learn": self.cmd_learn,
        "nux rhyme": self.cmd_rhyme,
        "nux synonym": self.cmd_synonym,
        "nux barcode": self.cmd_barcode,
        "nux nasaapod": self.cmd_nasaapod,
        "nux steamprofile": self.cmd_steamprofile,
        "nux osu": self.cmd_osu,
        "nux pull": self.cmd_pull,
        "nux autoowod": self.cmd_autoowod,
        "nux voicewatch": self.cmd_voicewatch,
        "nux autoreact": self.cmd_autoreact,
        "nux config": self.cmd_config,
        "nux version": self.cmd_version
}

    def build_help_message(self):
        help_message = "available commands\n\n"
        for category, commands in sorted(self.help_categories.items(), key=lambda x: x[0]):
            help_message += f"{category}\n"
            if not isinstance(commands, dict):
                help_message += f"error {category} is not formatted correctly\n"
                continue
            for cmd, desc in sorted(commands.items()):
                help_message += f"- `{cmd}` {desc}\n"
            help_message += "\n"
        return help_message

    def build_spaced_help_message(self):
        help_message = "available commands\n\n\n"
        for category, commands in sorted(self.help_categories.items(), key=lambda x: x[0]):
            help_message += f"{category}\n\n"
            if not isinstance(commands, dict):
                help_message += f"error {category} is not formatted correctly\n\n\n"
                continue
            for cmd, desc in sorted(commands.items()):
                help_message += f"- `{cmd}` {desc}\n\n\n"
            help_message += "\n\n"
        return help_message

    def build_nsfwhelp_message(self):
        nsfwhelp_message = "available commands\n\n"
        for category, commands in sorted(self.nsfwhelp_categories.items(), key=lambda x: x[0]):
            nsfwhelp_message += f"{category}\n"
            if not isinstance(commands, dict):
                nsfwhelp_message += f"error {category} is not formatted correctly\n"
                continue
            for cmd, desc in sorted(commands.items()):
                nsfwhelp_message += f"- `{cmd}` {desc}\n"
            nsfwhelp_message += "\n"
        return nsfwhelp_message

    def owner_only():
        def decorator(func):
            async def wrapper(self, message, *args, **kwargs):
                if message.author.id != self.owner_id:
                    await message.channel.send("only i can do that")
                    return
                return await func(self, message, *args, **kwargs)
            return wrapper
        return decorator

    async def on_ready(self):
        self.start_time = datetime.datetime.utcnow()
        self.owner_id = self.user.id 
        # this is how i use to have my status cycle, but that new command does it for me
        # self.status_task = self.loop.create_task(self.change_status_periodically())
        print(f"{self.user}")
        if getattr(self, 'status_enabled', False) and not getattr(self, 'status_task', None) and not self.ghost_mode:
            try:
                self.status_task = self.loop.create_task(self.change_status_periodically())
            except Exception:
                pass
    async def on_message(self, message):
        if message.author.bot:
            return

        await self.log_message(message)

        if message.author.id != self.owner_id and message.author.id not in ALLOWED_USER_IDS:
            return

        content = message.content.strip()
        lowered = content.lower()

        matched_command_key = None
        command_args = ""
        for cmd_prefix in sorted(self.commands.keys(), key=len, reverse=True):
            if lowered == cmd_prefix:
                matched_command_key = cmd_prefix
                command_args = ""
                break
            elif lowered.startswith(cmd_prefix + " "):
                matched_command_key = cmd_prefix
                command_args = content[len(cmd_prefix):].strip()
                break

        if matched_command_key:
            command_func = self.commands[matched_command_key]
            await command_func(message, command_args)
            try:
                await message.delete()
            except:
                pass
            return

        if self.ghost_mode and message.author == self.user:
            await asyncio.sleep(15)
            await message.delete()

        if hasattr(self, 'autoreplies') and self.autoreplies:
            for trigger, responses in self.autoreplies.items():
                if trigger in lowered:
                    response = self.rand.choice(responses)
                    await self.send_and_clean(message.channel, response)
                    break

        custom_responses = self.ai_config.get('custom_responses', {})
        if lowered in custom_responses:
            await self.send_and_clean(message.channel, custom_responses[lowered])
            return

        if self.ai_enabled and not lowered.startswith("nux ") and not lowered.startswith("all "):
            if self.user in message.mentions and isinstance(message.channel, discord.DMChannel):
                async with message.channel.typing():
                    delay = max(1, min(len(message.content) * 0.05, 13))
                    await asyncio.sleep(delay)
                    reply = await self.ask_openrouter(message.author.id, message.author.name, message.content)
                    await self.send_and_clean(message.channel, reply)
                return

        for rule in self.autoreact_rules:
            if rule['channel_id'] == message.channel.id and rule['keyword'].lower() in message.content.lower():
                try:
                    emoji_str = rule['emoji']
                    if rule.get('emoji_id'):
                        emoji = self.get_emoji(rule['emoji_id'])
                        if emoji:
                            await message.add_reaction(emoji)
                    else:
                        await message.add_reaction(emoji_str)
                except Exception as e:
                    print(f"Autoreact error: {e}")

        if message.author.id == self.owner_id:
            if lowered == "nux ai off":
                self.ai_enabled = False
                self.save_config()
                await self.send_and_clean(message.channel, "finally i can go back to my slumber")
                return

            elif lowered == "nux ai on":
                self.ai_enabled = True
                self.save_config()
                await self.send_and_clean(message.channel, "nuxified awakens unfortunately")
                return

            elif lowered == "nux ai status":
                status = "awake and moody" if self.ai_enabled else "asleep in its coffin"
                await self.send_and_clean(message.channel, f"nuxified is {status}")
                return
            elif lowered.startswith("nux ai setup"):
                if not isinstance(message.channel, discord.DMChannel):
                    return await self.send_and_clean(message.channel, "this command can only be used in direct messages")

                openrouter_key = os.getenv('OpenRouter')
                if not openrouter_key:
                    return await self.send_and_clean(message.channel, "openrouter token not found in .env")
                await message.channel.send("What personality should the ai have? Type your custom personality.")
                def check(m):
                    return m.author == message.author and m.channel == message.channel
                try:
                    personality_msg = await self.wait_for('message', timeout=120.0, check=check)
                    personality = personality_msg.content.strip()
                    if not personality:
                        return await self.send_and_clean(message.channel, "no personality provided")
                    full_personality = personality + FIXED_AI_PART
                    self.ai_config['personality'] = full_personality
                    with open('ai_config.pkl', 'wb') as f:
                        pickle.dump(self.ai_config, f)
                    await self.send_and_clean(message.channel, "ai personality set")
                    await message.channel.send("Do you want to save this personality as a preset? Reply 'yes <preset_name>' or 'no'")
                    try:
                        save_msg = await self.wait_for('message', timeout=60.0, check=check)
                        save_resp = save_msg.content.strip().lower()
                        if save_resp.startswith('yes '):
                            preset_name = save_resp[len('yes '):].strip()
                            if preset_name:
                                self.ai_config.setdefault('presets', {})[preset_name] = personality
                                with open('ai_config.pkl', 'wb') as f:
                                    pickle.dump(self.ai_config, f)
                                await self.send_and_clean(message.channel, f"preset '{preset_name}' saved")
                            else:
                                await self.send_and_clean(message.channel, "no preset name provided, not saved")
                        else:
                            await self.send_and_clean(message.channel, "not saved as preset")
                    except asyncio.TimeoutError:
                        await self.send_and_clean(message.channel, "timed out, not saved as preset")
                    await self.send_and_clean(message.channel, "you can now turn on ai with `nux ai on`")
                except asyncio.TimeoutError:
                    await self.send_and_clean(message.channel, "timed out waiting for personality")
                return

    async def cmd_targetdm(self, message, command_args):
        parts = command_args.split(maxsplit=2)
        if len(parts) < 3:
            return await self.send_and_clean(message.channel, "usage all tdm <user_id> <message>")

        try:
            user_id = int(parts[0])
            user = await self.fetch_user(user_id)
        except Exception as e:
            return await self.send_and_clean(message.channel, "couldn't find that user")

        dm_message = parts[1]

        try:
            await user.send(dm_message)
            await self.send_and_clean(message.channel, f"message sent to {user}")
        except Exception as e:
            await self.send_and_clean(message.channel, f"failed to send message {e}")


    async def cmd_targetdmspam(self, message, command_args):
        parts = command_args.split(maxsplit=2)
        if len(parts) < 3:
            return await self.send_and_clean(message.channel, "usage nux spam <user_id> <message>")

        try:
            user_id = int(parts[0])
            user = await self.fetch_user(user_id)
        except Exception as e:
            return await self.send_and_clean(message.channel, "couldn't find that user")

        dm_message = parts[1]
        spam_count = self.rand.randint(50, 150)

        await self.send_and_clean(message.channel, f"spamming {user} {spam_count} times")

        try:
            for i in range(spam_count):
                await user.send(dm_message)
                await asyncio.sleep(1.09)
            await self.send_and_clean(message.channel, f"finished spamming {user}")
        except Exception as e:
            await self.send_and_clean(message.channel, f"failed during spam {e}")

    async def cmd_uptime(self, message, command_args=""):
        uptime_seconds = (datetime.datetime.utcnow() - self.start_time).total_seconds()
        uptime_str = str(datetime.timedelta(seconds=int(uptime_seconds)))

        memory = psutil.virtual_memory()
        cpu_usage = psutil.cpu_percent()
        ram_usage = memory.percent

        msg = (
            f"uptime {uptime_str}\n"
            f"total cpu usage {cpu_usage}%\n"
            f"total ram usage {ram_usage}%\n"
        )

        await self.send_and_clean(message.channel, msg)

    async def cmd_qr(self, message, command_args):
        text = command_args
        if not text:
            return await self.send_and_clean(message.channel, "send me some text or a link to make a qr code")

        parsed = urllib.parse.urlparse(text)
        if parsed.scheme and parsed.netloc:
            qr_data = text
        else:
            qr_data = urllib.parse.quote(text)

        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        with io.BytesIO() as image_binary:
            img.save(image_binary, "PNG")
            image_binary.seek(0)
            await self.send_and_clean(message.channel, file=discord.File(fp=image_binary, filename="qr.png"))

    @owner_only()
    async def cmd_nickname(self, message, command_args):
       new_nick = command_args

       if not new_nick:
            await self.send_and_clean(message.channel, "please tell me the new nickname")
            return

       if message.guild is None:
            await self.send_and_clean(message.channel, "this command only works in a server text channel")
            return

       me = message.guild.get_member(self.user.id)

       try:
           await me.edit(nick=new_nick)
           await self.send_and_clean(message.channel, f"nickname changed to {new_nick}")
       except Exception as e:
           await self.send_and_clean(message.channel, f"failed to change nickname {e}")

    async def cmd_emc(self, message, command_args):
        text = command_args
        if not text:
            await self.send_and_clean(message.channel, "please provide the text to encode")
            return
        words = text.lower().split(' ')
        encoded_words = []
        for word in words:
            encoded_chars = []
            for char in word:
                morse = MORSE_CODE_DICT.get(char, '?')
                encoded_chars.append(morse)
            if encoded_chars:
                encoded_words.append(" ".join(encoded_chars))
        result = " / ".join(encoded_words)
        await self.send_and_clean(message.channel, f"```{result}```")

    async def cmd_dmc(self, message, command_args):
        code = command_args
        if not code:
            await self.send_and_clean(message.channel, "please provide the morse code to decode")
            return
        words = code.split(" / ")
        decoded_words = []
        for word in words:
            chars = word.split()
            decoded_chars = [MORSE_CODE_REVERSE.get(c, '?') for c in chars]
            decoded_words.append("".join(decoded_chars))
        await self.send_and_clean(message.channel, " ".join(decoded_words))

    async def cmd_fakenitro(self, message, command_args):
        characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        fake_code = ''.join(self.rand.choices(characters, k=16))
        fake_link = f"https://discord.gift/{fake_code}"

        await message.channel.send(f"{fake_link}")

    async def cmd_achievement(self, message, command_args):
        text = command_args
        if not text:
            await self.send_and_clean(message.channel, "usage nux achievement <text>")
            return
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.af_api}/achievement?text={urllib.parse.quote(text)}"
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await self.send_and_clean(message.channel, "couldn't generate achievement")
                    img_bytes = await resp.read()
            buffer = io.BytesIO(img_bytes)
            await self.send_and_clean(message.channel, file=discord.File(buffer, filename="achievement.png"))
        except Exception as e:
            await self.send_and_clean(message.channel, "couldn't generate achievement")

    async def cmd_userinfo(self, message, command_args):
        if not message.mentions:
            await self.send_and_clean(message.channel, "please mention a user to inspect")
            return

        user = message.mentions[0]
        created_at = user.created_at.strftime("%Y-%m-%d %H:%M:%S")
        joined_at = None

        if getattr(message.channel, "guild", None) is not None:
            member = message.channel.guild.get_member(user.id)
            if member and member.joined_at:
                joined_at = member.joined_at.strftime("%Y-%m-%d %H:%M:%S")

        info = f"user info\n"
        info += f"username {user}\n"
        info += f"id {user.id}\n"
        info += f"account created {created_at}\n"
        if joined_at:
            info += f"joined server {joined_at}\n"
        info += f"bot {'yes' if user.bot else 'no'}\n"

        if hasattr(user, 'global_name') and user.global_name:
            info += f"global display name {user.global_name}\n"

        if hasattr(user, 'accent_color') and user.accent_color:
            info += f"accent color {user.accent_color}\n"

        if user.avatar:
            info += f"avatar {user.avatar.url}\n"
        else:
            info += f"avatar none\n"

        if hasattr(user, 'banner') and user.banner:
            info += f"banner {user.banner.url}\n"

        if hasattr(user, 'public_flags') and user.public_flags:
            badges = [flag.name.replace("_", " ").title() for flag in user.public_flags.all()]
            info += f"badges {', '.join(badges)}\n"

        await self.send_and_clean(message.channel, info)


    async def cmd_inviteinfo(self, message, command_args):
        parts = command_args.split(maxsplit=1)
        if len(parts) < 1:
            await self.send_and_clean(message.channel, "usage nux inviteinfo <invite_code_or_url>")
            return

        invite_input = parts[0]

        match = re.search(
            r"(?:https?://)?(?:www\.)?(?:discord\.gg|discordapp\.com/invite)/?([a-zA-Z0-9\-]+)",
            invite_input,
            re.IGNORECASE
        )

        if not match:
            invite_code = invite_input.strip()
        else:
            invite_code = match.group(1)

        url = f"https://discord.com/api/v10/invites/{invite_code}?with_counts=true"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await self.send_and_clean(message.channel, "failed to fetch invite info invite might be invalid or expired")
                    return

                data = await resp.json()

        guild = data.get("guild")
        channel = data.get("channel")
        inviter = data.get("inviter")
        approximate_presence_count = data.get("approximate_presence_count")
        approximate_member_count = data.get("approximate_member_count")
        expires_at = data.get("expires_at")

        print(f"debug: extracted invite code: {invite_code}")

        url = f"https://discord.com/api/v10/invites/{invite_code}?with_counts=true"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as resp:
                    print(f"debug: discord api response status: {resp.status}")
                    if resp.status != 200:
                        return await self.send_and_clean(message.channel, "failed to fetch invite info invite might be invalid or expired")

                    data = await resp.json()
                    print(f"debug: discord api response data: {json.dumps(data, indent=2)}")

            except aiohttp.ClientError as e:
                print(f"error: aiohttp client error: {e}")
                return await self.send_and_clean(message.channel, f"network error while fetching invite info: {e}")
            except json.JSONDecodeError as e:
                print(f"error: json decode error: {e}")
                return await self.send_and_clean(message.channel, f"failed to parse invite info: {e}")
            except Exception as e:
                print(f"error: unexpected error: {e}")
                return await self.send_and_clean(message.channel, f"an unexpected error occurred: {e}")

        guild = data.get("guild")
        channel = data.get("channel")
        inviter = data.get("inviter")
        approximate_presence_count = data.get("approximate_presence_count")
        approximate_member_count = data.get("approximate_member_count")
        expires_at = data.get("expires_at")

        msg = f"invite info\n"
        if guild:
            msg += f"guild name {guild.get('name')}\n"
            msg += f"guild id {guild.get('id')}\n"
            msg += f"guild verified {'yes' if guild.get('verified') else 'no'}\n"
        if channel:
            msg += f"channel name {channel.get('name')} (id {channel.get('id')})\n"
        if inviter:
            inviter_name = inviter.get('global_name') or (f"{inviter.get('username')}" if inviter.get('discriminator') != "0" else inviter.get('username'))
            msg += f"inviter {inviter_name} (id {inviter.get('id')})\n"
        if approximate_presence_count is not None:
            msg += f"online members (approx) {approximate_presence_count}\n"
        if approximate_member_count is not None:
            msg += f"total members (approx) {approximate_member_count}\n"
        if expires_at:
            msg += f"expires at {expires_at}\n"

        await self.send_and_clean(message.channel, (msg))

    async def cmd_help(self, message, command_args=""):
        help_msg = self.build_help_message()
        chunks = self.split_message(help_msg)
        for chunk in chunks:
            await self.send_and_clean(message.channel, chunk)

    async def cmd_spacedhelp(self, message, command_args=""):
        help_msg = self.build_spaced_help_message()
        chunks = self.split_message(help_msg)
        async with message.channel.typing():
            for chunk in chunks:
                msg = await message.channel.send(chunk)
                await asyncio.sleep(2.3)

    async def delete_after_delay(self, msg, delay):
        await asyncio.sleep(delay)
        await msg.delete()

    def split_message(self, text, max_length=2000):
        lines = text.split('\n')
        chunks = []
        current_chunk = ''

        for line in lines:
            if len(current_chunk) + len(line) + 1 > max_length:
                chunks.append(current_chunk)
                current_chunk = ''
            current_chunk += line + '\n'

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    async def cmd_didyoumean(self, message, command_args):
        args = command_args.split(" - ")

        if len(args) != 2:
            await self.send_and_clean(message.channel, "usage nux didyoumean <text1> - <text2>")
            return

        text1, text2 = args
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.af_api}/didyoumean?top={urllib.parse.quote(text1)}&bottom={urllib.parse.quote(text2)}"
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await self.send_and_clean(message.channel, "couldn't generate image")
                    img_bytes = await resp.read()
            buffer = io.BytesIO(img_bytes)
            await self.send_and_clean(message.channel, file=discord.File(buffer, filename="didyoumean.png"))
        except Exception as e:
            await self.send_and_clean(message.channel, "couldn't generate image")

    async def cmd_facts(self, message, command_args):
        text = command_args
        if not text:
            await self.send_and_clean(message.channel, "usage nux facts <text>")
            return
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.af_api}/facts?text={urllib.parse.quote(text)}"
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await self.send_and_clean(message.channel, "couldn't generate facts")
                    img_bytes = await resp.read()
            buffer = io.BytesIO(img_bytes)
            await self.send_and_clean(message.channel, file=discord.File(buffer, filename="facts.png"))
        except Exception as e:
            await self.send_and_clean(message.channel, "couldn't generate facts")

    async def cmd_scroll(self, message, command_args):
        text = command_args
        if not text:
            await self.send_and_clean(message.channel, "usage nux scroll <text>")
            return
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.af_api}/scroll?text={urllib.parse.quote(text)}"
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await self.send_and_clean(message.channel, "couldn't generate scroll")
                    img_bytes = await resp.read()
            buffer = io.BytesIO(img_bytes)
            await self.send_and_clean(message.channel, file=discord.File(buffer, filename="scroll.png"))
        except Exception as e:
            await self.send_and_clean(message.channel, "couldn't generate scroll")

    async def cmd_pornhub(self, message, command_args):
        args = command_args.split(" - ")

        if len(args) != 2:
            await self.send_and_clean(message.channel, "usage nux pornhub <text1> - <text2>")
            return

        text1, text2 = args
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.af_api}/pornhub?text={urllib.parse.quote(text1)}&text2={urllib.parse.quote(text2)}"
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await self.send_and_clean(message.channel, "couldn't generate image")
                    img_bytes = await resp.read()
            buffer = io.BytesIO(img_bytes)
            await self.send_and_clean(message.channel, file=discord.File(buffer, filename="pornhub.png"))
        except Exception as e:
            await self.send_and_clean(message.channel, "couldn't generate image")

    async def cmd_hentai(self, message, commands_args=""):
        r = requests.get("https://nekobot.xyz/api/image?type=" + self.rand.choice(['hentai', 'hboobs', 'hthigh']))
        data = r.json()
        await self.send_and_clean(message.channel, data.get("message", "no image found"))

    async def cmd_thighs(self, message, command_args=""):
        r = requests.get("https://nekobot.xyz/api/image?type=thigh")
        data = r.json()
        await self.send_and_clean(message.channel, data.get("message", "no image found"))

    async def cmd_ass(self, message, command_args=""):
        r = requests.get("https://nekobot.xyz/api/image?type=ass")
        data = r.json()
        await self.send_and_clean(message.channel, data.get("message", "no image found"))

    async def cmd_boobs(self, message, command_args=""):
        r = requests.get("https://nekobot.xyz/api/image?type=boobs")
        data = r.json()
        await self.send_and_clean(message.channel, data.get("message", "no image found"))

    async def cmd_pussy(self, message, command_args=""):
        r = requests.get("https://nekobot.xyz/api/image?type=pussy")
        data = r.json()
        await self.send_and_clean(message.channel, data.get("message", "no image found"))

    async def cmd_pgif(self, message, command_args=""):
        r = requests.get("https://nekobot.xyz/api/image?type=pgif")
        data = r.json()
        await self.send_and_clean(message.channel, data.get("message", "no image found"))

    async def cmd_neko(self, message, command_args=""):
        r = requests.get("https://nekobot.xyz/api/image?type=neko")
        data = r.json()
        await self.send_and_clean(message.channel, data.get("message", "no image found"))

    async def _nekos_life_image_command(self, message, image_type):
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://nekos.life/api/v2/img/{image_type}') as resp:
                if resp.status != 200:
                    return await self.send_and_clean(message.channel, f"couldn't fetch {image_type} image")
                data = await resp.json()
                await self.send_and_clean(message.channel, data.get("url", "no image found"))

    async def cmd_hug(self, message, command_args=""):
        if not message.mentions:
            await self.send_and_clean(message.channel, "you need to mention someone to hug")
            return

        target = message.mentions[0]
        author = message.author

        async with aiohttp.ClientSession() as session:
            async with session.get('https://nekos.life/api/v2/img/hug') as resp:
                if resp.status != 200:
                    await self.send_and_clean(message.channel, "couldn't fetch hug gif")
                    return
                try:
                    data = await resp.json()
                    gif_url = data.get('url')
                    if not gif_url:
                        return await self.send_and_clean(message.channel, "couldn't get hug gif")
                except Exception:
                    return await self.send_and_clean(message.channel, "couldn't fetch hug gif")

        hug_messages = [
            f"{author.mention} [hugs]({gif_url}) {target.mention}",
            f"{author.mention} [embraces]({gif_url}) {target.mention}",
        ]

        msg = self.rand.choice(hug_messages)
        await self.send_and_clean(message.channel, msg)

    async def cmd_pat(self, message, command_args=""):
        if not message.mentions:
            await self.send_and_clean(message.channel, "you need to mention someone to pat")
            return

        target = message.mentions[0]
        author = message.author

        async with aiohttp.ClientSession() as session:
            async with session.get('https://nekos.life/api/v2/img/pat') as resp:
                if resp.status != 200:
                    await self.send_and_clean(message.channel, "couldn't fetch pat gif")
                    return
                try:
                    data = await resp.json()
                    gif_url = data.get('url')
                    if not gif_url:
                        return await self.send_and_clean(message.channel, "couldn't get pat gif")
                except Exception:
                    return await self.send_and_clean(message.channel, "couldn't fetch pat gif")

        pat_messages = [
            f"{author.mention} [pats]({gif_url}) {target.mention}",
            f"{author.mention} [gently pats]({gif_url}) {target.mention}",
        ]

        msg = self.rand.choice(pat_messages)
        await self.send_and_clean(message.channel, msg)

    async def cmd_slap(self, message, command_args=""):
        if not message.mentions:
            await self.send_and_clean(message.channel, "you need to mention someone to slap")
            return

        target = message.mentions[0]
        author = message.author

        async with aiohttp.ClientSession() as session:
            async with session.get('https://nekos.life/api/v2/img/slap') as resp:
                if resp.status != 200:
                    await self.send_and_clean(message.channel, "couldn't fetch slap gif")
                    return
                try:
                    data = await resp.json()
                    gif_url = data.get('url')
                    if not gif_url:
                        return await self.send_and_clean(message.channel, "couldn't get slap gif")
                except Exception:
                    return await self.send_and_clean(message.channel, "couldn't fetch slap gif")

        slap_messages = [
            f"{author.mention} [slaps]({gif_url}) {target.mention}",
            f"{author.mention} [gives a firm slap to]({gif_url}) {target.mention}",
        ]

        msg = self.rand.choice(slap_messages)
        await self.send_and_clean(message.channel, msg)

    async def cmd_echo(self, message, command_args):
        text = command_args
        if not text:
            await self.send_and_clean(message.channel, "you didn't tell me what to echo")
        else:
            await self.send_and_clean(message.channel, text)

    async def cmd_waveform(self, message, command_args):
        args = message.content.strip().split()
        if len(args) != 4:
            await message.channel.send("usage nux freq <frequency_hz> <wave_type (sine/square/triangle)>")
            return

        try:
            freq = float(args[2])
            wave_type = args[3].lower()
            duration = 10
            sample_rate = 128000

            t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

            if wave_type == "sine":
                waveform = np.sin(2 * np.pi * freq * t)
            elif wave_type == "square":
                waveform = sp_signal.square(2 * np.pi * freq * t)
            elif wave_type == "triangle":
                waveform = sp_signal.sawtooth(2 * np.pi * freq * t, 0.5)
            else:
                await message.channel.send("invalid waveform type use sine, square, or triangle")
                return

            waveform = waveform * 0.5

            filename = f"waveform_{freq}hz_{wave_type}.wav"
            sf.write(filename, waveform, sample_rate)

            await message.channel.send(file=discord.File(filename))
            os.remove(filename)

        except Exception as e:
            await message.channel.send(f"error {str(e)}")

    async def cmd_tts(self, message, command_args):
        text = command_args.strip()
        if not text:
            return await self.send_and_clean(message.channel, "speak what, darling")

        try:
            tts = gTTS(text=text, lang="en")
            buffer = io.BytesIO()
            tts.write_to_fp(buffer)
            buffer.seek(0)
            await self.send_and_clean(message.channel, file=discord.File(buffer, "tts.mp3"))
        except Exception as e:
            return await self.send_and_clean(message.channel, f"failed to generate tts: {e}")
        
    async def cmd_ascii(self, message, command_args):
        text = command_args
        if not text:
            return await self.send_and_clean(message.channel, "ascii needs a soul to shape")

        try:
            output = figlet_format(text)
            if len(output) > 1900:
                output = output[:1900] + "..."
            await self.send_and_clean(message.channel, f"```{output}```")
        except Exception as e:
            await self.send_and_clean(message.channel, "couldn't ascii-fy that")

    async def cmd_calc(self, message, command_args):
        expr = command_args
        if not expr:
            return await self.send_and_clean(message.channel, "give me something to calculate, genius")
        try:
            result = eval(expr, {"__builtins__": None}, {"sqrt": math.sqrt, "pow": pow, "abs": abs})
            await self.send_and_clean(message.channel, f"`{expr}` = **{result:,}**")
        except Exception as e:
            await self.send_and_clean(message.channel, "that's not a valid expression")

    async def cmd_cleardmsent(self, message, command_args=""):
        channel = message.channel
        channel_id = channel.id

        if not hasattr(self, 'cdm_tasks'):
            self.cdm_tasks = {}

        existing = self.cdm_tasks.get(channel_id)

        if existing and not existing.done():
            existing.cancel()
            try:
                await existing
            except asyncio.CancelledError:
                pass
            self.cdm_tasks.pop(channel_id, None)
            await self.send_and_clean(channel, "stopped cdm deletions")
            return

        task = asyncio.create_task(self._cdm_worker(channel))
        self.cdm_tasks[channel_id] = task
        await self.send_and_clean(channel, "started cdm deletions — run `nux cdm` again to stop")

    async def _cdm_worker(self, channel):
        deleted_count = 0
        channel_id = channel.id
        try:
            while True:
                found = False
                async for msg in channel.history(limit=250):
                    if channel_id not in self.cdm_tasks or self.cdm_tasks.get(channel_id) is None:
                        raise asyncio.CancelledError()
                    if msg.author.id == self.user.id:
                        found = True
                        try:
                            await msg.delete()
                            deleted_count += 1
                            await asyncio.sleep(1.25)
                        except asyncio.CancelledError:
                            raise
                        except Exception:
                            await asyncio.sleep(0.5)

                if not found:
                    break

                await asyncio.sleep(0.5)

        except asyncio.CancelledError:
            return
        finally:
            try:
                self.cdm_tasks.pop(channel_id, None)
            except Exception:
                pass

        try:
            await self.send_and_clean(channel, f"cdm finished, deleted {deleted_count} messages")
        except Exception:
            pass

    async def cmd_burstcdm(self, message, command_args=""):
        channel = message.channel
        deleted = 0
        async for msg in channel.history(limit=100):
            if msg.author.id == self.user.id:
                try:
                    await msg.delete()
                    deleted += 1
                    if deleted >= 5:
                        break
                    await asyncio.sleep(0.1)
                except:
                    pass
        if deleted > 0:
            await self.send_and_clean(channel, f"burst deleted {deleted} messages")

    async def cmd_nsfwhelp(self, message, command_args=""):
        nsfwhelp_msg = self.build_nsfwhelp_message()
        chunks = self.split_message(nsfwhelp_msg)

        for chunk in chunks:
            msg = await message.channel.send(chunk)
            asyncio.create_task(self.delete_after_delay(msg, 15))

    async def cmd_ownercmds(self, message, command_args=""):
        help_text = (
            "available commands\n"
            "- `nux nickname <nick>` changes my nickname in the current server\n"
            "- `nux cleaner <delay/on/off> <delay:time>` configure the message cleaner\n"
            "- `nux eval`  executes code straight into the terminal\n"
            "- `nux leaveguild`  leaves the guild with the specified id\n"
            "- `nux restart`  restarts nuxified - is slightly buggy and results in two of me running at once\n"
            "- `nux simulate <@person> <command>` uses a command as the person mentioned\n"
            "- `nux backup` saves my friends list and servers/guilds i'm to a file for me\n"
            "- `nux pull` pulls the latest changes from GitHub using git pull\n"
            "- `nux ai setup` sets up the ai personality for openrouter (dm only)\n"
            "- `nux ai preset <preset_name>` loads a saved ai personality preset (dm only)\n"
            "- `nux config` shows the current confg, and ai config.\n"
            "- `nux weatherip` enables/disables ip geolocation for weather command, off by default to avoid accidental doxxing\n\n"
                "[⠀](https://cdn.discordapp.com/attachments/1136379503116025939/1387306227842945106/image.png?ex=685cdd1b&is=685b8b9b&hm=25ee59d3d9c686073400a51a4f70fb45e9d036ce9e32293cf9afce57081fac15&)\n\n"
                "**how**\n"
                "using a @owner_only() decorator, that pulls my own id and uses it to make it so if the command has that decorator, only i can use it, and this is what it looks like in use\n-- you can try to use the command, but obviously nothing will happen --[⠀](https://cdn.discordapp.com/attachments/1136379503116025939/1387305398964326440/image.png?ex=685cdc56&is=685b8ad6&hm=c66308c3bc829df58dd0706ec264569a2aeffc4c58d5d1ea321b2ba57e4ea44f&)"
        )
        await self.send_and_clean(message.channel, help_text)

    async def cmd_zalgo(self, message, command_args):
        text = command_args
        if not text:
            return await self.send_and_clean(message.channel, "zalgo what")
        corrupted = ''.join(c + ''.join(self.rand.choices(zalgo_up, k=self.rand.randint(1, 3))) for c in text)
        await self.send_and_clean(message.channel, corrupted)

    async def cmd_cuddle(self, message, command_args):
        if not message.mentions:
            await self.send_and_clean(message.channel,"you need to mention someone to cuddle")
            return

        target = message.mentions[0]
        author = message.author

        async with aiohttp.ClientSession() as session:
            async with session.get('https://nekos.life/api/v2/img/cuddle') as resp:
                if resp.status != 200:
                    await self.send_and_clean(message.channel, "couldn't fetch cuddle gif")
                    return
                try:
                    data = await resp.json()
                    gif_url = data.get('url')
                    if not gif_url:
                        return await self.send_and_clean(message.channel, "couldn't get cuddle gif")
                except Exception:
                    return await self.send_and_clean(message.channel, "couldn't fetch cuddle gif")

        cuddle_messages = [
            f"{author.mention} [cuddles]({gif_url}) {target.mention}",
            f"{author.mention} [snuggles]({gif_url}) {target.mention}",
        ]

        msg = self.rand.choice(cuddle_messages)
        await self.send_and_clean(message.channel, msg)

    async def cmd_flip(self, message, command_args):
        text = command_args
        if not text:
            return await self.send_and_clean(message.channel, "what the flip")
        flipped = text[::-1].translate(flip_map)
        await self.send_and_clean(message.channel, flipped)

    async def cmd_weather(self, message, command_args):
        args = command_args.strip()
        if not args:
            if not self.weather_ip_enabled:
                return await self.send_and_clean(message.channel, "usage nux weather <location>")
            async with aiohttp.ClientSession() as session:
                resp = await session.get('https://api.ipify.org')
                if resp.status != 200:
                    return await self.send_and_clean(message.channel, "failed to get IP")
                ip = await resp.text()
                data = await session.get(f'https://ipapi.co/{ip}/json')
                if data.status != 200:
                    return await self.send_and_clean(message.channel, "failed to get geolocation")
                data = await data.json()
                city = data.get('city')
                if not city:
                    return await self.send_and_clean(message.channel, "couldn't determine city from IP")
                location = city
        else:
            location = args
        url = f"https://wttr.in/{location}?format=3"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await self.send_and_clean(message.channel, "couldn't fetch weather info")
                weather = await resp.text()
                await self.send_and_clean(message.channel, weather)

    @owner_only()
    async def cmd_weatherip_toggle(self, message, command_args):
        self.weather_ip_enabled = not self.weather_ip_enabled
        self.save_config()
        status = "enabled" if self.weather_ip_enabled else "disabled"
        await self.send_and_clean(message.channel, f"IP geolocation for weather {status}")

    @owner_only()
    async def cmd_guilds(self, message, command_args=""):
        guild_list = [f"{g.name} (id {g.id})" for g in self.guilds]
        if not guild_list:
            await self.send_and_clean(message.channel, "i'm not in any guilds")
        else:
            msg = "guilds i'm in\n" + "\n".join(guild_list)
            await self.send_and_clean(message.channel, msg)

    # i have to rework this command, i dont really like how it is rn
    async def cmd_dlmedia(self, message, command_args):
        tokens = command_args.rsplit(' ', 1)

        if len(tokens) != 2:
            await self.send_and_clean(message.channel, "usage nux dlmedia <url> <audio|video>")
            return

        url, mode = tokens
        mode = mode.lower()
        if mode not in ("audio", "video"):
            await self.send_and_clean(message.channel, "usage nux dlmedia <url> <audio|video>")
            return
        platform = "unknown"
        compress_required = False

        if "tiktok.com" in url:
            platform = "tiktok"
        elif "pinterest.com" in url or "pin.it" in url:
            platform = "pinterest"
            compress_required = True
        elif "youtube.com" in url or "youtu.be" in url:
            platform = "youtube"
        elif "twitter.com" in url or "x.com" in url:
            platform = "twitter"
            compress_required = True
        elif "instagram.com" in url:
            platform = "instagram"
            compress_required = True
        elif "reddit.com" in url or "v.redd.it" in url:
            platform = "reddit"
        elif "facebook.com" in url:
            platform = "facebook"
            compress_required = True
        elif "soundcloud.com" in url:
            platform = "soundcloud"
            compress_required = True
        elif "twitch.tv" in url:
            platform = "twitch"
        else:
            await self.send_and_clean(message.channel, "unsupported url supported tiktok, pinterest, youtube, twitter, instagram, reddit")
            return

        if mode == "audio":
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'noplaylist': True,
                'outtmpl': '%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
            }
        else:
            ydl_opts = {
                'format': 'mp4[filesize<8M]/mp4[height<=480]/mp4/best',
                'quiet': True,
                'noplaylist': True,
                'merge_output_format': 'mp4',
                'outtmpl': '%(title)s.%(ext)s',
            }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if mode == "audio":
                    filename = os.path.splitext(filename)[0] + ".mp3"

            file_size = os.path.getsize(filename) / (1024 * 1024)

            if mode == "video" and file_size > 8:
                if compress_required:
                    await self.send_and_clean(message.channel, f"video is too large to send ({file_size:.2f} mb) compressing")

                    compressed_filename = f"compressed_{os.path.basename(filename)}"

                    ffmpeg_command = [
                        'ffmpeg', '-i', filename,
                        '-vf', 'scale=640:-2',
                        '-c:v', 'libx264',
                        '-preset', 'fast',
                        '-crf', '32',
                        '-c:a', 'aac',
                        '-b:a', '96k',
                        compressed_filename,
                        '-y'
                    ]

                    process = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                    if process.returncode != 0 or not os.path.exists(compressed_filename):
                        await self.send_and_clean(message.channel, f"compression failed try downloading manually {url}")
                        os.remove(filename)
                        return

                    compressed_size = os.path.getsize(compressed_filename) / (1024 * 1024)

                    if compressed_size > 8:
                        await self.send_and_clean(message.channel, f"even after compression, the video is too large to send ({compressed_size:.2f} mb) try downloading manually {url}")
                        os.remove(filename)
                        os.remove(compressed_filename)
                        return

                    compression_ratio = (compressed_size / file_size) * 100

                    await self.send_and_clean(
                        message.channel,
                        f"downloaded and compressed {platform} video\noriginal size {file_size:.2f} mb\ncompressed size {compressed_size:.2f} mb\ncompression {compression_ratio:.1f}% of original size",
                        file=discord.File(compressed_filename)
                    )

                    os.remove(filename)
                    os.remove(compressed_filename)
                    return
                else:
                    await self.send_and_clean(message.channel, f"video is too large to send ({file_size:.2f} mb) sending direct download link instead")

                    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                        info = ydl.extract_info(url, download=False)

                    formats = info.get('formats')
                    if not formats:
                        await self.send_and_clean(message.channel, "failed to retrieve video formats")
                        os.remove(filename)
                        return

                    download_url = None
                    for fmt in reversed(formats):
                        if fmt.get('url'):
                            download_url = fmt['url']
                            break

                    if not download_url:
                        await self.send_and_clean(message.channel, "failed to retrieve direct download link")
                        os.remove(filename)
                        return

                    await self.send_and_clean(message.channel, f"direct video link {download_url}")
                    os.remove(filename)
                    return

            await self.send_and_clean(
                message.channel,
                f"downloaded {platform} {mode}",
                file=discord.File(filename)
            )
            os.remove(filename)

        except Exception as e:
            await self.send_and_clean(message.channel, f"failed to download {mode} {e}")
            if 'filename' in locals() and os.path.exists(filename):
                os.remove(filename)

    async def cmd_base64(self, message, command_args):
        content = message.content.strip()
        args = content[len("nux base64"):].strip().split(maxsplit=1)

        if len(args) < 2 or args[0] not in ["encode", "decode"]:
            return await self.send_and_clean(message.channel, "usage nux base64 <encode|decode> <text>")

        action = args[0]
        text = args[1]

        try:
            if action == "encode":
                result = base64.b64encode(text.encode()).decode()
            else:
                result = base64.b64decode(text.encode()).decode()

            await self.send_and_clean(message.channel, result)
        except Exception:
            await self.send_and_clean(message.channel, "invalid input")

    async def cmd_hash(self, message, command_args):
        content = message.content.strip()
        args = content[len("nux hash"):].strip().split(maxsplit=1)

        if len(args) < 1:
            return await self.send_and_clean(message.channel, "usage nux hash <algorithm> <text>\n\n-# supported algorithms: md5, sha1, sha256, sha512. type \"nux hash help\" for the help page.")

        algorithm = args[0].lower()

        if algorithm == "help":
            return await self.send_and_clean(message.channel, "hashes **cannot** be reversed, so you cannot get the original text back. however, if you run it again (e.g. ```nux hash md5 test```) it will always return the same hash, but that's the only thing you could do.\n\n-# test in md5 hash is \"098f6bcd4621d373cade4e832627b4f6\" by the way.")

        if len(args) < 2:
            return await self.send_and_clean(message.channel, "usage nux hash <algorithm> <text>\n\n-# supported algorithms: md5, sha1, sha256, sha512. type \"nux hash help\" for the help page.")

        text = args[1]

        try:
            if algorithm == "md5":
                hashed = hashlib.md5(text.encode()).hexdigest()
            elif algorithm == "sha1":
                hashed = hashlib.sha1(text.encode()).hexdigest()
            elif algorithm == "sha256":
                hashed = hashlib.sha256(text.encode()).hexdigest()
            elif algorithm == "sha512":
                hashed = hashlib.sha512(text.encode()).hexdigest()
            else:
                return await self.send_and_clean(message.channel, "unsupported algorithm use md5, sha1, sha256, or sha512")

            await self.send_and_clean(message.channel, f"hash ({algorithm}) {hashed}")
        except Exception as e:
            await self.send_and_clean(message.channel, f"hashing failed {e}")

    async def cmd_wordcount(self, message, command_args):
        text = command_args
        if not text:
            return await self.send_and_clean(message.channel, "usage nux wordcount <text>")

        words = text.split()
        await self.send_and_clean(message.channel, f"word count {len(words)}")

    async def cmd_charfreq(self, message, command_args):
        text = command_args
        if not text:
            return await self.send_and_clean(message.channel, "usage nux charfreq <text>")

        freq = {}
        for char in text:
            freq[char] = freq.get(char, 0) + 1

        freq_str = "\n".join([f"'{c}': {count}" for c, count in sorted(freq.items())])
        await self.send_and_clean(message.channel, f"character frequency\n```{freq_str}```")

    async def cmd_mock(self, message, command_args):
        text = command_args
        if not text:
            await self.send_and_clean(message.channel, "mock what, genius")
            return

        mocked = ''.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(text))
        await self.send_and_clean(message.channel, mocked)

    async def cmd_aping(self, message, command_args):
        await self.send_and_clean(message.channel, f"nux base64 decode dW5kZWFkIFsyXQ==.")

    @owner_only()
    async def cmd_cleaner(self, message, command_args=""):
        args = command_args.split()
        await message.delete()
        if not args:
            status = "enabled" if self.cleaner_settings["enabled"] else "disabled"
            await self.send_and_clean(message.channel, f"cleaner is currently {status} with a delay of {self.cleaner_settings['delay']}s")
            return
        if args[0].lower() == "on":
            self.cleaner_settings["enabled"] = True
            self.save_config()
            await self.send_and_clean(message.channel, "self-cleaner is now enabled")
        elif args[0].lower() == "off":
            self.cleaner_settings["enabled"] = False
            self.save_config()
            await self.send_and_clean(message.channel, "self-cleaner is now disabled")
        elif args[0].lower() == "delay" and len(args) > 1:
            try:
                delay = int(args[1])
                self.cleaner_settings["delay"] = max(0, delay)
                self.save_config()
                await self.send_and_clean(message.channel, f"cleaner delay set to {delay} seconds")
            except ValueError:
                await self.send_and_clean(message.channel, "invalid delay value")
        else:
            await self.send_and_clean(message.channel, "usage `nux cleaner on/off/delay <seconds>`")

    async def send_and_clean(self, channel, content=None, embed=None, **kwargs):
        if embed:
            msg = await channel.send(content, embed=embed, **kwargs)
        else:
            msg = await channel.send(content, **kwargs)
        if self.cleaner_settings.get("enabled", False):
            asyncio.create_task(self._delayed_delete(msg))
        return msg

    async def _delayed_delete(self, msg):
        await asyncio.sleep(self.cleaner_settings.get("delay", 3))
        try:
            await msg.delete()
        except Exception:
            pass

    @owner_only()
    async def cmd_ghost(self, message, command_args=""):
        if not self.ghost_mode:
            self.saved_activity = getattr(self.user, 'activity', None)
            self.saved_status = getattr(self.user, 'status', discord.Status.online)
            self.saved_status_enabled = self.status_enabled

            if self.status_task:
                self.status_task.cancel()
                self.status_task = None
            self.status_enabled = False 

            await self.change_presence(activity=None, status=discord.Status.offline)
            self.ghost_mode = True
            status_message = "active, profile is offline and messages delete after 15 seconds."
        else: 
            self.ghost_mode = False
            self.status_enabled = self.saved_status_enabled 

            if self.status_enabled:
                await self.change_presence(activity=self.saved_activity, status=self.saved_status)
                if not self.status_task or self.status_task.done():
                    self.status_task = self.loop.create_task(self.change_status_periodically())
            else:
                await self.change_presence(activity=None, status=discord.Status.online)

            status_message = "inactive, profile is online and messages will not delete."

        self.save_config()
        await self.send_and_clean(message.channel, status_message)

    async def cmd_loser(self, message, command_args):
        async with message.channel.typing():
            await asyncio.sleep(17.3)
        msg = await message.channel.send("loser")
        await asyncio.sleep(0.5)
        await msg.delete()

    async def cmd_font(self, message, command_args=""):
        args = command_args.split()
        if len(args) < 1:
            await self.send_and_clean(message.channel, "usage nux font... *breath...* <arathos|berosong|betterfields|brunoblack|hanah|krondos|maskneyes|maytorm|onerock|rockaura|roomach|spider|thunder> <text>")
            return

        font_name = args[0].lower()
        text = ' '.join(args[1:])

        font_dir = 'dmfonts'
        available_fonts = {f.split('.')[0].lower(): f for f in os.listdir(font_dir) if f.endswith(('.ttf', '.otf'))}

        if font_name not in available_fonts:
            await self.send_and_clean(message.channel, f"font '{font_name}' not found available fonts {', '.join(available_fonts.keys())}")
            return

        font_path = os.path.join(font_dir, available_fonts[font_name])

        font = ImageFont.truetype(font_path, size=150)
        img = Image.new('RGBA', (1600, 400), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.text((50, 100), text, font=font, fill=(255, 255, 255, 255))

        file_path = "output.png"
        img.save(file_path)

        await message.channel.send(file=discord.File(file_path))
        os.remove(file_path)

    async def cmd_dadjoke(self, message, command_args):
        url = "https://icanhazdadjoke.com/"
        headers = {"accept": "application/json"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    await self.send_and_clean(message.channel, data.get("joke", "no dad jokes found your dad left"))
                else:
                    await self.send_and_clean(message.channel, "couldn't reach the dad joke server guess that's the joke")

    async def cmd_shorten(self, message, command_args):
        content = command_args

        if not content:
            return await self.send_and_clean(
                message.channel,
                "choose your shortener\n"
                "1 is.gd\n"
                "2 x.gd\n"
                "usage\n"
                "`nux shorten <number> <url>`"
            )

        parts = content.split(maxsplit=1)
        choice = parts[0]

        async def ask(question):
            await message.channel.send(question)
            try:
                reply = await self.wait_for(
                    "message",
                    check=lambda m: m.author == message.author and m.channel == message.channel,
                    timeout=60
                )
                text = reply.content.strip()
                if text.lower() in ("skip", "none", "blank") or text == "":
                    return ""
                return text
            except asyncio.TimeoutError:
                await self.send_and_clean(message.channel, "timed out waiting for your response")
                return None

        try:
            if choice == "1":
                if len(parts) < 2:
                    return await self.send_and_clean(message.channel, "missing url")
                url = parts[1]
                api_url = f"https://is.gd/create.php?format=simple&url={urllib.parse.quote(url)}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(api_url) as resp:
                        if resp.status != 200:
                            return await self.send_and_clean(message.channel, "couldn't shrink that one")
                        short_url = await resp.text()
                        if len(short_url) > 4000:
                            short_url = short_url[:3997] + "..."
                        return await self.send_and_clean(message.channel, short_url)

            elif choice == "2":
                if len(parts) < 2:
                    return await self.send_and_clean(message.channel, "missing url")
                url = parts[1]
                api_url = f"https://xgd.io/V1/shorten?url={urllib.parse.quote(url)}&key={XGD_API_KEY}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(api_url) as resp:
                        if resp.status != 200:
                            return await self.send_and_clean(message.channel, "couldn't shrink that one")
                        data = await resp.json()
                        if "shorturl" in data:
                            short_url = data["shorturl"]
                            if len(short_url) > 4000:
                                short_url = short_url[:3997] + "..."
                            return await self.send_and_clean(message.channel, short_url)
                        else:
                            return await self.send_and_clean(message.channel, "no shortened url returned")

            else:
                return await self.send_and_clean(message.channel, "invalid choice use 1, or 2.")

        except Exception as e:
            print("[shorten error]", repr(e))
            await self.send_and_clean(message.channel, f"something blocked the shortening spell `{e}`")

    async def cmd_id(self, message, command_args):
        async with message.channel.typing():
            await asyncio.sleep(3.627)
            user = message.author
            content = (
                f"username {user.name}\n"
                f"user id {user.id}\n"
                "you still exist"
            )
            await self.send_and_clean(message.channel, content)

    async def cmd_dumpdm(self, message, command_args):
        messages = []
        async with message.channel.typing():
            await asyncio.sleep(7.836)
            async for msg in message.channel.history(limit=2500, oldest_first=True):
                timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M")
                author = "you" if msg.author == self.user else msg.author.name
                messages.append(f"[{timestamp}] {author} {msg.content}")

        with open("dm_dump.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(messages))

        file = discord.File("dm_dump.txt")
        await self.send_and_clean(message.channel, "your archive is ready", file=file)

    async def change_status_periodically(self):
        status_messages = [
            "nuxified straight to you", #1
            "playing with hexxedspider", #2
            "hell blunt", #3
            "nux help (limited access)", #4
            "im probably sleeping or something", #5
            "nuxified: v4mpire + cl9udempire", #6
            "it's pronounced \"cloud 9 empire\", not \"clnineoud empire\"", #7
            "i think ive had enough of you", #8
            "i love headlessryn", #9
            "i got my hands on you , and i aint letting go", #10
            "i change this every minute cause im just like that", #11
            "dont you miss me", #12
            "im the man and im in my prime", #13
            "the raven is watching", #14
            "github coming soon (it is not) (probably) (it came out)", #15
            "i know you missed me", #16
            "felt silly and ended up blowing my head off", #17 
            "autistic echo chamber", #18
            "fuck", #19
            "im coming straight from hell with love", #19
            "i lo", #20
            "one status is 'i lo' when i meant to type i love you", #21
            "nah twin she got u blushin twin ah hell naw twin", #22
            "new update is insane", #23
            "hexxedspider situation is crazy", #24
            "why the fuck u peepin my status", #25
            "i have a ai responder, just ping me", #26
            "@headlessryn on instagram <3", #27
            "hexxedspider.github.io", #28
            "headlessryn.github.io (peep the tos)", #29
            "nukumoxy.netlify.app for errors", #30
            "bruh", #31
            "this account is on github", #32
            "github.com/hexxedspider/nuxified", #33
            "rip to @hexxedspider but we up", #34
            "rest in peace my beloved", #35
            "rest in pieces my beloved", #36
            "im always online", #37
            "if im offline then something's wrong", #38
            "if you want me to put something as my status just ask", #39
            "i can put whatever you want as my status if u ask", #40
            "like did u get the memo", #41
            "g59 on top", #42
            "whole lotta grey", #43
            "i dont do this", #44
            "i love my 6th grade gf", #45
            "message me something you want me to make my status", #46
            "i change this every minute btw", #47
            "HOW THE FUCK YOU GET BANNED FROM SPOTIFY", #48
            "im not active often", #49
            "we love casting spells", #50
            "i will add whatever you want here", #51
            "discord.gg/dEnF55hgaG - free movies + shows (owned by me!)", #52
            "the mitochondria is the powerhouse of the cell", #53
            "in my room!", #54
            "if i do, she may come to life", #55
            "spidergang, choppa cough!", #56
            "spidergang", #57
            "lil dvrkie!", #58
            "join up - https://discord.gg/eAmEAhKZhJ", #59
            "take my knife and carve the initals", #60
            "where is darkie?", #61
            "tf u mean meltdown\nlike autism or smth", #62
            "\"sigmas got a major hand on the war field\"", #63
            "\"I think we should do a treaty between Kingdom of shrimps and sigmas\"", #64
            "big dinosaur teeth", #65
            "Bubbles!", #66
            "Cheat Code Fanny magnet activated", #67
            "this is more than a sick love story", #68
            "love, i cant ignore you", #69
            "do anything for you", #70
            "spotify.com/playlist/7t0InrUUJIlkExhF6b2r4B?si=03052a278395491f", #71
            "as of nov 15th my status changes every 30 seconds" #72
        ]
        while True:
            new_status = self.rand.choice(status_messages)
            await self.change_presence(activity=discord.CustomActivity(name=new_status), status=discord.Status.online)
            await asyncio.sleep(30)

    @owner_only()
    async def cmd_statustoggle(self, message, command_args=""):
        if self.status_enabled:
            if self.status_task:
                self.status_task.cancel()
                self.status_task = None
            self.status_enabled = False
            self.save_config()
            await self.change_presence(activity=None, status=discord.Status.online) 
            await self.send_and_clean(message.channel, "status messages are now off")
        else:
            self.status_task = self.loop.create_task(self.change_status_periodically())
            self.status_enabled = True
            self.save_config()
            await self.send_and_clean(message.channel, "status messages are now on")

    async def cmd_nsfw(self, message, command_args=""):
        args = message.content.strip().split()

        if len(args) < 3:
            return await self.send_and_clean(message.channel, "usage nux nsfw <category> [number]\nunsure of the categories use nux nsfwlist")

        category = args[2].strip().lower()

        if category not in nsfw_categories:
            return await self.send_and_clean(message.channel, "invalid category use 'nux nsfwlist' to see available categories")

        num_requested = 1
        if len(args) >= 4:
            try:
                num_requested = int(args[3])
                if num_requested <= 0:
                    num_requested = 1
            except ValueError:
                num_requested = 1

        if isinstance(message.channel, discord.DMChannel):
            pass
        elif hasattr(message.channel, "is_nsfw") and not message.channel.is_nsfw():
            return await self.send_and_clean(message.channel, "this command can only be used in nsfw channels or direct messages")

        max_attempts = 10
        attempt = 0
        collected_media = []
        tried_subreddits = set()

        channel_id = message.channel.id
        if channel_id not in self.sent_media:
            self.sent_media[channel_id] = set()

        available_subreddits = nsfw_categories[category][:]
        while attempt < max_attempts and len(collected_media) < num_requested:
            possible_subreddits = [sub for sub in available_subreddits if sub not in tried_subreddits]

            if not possible_subreddits:
                print("all subreddits have been tried, stopping early")
                break

            subreddit = self.rand.choice(possible_subreddits)
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=250"
            headers = {"user-agent": "mozilla/5.0"}

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as resp:
                    if resp.status != 200:
                        attempt += 1
                        print(f"attempt {attempt} failed to fetch from r/{subreddit}")
                        tried_subreddits.add(subreddit)
                        continue

                    try:
                        data = await resp.json()
                        posts = data.get("data", {}).get("children", [])
                        print(f"attempt {attempt + 1} retrieved {len(posts)} posts from r/{subreddit}")

                        if not posts:
                            attempt += 1
                            tried_subreddits.add(subreddit)
                            continue

                        valid_posts = []
                        for post in posts:
                            post_data = post.get("data", {})
                            media_url = post_data.get("url", "")
                            is_stickied = post_data.get("stickied", False)

                            if is_stickied:
                                continue
                            if media_url.endswith(('.gif', '.mp4', '.webm')):
                                if media_url not in self.sent_media[channel_id]:
                                    valid_posts.append(media_url)

                        print(f"found {len(valid_posts)} new valid media posts in r/{subreddit}")

                        if not valid_posts:
                            attempt += 1
                            tried_subreddits.add(subreddit)
                            continue

                        self.rand.shuffle(valid_posts)

                        for media_url in valid_posts:
                            if len(collected_media) >= num_requested:
                                break
                            self.sent_media[channel_id].add(media_url)
                            collected_media.append(media_url)

                        attempt += 1

                    except Exception as e:
                        print(f"exception while processing subreddit {e}")
                        attempt += 1
                        tried_subreddits.add(subreddit)
                        continue

        if collected_media:
            for media_url in collected_media:
                try:
                    await self.send_and_clean(message.channel, media_url)
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"failed to send media {media_url} {e}")
            return
        else:
            return await self.send_and_clean(message.channel, "could not find valid media after several attempts try again later")

    async def cmd_redgif(self, message, command_args):
        args = message.content.strip().split()

        if len(args) < 3:
            return await self.send_and_clean(message.channel, "usage nux redgif <search term(s)> [number]")

        num_requested = 1
        if len(args) > 3:
            try:
                possible_num = int(args[-1])
                if possible_num > 0:
                    num_requested = possible_num
                    search_terms = args[2:-1]
                else:
                    search_terms = args[2:]
            except ValueError:
                search_terms = args[2:]
        else:
            search_terms = args[2:]

        search_term = " ".join(search_terms).strip().lower()

        if isinstance(message.channel, discord.DMChannel):
            pass
        elif hasattr(message.channel, "is_nsfw") and not message.channel.is_nsfw():
            return await self.send_and_clean(message.channel, "this command can only be used in nsfw channels or direct messages")

        api = RedGifsAPI()
        api.login()

        try:
            search_result = api.search(search_term, count=50)
            gifs = search_result.gifs

            if not gifs:
                return await self.send_and_clean(message.channel, f"no results found for '{search_term}'")

            channel_id = message.channel.id
            if channel_id not in self.sent_media:
                self.sent_media[channel_id] = set()

            valid_gifs = [gif.urls.hd for gif in gifs if gif.urls.hd not in self.sent_media[channel_id]]

            if not valid_gifs:
                return await self.send_and_clean(message.channel, "couldn't find new media, try again later")

            self.rand.shuffle(valid_gifs)

            sent_count = 0
            for gif_url in valid_gifs:
                if sent_count >= num_requested:
                    break
                try:
                    await self.send_and_clean(message.channel, gif_url)
                    self.sent_media[channel_id].add(gif_url)
                    sent_count += 1
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"failed to send media {gif_url} {e}")

            if sent_count == 0:
                await self.send_and_clean(message.channel, "failed to send media, please try again")

        except Exception as e:
            print(f"redgifs api error {e}")
            await self.send_and_clean(message.channel, "an error occurred while fetching redgifs content")
        finally:
            pass

    async def cmd_rule34(self, message, command_args):
        args = message.content.strip().split()

        if len(args) < 3:
            return await self.send_and_clean(message.channel, "usage nux rule34 <search term(s)> [number]")

        num_requested = 1
        if len(args) > 3:
            try:
                possible_num = int(args[-1])
                if possible_num > 0:
                    num_requested = possible_num
                    search_terms = args[2:-1]
                else:
                    search_terms = args[2:]
            except ValueError:
                search_terms = args[2:]
        else:
            search_terms = args[2:]

        search_tags = "+".join(search_terms).strip().lower()

        if isinstance(message.channel, discord.DMChannel):
            pass
        elif hasattr(message.channel, "is_nsfw") and not message.channel.is_nsfw():
            return await self.send_and_clean(message.channel, "this command can only be used in nsfw channels or direct messages")

        url = f"https://rule34.xxx/index.php?page=dapi&s=post&q=index&limit=100&tags={search_tags}"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await self.send_and_clean(message.channel, "failed to fetch results from rule34")

                    text = await resp.text()
                    root = ET.fromstring(text)
                    posts = root.findall('post')

                    if not posts:
                        return await self.send_and_clean(message.channel, f"no results found for '{search_tags.replace('+', ' ')}'")

                    channel_id = message.channel.id
                    if channel_id not in self.sent_media:
                        self.sent_media[channel_id] = []

                    valid_posts = []
                    for post in posts:
                        file_url = post.attrib.get('file_url')
                        if file_url and file_url not in self.sent_media[channel_id]:
                            valid_posts.append(file_url)

                    if not valid_posts:
                        return await self.send_and_clean(message.channel, "couldn't find new media, try again later")

                    self.rand.shuffle(valid_posts)

                    sent_count = 0
                    for file_url in valid_posts:
                        if sent_count >= num_requested:
                            break
                        try:
                            await self.send_and_clean(message.channel, file_url)
                            MAX_TRACKED_URLS = 500
                            self.sent_media[channel_id].append(file_url)
                            if len(self.sent_media[channel_id]) > MAX_TRACKED_URLS:
                                self.sent_media[channel_id].pop(0)
                            sent_count += 1
                            await asyncio.sleep(1)
                        except Exception as e:
                            print(f"failed to send media {file_url} {e}")

                    if sent_count == 0:
                        await self.send_and_clean(message.channel, "failed to send media, please try again")

            except Exception as e:
                print(f"rule34 api error {e}")
                await self.send_and_clean(message.channel, "an error occurred while fetching rule34 content")

    async def cmd_nsfwlist(self, message, command_args=""):
        categories = ', '.join(nsfw_categories.keys())
        return await self.send_and_clean(message.channel, f"available nsfw categories {categories}")

    async def cmd_define(self, message, command_args):
        term = command_args.strip()
        if not term:
            return await self.send_and_clean(message.channel, "define what")
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{term}"
        async with aiohttp.ClientSession() as s:
            resp = await s.get(url)
            if resp.status != 200:
                return await self.send_and_clean(message.channel, f"no proper definition found for {term}")
            try:
                data = await resp.json()
                if not data or len(data) == 0:
                    return await self.send_and_clean(message.channel, f"no proper definition found for {term}")
                entry = data[0]
                if "meanings" not in entry or not entry["meanings"]:
                    return await self.send_and_clean(message.channel, f"no proper definition found for {term}")
                meanings = entry["meanings"]
                if not meanings[0].get("definitions"):
                    return await self.send_and_clean(message.channel, f"no proper definition found for {term}")
                defs = meanings[0]["definitions"][0]
                definition = defs.get("definition", "—")
                example = defs.get("example")
                out = f"{term} {definition}"
                if example:
                    out += f"\n» {example}"
                await self.send_and_clean(message.channel, out)
            except Exception:
                await self.send_and_clean(message.channel, f"couldn't process definition for {term}")

    async def cmd_udefine(self, message, command_args):
        term = command_args.strip()
        if not term:
            return await self.send_and_clean(message.channel, "give me a word")
        url = f"http://api.urbandictionary.com/v0/define?term={term}"
        async with aiohttp.ClientSession() as s:
            resp = await s.get(url)
            data = await resp.json()
        lst = data.get("list", [])
        if not lst:
            return await self.send_and_clean(message.channel, f"no slang found for {term}")
        top = max(lst, key=lambda x: x.get("thumbs_up", 0))
        definition = top.get("definition", "").replace("[", "").replace("]", "")
        example = top.get("example", "").replace("[", "").replace("]", "")
        await self.send_and_clean(message.channel, f"{term} (ud) {definition}\n» {example}\n{top.get('thumbs_up',0)} | {top.get('thumbs_down',0)}")

    async def ask_openrouter(self, user_id, username, user_input):
        openrouter_key = os.getenv('OpenRouter')
        if not openrouter_key:
            return "openrouter token not set"
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"authorization": f"bearer {openrouter_key}", "content-type": "application/json"}
        personality = self.ai_config.get('personality', FIXED_AI_PART)
        if user_id not in self.conversations:
            self.conversations[user_id] = [{"role": "system", "content": personality}]
        user_message = f"From {username}: {user_input}"
        self.conversations[user_id].append({"role": "user", "content": user_message})
        self.conversations[user_id] = self.conversations[user_id][-30:]
        
        models = [
            "z-ai/glm-4.5-air:free",
            "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
            "meituan/longcat-flash-chat:free",
            "nousresearch/hermes-3-llama-3.1-405b:free",
            "arliai/qwq-32b-arliai-rpr-v1:free"
        ]
        
        for model in models:
            payload = {
                "model": model,
                "messages": self.conversations[user_id],
                "stream": False,
                "max_tokens": 350
            }
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=payload) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            reply = data["choices"][0]["message"]["content"].strip()
                            sentences = reply.split(". ")
                            short_reply = ". ".join(sentences[:2]).strip()
                            if not short_reply.endswith(('.', '!', '?')):
                                short_reply += "."
                            self.conversations[user_id].append({"role": "assistant", "content": short_reply})
                            self.last_ai = True
                            return short_reply
                        else:
                            print(f"openrouter error with {model} {resp.status}")
                            continue
            except Exception as e:
                print(f"error with {model}: {e}")
                continue
        
        return "i errored sorry"

    async def cmd_piglatin(self, message, command_args):
        content = message.content.strip()
        args = content[len("nux piglatin"):].strip().split(maxsplit=1)

        if len(args) < 1 or args[0] not in ["encode", "decode"]:
            return await self.send_and_clean(message.channel, "usage nux piglatin <encode|decode> <text>")

        action = args[0]
        text = args[1] if len(args) > 1 else ""
        
        if not text:
            return await self.send_and_clean(message.channel, "usage nux piglatin <encode|decode> <text>")

        if action == "encode":
            def piglatinify(word):
                vowels = "aeiouAEIOU"
                if word[0] in vowels:
                    return word + "yay"
                else:
                    for i, letter in enumerate(word):
                        if letter in vowels:
                            return word[i:] + word[:i] + "ay"
                    return word + "ay"
            
            result = ' '.join([piglatinify(word) for word in text.split()])
        else:
            def unpiglatinify(word):
                if word.endswith("yay"):
                    return word[:-3]
                elif word.endswith("ay"):
                    word = word[:-2]
                    for i in range(len(word)):
                        rotated = word[i:] + word[:i]
                        vowels = "aeiouAEIOU"
                        if rotated[0] in vowels or i == len(word) - 1:
                            return rotated
                    return word
                return word
            
            result = ' '.join([unpiglatinify(word) for word in text.split()])
        
        await self.send_and_clean(message.channel, result)

    async def cmd_fexample(self, message, command_args=""):
        await self.send_and_clean(message.channel, f"this is what it looks like currently the timestamps are current though, as it's 6/28/25, at 4:30 a.m. when writing out this message")

    async def cmd_rot13(self, message, command_args):
        content = message.content.strip()
        args = content[len("nux rot"):].strip().split(maxsplit=1)

        if len(args) < 1 or args[0] not in ["encode", "decode"]:
            return await self.send_and_clean(message.channel, "usage nux rot <encode|decode> <text>")

        action = args[0]
        text = args[1] if len(args) > 1 else ""
        
        if not text:
            return await self.send_and_clean(message.channel, "usage nux rot <encode|decode> <text>")

        rot13_map = str.maketrans(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "nopqrstuvwxyzabcdefghijklmNOPQRSTUVWXYZABCDEFGHIJKLM"
        )
        
        result = text.translate(rot13_map)
        await self.send_and_clean(message.channel, result)

    async def cmd_removevowels(self, message, command_args):
        text = command_args.strip()
        if not text:
            return await self.send_and_clean(message.channel, "usage nux removevowels <text>")

        vowels = "aeiouaeiou"
        result = ''.join([char for char in text.lower() if char not in vowels])
        await self.send_and_clean(message.channel, result)

    async def cmd_ping(self, message, command_args=""):
        latency = round(self.latency * 1000)
        await self.send_and_clean(message.channel, f"{latency}ms")

    async def cmd_roleinfo(self, message, command_args):
       if not message.role_mentions:
           return await self.send_and_clean(message.channel, "please mention a role to inspect")

       role = message.role_mentions[0]

       created_at = role.created_at.strftime("%Y-%m-%d %H:%M:%S")
       info = f"role info\n"
       info += f"name {role.name}\n"
       info += f"id {role.id}\n"
       info += f"color {role.color}\n"
       info += f"members {len(role.members)}\n"
       info += f"mentionable {'yes' if role.mentionable else 'no'}\n"
       info += f"position {role.position}\n"
       info += f"hoisted {'yes' if role.hoist else 'no'}\n"
       info += f"created at {created_at}\n"

       await self.send_and_clean(message.channel, info)

    @owner_only()
    async def cmd_eval(self, message, command_args=""):
        if message.author.id != self.owner_id:
            return
        code = message.content[len("nux eval"):].strip()
        try:
            result = eval(code)
            if asyncio.iscoroutine(result):
                result = await result
            await self.send_and_clean(message.channel, f"result {result}")
        except Exception as e:
            await self.send_and_clean(message.channel, f"error {e}")

    @owner_only()
    async def cmd_leaveguild(self, message, command_args=""):
        if message.author.id != self.owner_id:
            return

        content = message.content.strip().split()
        if len(content) < 3:
            return await self.send_and_clean(message.channel, "usage nux leaveguild <guild_id>")

        guild_id = content[2]
        try:
            guild = self.get_guild(int(guild_id))
        except ValueError:
            return await self.send_and_clean(message.channel, "please provide a valid guild id")

        if guild:
            await guild.leave()
            await self.send_and_clean(message.channel, f"left guild {guild.name}")
        else:
            await self.send_and_clean(message.channel, "guild not found")

    @owner_only()
    async def cmd_restart(self, message, command_args=""):
        await self.send_and_clean(message.channel, "restarting")
        await self.close()
        os.execl(sys.executable, sys.executable, *sys.argv)

    @owner_only()
    async def cmd_simulate(self, message, command_args=""):
        parts = message.content.strip().split()
        if len(parts) < 4 or not message.mentions:
            return await self.send_and_clean(message.channel, "usage nux simulate <@user> <command>")

        simulated_user = message.mentions[0]
        command_text = ' '.join(parts[3:])

        if not command_text.lower().startswith('nux '):
            command_text = 'nux ' + command_text

        key = command_text.lower()

        if key not in self.commands:
            return await self.send_and_clean(message.channel, f"unknown command {key}")

        fake_message = message
        fake_message.author = simulated_user
        fake_message.content = command_text

        await self.commands[key](fake_message)

    @owner_only()
    async def cmd_backup(self, message, command_args=""):
        backup_data = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "guilds": [],
            "friends": [],
        }

        for guild in self.guilds:
            backup_data["guilds"].append({
                "id": guild.id,
                "name": guild.name,
                "member_count": guild.member_count
            })

        for user in self.user.friends:
            backup_data["friends"].append({
                "id": user.id,
                "name": str(user)
            })

        filename = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, indent=4)

        await self.send_and_clean(message.channel, f"backup saved as `{filename}`", file=discord.File(filename))

    @owner_only()
    async def cmd_print(self, message, command_args=""):
        raw_message = message.content.strip()
        if not raw_message.lower().startswith("nux print"):
            return

        content = raw_message[len("nux print"):].strip()

        if not content:
            return await self.send_and_clean(message.channel, "usage nux print <text>")

        print(f"[discord print] {content}")
        await self.send_and_clean(message.channel, "message printed to terminal")

    @owner_only()
    async def cmd_shutdown(self, message, command_args=""):
        await self.send_and_clean(message.channel, "shutting down gracefully")
        await self.close()
        import sys
        sys.exit(0)

    async def cmd_translate(self, message, command_args):
        args = command_args.strip().split(maxsplit=2)
        if len(args) < 3:
            return await self.send_and_clean(message.channel, "usage nux translate <from_lang> <to_lang> <text>")
        from_lang, to_lang, text = args
        translator = Translator()
        try:
            translated = await translator.translate(text, src=from_lang, dest=to_lang)
            await self.send_and_clean(message.channel, f"{from_lang} → {to_lang} {translated.text}")
        except Exception as e:
            await self.send_and_clean(message.channel, f"translation failed {e}")

    async def cmd_lyrics(self, message, command_args):
        args = command_args.strip().split(" - ", 1)
        if len(args) < 2:
            return await self.send_and_clean(message.channel, "usage nux lyrics <artist> - <song>")
        artist, song = args
        query = f"{artist} - {song}"
        url = "https://lrclib.net/api/search"
        params = {"q": query}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    return await self.send_and_clean(message.channel, "lyrics not found")
                data = await resp.json()
                if not data:
                    return await self.send_and_clean(message.channel, "lyrics not found")
                top_result = data[0]
                lyrics = top_result.get("plainLyrics", "no lyrics found")
                if len(lyrics) > 2000:
                    lyrics = lyrics[:1997] + "..."
                track_name = top_result.get("trackName", song)
                album_name = top_result.get("albumName", "")
                header = f"{artist} - {track_name}"
                if album_name:
                    header += f" ({album_name})"
                await self.send_and_clean(message.channel, f"{header}\n{lyrics}")

    async def cmd_usercount(self, message, command_args=""):
        if not message.guild:
            return await self.send_and_clean(message.channel, "this command only works in a server")
        online = len([m for m in message.guild.members if m.status == discord.Status.online])
        idle = len([m for m in message.guild.members if m.status == discord.Status.idle])
        dnd = len([m for m in message.guild.members if m.status == discord.Status.do_not_disturb])
        offline = len([m for m in message.guild.members if m.status == discord.Status.offline])
        total = message.guild.member_count
        await self.send_and_clean(message.channel, f"server member count\nonline {online}\nidle {idle}\ndnd {dnd}\noffline {offline}\ntotal {total}")

    async def cmd_iplookup(self, message, command_args):
        ip = message.content.strip()[len("nux iplookup"):].strip()
        if not ip:
            return await self.send_and_clean(message.channel, "usage nux iplookup <ip>")
        url = f"http://ip-api.com/json/{ip}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await self.send_and_clean(message.channel, "failed to lookup ip")
                data = await resp.json()
                if data.get("status") != "success":
                    return await self.send_and_clean(message.channel, "invalid ip or lookup failed")
                info = f"ip lookup\ncountry {data.get('country')}\nregion {data.get('regionName')}\ncity {data.get('city')}\nisp {data.get('isp')}\norg {data.get('org')}"
                await self.send_and_clean(message.channel, info)

    async def cmd_nsfw_nhentai(self, message, command_args=""):
        query = message.content.strip()[len("nux nhentai"):].strip()
        if not query:
            return await self.send_and_clean(message.channel, "usage nux nhentai <search>")
        if isinstance(message.channel, discord.DMChannel):
            pass
        elif hasattr(message.channel, "is_nsfw") and not message.channel.is_nsfw():
            return await self.send_and_clean(message.channel, "this command can only be used in nsfw channels or direct messages")
        url = f"https://nhentai.net/api/galleries/search?query={urllib.parse.quote(query)}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await self.send_and_clean(message.channel, "failed to search nhentai")
                data = await resp.json()
                if not data.get("result"):
                    return await self.send_and_clean(message.channel, "no results found")
                result = data["result"][0]
                title = result["title"]["english"]
                id = result["id"]
                link = f"https://nhentai.net/g/{id}/"
                await self.send_and_clean(message.channel, f"{title}\n{link}")

    @owner_only()
    async def cmd_autoreply(self, message, command_args=""):
        args = message.content.strip()[len("nux autoreply"):].strip().split(maxsplit=1)
        if not args:
            return await self.send_and_clean(message.channel, "usage nux autoreply <trigger> <response1> | <response2> | ...")
        if len(args) < 2:
            return await self.send_and_clean(message.channel, "provide trigger and responses separated by |")
        trigger, responses_str = args
        responses = [r.strip() for r in responses_str.split('|') if r.strip()]
        if not responses:
            return await self.send_and_clean(message.channel, "no responses provided")
        if not hasattr(self, 'autoreplies'):
            self.autoreplies = {}
        self.autoreplies[trigger.lower()] = responses
        self.save_config()
        await self.send_and_clean(message.channel, f"autoreply set for '{trigger}' with {len(responses)} responses")

    async def cmd_serverinfo(self, message, command_args=""):
        if not message.guild:
            return await self.send_and_clean(message.channel, "this command only works in a server")

        guild = message.guild
        created_at = guild.created_at.strftime("%Y-%m-%d %H:%M:%S")

        online = len([m for m in guild.members if m.status == discord.Status.online])
        idle = len([m for m in guild.members if m.status == discord.Status.idle])
        dnd = len([m for m in guild.members if m.status == discord.Status.do_not_disturb])
        offline = len([m for m in guild.members if m.status == discord.Status.offline])

        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)

        role_count = len(guild.roles)

        static_emojis = len([e for e in guild.emojis if not e.animated])
        animated_emojis = len([e for e in guild.emojis if e.animated])

        info = f"server information\n"
        info += f"name {guild.name}\n"
        info += f"id {guild.id}\n"
        info += f"owner {guild.owner}\n"
        info += f"created {created_at}\n"
        info += f"members {guild.member_count:,}\n"
        info += f"online {online} | idle {idle} | dnd {dnd} | offline {offline}\n"
        info += f"channels {text_channels} text, {voice_channels} voice, {categories} categories\n"
        info += f"roles {role_count}\n"
        info += f"emojis {static_emojis} static, {animated_emojis} animated\n"

        if guild.icon:
            info += f"[icon]({guild.icon.url})\n"
        if guild.banner:
            info += f"banner {guild.banner.url}\n"
        if guild.splash:
            info += f"splash {guild.splash.url}\n"

        info += f"verification level {guild.verification_level}\n"
        info += f"nsfw level {guild.explicit_content_filter}\n"
        info += f"boost level {guild.premium_tier}\n"
        info += f"boosts {guild.premium_subscription_count}\n"

        await self.send_and_clean(message.channel, info)

    async def cmd_channelinfo(self, message, command_args=""):
        if not message.guild:
            return await self.send_and_clean(message.channel, "this command only works in a server")

        channel = message.channel
        created_at = channel.created_at.strftime("%Y-%m-%d %H:%M:%S")

        info = f"channel information\n"
        info += f"name {channel.name}\n"
        info += f"id {channel.id}\n"
        info += f"type {channel.type}\n"
        info += f"created {created_at}\n"

        if hasattr(channel, 'position'):
            info += f"position {channel.position}\n"
        if hasattr(channel, 'bitrate') and channel.bitrate:
            info += f"bitrate {channel.bitrate}\n"
        if hasattr(channel, 'user_limit') and channel.user_limit:
            info += f"user limit {channel.user_limit}\n"
        if hasattr(channel, 'nsfw') and channel.nsfw:
            info += f"nsfw yes\n"
        if hasattr(channel, 'slowmode_delay') and channel.slowmode_delay:
            info += f"slowmode {channel.slowmode_delay}s\n"

        await self.send_and_clean(message.channel, info)

    async def cmd_emojis(self, message, command_args=""):
        if not message.guild:
            return await self.send_and_clean(message.channel, "this server has no custom emojis")

        guild = message.guild
        emojis = guild.emojis

        if not emojis:
            return await self.send_and_clean(message.channel, "this server has no custom emojis")

        static_emojis = [e for e in emojis if not e.animated]
        animated_emojis = [e for e in emojis if e.animated]

        info = f"server emojis\n\n"

        if static_emojis:
            info += "static emojis\n"
            for emoji in static_emojis[:50]:
                info += f"{emoji} `{emoji.name}`\n"
            if len(static_emojis) > 50:
                info += f"... and {len(static_emojis) - 50} more\n"
            info += "\n"

        if animated_emojis:
            info += "animated emojis\n"
            for emoji in animated_emojis[:50]:
                info += f"{emoji} `{emoji.name}`\n"
            if len(animated_emojis) > 50:
                info += f"... and {len(animated_emojis) - 50} more\n"

        info += f"\ntotal {len(static_emojis)} static, {len(animated_emojis)} animated"

        await self.send_and_clean(message.channel, info)

    async def cmd_ai_preset(self, message, command_args=""):
        if not command_args:
            presets = self.ai_config.get('presets', {})
            if not presets:
                await self.send_and_clean(message.channel, "no presets saved use `nux ai setup` to create one")
                return
            msg = "Saved presets:\n" + "\n".join([f"{name}: \"{desc[:50]}...\" " if len(desc) > 50 else f"{name}: \"{desc}\"" for name, desc in presets.items()])
            await self.send_and_clean(message.channel, msg)
            return
        preset_name = command_args.strip()
        presets = self.ai_config.get('presets', {})
        if preset_name not in presets:
            await self.send_and_clean(message.channel, f"preset '{preset_name}' not found")
            return
        personality = presets[preset_name]
        full_personality = personality + FIXED_AI_PART
        self.ai_config['personality'] = full_personality
        with open('ai_config.pkl', 'wb') as f:
            pickle.dump(self.ai_config, f)
        await self.send_and_clean(message.channel, f"ai personality set to preset '{preset_name}'")
        await self.send_and_clean(message.channel, "you can now turn on ai with `nux ai on`")

    async def cmd_anagram(self, message, command_args):
        text = command_args.strip()
        if not text:
            return await self.send_and_clean(message.channel, "usage nux anagram <text>")
        words = text.split()
        anagram_words = []
        for word in words:
            char_list = list(word)
            self.rand.shuffle(char_list)
            anagram_words.append(''.join(char_list))
        result = ' '.join(anagram_words)
        await self.send_and_clean(message.channel, result)

    async def cmd_uuid(self, message, command_args=""):
        generated_uuid = str(uuid.uuid4())
        await self.send_and_clean(message.channel, f"generated uuid: {generated_uuid}")

    @owner_only()
    async def cmd_autoowod(self, message, command_args=""):
        parts = command_args.split()

        if not parts:
            if self.autoowod_task and not self.autoowod_task.done():
                await self.send_and_clean(message.channel, f"autoowod running at {self.autoowod_time} UTC")
            else:
                await self.send_and_clean(message.channel, "autoowod not running")
            return

        action = parts[0].lower()

        if action == "start":
            if len(parts) < 3:
                await self.send_and_clean(message.channel, "usage nux autoowod start <channel_id> <HH:MM> (UTC)")
                return

            try:
                channel_id = int(parts[1])
                channel = self.get_channel(channel_id)
                if not channel or not isinstance(channel, discord.TextChannel):
                    await self.send_and_clean(message.channel, "invalid channel id or not text channel")
                    return

                time_str = parts[2]
                hour, minute = map(int, time_str.split(':'))
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    raise ValueError

                self.autoowod_time = time_str
                self.autoowod_channel = channel
                if self.autoowod_task and not self.autoowod_task.done():
                    await self.send_and_clean(message.channel, "autoowod already running")
                    return

                self.autoowod_task = self.loop.create_task(self._autoowod_worker())
                await self.send_and_clean(message.channel, f"autoowod started in {channel} at {self.autoowod_time} UTC")

            except ValueError:
                await self.send_and_clean(message.channel, "invalid channel id or time format")

        elif action == "stop":
            if self.autoowod_task:
                self.autoowod_task.cancel()
                try:
                    await self.autoowod_task
                except asyncio.CancelledError:
                    pass
                self.autoowod_task = None
                self.autoowod_time = None
                self.autoowod_channel = None
                await self.send_and_clean(message.channel, "autoowod stopped")
            else:
                await self.send_and_clean(message.channel, "autoowod not running")

        else:
            await self.send_and_clean(message.channel, "usage nux autoowod start/stop [channel_id] [time]")

    async def _autoowod_worker(self):
        while True:
            now = datetime.datetime.utcnow()
            hour, minute = map(int, self.autoowod_time.split(':'))
            scheduled = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if scheduled <= now:
                scheduled += datetime.timedelta(days=1)
            wait_seconds = (scheduled - now).total_seconds()
            variation = self.rand.uniform(-300, 300)
            wait_seconds += variation
            if wait_seconds < 0:
                wait_seconds = 900 
            await asyncio.sleep(wait_seconds)
            try:
                await self.autoowod_channel.send("owo daily")
            except:
                pass

    @owner_only()
    async def cmd_voicewatch(self, message, command_args=""):
        action = command_args.strip()

        if not action:
            await self.send_and_clean(message.channel, "usage nux voicewatch <guild_id | list>")
            return

        if action == "list":
            watched = [self.get_guild(gid).name for gid in self.voice_watch_enabled if self.get_guild(gid)]
            if watched:
                await self.send_and_clean(message.channel, "voice watching: " + ", ".join(watched))
            else:
                await self.send_and_clean(message.channel, "no voice watching")
            return

        try:
            guild_id = int(action)
            guild = self.get_guild(guild_id)
            if not guild:
                await self.send_and_clean(message.channel, "invalid guild id")
                return

            if guild_id in self.voice_watch_enabled:
                self.voice_watch_enabled.remove(guild_id)
                await self.send_and_clean(message.channel, f"stopped voice watching {guild.name}")
            else:
                self.voice_watch_enabled.add(guild_id)
                await self.send_and_clean(message.channel, f"now voice watching {guild.name}")

        except ValueError:
            await self.send_and_clean(message.channel, "invalid guild id")

    async def handle_voice_state_update(self, member, before, after):
        if not self.voice_watch_enabled:
            return

        guild = member.guild
        if guild.id not in self.voice_watch_enabled:
            return

        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        user = str(member)
        before_channel = before.channel.name if before.channel else "None"
        after_channel = after.channel.name if after.channel else "None"

        if before.channel != after.channel:
            log_line = f"[{timestamp}] {user} voice channel change: from {before_channel} to {after_channel}"
            filename = f"logs/voice_{guild.id}.txt"
            log_dir = "logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            with open(filename, "a", encoding="utf-8") as f:
                f.write(log_line + "\n")

    async def cmd_autoreact(self, message, command_args=""):
        args = command_args.split()
        if not args:
            if not self.autoreact_rules:
                await self.send_and_clean(message.channel, "no autoreact rules set")
                return
            response = "autoreact rules:\n"
            for rule in self.autoreact_rules:
                try:
                    emoji = self.get_emoji(rule['emoji_id']) if 'emoji_id' in rule else rule['emoji']
                    channel = self.get_channel(rule['channel_id'])
                    response += f"- {channel.name if channel else 'unknown'}: '{rule['keyword']}' -> {emoji}\n"
                except:
                    response += f"- unknown: '{rule['keyword']}' -> {rule.get('emoji', 'unknown')}\n"
            await self.send_and_clean(message.channel, response.strip())
            return

        action = args[0].lower()

        if action == "remove":
            if len(args) < 3:
                await self.send_and_clean(message.channel, "usage nux autoreact remove <channel_id> <keyword>")
                return
            try:
                channel_id = int(args[1])
                keyword = args[2].lower()
                new_rules = [r for r in self.autoreact_rules if not (r['channel_id'] == channel_id and r['keyword'] == keyword)]
                if len(new_rules) == len(self.autoreact_rules):
                    await self.send_and_clean(message.channel, "no matching rule found")
                else:
                    self.autoreact_rules = new_rules
                    self.save_config()
                    await self.send_and_clean(message.channel, f"removed autoreact rule for keyword '{keyword}' in channel {channel_id}")
            except ValueError:
                await self.send_and_clean(message.channel, "invalid channel id")
        elif len(args) >= 3:
            try:
                channel_id = int(action)
                keyword = args[1].lower()
                emoji = args[2]
                emoji_id = None
                if emoji.startswith("<:") and emoji.endswith(">"):
                    emoji_id = emoji.split(":")[-1][:-1]
                    try:
                        emoji_id = int(emoji_id)
                    except:
                        pass
                rule = {
                    'channel_id': channel_id,
                    'keyword': keyword,
                    'emoji': emoji,
                    'emoji_id': emoji_id
                }
                self.autoreact_rules.append(rule)
                self.save_config()
                await self.send_and_clean(message.channel, f"added autoreact rule: channel {channel_id}, keyword '{keyword}', emoji {emoji}")
            except ValueError:
                await self.send_and_clean(message.channel, "invalid channel id")
        else:
            await self.send_and_clean(message.channel, "usage nux autoreact [<channel_id> <keyword> <emoji> | remove <channel_id> <keyword>]")

    async def cmd_kiss(self, message, command_args):
        if not message.mentions:
            return await self.send_and_clean(message.channel, "you need to mention someone to kiss")

        target = message.mentions[0]
        author = message.author

        async with aiohttp.ClientSession() as session:
            async with session.get('https://nekos.life/api/v2/img/kiss') as resp:
                if resp.status != 200:
                    return await self.send_and_clean(message.channel, "couldn't fetch kiss gif")
                try:
                    data = await resp.json()
                    gif_url = data.get('url')
                    if not gif_url:
                        return await self.send_and_clean(message.channel, "couldn't get kiss gif")
                except Exception:
                    return await self.send_and_clean(message.channel, "couldn't fetch kiss gif")

        kiss_messages = [
            f"{author.mention} [kisses]({gif_url}) {target.mention}",
            f"{author.mention} [smooches]({gif_url}) {target.mention}",
            f"{author.mention} gives {target.mention} a [kiss]({gif_url})",
        ]

        msg = self.rand.choice(kiss_messages)
        await self.send_and_clean(message.channel, msg)

    async def cmd_coinflip(self, message, command_args=""):
        result = self.rand.choice(["heads", "tails"])
        await self.send_and_clean(message.channel, f"coin flip {result}")

    async def cmd_avatar(self, message, command_args=""):
        if not message.mentions:
            user = message.author
        else:
            user = message.mentions[0]

        avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
        await self.send_and_clean(message.channel, f"{user}'s [avatar]({avatar_url})")

    async def cmd_banner(self, message, command_args=""):
        if not message.mentions:
            user = message.author
        else:
            user = message.mentions[0]

        if not hasattr(user, 'banner') or not user.banner:
            return await self.send_and_clean(message.channel, f"{user.mention} doesn't have a banner set")

        banner_url = user.banner.url
        await self.send_and_clean(message.channel, f"{user}'s [banner]({banner_url})")

    async def cmd_wiki(self, message, command_args=""):
        query = message.content.strip()[len("nux wiki"):].strip()
        if not query:
            return await self.send_and_clean(message.channel, "usage nux wiki <search term>")

        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(query)}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await self.send_and_clean(message.channel, f"no wikipedia page found for '{query}'")

                data = await resp.json()

                title = data.get('title', 'unknown')
                extract = data.get('extract', 'no description available')
                page_url = data.get('content_urls', {}).get('desktop', {}).get('page', '')

                if len(extract) > 1800:
                    extract = extract[:1800] + "..."

                info = f"{title}\n{extract}\n\nread more on wikipedia {page_url}"
                await self.send_and_clean(message.channel, info)

    async def cmd_github(self, message, command_args=""):
        username = message.content.strip()[len("nux github"):].strip()
        if not username:
            return await self.send_and_clean(message.channel, "usage nux github <username>")

        url = f"https://api.github.com/users/{username}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await self.send_and_clean(message.channel, f"github user '{username}' not found")

                data = await resp.json()

                name = data.get('name', 'not provided')
                bio = data.get('bio', 'no bio available')
                company = data.get('company', 'none')
                location = data.get('location', 'unknown')
                public_repos = data.get('public_repos', 0)
                followers = data.get('followers', 0)
                following = data.get('following', 0)
                created_at = data.get('created_at', '')[:10] if data.get('created_at') else 'unknown'

                info = f"github profile {username}\n"
                if name != 'not provided':
                    info += f"name {name}\n"
                info += f"bio {bio}\n"
                info += f"company {company}\n"
                info += f"location {location}\n"
                info += f"public repos {public_repos:,}\n"
                info += f"followers {followers:,}\n"
                info += f"following {following:,}\n"
                info += f"joined {created_at}\n"
                info += f"profile https://github.com/{username}"

                await self.send_and_clean(message.channel, info)

    @owner_only()
    async def cmd_config(self, message, command_args=""):
        try:
            configuration = {}
            if os.path.exists('config.pkl'):
                with open('config.pkl', 'rb') as f:
                    configuration['config'] = pickle.load(f)
            if os.path.exists('ai_config.pkl'):
                with open('ai_config.pkl', 'rb') as f:
                    configuration['ai_config'] = pickle.load(f)

            formatted = json.dumps(configuration, indent=4, default=str)
            chunks = [formatted[i:i+1900] for i in range(0, len(formatted), 1900)]
            for chunk in chunks:
                await self.send_and_clean(message.channel, f"```\n{chunk}```")
        except Exception as e:
            await self.send_and_clean(message.channel, f"failed to load config: {e}")

    async def cmd_stats(self, message, command_args=""):
        uptime_seconds = (datetime.datetime.utcnow() - self.start_time).total_seconds()
        uptime_str = str(datetime.timedelta(seconds=int(uptime_seconds)))

        memory = psutil.virtual_memory()
        cpu_usage = psutil.cpu_percent(interval=0.5)
        ram_usage = memory.percent

        total_guilds = len(self.guilds)
        total_users = sum(guild.member_count for guild in self.guilds)

        total_commands = sum(len(commands) for commands in self.help_categories.values()) + len(self.nsfwhelp_categories)

        info = f"bot statistics\n"
        info += f"uptime {uptime_str}\n"
        info += f"cpu usage {cpu_usage}%\n"
        info += f"ram usage {ram_usage}%\n"
        info += f"latency {round(self.latency * 1000)}ms\n"
        info += f"servers {total_guilds:,}\n"
        info += f"exposed to {total_users:,} users\n"
        info += f"total commands {total_commands}\n"
        info += f"python version {platform.python_version()}\n"
        info += f"discord.py version {discord.__version__}"

        fig, ax = plt.subplots()
        labels = ['CPU', 'RAM']
        values = [cpu_usage, ram_usage]
        ax.bar(labels, values, color=['blue', 'green'])
        ax.set_ylabel('Percentage')
        ax.set_title('System Usage')
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        plt.close(fig)
        file = discord.File(buf, 'stats_graph.png')

        await self.send_and_clean(message.channel, info, file=file)

    async def cmd_bug(self, message, command_args=""):
        await self.send_and_clean(message.channel, "send a [report](https://nukumoxy.netlify.app/), and it'll send to [here.](https://discord.gg/63mSzU8hkR)")
        await self.send_and_clean(message.channel, "\n\n-# originally, you would send a description and it would send a webhook embed to my server, but it would 100% always make your account need to reset it's password.")

    async def cmd_repo(self, message, command_args=""):
        await self.send_and_clean(message.channel, "https://github.com/hexxedspider/nuxified")

    async def cmd_update(self, message, command_args=""):
        try:
            url = "https://api.github.com/repos/hexxedspider/nuxified/releases/latest"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        latest_version = data.get('tag_name', '')
                        if latest_version and latest_version != f"v{VERSION}":
                            await self.send_and_clean(message.channel, f"your version: v{VERSION}\nlatest version: {latest_version}\nupdate available at https://github.com/hexxedspider/nuxified/releases/latest")
                        else:
                            await self.send_and_clean(message.channel, f"your version: v{VERSION}\nyou are up to date")
                    else:
                        await self.send_and_clean(message.channel, "failed to check for updates")
        except Exception as e:
            await self.send_and_clean(message.channel, f"error checking updates: {e}")

    @owner_only()
    async def cmd_pull(self, message, command_args=""):
        try:
            result = subprocess.run(['git', 'pull', 'origin', 'main'], capture_output=True, text=True, cwd=os.getcwd())
            if result.returncode == 0:
                await self.send_and_clean(message.channel, f"git pull successful\n{result.stdout}")
            else:
                await self.send_and_clean(message.channel, f"git pull failed\n{result.stderr}")
        except Exception as e:
            await self.send_and_clean(message.channel, f"error running git pull: {e}")

    @owner_only()
    async def cmd_watch(self, message, command_args):
        args = message.content.lower().split()
        if len(args) < 3:
            return await self.send_and_clean(message.channel, "usage: nux watch <guild_id | dm | list>")

        target = args[2]

        if target == "dm":
            self.watch_all_dms = not self.watch_all_dms
            status = "now" if self.watch_all_dms else "no longer"
            await self.send_and_clean(message.channel, f"i am {status} tracking all dms")
        elif target == "list":
            watched_list = []
            if self.watch_all_dms:
                watched_list.append("direct messages (dm)")
            for guild_id in list(self.watched_guilds):
                guild = self.get_guild(guild_id)
                if guild:
                    watched_list.append(f"{guild.name} (id {guild_id})")
                else:
                    self.watched_guilds.remove(guild_id)
                    self.save_config()
            
            if watched_list:
                response = "currently watching:\n" + "\n".join(watched_list)
            else:
                response = "not currently watching any servers or dms"
            await self.send_and_clean(message.channel, response)
            return
        else:
            try:
                guild_id = int(target)
            except ValueError:
                return await self.send_and_clean(message.channel, "invalid guild id or target")

            if guild_id in self.watched_guilds:
                self.watched_guilds.remove(guild_id)
                await self.send_and_clean(message.channel, f"stopped watching guild {guild_id}")
            else:
                self.watched_guilds.add(guild_id)
                await self.send_and_clean(message.channel, f"now watching guild {guild_id}")
        
        self.save_config()

    def save_config(self):
        config_data = {
            'watched_guilds': self.watched_guilds,
            'watch_all_dms': self.watch_all_dms,
            'tracked_joins': self.tracked_joins,
            'join_webhook': self.join_webhook,
            'cleaner_settings': self.cleaner_settings,
            'status_enabled': self.status_enabled,
            'ai_enabled': self.ai_enabled,
            'ghost_mode': self.ghost_mode,
            'ai_cooldown_seconds': self.ai_cooldown_seconds,
            'autoreplies': self.autoreplies,
            'autoowod_channel_id': self.autoowod_channel.id if self.autoowod_channel else None,
            'autoowod_time': self.autoowod_time,
            'voice_watch_enabled': self.voice_watch_enabled,
            'autoreact_rules': self.autoreact_rules,
            'weather_ip_enabled': self.weather_ip_enabled,
        }
        try:
            with open('config.pkl', 'wb') as f:
                pickle.dump(config_data, f)
        except Exception as e:
            print(f"error saving config.pkl: {e}")

    async def log_message(self, message):
        log_to_file = False
        filename = None

        if message.guild:
            if message.guild.id in self.watched_guilds:
                log_to_file = True
                filename = f"logs/logs_{message.guild.id}.txt"
        elif isinstance(message.channel, discord.DMChannel) and self.watch_all_dms:
            log_to_file = True
            filename = f"logs/logs_dms.txt" # ALL DMS GO HERE

        if not log_to_file:
            return

        log_dir = os.path.dirname(filename)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
        author = str(message.author)
        channel_name = str(message.channel) if message.guild else "DM"
        content = message.content.replace('\n', '\\n').replace('\r', '\\r')
        attachments = [att.url for att in message.attachments] if message.attachments else []
        embeds = message.embeds

        log_line = f"[{timestamp}] {author} in #{channel_name}: {content}"
        if attachments:
            log_line += f" | Attachments: {', '.join(attachments)}"
        if embeds:
            log_line += f" | Embeds: {len(embeds)}"
        try:
            with open(filename, "a", encoding="utf-8") as f:
                f.write(log_line + "\n")
        except Exception as e:
            print(f"error writing to log file {filename}: {e}")

    @owner_only()
    async def cmd_setjoinwebhook(self, message, command_args=""):
        if not command_args or command_args.lower() in ["status", "stat"]:
            if not self.join_webhook:
                await self.send_and_clean(message.channel, "no join webhook set")
                return
            embed = {
                "title": "webhook test",
                "description": "this is a test message for the join webhook",
                "color": 0x00ff00
            }
            try:
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "username": "nux worker test",
                        "avatar_url": self.user.avatar.url if self.user.avatar else None,
                        "embeds": [embed]
                    }
                    resp = await session.post(self.join_webhook, json=payload)
                    if resp.status == 204:
                        await self.send_and_clean(message.channel, "join webhook is set and working")
                    else:
                        await self.send_and_clean(message.channel, "join webhook is set but not working (check url)")
            except Exception as e:
                await self.send_and_clean(message.channel, f"join webhook is set but error: {e}")
        else:
            webhook_url = command_args.strip()
            if not webhook_url:
                await self.send_and_clean(message.channel, "provide a webhook url")
                return
            if not webhook_url.startswith("https://discordapp.com/api/webhooks/") and not webhook_url.startswith("https://discord.com/api/webhooks/"):
                await self.send_and_clean(message.channel, "provide a valid discord webhook url")
                return
            self.join_webhook = webhook_url
            self.save_config()
            await self.send_and_clean(message.channel, "join notification webhook set")

    @owner_only()
    async def cmd_trackjoins(self, message, command_args):
        if not command_args or command_args.lower().strip() == "list":
            tracked_list = []
            for guild_id in self.tracked_joins:
                guild = self.get_guild(guild_id)
                if guild:
                    tracked_list.append(f"{guild.name} (id {guild_id})")
            if tracked_list:
                response = "currently tracking joins for:\n" + "\n".join(tracked_list)
            else:
                response = "no guilds are being tracked for joins"
            await self.send_and_clean(message.channel, response)
        else:
            try:
                guild_id = int(command_args.strip())
            except ValueError:
                await self.send_and_clean(message.channel, "provide a valid guild id or use 'list' to see tracked guilds")
                return
            if guild_id in self.tracked_joins:
                self.tracked_joins.remove(guild_id)
                await self.send_and_clean(message.channel, f"stopped tracking joins in guild {guild_id}")
            else:
                self.tracked_joins.add(guild_id)
                await self.send_and_clean(message.channel, f"now tracking joins in guild {guild_id}")
            self.save_config()

    async def cmd_ai_memory(self, message, command_args=""):
        try:
            user_id = int(command_args)
            if user_id not in self.conversations:
                await self.send_and_clean(message.channel, "no conversation history with that user")
                return
            history = self.conversations[user_id]
            if len(history) <= 1:
                await self.send_and_clean(message.channel, "no conversation history with that user")
                return
            summary = f"conversation with {user_id}\n" + "\n".join([f"{msg['role']}: {(msg['content'][:50] + '...') if len(msg['content']) > 50 else msg['content']}" for msg in history[-10:] if msg['role'] != 'system'])
            await self.send_and_clean(message.channel, summary)
        except ValueError:
            await self.send_and_clean(message.channel, "invalid user id")

    async def cmd_learn(self, message, command_args="s"):
        args = command_args.split(" | ", 1)
        if len(args) != 2:
            await self.send_and_clean(message.channel, "usage nux learn <input_phrase> | <output_response>")
            return
        phrase, response = args
        phrase = phrase.strip().lower()
        response = response.strip()
        if 'custom_responses' not in self.ai_config:
            self.ai_config['custom_responses'] = {}
        self.ai_config['custom_responses'][phrase] = response
        with open('ai_config.pkl', 'wb') as f:
            pickle.dump(self.ai_config, f)
        await self.send_and_clean(message.channel, f"learned '{phrase}' -> '{response}'")

    async def cmd_rhyme(self, message, command_args):
        word = command_args.strip()
        if not word:
            return await self.send_and_clean(message.channel, "usage nux rhyme <word>")
        url = f"https://api.datamuse.com/words?rel_rhy={word}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await self.send_and_clean(message.channel, "couldn't fetch rhymes")
                data = await resp.json()
                if not data:
                    return await self.send_and_clean(message.channel, f"no rhymes found for {word}")
                rhymes = [item['word'] for item in data[:10]]
                result = f"rhymes for {word}\n" + ", ".join(rhymes)
                await self.send_and_clean(message.channel, result)

    async def cmd_synonym(self, message, command_args):
        word = command_args.strip()
        if not word:
            return await self.send_and_clean(message.channel, "usage nux synonym <word>")
        url = f"https://api.datamuse.com/words?rel_syn={word}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await self.send_and_clean(message.channel, "couldn't fetch synonyms")
                data = await resp.json()
                if not data:
                    return await self.send_and_clean(message.channel, f"no synonyms found for {word}")
                synonyms = [item['word'] for item in data[:10]]
                result = f"synonyms for {word}\n" + ", ".join(synonyms)
                await self.send_and_clean(message.channel, result)

    async def cmd_barcode(self, message, command_args):
        text = command_args.strip()
        if not text:
            return await self.send_and_clean(message.channel, "usage nux barcode <text>")

        try:
            barcode_class = barcode.get('code128', text, writer=ImageWriter())
            buffer = io.BytesIO()
            barcode_class.write(buffer)
            buffer.seek(0)
            await self.send_and_clean(message.channel, file=discord.File(buffer, filename="barcode.png"))
        except Exception as e:
            await self.send_and_clean(message.channel, f"failed to generate barcode: {e}")

    async def cmd_nasaapod(self, message):
        url = "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await self.send_and_clean(message.channel, "failed to fetch nasa apod")
                data = await resp.json()
                title = data.get('title', 'No title')
                date = data.get('date', 'No date')
                explanation = data.get('explanation', 'No explanation')
                hdurl = data.get('hdurl')
                if hdurl:
                    await self.send_and_clean(message.channel, f"**{title}**\n{date}\n{explanation[:500]}{'...' if len(explanation) > 500 else ''}\n{hdurl}")
                else:
                    await self.send_and_clean(message.channel, f"{title}\n{date}\n{explanation}")

    async def cmd_osu(self, message, command_args):
        username = command_args.strip()
        if not username:
            return await self.send_and_clean(message.channel, "usage nux osu <username>")
        username = urllib.parse.quote(username)
        profile_url = f"https://osu.ppy.sh/users/{username}"
        await self.send_and_clean(message.channel, f"osu! profile link: {profile_url}")

    async def cmd_steamprofile(self, message, command_args):
        steamid = command_args.strip()
        if not steamid:
            return await self.send_and_clean(message.channel, "usage nux steamprofile <steamid64 or vanity url slug>")

        if not STEAM_API_KEY:
            return await self.send_and_clean(message.channel, "steam api key not set")

        loop = asyncio.get_event_loop()
        try:
            resolved_steamid = await loop.run_in_executor(None, self.resolve_steamid, steamid)
            if not resolved_steamid:
                return await self.send_and_clean(message.channel, "could not resolve steamid")

            profile = await loop.run_in_executor(None, self.get_player_summary, resolved_steamid)
            bans = await loop.run_in_executor(None, self.get_player_bans, resolved_steamid)
            friend_count = await loop.run_in_executor(None, self.get_friend_count, resolved_steamid)

            if not profile:
                return await self.send_and_clean(message.channel, "failed to fetch profile")

            buffer = await loop.run_in_executor(None, self.create_steam_profile_card, profile, bans, friend_count)
            await self.send_and_clean(message.channel, file=discord.File(buffer, filename="steam_profile.png"))
        except Exception as e:
            await self.send_and_clean(message.channel, f"error: {e}")

    def resolve_steamid(self, identifier):
        if identifier.isdigit() and len(identifier) >= 17:
            return identifier
        url = f"{STEAM_API_BASE}/ISteamUser/ResolveVanityURL/v1/"
        params = {"key": STEAM_API_KEY, "vanityurl": identifier}
        r = requests.get(url, params=params)
        if r.status_code != 200:
            return None
        try:
            data = r.json()
        except ValueError:
            return None
        return data.get("response", {}).get("steamid")

    def get_player_summary(self, steamid):
        url = f"{STEAM_API_BASE}/ISteamUser/GetPlayerSummaries/v2/"
        params = {"key": STEAM_API_KEY, "steamids": steamid}
        r = requests.get(url, params=params)
        if r.status_code != 200:
            return None
        try:
            data = r.json()
        except ValueError:
            return None
        players = data.get("response", {}).get("players", [])
        return players[0] if players else None

    def get_player_bans(self, steamid):
        url = f"{STEAM_API_BASE}/ISteamUser/GetPlayerBans/v1/"
        params = {"key": STEAM_API_KEY, "steamids": steamid}
        r = requests.get(url, params=params)
        if r.status_code != 200:
            return {}
        try:
            data = r.json()
        except ValueError:
            return {}
        bans = data.get("players", [])
        return bans[0] if bans else {}

    def get_friend_count(self, steamid):
        url = f"{STEAM_API_BASE}/ISteamUser/GetFriendList/v1/"
        params = {"key": STEAM_API_KEY, "steamid": steamid, "relationship": "friend"}
        r = requests.get(url, params=params)
        if r.status_code != 200:
            return 0
        try:
            data = r.json()
        except ValueError:
            return 0
        return len(data.get("friendslist", {}).get("friends", []))

    def format_timestamp(self, ts):
        return datetime.datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') if ts else "N/A"

    def draw_wrapped_text(self, draw, text, position, font, max_width, fill):
        words = text.split()
        lines, line = [], ""
        while words:
            test_line = line + (words[0] + " ")
            if draw.textlength(test_line, font=font) <= max_width:
                line = test_line
                words.pop(0)
            else:
                lines.append(line)
                line = ""
        if line:
            lines.append(line)

        x, y = position
        for l in lines:
            draw.text((x, y), l.strip(), font=font, fill=fill)
            y += font.size + 2
        return y

    def create_steam_profile_card(self, profile, bans, friend_count):
        avatar_url = profile.get("avatarfull")
        avatar_response = requests.get(avatar_url)
        avatar_img = Image.open(io.BytesIO(avatar_response.content)).convert("RGBA")

        try:
            font_title = ImageFont.truetype("dmfonts/thunder.otf", 32)
            font_text = ImageFont.truetype("dmfonts/hanah.ttf", 20)
        except:
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()

        card_width, card_height = 1600, 800
        card = Image.new("RGBA", (card_width, card_height))
        draw = ImageDraw.Draw(card)

        for y in range(card_height):
            r = min(255, int(100 + y * 0.2))
            g = min(255, int(50 + y * 0.1))
            b = min(255, int(150 + y * 0.05))
            draw.line([(0, y), (card_width, y)], fill=(r, g, b))

        avatar_size = 180
        avatar_img = avatar_img.resize((avatar_size, avatar_size))
        avatar_border_size = 10
        avatar_pos = (30 + avatar_border_size, 35 + avatar_border_size)
        draw.rectangle([30, 35, 30 + avatar_size + 2*avatar_border_size, 35 + avatar_size + 2*avatar_border_size], fill=(255, 255, 255))
        card.paste(avatar_img, avatar_pos)

        x_start = 270
        y_offset = 50
        max_text_width = card_width - x_start - 40

        draw.text((x_start, y_offset), profile.get("personaname", "Unknown"), font=font_title, fill=(255, 255, 255))
        y_offset += 60

        draw.text((x_start, y_offset), f"SteamID: {profile.get('steamid')}", font=font_text, fill=(200, 200, 200))
        y_offset += 35

        y_offset = self.draw_wrapped_text(draw, f"Profile: {profile.get('profileurl')}", (x_start, y_offset), font_text, max_text_width, (200,200,200)) + 15

        status_map = {
            0: "Offline",
            1: "Online",
            2: "Busy",
            3: "Away",
            4: "Snooze",
            5: "Looking to Trade",
            6: "Looking to Play"
        }
        status = status_map.get(profile.get("personastate", 0), "Unknown")
        draw.text((x_start, y_offset), f"Status: {status}", font=font_text, fill=(150, 255, 150))
        y_offset += 35

        real_name = profile.get("realname", "N/A")
        country = profile.get("loccountrycode", "N/A")
        last_online = self.format_timestamp(profile.get("lastlogoff"))
        created = self.format_timestamp(profile.get("timecreated"))
        game = profile.get("gameextrainfo", None)

        draw.text((x_start, y_offset), f"Real Name: {real_name}", font=font_text, fill=(200,200,200)); y_offset += 30
        draw.text((x_start, y_offset), f"Country: {country}", font=font_text, fill=(200,200,200)); y_offset += 30
        draw.text((x_start, y_offset), f"Last Online: {last_online}", font=font_text, fill=(200,200,200)); y_offset += 30
        draw.text((x_start, y_offset), f"Created: {created}", font=font_text, fill=(200,200,200)); y_offset += 30

        if game:
            draw.text((x_start, y_offset), f"Currently Playing: {game}", font=font_text, fill=(150,200,255)); y_offset += 40

        draw.text((x_start, y_offset), f"Friends: {friend_count}", font=font_text, fill=(200,200,200)); y_offset += 30
        if bans:
            draw.text((x_start, y_offset), f"VAC Bans: {bans.get('NumberOfVACBans', 0)}", font=font_text, fill=(255,150,150)); y_offset += 30
            draw.text((x_start, y_offset), f"Game Bans: {bans.get('NumberOfGameBans', 0)}", font=font_text, fill=(255,150,150)); y_offset += 30
            draw.text((x_start, y_offset), f"Community Banned: {bans.get('CommunityBanned', False)}", font=font_text, fill=(255,150,150)); y_offset += 30

        used_height = y_offset + 50
        used_width = max(max_text_width + x_start + 40, 1400)
        card = card.crop((0, 0, used_width, used_height))

        buffer = io.BytesIO()
        card.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer

    async def on_member_join_handler(self, member):
        if member.guild.id not in self.tracked_joins or member.bot:
            return
        if not self.join_webhook:
            return
        if member == self.user:
            return

        account_age_days = (member.joined_at - member.created_at).days
        embed = {
            "title": "user joined",
            "color": 0x00ff00,
            "thumbnail": {
                "url": member.avatar.url if member.avatar else member.default_avatar.url
            },
            "fields": [
                {
                    "name": "Username",
                    "value": str(member),
                    "inline": True
                },
                {
                    "name": "User ID",
                    "value": str(member.id),
                    "inline": True
                },
                {
                    "name": "Account Created",
                    "value": member.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "inline": False
                },
                {
                    "name": "Account Age",
                    "value": f"{account_age_days} days",
                    "inline": True
                },
                {
                    "name": "Joined At",
                    "value": member.joined_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "inline": False
                },
                {
                    "name": "Bot",
                    "value": "Yes" if member.bot else "No",
                    "inline": True
                }
            ],
            "timestamp": member.joined_at.isoformat(),
            "footer": {
                "text": f"server: {member.guild.name}"
            }
        }

        if hasattr(member, 'banner') and member.banner:
            embed["image"] = {"url": member.banner.url}

        if hasattr(member, 'global_name') and member.global_name and member.global_name != member.name:
            embed["fields"].insert(1, {
                "name": "Display Name",
                "value": member.global_name,
                "inline": True
            })

        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "username": "nux's worker",
                    "avatar_url": self.user.avatar.url if self.user.avatar else None,
                    "embeds": [embed]
                }
                await session.post(self.join_webhook, json=payload)
        except Exception as e:
            print(f"failed to send join notification: {e}")

    async def cmd_version(self, messages, command_args=""):
        await self.send_and_clean(messages.channel, f"nuxified version: {VERSION}")

client = AIResponder()

@client.event
async def on_member_join(member):
    await client.on_member_join_handler(member)

@client.event
async def on_voice_state_update(member, before, after):
    await client.handle_voice_state_update(member, before, after)

client.run(TOKEN)
