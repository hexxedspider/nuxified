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
        "nux ai memory <user_id>": "show ai conversation memory",
        "nux learn <phrase> | <response>": "teach the ai a custom response",
        "nux servericon": "get the server icon",
        "nux habit <phrase>": "message frequency heatmap for phrase",
        "nux antivocab": "identify least used words in chat",
        "nux timezone <@user>": "user activity peaks heatmap",
    }
}

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

    def _load_custom_commands(self):
        try:
            with open("custom_commands.json", "r") as f:
                return json.load(f)
        except:
            return {}

    def _save_custom_commands(self, commands):
        with open("custom_commands.json", "w") as f:
            json.dump(commands, f, indent=2)

    async def cmd_addcmd(self, message, command_args):
        if message.author.id != self.bot.owner_id:
            return await self.bot.send_and_clean(message.channel, "only owner can use this command")

        parts = command_args.split(maxsplit=1)
        if len(parts) < 2:
            return await self.bot.send_and_clean(message.channel, "usage: nux addcmd <name> <response>")
        
        name = parts[0].lower()
        response = parts[1]
        
        commands = self._load_custom_commands()
        commands[name] = response
        self._save_custom_commands(commands)
        
        await self.bot.send_and_clean(message.channel, f"added custom command '{name}'")

    async def cmd_delcmd(self, message, command_args):
        if message.author.id != self.bot.owner_id:
            return await self.bot.send_and_clean(message.channel, "only owner can use this command")

        name = command_args.strip().lower()
        if not name:
            return await self.bot.send_and_clean(message.channel, "usage: nux delcmd <name>")
        
        commands = self._load_custom_commands()
        if name not in commands:
            return await self.bot.send_and_clean(message.channel, f"command '{name}' not found")
        
        del commands[name]
        self._save_custom_commands(commands)
        await self.bot.send_and_clean(message.channel, f"deleted custom command '{name}'")

    async def cmd_listcmds(self, message, command_args=""):
        if message.author.id != self.bot.owner_id:
            return await self.bot.send_and_clean(message.channel, "only owner can use this command")

        commands = self._load_custom_commands()
        if not commands:
            return await self.bot.send_and_clean(message.channel, "no custom commands")
        
        cmd_list = "\n".join([f"- {name}: {response[:50]}{'...' if len(response) > 50 else ''}" for name, response in commands.items()])
        await self.bot.send_and_clean(message.channel, f"custom commands:\n{cmd_list}")

    async def handle_custom_command(self, message, cmd_name):
        commands = self._load_custom_commands()
        if cmd_name.lower() in commands:
            await self.bot.send_and_clean(message.channel, commands[cmd_name.lower()])
            return True
        return False

    def _load_affix_settings(self):
        try:
            with open("affix_settings.json", "r") as f:
                return json.load(f)
        except:
            return {"prefix": "", "suffix": "", "enabled": False}

    def _save_affix_settings(self, settings):
        with open("affix_settings.json", "w") as f:
            json.dump(settings, f, indent=2)

    async def handle_affix_message(self, message):
        settings = self._load_affix_settings()
        if not settings.get("enabled"):
            return False
        if not settings.get("prefix") and not settings.get("suffix"):
            return False
        if message.content.startswith("nux "):
            return False

        response_keywords = ["set to:", "enabled", "disabled", "cleared", "added", "deleted", "removed", "stopped", "started", "changed to", "nickname changed", "backup saved", "git pull", "left guild", "message sent", "finished", "burst deleted", "spamming", "stopped deleting", "started deletions", "prefix cleared", "suffix cleared", "affix enabled", "affix disabled"]
        if any(keyword in message.content.lower() for keyword in response_keywords):
            return False

        prefix = settings.get('prefix', '')
        if prefix and message.content.startswith(prefix):
            return False

        suffix = settings.get('suffix', '')
        if suffix and message.content.endswith(suffix):
            return False

        new_content = f"{prefix}{message.content}{suffix}"
        try:
            await message.delete()
            await message.channel.send(new_content)
            return True
        except:
            return False

def setup(bot):
    util_cog = Utilities(bot)
    return util_cog, HELP_TEXT
