# this is the main fork of the script, i will try to keep it updated with the latest changes.
# i might end up actually forking the repo on github with just specific utils.
# the folder (excluded, .gitignore) other_accounts is just this script but pasted with other names and what not, branded to those accounts.
# it's in a seperate folder since they don't really matter to me, hence why i don't keep them updated, and dont bother trying to update them... not that you'd know anyway.

import discord, asyncio, random, aiohttp, datetime, io, qrcode, requests, base64, math, yt_dlp, os, logging, re, psutil, platform, subprocess, sys, json, hashlib, urllib.parse, uuid, importlib.util
from gtts import gTTS
from redgifs import API as RedGifsAPI
from pyfiglet import figlet_format
from PIL import Image, ImageDraw, ImageFont, ImageOps
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

VERSION = "5.0.0"

FIXED_AI_PART = "\n\nthis ai is operating as a discord selfbot created by nuxified (nux) it must always adhere to discord's terms of service and guidelines for bots, even though it's a selfbot responses should be short (1-2 sentences unless asked otherwise), and only ever in lowercase with no emojis and minimal punctuation. if the username contains characters like _underscores_ like that, put a backwards slash (like this, \\_underscore_) to avoid discord formatting."

def owner_only():
    def decorator(func):
        async def wrapper(self, message, *args, **kwargs):
            if message.author.id != self.owner_id:
                await message.channel.send("only i can do that")
                return
            return await func(self, message, *args, **kwargs)
        return wrapper
    return decorator

class nuxified(discord.Client):
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
                self.todo_list = config_data.get('todo_list', [])
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
            self.todo_list = []
            self.saved_status_enabled = False
        self.cdm_tasks = {}
        self.api = RedGifsAPI()
        self.af_api = "https://api.alexflipnote.dev"
        self.commands = {}

        self.help_categories = {}
        curses_folder = 'curses'
        curse_files = [f for f in os.listdir(curses_folder) if f.endswith('.py') and f != '__init__.py']
        for curse_file in curse_files:
            module_name = curse_file[:-3]
            spec = importlib.util.spec_from_file_location(module_name, f'{curses_folder}/{curse_file}')
            module = importlib.util.module_from_spec(spec)
            module.owner_only = owner_only
            spec.loader.exec_module(module)
            if hasattr(module, 'setup'):
                curse_instance, help_dict = module.setup(self)
                for category in help_dict:
                    if category not in self.help_categories:
                        self.help_categories[category] = {}
                    self.help_categories[category].update(help_dict[category])
                for category, cmds in help_dict.items():
                    for cmd_trigger in cmds.keys():
                        parts = cmd_trigger.split()
                        method_name = 'cmd_' + '_'.join(parts[1:]) if len(parts) > 1 else 'cmd_' + cmd_trigger
                        if hasattr(curse_instance, method_name):
                            self.commands[cmd_trigger] = getattr(curse_instance, method_name)
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

        if not hasattr(self, 'commands') or not self.commands:
            self.commands = {}

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

client = nuxified()

@client.event
async def on_member_join(member):
    await client.on_member_join_handler(member)

@client.event
async def on_voice_state_update(member, before, after):
    await client.handle_voice_state_update(member, before, after)

client.run(TOKEN)
