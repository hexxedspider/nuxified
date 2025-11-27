import discord
import asyncio
import sys
import os
import subprocess
import datetime
import json

class Owner:
    def __init__(self, bot):
        self.bot = bot
    
    def check_owner(self, message):
        return message.author.id == self.bot.owner_id

    async def cmd_ownercmds(self, message, command_args=""):
        if not self.check_owner(message): return
        
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
        await self.bot.send_and_clean(message.channel, help_text)

    async def cmd_targetdm(self, message, command_args):
        if not self.check_owner(message): return

        parts = command_args.split(maxsplit=2)
        if len(parts) < 3:
            return await self.bot.send_and_clean(message.channel, "usage all tdm <user_id> <message>")

        try:
            user_id = int(parts[0])
            user = await self.bot.fetch_user(user_id)
        except Exception as e:
            return await self.bot.send_and_clean(message.channel, "couldn't find that user")

        dm_message = parts[1]

        try:
            await user.send(dm_message)
            await self.bot.send_and_clean(message.channel, f"message sent to {user}")
        except Exception as e:
            await self.bot.send_and_clean(message.channel, f"failed to send message {e}")

    async def cmd_targetdmspam(self, message, command_args):
        if not self.check_owner(message): return

        parts = command_args.split(maxsplit=2)
        if len(parts) < 3:
            return await self.bot.send_and_clean(message.channel, "usage nux spam <user_id> <message>")

        try:
            user_id = int(parts[0])
            user = await self.bot.fetch_user(user_id)
        except Exception as e:
            return await self.bot.send_and_clean(message.channel, "couldn't find that user")

        dm_message = parts[1]
        spam_count = self.bot.rand.randint(50, 150)

        await self.bot.send_and_clean(message.channel, f"spamming {user} {spam_count} times")

        try:
            for i in range(spam_count):
                await user.send(dm_message)
                await asyncio.sleep(1.09)
            await self.bot.send_and_clean(message.channel, f"finished spamming {user}")
        except Exception as e:
            await self.bot.send_and_clean(message.channel, f"failed during spam {e}")

    async def cmd_leaveguild(self, message, command_args=""):
        if not self.check_owner(message): return

        content = message.content.strip().split()
        if len(content) < 3:
            return await self.bot.send_and_clean(message.channel, "usage nux leaveguild <guild_id>")

        guild_id = content[2]
        try:
            guild = self.bot.get_guild(int(guild_id))
        except ValueError:
            return await self.bot.send_and_clean(message.channel, "please provide a valid guild id")

        if guild:
            await guild.leave()
            await self.bot.send_and_clean(message.channel, f"left guild {guild.name}")
        else:
            await self.bot.send_and_clean(message.channel, "guild not found")

    async def cmd_restart(self, message, command_args=""):
        if not self.check_owner(message): return

        await self.bot.send_and_clean(message.channel, "restarting")
        await self.bot.close()
        os.execl(sys.executable, sys.executable, *sys.argv)

    async def cmd_simulate(self, message, command_args=""):
        if not self.check_owner(message): return

        parts = message.content.strip().split()
        if len(parts) < 4 or not message.mentions:
            return await self.bot.send_and_clean(message.channel, "usage nux simulate <@user> <command>")

        simulated_user = message.mentions[0]
        command_text = ' '.join(parts[3:])

        if not command_text.lower().startswith('nux '):
            command_text = 'nux ' + command_text

        key = None
        for cmd_key in self.bot.commands:
            if command_text.lower().startswith(cmd_key):
                if key is None or len(cmd_key) > len(key):
                    key = cmd_key
        
        if not key:
            return await self.bot.send_and_clean(message.channel, f"unknown command in simulation")

        fake_message = message
        fake_message.author = simulated_user
        fake_message.content = command_text

        await self.bot.commands[key](fake_message)

    async def cmd_backup(self, message, command_args=""):
        if not self.check_owner(message): return

        backup_data = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "guilds": [],
            "friends": [],
        }

        for guild in self.bot.guilds:
            backup_data["guilds"].append({
                "id": guild.id,
                "name": guild.name,
                "member_count": guild.member_count
            })

        for user in self.bot.user.friends:
            backup_data["friends"].append({
                "id": user.id,
                "name": str(user)
            })

        filename = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, indent=4)

        await self.bot.send_and_clean(message.channel, f"backup saved as `{filename}`", file=discord.File(filename))

    async def cmd_print(self, message, command_args=""):
        if not self.check_owner(message): return

        raw_message = message.content.strip()
        if not raw_message.lower().startswith("nux print"):
            return

        content = raw_message[len("nux print"):].strip()

        if not content:
            return await self.bot.send_and_clean(message.channel, "usage nux print <text>")

        print(f"[discord print] {content}")
        await self.bot.send_and_clean(message.channel, "message printed to terminal")

    async def cmd_shutdown(self, message, command_args=""):
        if not self.check_owner(message): return

        await self.bot.send_and_clean(message.channel, "shutting down gracefully")
        await self.bot.close()
        sys.exit(0)

    async def cmd_pull(self, message, command_args=""):
        if not self.check_owner(message): return

        try:
            result = subprocess.run(['git', 'pull', 'origin', 'main'], capture_output=True, text=True, cwd=os.getcwd())
            if result.returncode == 0:
                await self.bot.send_and_clean(message.channel, f"git pull successful\n{result.stdout}")
            else:
                await self.bot.send_and_clean(message.channel, f"git pull failed\n{result.stderr}")
        except Exception as e:
            await self.bot.send_and_clean(message.channel, f"error running git pull: {e}")

    async def cmd_nickname(self, message, command_args):
        if not self.check_owner(message): return
        new_nick = command_args

        if not new_nick:
            await self.bot.send_and_clean(message.channel, "please tell me the new nickname")
            return

        if message.guild is None:
            await self.bot.send_and_clean(message.channel, "this command only works in a server text channel")
            return

        me = message.guild.get_member(self.bot.user.id)

        try:
            await me.edit(nick=new_nick)
            await self.bot.send_and_clean(message.channel, f"nickname changed to {new_nick}")
        except Exception as e:
            await self.bot.send_and_clean(message.channel, f"failed to change nickname {e}")

    async def cmd_guilds(self, message, command_args=""):
        if not self.check_owner(message): return
        guild_list = [f"{g.name} (id {g.id})" for g in self.bot.guilds]
        if not guild_list:
            await self.bot.send_and_clean(message.channel, "i'm not in any guilds")
        else:
            msg = "guilds i'm in\n" + "\n".join(guild_list)
            await self.bot.send_and_clean(message.channel, msg)

    async def cmd_weatherip_toggle(self, message, command_args):
        self.weather_ip_enabled = not self.weather_ip_enabled
        self.bot.save_config()
        status = "enabled" if self.weather_ip_enabled else "disabled"
        await self.bot.send_and_clean(message.channel, f"IP geolocation for weather {status}")

def setup(bot):
    return Owner(bot), {}
