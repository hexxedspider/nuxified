import discord
import asyncio
import sys
import os
import subprocess
import datetime
import json

HELP_TEXT = {
    "owner": {
        "nux ownercmds": "show owner commands",
        "nux targetdm <user_id> <message>": "dm a user",
        "nux targetdmspam <user_id> <message>": "spam dm a user",
        "nux leaveguild <guild_id>": "leave a guild",
        "nux restart": "restart the bot",
        "nux simulate <@user> <command>": "simulate a command as another user",
        "nux backup": "backup friends and guilds",
        "nux pull": "git pull latest changes",
        "nux nickname <nick>": "change bot nickname",
        "nux guilds": "list all guilds",
        "nux weatherip": "toggle IP geolocation for weather",
        "nux addcmd <name> <response>": "add a custom text command",
        "nux delcmd <name>": "delete a custom command",
        "nux listcmds": "list all custom commands",
        "nux prefix <text>": "set message prefix (use 'clear' to remove)",
        "nux suffix <text>": "set message suffix (use 'clear' to remove)",
        "nux affix": "toggle prefix/suffix on messages",
        "nux dumpdm": "dump all dms in the current channel to a file",
        "nux imagedump": "dump all images in a channel to a zip file"
    }
}

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
            "- `nux weatherip` enables/disables ip geolocation for weather command, off by default to avoid accidental doxxing"
            "- `nux cdm` starts deleting all messages sent by me in the current channel - run again to stop"
            "- `nux burstcdm` deletes the last 5 messages sent by me in the current channel"
        )
        await self.bot.send_and_clean(message.channel, help_text)

    async def cmd_targetdm(self, message, command_args):
        if not self.check_owner(message): return

        parts = command_args.split(maxsplit=1)
        if len(parts) < 2:
            return await self.bot.send_and_clean(message.channel, "usage: nux targetdm <user_id> <message>")

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

    async def cmd_weatherip(self, message, command_args):
        if not self.check_owner(message): return
        self.bot.weather_ip_enabled = not getattr(self.bot, 'weather_ip_enabled', False)
        self.bot.save_config()
        status = "enabled" if self.bot.weather_ip_enabled else "disabled"
        await self.bot.send_and_clean(message.channel, f"IP geolocation for weather {status}")

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

    async def cmd_prefix(self, message, command_args):
        text = command_args.strip()
        if not text:
            return await self.bot.send_and_clean(message.channel, "usage: nux prefix <text> (use 'clear' to remove)")
        
        settings = self._load_affix_settings()
        if text.lower() == "clear":
            settings["prefix"] = ""
            await self.bot.send_and_clean(message.channel, "prefix cleared")
        else:
            settings["prefix"] = text
            await self.bot.send_and_clean(message.channel, f"prefix set to: {text}")
        self._save_affix_settings(settings)

    async def cmd_suffix(self, message, command_args):
        text = command_args.strip()
        if not text:
            return await self.bot.send_and_clean(message.channel, "usage: nux suffix <text> (use 'clear' to remove)")
        
        settings = self._load_affix_settings()
        if text.lower() == "clear":
            settings["suffix"] = ""
            await self.bot.send_and_clean(message.channel, "suffix cleared")
        else:
            settings["suffix"] = text
            await self.bot.send_and_clean(message.channel, f"suffix set to: {text}")
        self._save_affix_settings(settings)

    async def cmd_affix(self, message, command_args=""):
        settings = self._load_affix_settings()
        settings["enabled"] = not settings["enabled"]
        self._save_affix_settings(settings)
        
        status = "enabled" if settings["enabled"] else "disabled"
        prefix_info = f"prefix: '{settings['prefix']}'" if settings['prefix'] else "no prefix"
        suffix_info = f"suffix: '{settings['suffix']}'" if settings['suffix'] else "no suffix"
        await self.bot.send_and_clean(message.channel, f"affix {status} ({prefix_info}, {suffix_info})")

    async def handle_affix_message(self, message):
        settings = self._load_affix_settings()
        if not settings.get("enabled"):
            return False
        if not settings.get("prefix") and not settings.get("suffix"):
            return False
        if message.content.startswith("nux "):
            return False
        
        new_content = f"{settings.get('prefix', '')}{message.content}{settings.get('suffix', '')}"
        try:
            await message.delete()
            await message.channel.send(new_content)
            return True
        except:
            return False

    async def cmd_imagedump(self, message, command_args=""):
        import zipfile
        import shutil
        
        dump_dir = "image_dump_temp"
        if os.path.exists(dump_dir):
            shutil.rmtree(dump_dir)
        os.makedirs(dump_dir)
        
        await self.bot.send_and_clean(message.channel, "starting image dump, this may take a while...")
        
        count = 0
        async with message.channel.typing():
            async for msg in message.channel.history(limit=2500):
                for attachment in msg.attachments:
                    if any(attachment.filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.webm', '.mov']):
                        try:
                            filepath = os.path.join(dump_dir, f"{msg.id}_{attachment.filename}")
                            await attachment.save(filepath)
                            count += 1
                        except:
                            pass
                
                for embed in msg.embeds:
                    if embed.image and embed.image.url:
                        try:
                            async with aiohttp.ClientSession() as session:
                                async with session.get(embed.image.url) as resp:
                                    if resp.status == 200:
                                        ext = embed.image.url.split('.')[-1].split('?')[0][:4]
                                        filepath = os.path.join(dump_dir, f"{msg.id}_embed.{ext}")
                                        with open(filepath, 'wb') as f:
                                            f.write(await resp.read())
                                        count += 1
                        except:
                            pass
        
        if count == 0:
            shutil.rmtree(dump_dir)
            return await self.bot.send_and_clean(message.channel, "no images found")
        
        zip_path = "image_dump.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(dump_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, file)
        
        shutil.rmtree(dump_dir)
        
        try:
            file_size = os.path.getsize(zip_path)
            if file_size > 8 * 1024 * 1024:
                await self.bot.send_and_clean(message.channel, f"dumped {count} images but zip is too large to send ({file_size // (1024*1024)}MB). saved to {os.path.abspath(zip_path)}")
            else:
                await self.bot.send_and_clean(message.channel, f"dumped {count} images", file=discord.File(zip_path))
                os.remove(zip_path)
        except Exception as e:
            await self.bot.send_and_clean(message.channel, f"error: {e}")

    async def cmd_cdm(self, message, command_args=""):
        channel = message.channel
        channel_id = channel.id

        if not hasattr(self.bot, 'cdm_tasks'):
            self.bot.cdm_tasks = {}

        existing = self.bot.cdm_tasks.get(channel_id)

        if existing and not existing.done():
            existing.cancel()
            try:
                await existing
            except asyncio.CancelledError:
                pass
            self.bot.cdm_tasks.pop(channel_id, None)
            await self.bot.send_and_clean(channel, "stopped deleting")
            return

        task = asyncio.create_task(self._cdm_worker(channel))
        self.bot.cdm_tasks[channel_id] = task
        await self.bot.send_and_clean(channel, "started deletions - run `nux cdm` again to stop")

    async def _cdm_worker(self, channel):
        deleted_count = 0
        channel_id = channel.id
        try:
            while True:
                found = False
                async for msg in channel.history(limit=250):
                    if channel_id not in self.bot.cdm_tasks or self.bot.cdm_tasks.get(channel_id) is None:
                        raise asyncio.CancelledError()
                    if msg.author.id == self.bot.user.id:
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
                self.bot.cdm_tasks.pop(channel_id, None)
            except Exception:
                pass

        try:
            await self.bot.send_and_clean(channel, f"cdm finished, deleted {deleted_count} messages")
        except Exception:
            pass

    async def cmd_burstcdm(self, message, command_args=""):
        channel = message.channel
        deleted = 0
        async for msg in channel.history(limit=100):
            if msg.author.id == self.bot.user.id:
                try:
                    await msg.delete()
                    deleted += 1
                    if deleted >= 5:
                        break
                    await asyncio.sleep(0.1)
                except:
                    pass
        if deleted > 0:
            await self.bot.send_and_clean(channel, f"burst deleted {deleted} messages")

    async def cmd_dumpdm(self, message, command_args):
        messages = []
        async with message.channel.typing():
            await asyncio.sleep(7.836)
            async for msg in message.channel.history(limit=2500, oldest_first=True):
                timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M")
                author = "you" if msg.author == self.bot.user else msg.author.name
                messages.append(f"[{timestamp}] {author} {msg.content}")

        filepath = "dm_dump.txt"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(messages))

        file = discord.File(filepath)
        await self.bot.send_and_clean(message.channel, "your archive is ready", file=file)
        
        try:
            os.remove(filepath)
        except:
            pass

def setup(bot):
    return Owner(bot), HELP_TEXT
