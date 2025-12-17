import discord
import aiohttp
import asyncio
import sys
import os
import subprocess
import datetime
import json
import pickle

HELP_TEXT = { # NOT USED, ONLY SO COMMANDS ARE REGISTERED
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
        "nux imagedump": "dump all images in a channel to a zip file",
        "nux cdm": "starts deleting all messages sent by me in the current channel - run again to stop",
        "nux burstcdm": "deletes the last 5 messages sent by me in the current channel",
        "nux watch <guild_id|dm|list>": "watch a guild or dms",
        "nux trackjoins <guild_id|list>": "track joins in a guild",
        "nux setjoinwebhook <url>": "set webhook for join tracking",
        "nux voicewatch <guild_id|list>": "watch voice channels",
        "nux autoowod <start|stop>": "auto owo daily",
        "nux config": "show current config",
        "nux ghost": "toggle ghost mode",
        "nux statustoggle": "toggle status rotation",
        "nux webhook <set|assign|list|delete> ...": "manage webhooks for different features",
        "nux marketplace": "browse community extensions from the LLC marketplace",
        "nux marketplace info <id>": "get detailed info about a marketplace extension",
        "nux marketplace install <id>": "install a community extension",
        "nux marketplace submit": "get invite link to submit extensions",
        "nux autocorrect": "toggle auto-correct for mistyped commands",
        "nux todo <add|list|remove|clear>": "manage todo list",
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
            "- `nux ownercmds` show owner commands\n"
            "- `nux targetdm <user_id> <message>` dm a user\n"
            "- `nux targetdmspam <user_id> <message>` spam dm a user\n"
            "- `nux leaveguild <guild_id>` leave a guild\n"
            "- `nux restart` restart the bot\n"
            "- `nux simulate <@user> <command>` simulate a command as another user\n"
            "- `nux backup` backup friends and guilds\n"
            "- `nux pull` git pull latest changes\n"
            "- `nux nickname <nick>` change bot nickname\n"
            "- `nux guilds` list all guilds\n"
            "- `nux weatherip` toggle IP geolocation for weather\n"
            "- `nux addcmd <name> <response>` add a custom text command\n"
            "- `nux delcmd <name>` delete a custom command\n"
            "- `nux listcmds` list all custom commands\n"
            "- `nux prefix <text>` set message prefix (use 'clear' to remove)\n"
            "- `nux suffix <text>` set message suffix (use 'clear' to remove)\n"
            "- `nux affix` toggle prefix/suffix on messages\n"
            "- `nux dumpdm` dump all dms in the current channel to a file\n"
            "- `nux imagedump` dump all images in a channel to a zip file\n"
            "- `nux cdm` starts deleting all messages sent by me in the current channel - run again to stop\n"
            "- `nux burstcdm` deletes the last 5 messages sent by me in the current channel\n"
            "- `nux watch <guild_id|dm|list>` watch a guild or dms\n"
            "- `nux trackjoins <guild_id|list>` track joins in a guild\n"
            "- `nux setjoinwebhook <url>` set webhook for join tracking\n"
            "- `nux voicewatch <guild_id|list>` watch voice channels\n"
            "- `nux autoowod <start|stop>` auto owo daily\n"
            "- `nux config` show current config\n"
            "- `nux ghost` toggle ghost mode\n"
            "- `nux statustoggle` toggle status rotation\n"
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
            "- `nux weatherip` enables/disables ip geolocation for weather command, off by default to avoid accidental doxxing\n"
            "- `nux cdm` starts deleting all messages sent by me in the current channel - run again to stop\n"
            "- `nux burstcdm` deletes the last 5 messages sent by me in the current channel\n"
            "- `nux statustoggle` turn the status switcher on/off.\n-# Change what statuses are said in owner.py.\n"
            "- `nux webhook <set|assign|list|delete> ...`: manage webhooks for different features\n"
            "- `nux autocorrect` toggle auto-correct for mistyped commands\n"
            
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

        await self.bot.send_and_clean(message.channel, "restarting...")
        await self.bot.close()
        sys.exit(0)

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

        if text.startswith('"') and text.endswith('"') and len(text) > 1:
            text = text[1:-1]

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

    async def cmd_watch(self, message, command_args):
        if not self.check_owner(message): return

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

    async def cmd_trackjoins(self, message, command_args):
        if not self.check_owner(message): return

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

    async def cmd_setjoinwebhook(self, message, command_args=""):
        if not self.check_owner(message): return

        if not command_args or command_args.lower() in ["status", "stat"]:
            if "join" not in self.bot.webhook_assignments or self.bot.webhook_assignments["join"] not in self.bot.webhooks:
                await self.bot.send_and_clean(message.channel, "no join webhook set")
                return
            embed = {
                "title": "webhook test",
                "description": "this is a test message for the join webhook",
                "color": 0x00ff00
            }
            payload = {
                "username": "nux worker test",
                "avatar_url": self.bot.user.avatar.url if self.bot.user.avatar else None,
                "embeds": [embed]
            }
            await self.bot.send_to_webhook("join", payload)
            await self.bot.send_and_clean(message.channel, "join webhook test sent")
        else:
            webhook_url = command_args.strip()
            if not webhook_url:
                await self.bot.send_and_clean(message.channel, "provide a webhook url")
                return
            if not (webhook_url.startswith("https://") and "/api/webhooks/" in webhook_url):
                await self.bot.send_and_clean(message.channel, "provide a valid discord webhook url")
                return
            self.bot.webhooks["join"] = webhook_url
            self.bot.webhook_assignments["join"] = "join"
            self.bot.save_config()
            await self.bot.send_and_clean(message.channel, "join notification webhook set")

    async def cmd_voicewatch(self, message, command_args=""):
        if not self.check_owner(message): return

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

    async def cmd_autoowod(self, message, command_args=""):
        if not self.check_owner(message): return

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

    async def cmd_config(self, message, command_args=""):
        if not self.check_owner(message): return

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

    async def cmd_ghost(self, message, command_args=""):
        if not self.check_owner(message): return

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

    async def cmd_statustoggle(self, message, command_args=""):
        if not self.check_owner(message): return

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

    async def cmd_webhook(self, message, command_args):
        if not self.check_owner(message): return

        parts = command_args.split()

        if not parts or parts[0].lower() == "help":
            help_msg = (
                "Webhook management commands:\n"
                "`nux webhook set <name> <url>` - Set a named webhook URL\n"
                "`nux webhook assign <feature> <name>` - Assign a webhook to a feature\n"
                "`nux webhook list` - Show all webhooks and assignments\n"
                "`nux webhook delete <name>` - Remove a webhook\n"
                "`nux webhook help` - Show this help\n\n"
                "Features: dm (DM messages), load (bot startup), join (member joins)\n"
                "Example: `nux webhook set myhook https://discord.com/api/webhooks/...` then `nux webhook assign dm myhook`"
            )
            await self.bot.send_and_clean(message.channel, help_msg)
            return

        subcmd = parts[0].lower()

        if subcmd == "set":
            if len(parts) < 3:
                await self.bot.send_and_clean(message.channel, "usage: nux webhook set <name> <url>")
                return

            name = parts[1]
            url = ' '.join(parts[2:])

            if not url.startswith("https://"):
                await self.bot.send_and_clean(message.channel, "url must start with https://")
                return
            if "/api/webhooks/" not in url:
                await self.bot.send_and_clean(message.channel, "url must be a valid webhook url containing /api/webhooks/")
                return

            self.bot.webhooks[name] = url
            self.bot.save_config()
            await self.bot.send_and_clean(message.channel, f"webhook '{name}' set")

        elif subcmd == "assign":
            if len(parts) < 3:
                await self.bot.send_and_clean(message.channel, "usage: nux webhook assign <feature> <name>")
                return

            feature = parts[1]
            name = parts[2]

            if name not in self.bot.webhooks:
                await self.bot.send_and_clean(message.channel, f"webhook '{name}' not found")
                return

            self.bot.webhook_assignments[feature] = name
            self.bot.save_config()
            await self.bot.send_and_clean(message.channel, f"assigned webhook '{name}' to feature '{feature}'")

        elif subcmd == "list":
            webhooks = "\n".join([f"{name}: {url}" for name, url in self.bot.webhooks.items()]) if self.bot.webhooks else "No webhooks set"
            assignments = "\n".join([f"{feat}: {name}" for feat, name in self.bot.webhook_assignments.items()]) if self.bot.webhook_assignments else "No assignments"

            msg = f"**Webhooks:**\n{webhooks}\n\n**Assignments:**\n{assignments}"
            await self.bot.send_and_clean(message.channel, msg)

        elif subcmd == "delete":
            if len(parts) < 2:
                await self.bot.send_and_clean(message.channel, "usage: nux webhook delete <name>")
                return

            name = parts[1]

            if name in self.bot.webhooks:
                del self.bot.webhooks[name]
                self.bot.webhook_assignments = {k:v for k,v in self.bot.webhook_assignments.items() if v != name}
                self.bot.save_config()
                await self.bot.send_and_clean(message.channel, f"deleted webhook '{name}'")
            else:
                await self.bot.send_and_clean(message.channel, f"webhook '{name}' not found")

        else:
            await self.bot.send_and_clean(message.channel, f"unknown subcommand '{subcmd}'. Use `nux webhook help` for usage.")

    async def cmd_marketplace(self, message, command_args=""):
        """Browse available community extensions from the LLC marketplace"""
        if not self.check_owner(message): return

        await self.bot.send_and_clean(message.channel,
            "**WARNING**: These are community-made extensions. I cannot 100% guarantee their safety or functionality. Use at your own risk!\n\n"
            "Loading marketplace..."
        )

        try:
            server_id = 1371333297669537893
            channel_id = 1443400773353472060

            server = self.bot.get_guild(server_id)
            if not server:
                return await self.bot.send_and_clean(message.channel, "Unable to access marketplace server")

            channel = server.get_channel(channel_id)
            if not channel:
                return await self.bot.send_and_clean(message.channel, "Marketplace channel not found")

            extensions = []
            async for msg in channel.history(limit=100):
                if msg.embeds:
                    embed = msg.embeds[0]
                    if embed.title and embed.description:
                        extension_id = None
                        github_url = None

                        title_lower = embed.title.lower()
                        desc_lower = embed.description.lower()

                        import re
                        id_match = re.search(r'\b([a-zA-Z0-9]{8})\b', title_lower + ' ' + desc_lower)
                        if id_match:
                            extension_id = id_match.group(1).upper()

                        if embed.fields:
                            for field in embed.fields:
                                if 'github' in field.name.lower() or 'download' in field.name.lower():
                                    github_match = re.search(r'https://github\.com/[^\s]+', field.value)
                                    if github_match:
                                        github_url = github_match.group(0)
                                        break

                        github_match = re.search(r'https://github\.com/[^\s]+', embed.description)
                        if github_match:
                            github_url = github_match.group(0)

                        if extension_id and github_url:
                            extensions.append({
                                'id': extension_id,
                                'title': embed.title,
                                'description': embed.description[:200] + '...' if len(embed.description) > 200 else embed.description,
                                'github_url': github_url,
                                'message_url': msg.jump_url
                            })

            if not extensions:
                return await self.bot.send_and_clean(message.channel, "No extensions found in marketplace")

            response = "**Community Marketplace Extensions**\n\n"
            for ext in extensions[:10]:
                response += f"**{ext['id']}** - {ext['title']}\n{ext['description']}\n\n"

            if len(extensions) > 10:
                response += f"... and {len(extensions) - 10} more\n\n"

            response += "Use `nux marketplace info <ID>` for details or `nux marketplace install <ID>` to install"

            await self.bot.send_and_clean(message.channel, response)

        except Exception as e:
            await self.bot.send_and_clean(message.channel, f"Error loading marketplace: {e}")

    async def cmd_marketplace_info(self, message, command_args):
        """Get detailed info about a marketplace extension"""
        if not self.check_owner(message): return

        if not command_args:
            return await self.bot.send_and_clean(message.channel, "Usage: nux marketplace info <extension_id>")

        extension_id = command_args.strip().upper()

        try:
            server_id = 1371333297669537893
            channel_id = 1443400773353472060

            server = self.bot.get_guild(server_id)
            if not server:
                return await self.bot.send_and_clean(message.channel, "Unable to access marketplace server")

            channel = server.get_channel(channel_id)
            if not channel:
                return await self.bot.send_and_clean(message.channel, "Marketplace channel not found")

            async for msg in channel.history(limit=100):
                if msg.embeds:
                    embed = msg.embeds[0]
                    if embed.title and embed.description:
                        content = (embed.title + ' ' + embed.description).lower()
                        if extension_id.lower() in content:
                            github_url = None
                            import re
                            github_match = re.search(r'https://github\.com/[^\s]+', embed.description)
                            if github_match:
                                github_url = github_match.group(0)

                            response = f"**Extension: {embed.title}**\n\n"
                            response += f"**ID:** {extension_id}\n"
                            response += f"**Description:**\n{embed.description}\n\n"
                            if github_url:
                                response += f"**GitHub:** {github_url}\n"
                            response += f"**Message:** {msg.jump_url}\n\n"
                            response += "**Safety Warning**: This is community code. Review it before installing!"

                            await self.bot.send_and_clean(message.channel, response)
                            return

            await self.bot.send_and_clean(message.channel, f"Extension '{extension_id}' not found")

        except Exception as e:
            await self.bot.send_and_clean(message.channel, f"Error getting extension info: {e}")

    async def cmd_marketplace_install(self, message, command_args):
        """Install a community extension with confirmation"""
        if not self.check_owner(message): return

        if not command_args:
            return await self.bot.send_and_clean(message.channel, "Usage: nux marketplace install <extension_id>")

        extension_id = command_args.strip().upper()

        confirm_msg = await self.bot.send_and_clean(message.channel,
            f"**INSTALLATION CONFIRMATION**\n\n"
            f"You are about to install extension '{extension_id}' from the community marketplace.\n\n"
            "**WARNINGS:**\n"
            "• This code comes from unverified community members\n"
            "• It may contain malicious code or bugs\n"
            "• It could compromise your bot or data\n"
            "• The creator cannot provide support or guarantees\n\n"
            f"React with ✅ to proceed or ❌ to cancel"
        )

        await confirm_msg.add_reaction("✅")
        await confirm_msg.add_reaction("❌")

        def check(reaction, user):
            return user == message.author and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == confirm_msg.id

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)

            if str(reaction.emoji) == "❌":
                await self.bot.send_and_clean(message.channel, "Installation cancelled")
                return

        except asyncio.TimeoutError:
            await self.bot.send_and_clean(message.channel, "Installation timed out")
            return

        await self.bot.send_and_clean(message.channel, "Installing extension...")

        try:
            server_id = 1371333297669537893
            channel_id = 1443400773353472060

            server = self.bot.get_guild(server_id)
            if not server:
                return await self.bot.send_and_clean(message.channel, "Unable to access marketplace server")

            channel = server.get_channel(channel_id)
            if not channel:
                return await self.bot.send_and_clean(message.channel, "Marketplace channel not found")

            extension_data = None
            async for msg in channel.history(limit=100):
                if msg.embeds:
                    embed = msg.embeds[0]
                    if embed.title and embed.description:
                        content = (embed.title + ' ' + embed.description).lower()
                        if extension_id.lower() in content:
                            import re
                            github_match = re.search(r'https://github\.com/[^\s]+', embed.description)
                            if github_match:
                                extension_data = {
                                    'title': embed.title,
                                    'github_url': github_match.group(0)
                                }
                            break

            if not extension_data:
                return await self.bot.send_and_clean(message.channel, f"Extension '{extension_id}' not found")

            github_url = extension_data['github_url']
            repo_name = github_url.split('/')[-1]
            await self.bot.send_and_clean(message.channel,
                f"Extension '{extension_data['title']}' found!\n"
                f"GitHub: {github_url}\n\n"
                "**Note**: Full GitHub repo installation not yet implemented.\n"
                "Please download manually from the GitHub link above and place in the `extensions/` folder.\n\n"
                "The extension will be loaded automatically on next restart."
            )

        except Exception as e:
            await self.bot.send_and_clean(message.channel, f"Installation failed: {e}")

    async def cmd_marketplace_submit(self, message, command_args=""):
        """Get invite link for marketplace submissions"""
        if not self.check_owner(message): return

        invite_link = "https://discord.gg/DH2KHqS2hq"
        await self.bot.send_and_clean(message.channel,
            f"**Submit Community Extensions**\n\n"
            f"Want to share your nuxified extensions with the community?\n\n"
            f"**Submission Guidelines:**\n"
            f"- Create a GitHub repository with your extension\n"
            f"- Follow the template in `extensions/__init__.py`\n"
            f"- Test thoroughly before submitting\n\n"
            f"**Submit Here:** {invite_link}\n\n"
            f"Join the LLC server and post in the marketplace channel with:\n"
            f"- Extension title\n"
            f"- Short description\n"
            f"- GitHub repository link"
        )

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

    async def cmd_autocorrect(self, message, command_args=""):
        if not self.check_owner(message): return
        self.bot.auto_correct_enabled = not self.bot.auto_correct_enabled
        self.bot.save_config()
        status = "enabled" if self.bot.auto_correct_enabled else "disabled"
        await self.bot.send_and_clean(message.channel, f"auto-correct {status}")

    async def on_member_join_handler(self, member):
        if member.guild.id in self.bot.tracked_joins:
            print(f"[Join Watch] {member} joined {member.guild.name}")
            embed = {
                "title": f"Member Joined",
                "description": f"{member} joined {member.guild.name}",
                "color": 0x00ff00,
                "timestamp": member.joined_at.isoformat() if member.joined_at else None,
                "thumbnail": {"url": member.avatar.url if member.avatar else None}
            }
            payload = {
                "username": "Join Watcher",
                "avatar_url": self.bot.user.avatar.url if self.bot.user.avatar else None,
                "embeds": [embed]
            }
            await self.bot.send_to_webhook("join", payload)

def setup(bot):
    owner_cog = Owner(bot)
    bot.handle_voice_state_update = owner_cog.handle_voice_state_update
    bot.on_member_join_handler = owner_cog.on_member_join_handler
    return owner_cog, HELP_TEXT
