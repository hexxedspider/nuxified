import discord
import aiohttp
import asyncio
import io
import urllib.parse
import os
import datetime
import requests
import barcode
import random
import dotenv
from googletrans import Translator
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont, ImageOps

dotenv.load_dotenv()

STEAM_API_BASE = "https://api.steampowered.com"
STEAM_API_KEY = os.getenv('STEAM_API_KEY')

HELP_TEXT = {
    "fun": {
        "nux achievement <text>": "generate a minecraft achievement",
        "nux fakenitro": "generate a fake nitro link",
        "nux hug <@user>": "hug someone",
        "nux pat <@user>": "pat someone",
        "nux slap <@user>": "slap someone",
        "nux kiss <@user>": "kiss someone",
        "nux cuddle <@user>": "cuddle someone",
        "nux echo <text>": "repeat text",
        "nux dadjoke": "tell a dad joke",
        "nux coinflip": "flip a coin",
        "nux weather <location>": "check weather",
        "nux translate <from> <to> <text>": "translate text",
        "nux lyrics <artist> - <song>": "get song lyrics",
        "nux rhyme <word>": "find rhymes",
        "nux synonym <word>": "find synonyms",
        "nux barcode <text>": "generate a barcode",
        "nux nasaapod": "nasa astronomy picture of the day",
        "nux osu <user>": "get osu! stats",
        "nux steamprofile <id/url>": "generate steam profile card",
        "nux rate <user/text>": "rate something 0-10",
        "nux ship <user1> <user2>": "ship two users",
        "nux haiku <prompt>": "generate AI haiku from prompt",
        "nux clippy <text>": "get passive-aggressive paperclip responses",
        "nux songlyrics <theme/genre>": "generate AI song lyrics",
        "nux advice <topic>": "get AI advice on any topic",
        "nux roast <user/text>": "generate creative AI roasts",
        "nux compliment <user/text>": "generate personalized AI compliments",
        "nux summarize <text>": "summarize long text with AI",
        "nux code <description>": "generate code snippets from description",
    }
}

class Fun:
    def __init__(self, bot):
        self.bot = bot
    
    async def cmd_achievement(self, message, command_args):
        text = command_args
        if not text:
            await self.bot.send_and_clean(message.channel, "usage nux achievement <text>")
            return
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.bot.af_api}/achievement?text={urllib.parse.quote(text)}"
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await self.bot.send_and_clean(message.channel, "couldn't generate achievement")
                    img_bytes = await resp.read()
            buffer = io.BytesIO(img_bytes)
            await self.bot.send_and_clean(message.channel, file=discord.File(buffer, filename="achievement.png"))
        except Exception as e:
            await self.bot.send_and_clean(message.channel, "couldn't generate achievement")

    async def cmd_fakenitro(self, message, command_args):
        characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        fake_code = ''.join(self.bot.rand.choices(characters, k=16))
        fake_link = f"https://discord.gift/{fake_code}"

        await message.channel.send(f"{fake_link}")

    async def cmd_hug(self, message, command_args=""):
        if not message.mentions:
            await self.bot.send_and_clean(message.channel, "you need to mention someone to hug")
            return

        target = message.mentions[0]
        author = message.author

        async with aiohttp.ClientSession() as session:
            async with session.get('https://nekos.life/api/v2/img/hug') as resp:
                if resp.status != 200:
                    await self.bot.send_and_clean(message.channel, "couldn't fetch hug gif")
                    return
                try:
                    data = await resp.json()
                    gif_url = data.get('url')
                    if not gif_url:
                        return await self.bot.send_and_clean(message.channel, "couldn't get hug gif")
                except Exception:
                    return await self.bot.send_and_clean(message.channel, "couldn't fetch hug gif")

        hug_messages = [
            f"{author.mention} [hugs]({gif_url}) {target.mention}",
            f"{author.mention} [embraces]({gif_url}) {target.mention}",
        ]

        msg = self.bot.rand.choice(hug_messages)
        await self.bot.send_and_clean(message.channel, msg)

    async def cmd_pat(self, message, command_args=""):
        if not message.mentions:
            await self.bot.send_and_clean(message.channel, "you need to mention someone to pat")
            return

        target = message.mentions[0]
        author = message.author

        async with aiohttp.ClientSession() as session:
            async with session.get('https://nekos.life/api/v2/img/pat') as resp:
                if resp.status != 200:
                    await self.bot.send_and_clean(message.channel, "couldn't fetch pat gif")
                    return
                try:
                    data = await resp.json()
                    gif_url = data.get('url')
                    if not gif_url:
                        return await self.bot.send_and_clean(message.channel, "couldn't get pat gif")
                except Exception:
                    return await self.bot.send_and_clean(message.channel, "couldn't fetch pat gif")

        pat_messages = [
            f"{author.mention} [pats]({gif_url}) {target.mention}",
            f"{author.mention} [gently pats]({gif_url}) {target.mention}",
        ]

        msg = self.bot.rand.choice(pat_messages)
        await self.bot.send_and_clean(message.channel, msg)

    async def cmd_slap(self, message, command_args=""):
        if not message.mentions:
            await self.bot.send_and_clean(message.channel, "you need to mention someone to slap")
            return

        target = message.mentions[0]
        author = message.author

        async with aiohttp.ClientSession() as session:
            async with session.get('https://nekos.life/api/v2/img/slap') as resp:
                if resp.status != 200:
                    await self.bot.send_and_clean(message.channel, "couldn't fetch slap gif")
                    return
                try:
                    data = await resp.json()
                    gif_url = data.get('url')
                    if not gif_url:
                        return await self.bot.send_and_clean(message.channel, "couldn't get slap gif")
                except Exception:
                    return await self.bot.send_and_clean(message.channel, "couldn't fetch slap gif")

        slap_messages = [
            f"{author.mention} [slaps]({gif_url}) {target.mention}",
            f"{author.mention} [hits]({gif_url}) {target.mention}",
        ]

        msg = self.bot.rand.choice(slap_messages)
        await self.bot.send_and_clean(message.channel, msg)

    async def cmd_kiss(self, message, command_args):
        if not message.mentions:
            await self.bot.send_and_clean(message.channel, "you need to mention someone to kiss")
            return

        target = message.mentions[0]
        author = message.author

        async with aiohttp.ClientSession() as session:
            async with session.get('https://nekos.life/api/v2/img/kiss') as resp:
                if resp.status != 200:
                    await self.bot.send_and_clean(message.channel, "couldn't fetch kiss gif")
                    return
                try:
                    data = await resp.json()
                    gif_url = data.get('url')
                    if not gif_url:
                        return await self.bot.send_and_clean(message.channel, "couldn't get kiss gif")
                except Exception:
                    return await self.bot.send_and_clean(message.channel, "couldn't fetch kiss gif")

        kiss_messages = [
            f"{author.mention} [kisses]({gif_url}) {target.mention}",
            f"{author.mention} [smooches]({gif_url}) {target.mention}",
        ]

        msg = self.bot.rand.choice(kiss_messages)
        await self.bot.send_and_clean(message.channel, msg)

    async def cmd_cuddle(self, message, command_args):
        if not message.mentions:
            await self.bot.send_and_clean(message.channel,"you need to mention someone to cuddle")
            return

        target = message.mentions[0]
        author = message.author

        async with aiohttp.ClientSession() as session:
            async with session.get('https://nekos.life/api/v2/img/cuddle') as resp:
                if resp.status != 200:
                    await self.bot.send_and_clean(message.channel, "couldn't fetch cuddle gif")
                    return
                try:
                    data = await resp.json()
                    gif_url = data.get('url')
                    if not gif_url:
                        return await self.bot.send_and_clean(message.channel, "couldn't get cuddle gif")
                except Exception:
                    return await self.bot.send_and_clean(message.channel, "couldn't fetch cuddle gif")

        cuddle_messages = [
            f"{author.mention} [cuddles]({gif_url}) {target.mention}",
            f"{author.mention} [snuggles]({gif_url}) {target.mention}",
        ]

        msg = self.bot.rand.choice(cuddle_messages)
        await self.bot.send_and_clean(message.channel, msg)

    async def cmd_echo(self, message, command_args):
        if not command_args:
            await self.bot.send_and_clean(message.channel, "usage nux echo <text>")
            return
        await self.bot.send_and_clean(message.channel, command_args)

    async def cmd_dadjoke(self, message, command_args):
        url = "https://icanhazdadjoke.com/"
        headers = {"accept": "application/json"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    await self.bot.send_and_clean(message.channel, data.get("joke", "no dad jokes found your dad left"))
                else:
                    await self.bot.send_and_clean(message.channel, "couldn't reach the dad joke server guess that's the joke")

    async def cmd_weather(self, message, command_args):
        args = command_args.strip()
        if not args:
            if not self.bot.weather_ip_enabled:
                return await self.bot.send_and_clean(message.channel, "usage nux weather <location>")
            async with aiohttp.ClientSession() as session:
                resp = await session.get('https://api.ipify.org')
                if resp.status != 200:
                    return await self.bot.send_and_clean(message.channel, "failed to get IP")
                ip = await resp.text()
                data = await session.get(f'https://ipapi.co/{ip}/json')
                if data.status != 200:
                    return await self.bot.send_and_clean(message.channel, "failed to get geolocation")
                data = await data.json()
                city = data.get('city')
                if not city:
                    return await self.bot.send_and_clean(message.channel, "couldn't determine city from IP")
                location = city
        else:
            location = args
        url = f"https://wttr.in/{location}?format=3"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await self.bot.send_and_clean(message.channel, "couldn't fetch weather info")
                weather = await resp.text()
                await self.bot.send_and_clean(message.channel, weather)

    async def cmd_translate(self, message, command_args):
        args = command_args.strip().split(maxsplit=2)
        if len(args) < 3:
            return await self.bot.send_and_clean(message.channel, "usage nux translate <from_lang> <to_lang> <text>")
        from_lang, to_lang, text = args
        translator = Translator()
        try:
            translated = await translator.translate(text, src=from_lang, dest=to_lang)
            await self.bot.send_and_clean(message.channel, f"{from_lang} → {to_lang} {translated.text}")
        except Exception as e:
            await self.bot.send_and_clean(message.channel, f"translation failed {e}")

    async def cmd_lyrics(self, message, command_args):
        args = command_args.strip().split(" - ", 1)
        if len(args) < 2:
            return await self.bot.send_and_clean(message.channel, "usage nux lyrics <artist> - <song>")
        artist, song = args
        query = f"{artist} - {song}"
        url = "https://lrclib.net/api/search"
        params = {"q": query}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    return await self.bot.send_and_clean(message.channel, "lyrics not found")
                data = await resp.json()
                if not data:
                    return await self.bot.send_and_clean(message.channel, "lyrics not found")
                top_result = data[0]
                lyrics = top_result.get("plainLyrics", "no lyrics found")
                if len(lyrics) > 2000:
                    lyrics = lyrics[:1997] + "..."
                track_name = top_result.get("trackName", song)
                album_name = top_result.get("albumName", "")
                header = f"{artist} - {track_name}"
                if album_name:
                    header += f" ({album_name})"
                await self.bot.send_and_clean(message.channel, f"{header}\n{lyrics}")

    async def cmd_rhyme(self, message, command_args):
        word = command_args.strip()
        if not word:
            return await self.bot.send_and_clean(message.channel, "usage nux rhyme <word>")
        url = f"https://api.datamuse.com/words?rel_rhy={word}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await self.bot.send_and_clean(message.channel, "couldn't fetch rhymes")
                data = await resp.json()
                if not data:
                    return await self.bot.send_and_clean(message.channel, f"no rhymes found for {word}")
                rhymes = [item['word'] for item in data[:10]]
                result = f"rhymes for {word}\n" + ", ".join(rhymes)
                await self.bot.send_and_clean(message.channel, result)

    async def cmd_synonym(self, message, command_args):
        word = command_args.strip()
        if not word:
            return await self.bot.send_and_clean(message.channel, "usage nux synonym <word>")
        url = f"https://api.datamuse.com/words?rel_syn={word}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await self.bot.send_and_clean(message.channel, "couldn't fetch synonyms")
                data = await resp.json()
                if not data:
                    return await self.bot.send_and_clean(message.channel, f"no synonyms found for {word}")
                synonyms = [item['word'] for item in data[:10]]
                result = f"synonyms for {word}\n" + ", ".join(synonyms)
                await self.bot.send_and_clean(message.channel, result)

    async def cmd_barcode(self, message, command_args):
        text = command_args.strip()
        if not text:
            return await self.bot.send_and_clean(message.channel, "usage nux barcode <text>")

        try:
            barcode_class = barcode.get('code128', text, writer=ImageWriter())
            buffer = io.BytesIO()
            barcode_class.write(buffer)
            buffer.seek(0)
            await self.bot.send_and_clean(message.channel, file=discord.File(buffer, filename="barcode.png"))
        except Exception as e:
            await self.bot.send_and_clean(message.channel, f"failed to generate barcode: {e}")

    async def cmd_nasaapod(self, message, command_args=""):
        url = "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await self.bot.send_and_clean(message.channel, "failed to fetch nasa apod")
                data = await resp.json()
                title = data.get('title', 'No title')
                date = data.get('date', 'No date')
                explanation = data.get('explanation', 'No explanation')
                hdurl = data.get('hdurl')
                if hdurl:
                    await self.bot.send_and_clean(message.channel, f"**{title}**\n{date}\n{explanation[:500]}{'...' if len(explanation) > 500 else ''}\n{hdurl}")
                else:
                    await self.bot.send_and_clean(message.channel, f"{title}\n{date}\n{explanation}")

    async def cmd_osu(self, message, command_args):
        username = command_args.strip()
        if not username:
            return await self.bot.send_and_clean(message.channel, "usage nux osu <username>")
        username = urllib.parse.quote(username)
        profile_url = f"https://osu.ppy.sh/users/{username}"
        await self.bot.send_and_clean(message.channel, f"osu! profile link: {profile_url}")

    async def cmd_steamprofile(self, message, command_args):
        steamid = command_args.strip()
        if not steamid:
            return await self.bot.send_and_clean(message.channel, "usage nux steamprofile <steamid64 or vanity url slug>")

        if not STEAM_API_KEY:
            return await self.bot.send_and_clean(message.channel, "steam api key not set")

        loop = asyncio.get_event_loop()
        try:
            resolved_steamid = await loop.run_in_executor(None, self.resolve_steamid, steamid)
            if not resolved_steamid:
                return await self.bot.send_and_clean(message.channel, "could not resolve steamid")

            profile = await loop.run_in_executor(None, self.get_player_summary, resolved_steamid)
            bans = await loop.run_in_executor(None, self.get_player_bans, resolved_steamid)
            friend_count = await loop.run_in_executor(None, self.get_friend_count, resolved_steamid)

            if not profile:
                return await self.bot.send_and_clean(message.channel, "failed to fetch profile")

            buffer = await loop.run_in_executor(None, self.create_steam_profile_card, profile, bans, friend_count)
            await self.bot.send_and_clean(message.channel, file=discord.File(buffer, filename="steam_profile.png"))
        except Exception as e:
            await self.bot.send_and_clean(message.channel, f"error: {e}")

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
            font_title = ImageFont.truetype("arial.ttf", 40)
            font_text = ImageFont.truetype("arial.ttf", 24)
            font_small = ImageFont.truetype("arial.ttf", 18)
        except:
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()
            font_small = ImageFont.load_default()

        card_width, card_height = 1000, 450
        card = Image.new("RGBA", (card_width, card_height), (25, 25, 35, 255))
        draw = ImageDraw.Draw(card)

        for y in range(card_height):
            r = int(25 + y * 0.02)
            g = int(25 + y * 0.02)
            b = int(35 + y * 0.05)
            draw.line([(0, y), (card_width, y)], fill=(r, g, b))

        avatar_size = 150
        mask = Image.new("L", (avatar_size, avatar_size), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, avatar_size, avatar_size), fill=255)
        
        avatar_img = ImageOps.fit(avatar_img, (avatar_size, avatar_size), centering=(0.5, 0.5))
        avatar_img.putalpha(mask)
        
        avatar_x, avatar_y = 50, 50
        card.paste(avatar_img, (avatar_x, avatar_y), avatar_img)

        status_map = {
            0: ("Offline", (120, 120, 120)),
            1: ("Online", (87, 242, 135)),
            2: ("Busy", (237, 66, 69)),
            3: ("Away", (254, 231, 92)),
            4: ("Snooze", (88, 101, 242)),
            5: ("Looking to Trade", (88, 101, 242)),
            6: ("Looking to Play", (88, 101, 242))
        }
        persona_state = profile.get("personastate", 0)
        status_text, status_color = status_map.get(persona_state, ("Unknown", (120, 120, 120)))
        
        status_radius = 15
        status_x = avatar_x + avatar_size - 25
        status_y = avatar_y + avatar_size - 25
        draw.ellipse((status_x, status_y, status_x + status_radius*2, status_y + status_radius*2), fill=status_color, outline=(25, 25, 35), width=3)

        text_x = avatar_x + avatar_size + 40
        text_y = 60
        
        name = profile.get("personaname", "Unknown")
        draw.text((text_x, text_y), name, font=font_title, fill=(255, 255, 255))
        
        real_name = profile.get("realname")
        country = profile.get("loccountrycode")
        sub_info = []
        if real_name: sub_info.append(real_name)
        if country: sub_info.append(country)
        
        if sub_info:
            draw.text((text_x, text_y + 50), " • ".join(sub_info), font=font_small, fill=(180, 180, 180))
            text_y += 30
        else:
             text_y += 10

        text_y += 50
        
        draw.text((text_x, text_y), f"Currently: {status_text}", font=font_text, fill=status_color)
        text_y += 35

        game = profile.get("gameextrainfo")
        if game:
            draw.text((text_x, text_y), f"Playing: {game}", font=font_text, fill=(150, 200, 255))
            text_y += 35

        stats_y = 250
        
        draw.line([(50, 230), (card_width - 50, 230)], fill=(60, 60, 70), width=2)

        col1_x = 50
        col2_x = 400
        col3_x = 700
        
        draw.text((col1_x, stats_y), "Steam ID", font=font_small, fill=(150, 150, 150))
        draw.text((col1_x, stats_y + 25), str(profile.get("steamid")), font=font_text, fill=(220, 220, 220))
        
        draw.text((col1_x, stats_y + 70), "Account Created", font=font_small, fill=(150, 150, 150))
        created = self.format_timestamp(profile.get("timecreated"))
        draw.text((col1_x, stats_y + 95), created, font=font_text, fill=(220, 220, 220))

        draw.text((col2_x, stats_y), "Friends", font=font_small, fill=(150, 150, 150))
        draw.text((col2_x, stats_y + 25), str(friend_count), font=font_text, fill=(220, 220, 220))
        
        draw.text((col2_x, stats_y + 70), "Last Online", font=font_small, fill=(150, 150, 150))
        last_online = self.format_timestamp(profile.get("lastlogoff"))
        draw.text((col2_x, stats_y + 95), last_online, font=font_text, fill=(220, 220, 220))

        vac_bans = bans.get("NumberOfVACBans", 0)
        game_bans = bans.get("NumberOfGameBans", 0)
        comm_ban = bans.get("CommunityBanned", False)
        
        ban_text = "None"
        ban_color = (100, 255, 100)
        if vac_bans > 0 or game_bans > 0 or comm_ban:
            ban_text = f"{vac_bans} VAC, {game_bans} Game"
            if comm_ban: ban_text += ", Comm Ban"
            ban_color = (255, 100, 100)

        draw.text((col3_x, stats_y), "Bans", font=font_small, fill=(150, 150, 150))
        draw.text((col3_x, stats_y + 25), ban_text, font=font_text, fill=ban_color)

        buffer = io.BytesIO()
        card.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer

    async def cmd_wiki(self, message, command_args=""):
        query = message.content.strip()[len("nux wiki"):].strip()
        if not query:
            return await self.bot.send_and_clean(message.channel, "usage nux wiki <search term>")

        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(query)}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await self.bot.send_and_clean(message.channel, f"no wikipedia page found for '{query}'")

                data = await resp.json()

                title = data.get('title', 'unknown')
                extract = data.get('extract', 'no description available')
                page_url = data.get('content_urls', {}).get('desktop', {}).get('page', '')

                if len(extract) > 1800:
                    extract = extract[:1800] + "..."

                info = f"{title}\n{extract}\n\nread more on wikipedia {page_url}"
                await self.bot.send_and_clean(message.channel, info)

    async def cmd_github(self, message, command_args=""):
        username = message.content.strip()[len("nux github"):].strip()
        if not username:
            return await self.bot.send_and_clean(message.channel, "usage nux github <username>")

        url = f"https://api.github.com/users/{username}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await self.bot.send_and_clean(message.channel, f"github user '{username}' not found")

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

                await self.bot.send_and_clean(message.channel, info)

    async def cmd_coinflip(self, message, command_args=""):
        coin_landed = random.choice(["heads", "tails"])
        await self.bot.send_and_clean(message.channel, f"coin landed on {coin_landed}")

    async def cmd_rate(self, message, command_args):
        thing = command_args.strip()
        if not thing:
            return await self.bot.send_and_clean(message.channel, "rate what?")
        rating = self.bot.rand.randint(0, 10)
        await self.bot.send_and_clean(message.channel, f"i rate {thing} a {rating}/10")

    async def cmd_ship(self, message, command_args):
        if len(message.mentions) < 2:
            args = command_args.split()
            if len(args) < 2:
                 return await self.bot.send_and_clean(message.channel, "mention two people to ship")
            user1 = args[0]
            user2 = args[1]
        else:
            user1 = message.mentions[0].mention
            user2 = message.mentions[1].mention
        
        score = self.bot.rand.randint(0, 100)
        msg = f"shipping {user1} and {user2}\ncompatibility: {score}%"
        
        if score == 100: msg += " \nperfect match 💖"
        elif score > 80: msg += " \ngreat match ❤️"
        elif score > 50: msg += " \ngood match 💛"
        elif score > 20: msg += " \nmeh match 💔"
        else: msg += " \nawful match 🖤"
        
        await self.bot.send_and_clean(message.channel, msg)

    async def cmd_haiku(self, message, command_args):
        prompt = command_args.strip()
        if not prompt:
            return await self.bot.send_and_clean(message.channel, "provide a prompt for the haiku")
        
        messages = [{"role": "user", "content": f"Write a haiku about: {prompt}. Only respond with the haiku, nothing else."}]
        haiku = await self.bot.ask_ai(messages)
        
        if haiku:
            await self.bot.send_and_clean(message.channel, haiku)
        else:
            await self.bot.send_and_clean(message.channel, "failed to generate haiku")

    async def cmd_clippy(self, message, command_args):
        text = command_args.strip()
        if not text:
            return await self.bot.send_and_clean(message.channel, "what do you need help with?")
        
        messages = [
            {"role": "system", "content": "You are Clippy, the passive-aggressive Microsoft Office assistant. Respond in a condescending, sarcastic way while pretending to be helpful. Keep responses short (1-2 sentences)."},
            {"role": "user", "content": text}
        ]
        response = await self.bot.ask_ai(messages)
        
        if response:
            await self.bot.send_and_clean(message.channel, f"📎 {response}")
        else:
            await self.bot.send_and_clean(message.channel, "looks like even I can't help with that one")

    async def cmd_songlyrics(self, message, command_args):
        theme = command_args.strip()
        if not theme:
            return await self.bot.send_and_clean(message.channel, "provide a theme or genre for the song")
        
        messages = [{"role": "user", "content": f"Write song lyrics about: {theme}. Include verse, chorus, and bridge. Make it creative and catchy."}]
        lyrics = await self.bot.ask_ai(messages, max_tokens=1000)
        
        if lyrics:
            if len(lyrics) > 2000:
                lyrics = lyrics[:1997] + "..."
            await self.bot.send_and_clean(message.channel, f"🎵 **Song Lyrics**\n{lyrics}")
        else:
            await self.bot.send_and_clean(message.channel, "failed to generate lyrics")

    async def cmd_advice(self, message, command_args):
        topic = command_args.strip()
        if not topic:
            return await self.bot.send_and_clean(message.channel, "what do you need advice on?")
        
        messages = [
            {"role": "system", "content": "You are a helpful advisor. Give practical, thoughtful advice. Keep responses concise (2-3 sentences max)."},
            {"role": "user", "content": topic}
        ]
        advice = await self.bot.ask_ai(messages)
        
        if advice:
            await self.bot.send_and_clean(message.channel, f"💡 {advice}")
        else:
            await self.bot.send_and_clean(message.channel, "couldn't generate advice")

    async def cmd_roast(self, message, command_args):
        target = command_args.strip()
        if not target and not message.mentions:
            return await self.bot.send_and_clean(message.channel, "who am I roasting?")
        
        if message.mentions:
            target = message.mentions[0].display_name
        
        messages = [
            {"role": "system", "content": "You are a master of creative, witty roasts. Generate a clever, funny roast that's harsh but not genuinely hurtful. Keep it to 1-2 sentences."},
            {"role": "user", "content": f"Roast {target}"}
        ]
        roast = await self.bot.ask_ai(messages)
        
        if roast:
            mention = message.mentions[0].mention if message.mentions else target
            await self.bot.send_and_clean(message.channel, f"🔥 {mention}: {roast}")
        else:
            await self.bot.send_and_clean(message.channel, "couldn't generate roast")

    async def cmd_compliment(self, message, command_args):
        target = command_args.strip()
        if not target and not message.mentions:
            return await self.bot.send_and_clean(message.channel, "who am I complimenting?")
        
        if message.mentions:
            target = message.mentions[0].display_name
        
        messages = [
            {"role": "system", "content": "You are a master of genuine, heartfelt compliments. Generate a creative, specific compliment that feels personal and uplifting. Keep it to 1-2 sentences."},
            {"role": "user", "content": f"Compliment {target}"}
        ]
        compliment = await self.bot.ask_ai(messages)
        
        if compliment:
            mention = message.mentions[0].mention if message.mentions else target
            await self.bot.send_and_clean(message.channel, f"✨ {mention}: {compliment}")
        else:
            await self.bot.send_and_clean(message.channel, "couldn't generate compliment")

    async def cmd_summarize(self, message, command_args):
        text = command_args.strip()
        if not text:
            return await self.bot.send_and_clean(message.channel, "provide text to summarize")
        
        messages = [
            {"role": "system", "content": "You are an expert at summarizing text. Provide a clear, concise summary of the key points. Keep it brief."},
            {"role": "user", "content": f"Summarize this: {text}"}
        ]
        summary = await self.bot.ask_ai(messages)
        
        if summary:
            await self.bot.send_and_clean(message.channel, f"📝 **Summary**\n{summary}")
        else:
            await self.bot.send_and_clean(message.channel, "couldn't generate summary")

    async def cmd_code(self, message, command_args):
        description = command_args.strip()
        if not description:
            return await self.bot.send_and_clean(message.channel, "describe what code you need")
        
        messages = [
            {"role": "system", "content": "You are a coding assistant. Generate clean, working code based on the description. Include brief comments. Only output code, no explanations unless asked."},
            {"role": "user", "content": description}
        ]
        code = await self.bot.ask_ai(messages, max_tokens=1000)
        
        if code:
            if len(code) > 1900:
                code = code[:1897] + "..."
            await self.bot.send_and_clean(message.channel, f"```\n{code}\n```")
        else:
            await self.bot.send_and_clean(message.channel, "couldn't generate code")
        
def setup(bot):
    return Fun(bot), HELP_TEXT
