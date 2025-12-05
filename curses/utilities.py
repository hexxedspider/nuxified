import discord
import aiohttp
import asyncio
import datetime
import psutil
import platform
import io
import os
import json
import pickle
import math
import re
import urllib.parse
import collections
from difflib import SequenceMatcher
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
from simpleeval import simple_eval

XGD_API_KEY = "25ff18ddf60a188f5f2b412db909b8f9"

HELP_TEXT = {
    "utilities": {
        "nux id": "show your user id",
        "nux help": "shows this message",
        "nux help spaced": "shows this message but spaced out to prevent automod",
        "nux uptime": "shows how long the bot has been online",
        "nux ping": "shows the bot's latency",
        "nux userinfo <@user>": "shows info about a user",
        "nux serverinfo": "shows info about the server",
        "nux channelinfo": "shows info about the channel",
        "nux roleinfo <@role>": "shows info about a role",
        "nux avatar <@user>": "shows a user's avatar",
        "nux banner <@user>": "shows a user's banner",
        "nux emojis": "shows all emojis in the server",
        "nux usercount": "shows the member count of the server",
        "nux iplookup <ip>": "looks up an ip address",
        "nux inviteinfo <invite>": "shows info about an invite",
        "nux shorten <1|2> <url>": "shortens a url",
        "nux calc <expression>": "calculates a math expression",
        "nux stats": "shows bot statistics",
        "nux bug": "report a bug",
        "nux repo": "link to the github repo",
        "nux version": "shows the current bot version",
        "nux update": "check for updates",
        "nux color <hex>": "shows color info and preview",
        "nux temperature <value> <c|f>": "convert temperature",
        "nux binary <encode|decode> <text>": "convert text to/from binary",
        "nux todo <add|list|remove|clear>": "manage todo list",
        "nux steal <emoji/sticker>": "steal an emoji or sticker",
        "nux topmembers <limit>": "show most active members in channel",
        "nux watch <guild_id|dm|list>": "watch a guild or dms",
        "nux trackjoins <guild_id|list>": "track joins in a guild",
        "nux setjoinwebhook <url>": "set webhook for join tracking",
        "nux voicewatch <guild_id|list>": "watch voice channels",
        "nux autoowod <start|stop>": "auto owo daily",
        "nux autoreact <channel_id> <keyword> <emoji>": "auto react to keywords",
        "nux ai memory <user_id>": "show ai conversation memory",
        "nux learn <phrase> | <response>": "teach the ai a custom response",
        "nux config": "show current config",
        "nux ghost": "toggle ghost mode",
        "nux statustoggle": "toggle status rotation",
        "nux servericon": "get the server icon",
        "nux habit <phrase>": "message frequency heatmap for phrase",
        "nux antivocab": "identify least used words in chat",
        "nux timezone <@user>": "user activity peaks heatmap",
    }
}

def owner_only():
    def decorator(func):
        async def wrapper(self, message, *args, **kwargs):
            if message.author.id != self.bot.owner_id:
                await self.bot.send_and_clean(message.channel, "only i can do that")
                return
            return await func(self, message, *args, **kwargs)
        return wrapper
    return decorator

class Utilities:
    def __init__(self, bot):
        self.bot = bot
    
    def build_help_message(self):
        help_message = "available commands\n\n"
        for category, commands in sorted(self.bot.help_categories.items(), key=lambda x: x[0]):
            if category.lower() in ["nsfw", "owner"]:
                continue
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
        for category, commands in sorted(self.bot.help_categories.items(), key=lambda x: x[0]):
            if category.lower() in ["nsfw", "owner"]:
                continue
            help_message += f"{category}\n\n"
            if not isinstance(commands, dict):
                help_message += f"error {category} is not formatted correctly\n\n\n"
                continue
            for cmd, desc in sorted(commands.items()):
                help_message += f"- `{cmd}` {desc}\n\n\n"
            help_message += "\n\n"
        return help_message

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

    async def cmd_help(self, message, command_args=""):
        help_msg = self.build_help_message()
        chunks = self.split_message(help_msg)
        for chunk in chunks:
            await self.bot.send_and_clean(message.channel, chunk)

    async def cmd_spacedhelp(self, message, command_args=""):
        help_msg = self.build_spaced_help_message()
        chunks = self.split_message(help_msg)
        async with message.channel.typing():
            for chunk in chunks:
                msg = await message.channel.send(chunk)
                await asyncio.sleep(2.3)

    async def cmd_id(self, message, command_args):
        async with message.channel.typing():
            await asyncio.sleep(3.627)
            user = message.author
            content = (
                f"username {user.name}\n"
                f"user id {user.id}\n"
                "you still exist"
            )
            await self.bot.send_and_clean(message.channel, content)

    async def cmd_uptime(self, message, command_args=""):
        if hasattr(self.bot, 'start_time'):
            uptime_seconds = (datetime.datetime.utcnow() - self.bot.start_time).total_seconds()
            uptime_str = str(datetime.timedelta(seconds=int(uptime_seconds)))
        else:
            uptime_str = "unknown"

        memory = psutil.virtual_memory()
        cpu_usage = psutil.cpu_percent()
        ram_usage = memory.percent

        msg = (
            f"uptime {uptime_str}\n"
            f"total cpu usage {cpu_usage}%\n"
            f"total ram usage {ram_usage}%\n"
        )

        await self.bot.send_and_clean(message.channel, msg)

    async def cmd_ping(self, message, command_args=""):
        latency = round(self.bot.latency * 1000)
        await self.bot.send_and_clean(message.channel, f"{latency}ms")

    async def cmd_version(self, message, command_args=""):
        version = getattr(self.bot, 'VERSION', 'unknown')
        await self.bot.send_and_clean(message.channel, f"nuxified version: {version}")

    async def cmd_about(self, message, command_args=""):
        await self.bot.send_and_clean(message.channel, "github repo: https://github.com/hexxedspider/nuxified [⠀](https://files.catbox.moe/t5frn4.png)\n\ndocs: https://github.com/hexxedspider/nuxified/wiki\n\nwebsite: https://hexxedspider.github.io/nuxified")

    async def cmd_repo(self, message, command_args=""):
        await self.bot.send_and_clean(message.channel, "https://github.com/hexxedspider/nuxified")


    async def cmd_userinfo(self, message, command_args):
        if not message.mentions:
            await self.bot.send_and_clean(message.channel, "please mention a user to inspect")
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

        await self.bot.send_and_clean(message.channel, info)

    async def cmd_roleinfo(self, message, command_args):
       if not message.role_mentions:
           return await self.bot.send_and_clean(message.channel, "please mention a role to inspect")

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

       await self.bot.send_and_clean(message.channel, info)

    async def cmd_serverinfo(self, message, command_args=""):
        if not message.guild:
            return await self.bot.send_and_clean(message.channel, "this command only works in a server")

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

        await self.bot.send_and_clean(message.channel, info)

    async def cmd_servericon(self, message, command_args=""):
        if not message.guild:
            return await self.bot.send_and_clean(message.channel, "this command only works in a server")
        
        if not message.guild.icon:
            return await self.bot.send_and_clean(message.channel, "this server has no icon")
            
        await self.bot.send_and_clean(message.channel, f"{message.guild.name}'s [icon]({message.guild.icon.url})")

    async def cmd_channelinfo(self, message, command_args=""):
        if not message.guild:
            return await self.bot.send_and_clean(message.channel, "this command only works in a server")

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

        await self.bot.send_and_clean(message.channel, info)

    async def cmd_emojis(self, message, command_args=""):
        if not message.guild:
            return await self.bot.send_and_clean(message.channel, "this server has no custom emojis")

        guild = message.guild
        emojis = guild.emojis

        if not emojis:
            return await self.bot.send_and_clean(message.channel, "this server has no custom emojis")

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

        await self.bot.send_and_clean(message.channel, info)

    async def cmd_avatar(self, message, command_args=""):
        if not message.mentions:
            user = message.author
        else:
            user = message.mentions[0]

        avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
        await self.bot.send_and_clean(message.channel, f"{user}'s [avatar]({avatar_url})")

    async def cmd_banner(self, message, command_args=""):
        if not message.mentions:
            user = message.author
        else:
            user = message.mentions[0]

        if not hasattr(user, 'banner') or not user.banner:
            return await self.bot.send_and_clean(message.channel, f"{user.mention} doesn't have a banner set")

        banner_url = user.banner.url
        await self.bot.send_and_clean(message.channel, f"{user}'s [banner]({banner_url})")

    async def cmd_usercount(self, message, command_args=""):
        if not message.guild:
            return await self.bot.send_and_clean(message.channel, "this command only works in a server")
        online = len([m for m in message.guild.members if m.status == discord.Status.online])
        idle = len([m for m in message.guild.members if m.status == discord.Status.idle])
        dnd = len([m for m in message.guild.members if m.status == discord.Status.do_not_disturb])
        offline = len([m for m in message.guild.members if m.status == discord.Status.offline])
        total = message.guild.member_count
        await self.bot.send_and_clean(message.channel, f"server member count\nonline {online}\nidle {idle}\ndnd {dnd}\noffline {offline}\ntotal {total}")

    async def cmd_iplookup(self, message, command_args):
        ip = message.content.strip()[len("nux iplookup"):].strip()
        if not ip:
            return await self.bot.send_and_clean(message.channel, "usage nux iplookup <ip>")
        url = f"http://ip-api.com/json/{ip}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await self.bot.send_and_clean(message.channel, "failed to lookup ip")
                data = await resp.json()
                if data.get("status") != "success":
                    return await self.bot.send_and_clean(message.channel, "invalid ip or lookup failed")
                info = f"ip lookup\ncountry {data.get('country')}\nregion {data.get('regionName')}\ncity {data.get('city')}\nisp {data.get('isp')}\norg {data.get('org')}"
                await self.bot.send_and_clean(message.channel, info)

    async def cmd_inviteinfo(self, message, command_args):
        parts = command_args.split(maxsplit=1)
        if len(parts) < 1:
            await self.bot.send_and_clean(message.channel, "usage nux inviteinfo <invite_code_or_url>")
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
            try:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await self.bot.send_and_clean(message.channel, "failed to fetch invite info invite might be invalid or expired")

                    data = await resp.json()

            except Exception as e:
                return await self.bot.send_and_clean(message.channel, f"error fetching invite info: {e}")

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

        await self.bot.send_and_clean(message.channel, msg)

    async def cmd_shorten(self, message, command_args):
        content = command_args

        if not content:
            return await self.bot.send_and_clean(
                message.channel,
                "choose your shortener\n"
                "1 is.gd\n"
                "2 x.gd\n"
                "usage\n"
                "`nux shorten <number> <url>`"
            )

        parts = content.split(maxsplit=1)
        choice = parts[0]

        try:
            if choice == "1":
                if len(parts) < 2:
                    return await self.bot.send_and_clean(message.channel, "missing url")
                url = parts[1]
                api_url = f"https://is.gd/create.php?format=simple&url={urllib.parse.quote(url)}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(api_url) as resp:
                        if resp.status != 200:
                            return await self.bot.send_and_clean(message.channel, "couldn't shrink that one")
                        short_url = await resp.text()
                        if len(short_url) > 4000:
                            short_url = short_url[:3997] + "..."
                        return await self.bot.send_and_clean(message.channel, short_url)

            elif choice == "2":
                if len(parts) < 2:
                    return await self.bot.send_and_clean(message.channel, "missing url")
                url = parts[1]
                api_url = f"https://xgd.io/V1/shorten?url={urllib.parse.quote(url)}&key={XGD_API_KEY}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(api_url) as resp:
                        if resp.status != 200:
                            return await self.bot.send_and_clean(message.channel, "couldn't shrink that one")
                        data = await resp.json()
                        if "shorturl" in data:
                            short_url = data["shorturl"]
                            if len(short_url) > 4000:
                                short_url = short_url[:3997] + "..."
                            return await self.bot.send_and_clean(message.channel, short_url)
                        else:
                            return await self.bot.send_and_clean(message.channel, "no shortened url returned")

            else:
                return await self.bot.send_and_clean(message.channel, "invalid choice use 1, or 2.")

        except Exception as e:
            print("[shorten error]", repr(e))
            await self.bot.send_and_clean(message.channel, f"something blocked the shortening spell `{e}`")

    async def cmd_calc(self, message, command_args):
        expr = command_args
        if not expr:
            return await self.bot.send_and_clean(message.channel, "give me something to calculate, genius")
        try:
            result = simple_eval(expr, functions={"sqrt": math.sqrt, "pow": pow, "abs": abs})
            await self.bot.send_and_clean(message.channel, f"`{expr}` = **{result}**")
        except Exception as e:
            await self.bot.send_and_clean(message.channel, "that's not a valid expression")
            
    async def cmd_stats(self, message, command_args=""):
        if hasattr(self.bot, 'start_time'):
            uptime_seconds = (datetime.datetime.utcnow() - self.bot.start_time).total_seconds()
            uptime_str = str(datetime.timedelta(seconds=int(uptime_seconds)))
        else:
            uptime_str = "unknown"

        memory = psutil.virtual_memory()
        cpu_usage = psutil.cpu_percent(interval=0.5)
        ram_usage = memory.percent

        total_guilds = len(self.bot.guilds)
        total_users = sum(guild.member_count for guild in self.bot.guilds)

        total_commands = sum(len(commands) for commands in self.bot.help_categories.values())

        info = f"bot statistics\n"
        info += f"uptime {uptime_str}\n"
        info += f"cpu usage {cpu_usage}%\n"
        info += f"ram usage {ram_usage}%\n"
        info += f"latency {round(self.bot.latency * 1000)}ms\n"
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

        await self.bot.send_and_clean(message.channel, info, file=file)

    async def cmd_bug(self, message, command_args=""):
        await self.bot.send_and_clean(message.channel, "send a [report](https://nukumoxy.netlify.app/), and it'll send to [here.](https://discord.gg/63mSzU8hkR)")
        await self.bot.send_and_clean(message.channel, "\n\n-# originally, you would send a description and it would send a webhook embed to my server, but it would 100% always make your account need to reset it's password.")

    async def cmd_update(self, message, command_args=""):
        try:
            url = "https://api.github.com/repos/hexxedspider/nuxified/releases/latest"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        latest_tag = data.get('tag_name', '').lstrip('v')
                        current_ver_str = getattr(self.bot, 'VERSION', '0.0.0').lstrip('v')
                        
                        try:
                            latest_parts = [int(x) for x in latest_tag.split('.')]
                            current_parts = [int(x) for x in current_ver_str.split('.')]
                            
                            while len(latest_parts) < 3: latest_parts.append(0)
                            while len(current_parts) < 3: current_parts.append(0)
                            
                            if current_parts > latest_parts:
                                await self.bot.send_and_clean(message.channel, f"your version: v{current_ver_str} - unreleased\nlatest release: v{latest_tag}\nyou are on an unverified (test?) build.") # for when im developing
                            elif current_parts < latest_parts:
                                await self.bot.send_and_clean(message.channel, f"your version: v{current_ver_str}\nlatest release: v{latest_tag}\nupdate available at https://github.com/hexxedspider/nuxified/releases/latest") # users will see this more than me
                            else:
                                await self.bot.send_and_clean(message.channel, f"your version: v{current_ver_str}\nyou are up to date.")
                        except ValueError:
                             if latest_tag != current_ver_str:
                                 await self.bot.send_and_clean(message.channel, f"your version: v{current_ver_str}\nlatest release: v{latest_tag}\nupdate available (version mismatch)") # i will never see this
                             else:
                                 await self.bot.send_and_clean(message.channel, f"your version: v{current_ver_str}\nyou are up to date.")

                    else:
                        await self.bot.send_and_clean(message.channel, "failed to check for updates")
        except Exception as e:
            await self.bot.send_and_clean(message.channel, f"error checking updates: {e}")
            
    async def cmd_color(self, message, command_args):
        hex_color = command_args.strip().lstrip('#')
        if not hex_color:
            return await self.bot.send_and_clean(message.channel, "usage: nux color <hex>")
        
        if len(hex_color) not in [3, 6] or not all(c in '0123456789ABCDEFabcdef' for c in hex_color):
            return await self.bot.send_and_clean(message.channel, "invalid hex color")
        
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        r_norm, g_norm, b_norm = r/255, g/255, b/255
        max_val = max(r_norm, g_norm, b_norm)
        min_val = min(r_norm, g_norm, b_norm)
        l = (max_val + min_val) / 2
        
        if max_val == min_val:
            h = s = 0
        else:
            d = max_val - min_val
            s = d / (2 - max_val - min_val) if l > 0.5 else d / (max_val + min_val)
            if max_val == r_norm:
                h = (g_norm - b_norm) / d + (6 if g_norm < b_norm else 0)
            elif max_val == g_norm:
                h = (b_norm - r_norm) / d + 2
            else:
                h = (r_norm - g_norm) / d + 4
            h /= 6
        
        h_deg = int(h * 360)
        s_pct = int(s * 100)
        l_pct = int(l * 100)
        
        decimal = (r << 16) + (g << 8) + b
        
        img = Image.new('RGB', (200, 100), (r, g, b))
        draw = ImageDraw.Draw(img)
        
        info = f"color #{hex_color.upper()}\n"
        info += f"RGB: rgb({r}, {g}, {b})\n"
        info += f"HSL: hsl({h_deg}°, {s_pct}%, {l_pct}%)\n"
        info += f"Decimal: {decimal}"
        
        with io.BytesIO() as image_binary:
            img.save(image_binary, "PNG")
            image_binary.seek(0)
            await self.bot.send_and_clean(message.channel, content=info, file=discord.File(fp=image_binary, filename=f"color_{hex_color}.png"))

    async def cmd_temperature(self, message, command_args):
        parts = command_args.strip().split()
        if len(parts) != 2:
            return await self.bot.send_and_clean(message.channel, "usage: nux temperature <value> <c|f>")
        
        try:
            value = float(parts[0])
        except ValueError:
            return await self.bot.send_and_clean(message.channel, "invalid temperature value")
        
        unit = parts[1].lower()
        
        if unit == 'c':
            fahrenheit = (value * 9/5) + 32
            await self.bot.send_and_clean(message.channel, f"{value}°C = {fahrenheit:.2f}°F")
        elif unit == 'f':
            celsius = (value - 32) * 5/9
            await self.bot.send_and_clean(message.channel, f"{value}°F = {celsius:.2f}°C")
        else:
            await self.bot.send_and_clean(message.channel, "unit must be 'c' or 'f'")

    async def cmd_binary(self, message, command_args):
        parts = command_args.strip().split(maxsplit=1)
        if len(parts) < 2:
            return await self.bot.send_and_clean(message.channel, "usage: nux binary <encode|decode> <text>")
        
        mode = parts[0].lower()
        text = parts[1]
        
        if mode == 'encode':
            binary = ' '.join(format(ord(c), '08b') for c in text)
            await self.bot.send_and_clean(message.channel, f"```{binary}```")
        elif mode == 'decode':
            try:
                binary_str = text.replace(' ', '')
                if len(binary_str) % 8 != 0:
                    return await self.bot.send_and_clean(message.channel, "invalid binary string (must be multiple of 8 bits)")
                
                chars = []
                for i in range(0, len(binary_str), 8):
                    byte = binary_str[i:i+8]
                    chars.append(chr(int(byte, 2)))
                
                result = ''.join(chars)
                await self.bot.send_and_clean(message.channel, result)
            except Exception as e:
                await self.bot.send_and_clean(message.channel, f"failed to decode binary: {e}")
        else:
            await self.bot.send_and_clean(message.channel, "mode must be 'encode' or 'decode'")

    async def cmd_aping(self, message, command_args):
        await self.bot.send_and_clean(message.channel, f"nux base64 decode dW5kZWFkIFsyXQ==.")

    async def cmd_todo(self, message, command_args):
        parts = command_args.strip().split(maxsplit=1)
        if not parts:
            return await self.bot.send_and_clean(message.channel, "usage: nux todo <add|list|remove|clear> [text]")
        
        action = parts[0].lower()
        
        if action == 'add':
            if len(parts) < 2:
                return await self.bot.send_and_clean(message.channel, "usage: nux todo add <item>")
            
            item = parts[1]
            self.bot.todo_list.append(item)
            self.bot.save_config()
            await self.bot.send_and_clean(message.channel, f"added todo item #{len(self.bot.todo_list)}: {item}")
        
        elif action == 'list':
            if not self.bot.todo_list:
                return await self.bot.send_and_clean(message.channel, "todo list is empty")
            
            todo_text = "todo list:\n"
            for i, item in enumerate(self.bot.todo_list, 1):
                todo_text += f"{i}. {item}\n"
            await self.bot.send_and_clean(message.channel, todo_text.rstrip())
        
        elif action == 'remove':
            if len(parts) < 2:
                return await self.bot.send_and_clean(message.channel, "usage: nux todo remove <number>")
            
            try:
                index = int(parts[1]) - 1
                if 0 <= index < len(self.bot.todo_list):
                    removed = self.bot.todo_list.pop(index)
                    self.bot.save_config()
                    await self.bot.send_and_clean(message.channel, f"removed: {removed}")
                else:
                    await self.bot.send_and_clean(message.channel, f"invalid index (1-{len(self.bot.todo_list)})")
            except ValueError:
                await self.bot.send_and_clean(message.channel, "index must be a number")
        
        elif action == 'clear':
            count = len(self.bot.todo_list)
            self.bot.todo_list = []
            self.bot.save_config()
            await self.bot.send_and_clean(message.channel, f"cleared {count} todo items")
        
        else:
            await self.bot.send_and_clean(message.channel, "action must be: add, list, remove, or clear")

    async def cmd_steal(self, message, command_args):
        if message.stickers:
            sticker = message.stickers[0]
            sticker_url = sticker.url
            filename = f"{sticker.name}.png"
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(sticker_url) as resp:
                        if resp.status != 200:
                            return await self.bot.send_and_clean(message.channel, "failed to download sticker")
                        
                        sticker_data = await resp.read()
                
                buffer = io.BytesIO(sticker_data)
                await self.bot.send_and_clean(message.channel, file=discord.File(buffer, filename=filename))
            except Exception as e:
                await self.bot.send_and_clean(message.channel, f"error downloading sticker: {e}")
            return
        
        emoji_match = re.search(r'<(a?):(\w+):(\d+)>', command_args)
        if emoji_match:
            animated = emoji_match.group(1) == 'a'
            emoji_name = emoji_match.group(2)
            emoji_id = emoji_match.group(3)
            
            ext = 'gif' if animated else 'png'
            emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}"
            filename = f"{emoji_name}.{ext}"
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(emoji_url) as resp:
                        if resp.status != 200:
                            return await self.bot.send_and_clean(message.channel, "failed to download emoji")
                        
                        emoji_data = await resp.read()
                
                buffer = io.BytesIO(emoji_data)
                await self.bot.send_and_clean(message.channel, file=discord.File(buffer, filename=filename))
            except Exception as e:
                await self.bot.send_and_clean(message.channel, f"error downloading emoji: {e}")
            return
        
        await self.bot.send_and_clean(message.channel, "usage: nux steal <emoji> or use on a message with a sticker")

    async def cmd_topmembers(self, message, command_args):
        if not message.guild:
            return await self.bot.send_and_clean(message.channel, "this command only works in servers")
        
        limit = 10
        if command_args.strip():
            try:
                limit = int(command_args.strip())
                limit = max(1, min(limit, 25))
            except ValueError:
                return await self.bot.send_and_clean(message.channel, "limit must be a number")
        
        member_counts = {}
        
        try:
            async for msg in message.channel.history(limit=500):
                if msg.author.bot:
                    continue
                if msg.author.id not in member_counts:
                    member_counts[msg.author.id] = {
                        'name': str(msg.author),
                        'count': 0
                    }
                member_counts[msg.author.id]['count'] += 1
            
            if not member_counts:
                return await self.bot.send_and_clean(message.channel, "no messages found in recent history")
            
            sorted_members = sorted(member_counts.items(), key=lambda x: x[1]['count'], reverse=True)
            
            response = f"top {min(limit, len(sorted_members))} members (last 500 messages):\n"
            for i, (member_id, data) in enumerate(sorted_members[:limit], 1):
                response += f"{i}. {data['name']}: {data['count']} messages\n"
            
            await self.bot.send_and_clean(message.channel, response.rstrip())
        
        except Exception as e:
            await self.bot.send_and_clean(message.channel, f"error analyzing messages: {e}")

    @owner_only()
    async def cmd_watch(self, message, command_args):
        args = message.content.lower().split()
        if len(args) < 3:
            return await self.bot.send_and_clean(message.channel, "usage: nux watch <guild_id | dm | list>")

        target = args[2]

        if target == "dm":
            self.bot.watch_all_dms = not self.bot.watch_all_dms
            status = "now" if self.bot.watch_all_dms else "no longer"
            await self.bot.send_and_clean(message.channel, f"i am {status} tracking all dms")
        elif target == "list":
            watched_list = []
            if self.bot.watch_all_dms:
                watched_list.append("direct messages (dm)")
            for guild_id in list(self.bot.watched_guilds):
                guild = self.bot.get_guild(guild_id)
                if guild:
                    watched_list.append(f"{guild.name} (id {guild_id})")
                else:
                    self.bot.watched_guilds.remove(guild_id)
                    self.bot.save_config()
            
            if watched_list:
                response = "currently watching:\n" + "\n".join(watched_list)
            else:
                response = "not currently watching any servers or dms"
            await self.bot.send_and_clean(message.channel, response)
            return
        else:
            try:
                guild_id = int(target)
            except ValueError:
                return await self.bot.send_and_clean(message.channel, "invalid guild id or target")

            if guild_id in self.bot.watched_guilds:
                self.bot.watched_guilds.remove(guild_id)
                await self.bot.send_and_clean(message.channel, f"stopped watching guild {guild_id}")
            else:
                self.bot.watched_guilds.add(guild_id)
                await self.bot.send_and_clean(message.channel, f"now watching guild {guild_id}")
        
        self.bot.save_config()

    @owner_only()
    async def cmd_trackjoins(self, message, command_args):
        if not command_args or command_args.lower().strip() == "list":
            tracked_list = []
            for guild_id in self.bot.tracked_joins:
                guild = self.bot.get_guild(guild_id)
                if guild:
                    tracked_list.append(f"{guild.name} (id {guild_id})")
            if tracked_list:
                response = "currently tracking joins for:\n" + "\n".join(tracked_list)
            else:
                response = "no guilds are being tracked for joins"
            await self.bot.send_and_clean(message.channel, response)
        else:
            try:
                guild_id = int(command_args.strip())
            except ValueError:
                await self.bot.send_and_clean(message.channel, "provide a valid guild id or use 'list' to see tracked guilds")
                return
            if guild_id in self.bot.tracked_joins:
                self.bot.tracked_joins.remove(guild_id)
                await self.bot.send_and_clean(message.channel, f"stopped tracking joins in guild {guild_id}")
            else:
                self.bot.tracked_joins.add(guild_id)
                await self.bot.send_and_clean(message.channel, f"now tracking joins in guild {guild_id}")
            self.bot.save_config()

    @owner_only()
    async def cmd_setjoinwebhook(self, message, command_args=""):
        if not command_args or command_args.lower() in ["status", "stat"]:
            if not self.bot.join_webhook:
                await self.bot.send_and_clean(message.channel, "no join webhook set")
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
                        "avatar_url": self.bot.user.avatar.url if self.bot.user.avatar else None,
                        "embeds": [embed]
                    }
                    resp = await session.post(self.bot.join_webhook, json=payload)
                    if resp.status == 204:
                        await self.bot.send_and_clean(message.channel, "join webhook is set and working")
                    else:
                        await self.bot.send_and_clean(message.channel, "join webhook is set but not working (check url)")
            except Exception as e:
                await self.bot.send_and_clean(message.channel, f"join webhook is set but error: {e}")
        else:
            webhook_url = command_args.strip()
            if not webhook_url:
                await self.bot.send_and_clean(message.channel, "provide a webhook url")
                return
            if not webhook_url.startswith("https://discordapp.com/api/webhooks/") and not webhook_url.startswith("https://discord.com/api/webhooks/"):
                await self.bot.send_and_clean(message.channel, "provide a valid discord webhook url")
                return
            self.bot.join_webhook = webhook_url
            self.bot.save_config()
            await self.bot.send_and_clean(message.channel, "join notification webhook set")

    @owner_only()
    async def cmd_voicewatch(self, message, command_args=""):
        action = command_args.strip()

        if not action:
            await self.bot.send_and_clean(message.channel, "usage nux voicewatch <guild_id | list>")
            return

        if action == "list":
            if not hasattr(self.bot, 'voice_watch_enabled'):
                self.bot.voice_watch_enabled = set()
            
            watched = [self.bot.get_guild(gid).name for gid in self.bot.voice_watch_enabled if self.bot.get_guild(gid)]
            if watched:
                await self.bot.send_and_clean(message.channel, "voice watching: " + ", ".join(watched))
            else:
                await self.bot.send_and_clean(message.channel, "no voice watching")
            return

        try:
            guild_id = int(action)
            guild = self.bot.get_guild(guild_id)
            if not guild:
                await self.bot.send_and_clean(message.channel, "invalid guild id")
                return

            if not hasattr(self.bot, 'voice_watch_enabled'):
                self.bot.voice_watch_enabled = set()

            if guild_id in self.bot.voice_watch_enabled:
                self.bot.voice_watch_enabled.remove(guild_id)
                await self.bot.send_and_clean(message.channel, f"stopped voice watching {guild.name}")
            else:
                self.bot.voice_watch_enabled.add(guild_id)
                await self.bot.send_and_clean(message.channel, f"now voice watching {guild.name}")

        except ValueError:
            await self.bot.send_and_clean(message.channel, "invalid guild id")

    @owner_only()
    async def cmd_autoowod(self, message, command_args=""):
        parts = command_args.split()

        if not parts:
            if self.bot.autoowod_task and not self.bot.autoowod_task.done():
                await self.bot.send_and_clean(message.channel, f"autoowod running at {self.bot.autoowod_time} UTC")
            else:
                await self.bot.send_and_clean(message.channel, "autoowod not running")
            return

        action = parts[0].lower()

        if action == "start":
            if len(parts) < 3:
                await self.bot.send_and_clean(message.channel, "usage nux autoowod start <channel_id> <HH:MM> (UTC)")
                return

            try:
                channel_id = int(parts[1])
                channel = self.bot.get_channel(channel_id)
                if not channel or not isinstance(channel, discord.TextChannel):
                    await self.bot.send_and_clean(message.channel, "invalid channel id or not text channel")
                    return

                time_str = parts[2]
                hour, minute = map(int, time_str.split(':'))
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    raise ValueError

                self.bot.autoowod_time = time_str
                self.bot.autoowod_channel = channel
                if self.bot.autoowod_task and not self.bot.autoowod_task.done():
                    await self.bot.send_and_clean(message.channel, "autoowod already running")
                    return

                self.bot.autoowod_task = self.bot.loop.create_task(self._autoowod_worker())
                await self.bot.send_and_clean(message.channel, f"autoowod started in {channel} at {self.bot.autoowod_time} UTC")

            except ValueError:
                await self.bot.send_and_clean(message.channel, "invalid channel id or time format")

        elif action == "stop":
            if self.bot.autoowod_task:
                self.bot.autoowod_task.cancel()
                try:
                    await self.bot.autoowod_task
                except asyncio.CancelledError:
                    pass
                self.bot.autoowod_task = None
                self.bot.autoowod_time = None
                self.bot.autoowod_channel = None
                await self.bot.send_and_clean(message.channel, "autoowod stopped")
            else:
                await self.bot.send_and_clean(message.channel, "autoowod not running")

        else:
            await self.bot.send_and_clean(message.channel, "usage nux autoowod start/stop [channel_id] [time]")

    async def _autoowod_worker(self):
        while True:
            now = datetime.datetime.utcnow()
            hour, minute = map(int, self.bot.autoowod_time.split(':'))
            scheduled = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if scheduled <= now:
                scheduled += datetime.timedelta(days=1)
            wait_seconds = (scheduled - now).total_seconds()
            variation = self.bot.rand.uniform(-300, 300)
            wait_seconds += variation
            if wait_seconds < 0:
                wait_seconds = 900 
            await asyncio.sleep(wait_seconds)
            try:
                await self.bot.autoowod_channel.send("owo daily")
            except:
                pass

    async def cmd_autoreact(self, message, command_args=""):
        args = command_args.split()
        if not args:
            if not self.bot.autoreact_rules:
                await self.bot.send_and_clean(message.channel, "no autoreact rules set")
                return
            response = "autoreact rules:\n"
            for rule in self.bot.autoreact_rules:
                try:
                    emoji = self.bot.get_emoji(rule['emoji_id']) if 'emoji_id' in rule else rule['emoji']
                    channel = self.bot.get_channel(rule['channel_id'])
                    response += f"- {channel.name if channel else 'unknown'}: '{rule['keyword']}' -> {emoji}\n"
                except:
                    response += f"- unknown: '{rule['keyword']}' -> {rule.get('emoji', 'unknown')}\n"
            await self.bot.send_and_clean(message.channel, response.strip())
            return

        action = args[0].lower()

        if action == "remove":
            if len(args) < 3:
                await self.bot.send_and_clean(message.channel, "usage nux autoreact remove <channel_id> <keyword>")
                return
            try:
                channel_id = int(args[1])
                keyword = args[2].lower()
                new_rules = [r for r in self.bot.autoreact_rules if not (r['channel_id'] == channel_id and r['keyword'] == keyword)]
                if len(new_rules) == len(self.bot.autoreact_rules):
                    await self.bot.send_and_clean(message.channel, "no matching rule found")
                else:
                    self.bot.autoreact_rules = new_rules
                    self.bot.save_config()
                    await self.bot.send_and_clean(message.channel, f"removed autoreact rule for keyword '{keyword}' in channel {channel_id}")
            except ValueError:
                await self.bot.send_and_clean(message.channel, "invalid channel id")
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
                if not hasattr(self.bot, 'autoreact_rules') or self.bot.autoreact_rules is None:
                    self.bot.autoreact_rules = []
                self.bot.autoreact_rules.append(rule)
                self.bot.save_config()
                await self.bot.send_and_clean(message.channel, f"added autoreact rule: channel {channel_id}, keyword '{keyword}', emoji {emoji}")
            except ValueError:
                await self.bot.send_and_clean(message.channel, "invalid channel id")
        else:
            await self.bot.send_and_clean(message.channel, "usage nux autoreact [<channel_id> <keyword> <emoji> | remove <channel_id> <keyword>]")

    async def cmd_ai_memory(self, message, command_args=""):
        try:
            user_id = int(command_args)
            if user_id not in self.bot.conversations:
                await self.bot.send_and_clean(message.channel, "no conversation history with that user")
                return
            history = self.bot.conversations[user_id]
            if len(history) <= 1:
                await self.bot.send_and_clean(message.channel, "no conversation history with that user")
                return
            summary = f"conversation with {user_id}\n" + "\n".join([f"{msg['role']}: {(msg['content'][:50] + '...') if len(msg['content']) > 50 else msg['content']}" for msg in history[-10:] if msg['role'] != 'system'])
            await self.bot.send_and_clean(message.channel, summary)
        except ValueError:
            await self.bot.send_and_clean(message.channel, "invalid user id")

    async def cmd_learn(self, message, command_args="s"):
        args = command_args.split(" | ", 1)
        if len(args) != 2:
            await self.bot.send_and_clean(message.channel, "usage nux learn <input_phrase> | <output_response>")
            return
        phrase, response = args
        phrase = phrase.strip().lower()
        response = response.strip()
        
        if not hasattr(self.bot, 'ai_config'):
            self.bot.ai_config = {}
            
        if 'custom_responses' not in self.bot.ai_config:
            self.bot.ai_config['custom_responses'] = {}
        self.bot.ai_config['custom_responses'][phrase] = response
        with open('ai_config.pkl', 'wb') as f:
            pickle.dump(self.bot.ai_config, f)
        await self.bot.send_and_clean(message.channel, f"learned '{phrase}' -> '{response}'")

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
                await self.bot.send_and_clean(message.channel, f"```\n{chunk}```")
        except Exception as e:
            await self.bot.send_and_clean(message.channel, f"failed to load config: {e}")

    @owner_only()
    async def cmd_ghost(self, message, command_args=""):
        if not self.bot.ghost_mode:
            self.bot.saved_activity = getattr(self.bot.user, 'activity', None)
            self.bot.saved_status = getattr(self.bot.user, 'status', discord.Status.online)
            self.bot.saved_status_enabled = self.bot.status_enabled

            if self.bot.status_task:
                self.bot.status_task.cancel()
                self.bot.status_task = None
            self.bot.status_enabled = False 

            await self.bot.change_presence(activity=None, status=discord.Status.offline)
            self.bot.ghost_mode = True
            status_message = "active, profile is offline and messages delete after 15 seconds."
        else: 
            self.bot.ghost_mode = False
            self.bot.status_enabled = self.bot.saved_status_enabled 

            if self.bot.status_enabled:
                await self.bot.change_presence(activity=self.bot.saved_activity, status=self.bot.saved_status)
                if not self.bot.status_task or self.bot.status_task.done():
                    self.bot.status_task = self.bot.loop.create_task(self.change_status_periodically())
            else:
                await self.bot.change_presence(activity=None, status=discord.Status.online)

            status_message = "inactive, profile is online and messages will not delete."

        self.bot.save_config()
        await self.bot.send_and_clean(message.channel, status_message)

    @owner_only()
    async def cmd_statustoggle(self, message, command_args=""):
        if self.bot.status_enabled:
            if self.bot.status_task:
                self.bot.status_task.cancel()
                self.bot.status_task = None
            self.bot.status_enabled = False
            self.bot.save_config()
            await self.bot.change_presence(activity=None, status=discord.Status.online) 
            await self.bot.send_and_clean(message.channel, "status messages are now off")
        else:
            self.bot.status_task = self.bot.loop.create_task(self.change_status_periodically())
            self.bot.status_enabled = True
            self.bot.save_config()
            await self.bot.send_and_clean(message.channel, "status messages are now on")

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
            new_status = self.bot.rand.choice(status_messages)
            await self.bot.change_presence(activity=discord.CustomActivity(name=new_status), status=discord.Status.online)
            await asyncio.sleep(30)

    async def handle_voice_state_update(self, member, before, after):
        if member.id == self.bot.user.id:
            return

        if not hasattr(member, 'guild') or not member.guild:
            return

        if member.guild.id not in self.bot.voice_watch_enabled:
            return

        if before.channel is None and after.channel is not None:
            print(f"[Voice Watch] {member} joined {after.channel.name} in {member.guild.name}")

        elif before.channel is not None and after.channel is None:
            print(f"[Voice Watch] {member} left {before.channel.name} in {member.guild.name}")

        elif before.channel is not None and after.channel is not None and before.channel != after.channel:
            print(f"[Voice Watch] {member} moved from {before.channel.name} to {after.channel.name} in {member.guild.name}")

    async def on_member_join_handler(self, member):
        if member.guild.id in self.bot.tracked_joins:
            print(f"[Join Watch] {member} joined {member.guild.name}")
            if self.bot.join_webhook:
                pass

    async def cmd_habit(self, message, command_args):
        phrase = command_args.strip().lower()
        if not phrase:
            return await self.bot.send_and_clean(message.channel, "provide a phrase to analyze")
        
        hour_counts = collections.Counter()
        day_counts = collections.Counter()
        
        try:
            async for msg in message.channel.history(limit=5000):
                if SequenceMatcher(None, phrase, msg.content.lower()).ratio() > 0.6:
                    hour_counts[msg.created_at.hour] += 1
                    day_counts[msg.created_at.weekday()] += 1
            
            if not hour_counts:
                return await self.bot.send_and_clean(message.channel, "no matches found")
            
            img = Image.new('RGB', (600, 200), 'white')
            draw = ImageDraw.Draw(img)
            
            max_count = max(hour_counts.values()) if hour_counts else 1
            for hour, count in hour_counts.items():
                intensity = int(255 * (1 - count / max_count))
                color = (intensity, intensity, 255)
                draw.rectangle([hour * 25, 0, (hour + 1) * 25, 100], fill=color)
                draw.text((hour * 25 + 5, 110), str(hour), fill='black')
            
            output = io.BytesIO()
            img.save(output, format='PNG')
            output.seek(0)
            
            await self.bot.send_and_clean(message.channel, f"habit heatmap for '{phrase}':", file=discord.File(output, 'habit.png'))
        except Exception as e:
            await self.bot.send_and_clean(message.channel, f"error: {e}")

    async def cmd_antivocab(self, message, command_args):
        try:
            word_counts = collections.Counter()
            
            async for msg in message.channel.history(limit=5000):
                words = msg.content.lower().split()
                words = [w.strip('.,!?;:"()[]{}') for w in words if len(w) > 3]
                word_counts.update(words)
            
            if not word_counts:
                return await self.bot.send_and_clean(message.channel, "no words found")
            
            least_used = word_counts.most_common()[-20:]
            result = "least used words:\n" + "\n".join([f"{word}: {count}" for word, count in least_used])
            await self.bot.send_and_clean(message.channel, result)
        except Exception as e:
            await self.bot.send_and_clean(message.channel, f"error: {e}")

    async def cmd_timezone(self, message, command_args):
        if not message.mentions:
            return await self.bot.send_and_clean(message.channel, "mention a user")
        
        user = message.mentions[0]
        hour_activity = collections.Counter()
        
        try:
            async for msg in message.channel.history(limit=5000):
                if msg.author.id == user.id:
                    hour_activity[msg.created_at.hour] += 1
            
            if not hour_activity:
                return await self.bot.send_and_clean(message.channel, "no activity found for user")
            
            img = Image.new('RGB', (600, 200), 'white')
            draw = ImageDraw.Draw(img)
            
            max_count = max(hour_activity.values())
            for hour in range(24):
                count = hour_activity.get(hour, 0)
                intensity = int(255 * (1 - count / max_count)) if max_count else 255
                color = (intensity, 255, intensity)
                draw.rectangle([hour * 25, 0, (hour + 1) * 25, 100], fill=color)
                draw.text((hour * 25 + 5, 110), str(hour), fill='black')
            
            output = io.BytesIO()
            img.save(output, format='PNG')
            output.seek(0)
            
            await self.bot.send_and_clean(message.channel, f"activity peaks for {user.name}:", file=discord.File(output, 'timezone.png'))
        except Exception as e:
            await self.bot.send_and_clean(message.channel, f"error: {e}")

def setup(bot):
    util_cog = Utilities(bot)
    bot.handle_voice_state_update = util_cog.handle_voice_state_update
    bot.on_member_join_handler = util_cog.on_member_join_handler
    return util_cog, HELP_TEXT
