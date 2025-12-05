import discord
import aiohttp
import asyncio
import requests
import xml.etree.ElementTree as ET
import os
import dotenv
from redgifs import API as RedGifsAPI

dotenv.load_dotenv()

nsfw_categories = {
    "ass": ["Ass", "SexyAss", "pawgtastic", "bigasses", "assgirls", "BigAss", "booty_queens", "hugeasses", "AssPillow", "OiledAss"],
    
    "boobs": ["Boobs", "Stacked", "BustyPetite", "YummyBoobs", "BigBoobsGW", "Boobies", "KnockoutBoobs", "BoobsAndTities", "TittyDrop", "EbonyBoobs", "BigBoobsSEX", "Titties", "PerfectTits", "massivetits", "boobbounce"],
    
    "hentai": ["hentai", "HENTAI_GIF", "animebooty", "Hentai_AnimeNSFW", "CuddlesAndHentai", "Hentai__videos", "CumHentai", "thick_hentai", "HypnoHentai", "HentaiCumsluts", "Tomboy_Hentai", "NSFWskyrim", "hentai_irl", "defeatedhentai", "short_hentai", "drunk_hentai", "incesthentailegal", "hentailimitless", "xrayhentai", "helplesshentai", "hentaibreeding", "stealthhentai", "forcedbreedinghentai", "freeusehentai", "hentai_animensfw", "thick_hentai", "masturbationhentai"],
    
    "milf": ["milf", "MILFs", "MilfPawg", "maturemilf", "youngerMILFS", "MommyMaterial", "MommyHeaven", "Mommy_tits", "JustMommy", "mommy_capts", "AnimeMILFS", "MommyMilfs"],
    
    "thighs": ["Thighs", "thickthighs", "thigh", "ThighFucking", "Thigh_Gap", "ThiccThighsSaveLives", "thighhighs", "thighdeology", "thighzone", "thighsupemacy", "thighjob_NSFW", "Thighjobhentai", "thighhighhentai"],
    
    "goth": ["BigEmoTitties", "GothPussy", "GothWhoress", "gothsluts", "goth_girls", "bigtiddygothgf", "GothChicks", "GothBlowjobs", "gothgirlsgw", "EmoGirlsFuck", "goth_babes", "BIGTITTYGOTHGF", "Hentai_Goth", "GothGirlsGlazed", "GothGoddess", "GothFuckdolls", "BigBootyGoTHICCgf", "GothGirlMommy", "altgonewild"],
    
    "bwomen": ["Ebony", "BlackGirlsCentral", "BlackHentai", "BlackPornMatters", "HotBlackChicks", "BlackTitties", "BlackGirlsKissing", "BlackGirlPics", "blackchickswhitedicks", "BlackChicksWorld", "blackchicks4whitedick", "BlackChicksPorn", "BrownChicksWhiteDicks"],
    
    "rreverse": ["FMRP", "ReverseGangBangz", "HentaiReverseRape2", "ReverseFreeUse"],
    
    "femdom": ["Femdom", "FemdomFetish", "SensualFemdom", "gentlefemdom", "femdomraw", "FemdomCreampie", "femdomhentai", "femdom_gifs", "FemdomAsians", "hentaifemdom", "dommes", "FemdomWithoutPegging", "femdomcaptions"],
    
    "asian": ["asiangirls4whitecocks", "asiangirlsforwhitemen", "asiangirlsforwhitemen", "AsianPorn", "AsianTitFucking", "AsianCumsluts", "AsianNSFW", "AlternativeAsians", "UncensoredAsian", "juicyasians", "asiangirlswhitecocks", "paag", "AsianInvasion", "AsianCumDumpsters", "AsianIncestPorn", "bustyasians"],
    
    "titfuck": ["titfuck", "titfuckblowjob", "titfuckheaven", "titfuckdicksuck", "tittyfuckclips", "differenttittyfuck", "cumcoveredtitfucking", "titfucknation", "frontaltitfuck", "tittyfucking", "cummingbetweentits", "asiantitfucking", "tittyfuck"],

    "thick": ["thickwhitegirls", "thickntall", "thickhips", "thickandcurves", "thick", "thickassandfatcock", "thickassamatures", "break_yo_dick_thick", "thickandebony", "thickmom", "slimthick", "thethiccness", "thickwoes", "thickerr", "thick_nerd", "thickwifegonewild", "thickchicksgw", "thickgothgirls", "thickchixx", "thickncurvy"],
}

nsfwhelp_msg = {
    "nsfw": {
        "nux nsfwhelp": "show nsfw commands",
        "nux hentai": "drawn nsfw",
        "nux thighs": "the best thing to ever exist",
        "nux ass": "the 1stnd best thing to ever exist",
        "nux boobs": "what do you think",
        "nux pussy": "do i need to explain",
        "nux pgif": "porn gif, pgif, yk?",
        "nux neko": "cat-girl related",
        "nux nsfw": "get nsfw images from reddit categories, usage: nux nsfw <category> [number]",
        "nux nsfwlist": "show available nsfw categories",
        "nux redgif": "search redgif for nsfw gifs, usage: nux redgif <search> <number>",
        #"nux rule34": "search rule34.xxx for nsfw images, usage: nux rule34 <search> <number>",
        "nux thighcalc": "estimate squeeze pressure based on bmi inputs, usage: nux thighcalc <height_cm> <weight_kg>",
        "nux jigphy": "estimate jiggle physics based on waist-to-hip ratio, usage: nux jigphy <waist_cm> <hip_cm>",
        "nux slowburn": "ai-generated slow burn story (requires openrouter), usage: nux slowburn <prompt>",
        "nux pickup": "generate AI pickup lines, usage: nux pickup [theme]",
        "nux lewdify <prompt>": "generate NSFW version of prompt using AI",
        "nux nsfwmix": "get random nsfw images from multiple categories, usage: nux nsfwmix <category1> <category2> [number]",
        "nux nsfwrandom": "get completely random nsfw content from any category, usage: nux nsfwrandom [number]",
        "nux nsfwsearch": "search across all nsfw subreddits for specific content, usage: nux nsfwsearch <query> [number]",
        "nux nsfwblacklist": "blacklist specific nsfw categories, usage: nux nsfwblacklist <category1> <category2> ...",
        "nux ngif": "get a random gif from any category, usage: nux ngif [number]",
        "nux nneko": "get a random lewd from any category, usage: nux nneko [number] (yes this is different from `nux neko` lol)",
        "nux nfoxgirl": "get a random lewd from any category, usage: nux nfoxgirl [number]",
        "nux kanal": "get a random lewd from any category, usage: nux kanal [number]",
        "nux kgonewild": "get a random lewd from any category, usage: nux kgonewild [number]",
        "nux khanal": "get a random lewd from any category, usage: nux khanal [number]",
        "nux khass": "get a random lewd from any category, usage: nux khass [number]",
        "nux khkitsune": "get a random lewd from any category, usage: nux khkitsune [number]",
        "nux khmidriff": "get a random lewd from any category, usage: nux khmidriff [number]",
        "nux khneko": "get a random lewd from any category, usage: nux khneko [number]",
        "nux kpaizuri": "get a random lewd from any category, usage: nux kpaizuri [number]",
        "nux ktentacle": "get a random lewd from any category, usage: nux ktentacle [number]",
        "nux kyaoi": "get a random lewd from any category, usage: nux kyaoi [number]",
    }
}

class NSFW:
    def __init__(self, bot):
        self.bot = bot
    
    def build_nsfwhelp_message(self):
        help_message = "nsfw commands\n\n"
        for cmd, desc in nsfwhelp_msg["nsfw"].items():
            help_message += f"- `{cmd}` {desc}\n"
        return help_message

    async def cmd_nsfwhelp(self, message, command_args=""):
        nsfwhelp_msg = self.build_nsfwhelp_message()
        chunks = self.bot.split_message(nsfwhelp_msg) if hasattr(self.bot, 'split_message') else [nsfwhelp_msg]

        async def delete_after(msg, delay):
            await asyncio.sleep(delay)
            try:
                await msg.delete()
            except:
                pass

        for chunk in chunks:
            msg = await message.channel.send(chunk)
            asyncio.create_task(delete_after(msg, 15))

    async def cmd_nsfwlist(self, message, command_args=""):
        categories = ", ".join(nsfw_categories.keys())
        await self.bot.send_and_clean(message.channel, f"available categories: {categories}")

    async def cmd_nsfw(self, message, command_args=""):
        args = message.content.strip().split()

        if len(args) < 3:
            return await self.bot.send_and_clean(message.channel, "usage nux nsfw <category> [number] [sort: hot/new/top]\nunsure of the categories use nux nsfwlist")

        category = args[2].strip('<>').lower()

        if category not in nsfw_categories:
            return await self.bot.send_and_clean(message.channel, "invalid category use 'nux nsfwlist' to see available categories")

        num_requested = 1
        sort_type = "hot"
        
        if len(args) >= 4:
            try:
                num_requested = int(args[3])
                if num_requested <= 0: num_requested = 1
            except ValueError:
                if args[3].lower() in ["hot", "new", "top"]:
                    sort_type = args[3].lower()
                else:
                    num_requested = 1
            
            if len(args) >= 5 and args[4].lower() in ["hot", "new", "top"]:
                sort_type = args[4].lower()

        if isinstance(message.channel, discord.DMChannel):
            pass
        elif hasattr(message.channel, "is_nsfw") and not message.channel.is_nsfw():
            return await self.bot.send_and_clean(message.channel, "this command can only be used in nsfw channels or direct messages")

        channel_id = message.channel.id
        if channel_id not in self.bot.sent_media:
            self.bot.sent_media[channel_id] = set()

        available_subreddits = nsfw_categories[category][:]
        collected_media = []
        tried_subreddits = set()
        
        async def fetch_posts(subreddit, sort):
            url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit=100"
            headers = {"user-agent": "mozilla/5.0"}
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return data.get("data", {}).get("children", [])
            except:
                pass
            return []

        def is_valid_media(post_data):
            url = post_data.get("url", "")
            if post_data.get("stickied", False): return False
            if "redgifs" in url.lower(): return False
            
            hint = post_data.get("post_hint", "")
            domain = post_data.get("domain", "")
            
            is_video = (
                hint in ["hosted:video", "rich:video"] or 
                domain == "v.redd.it" or
                url.endswith(('.mp4', '.webm', '.mov'))
            )
            
            is_image = url.endswith(('.jpg', '.jpeg', '.png', '.gif'))
            
            return (is_video or is_image) and url not in self.bot.sent_media[channel_id]

        max_attempts = 15
        attempt = 0
        
        sort_strategies = [sort_type]
        if sort_type != 'new': sort_strategies.append('new')
        if sort_type != 'top': sort_strategies.append('top')
        
        current_sort_idx = 0
        
        while attempt < max_attempts and len(collected_media) < num_requested:
            possible_subreddits = [sub for sub in available_subreddits if sub not in tried_subreddits]
            if not possible_subreddits:
                current_sort_idx += 1
                if current_sort_idx < len(sort_strategies):
                    tried_subreddits.clear()
                    continue
                break

            subreddit = self.bot.rand.choice(possible_subreddits)
            current_sort = sort_strategies[current_sort_idx]
            
            posts = await fetch_posts(subreddit, current_sort)
            
            if not posts:
                tried_subreddits.add(subreddit)
                attempt += 1
                continue
                
            valid_urls = []
            for post in posts:
                if is_valid_media(post.get("data", {})):
                    valid_urls.append(post.get("data", {}).get("url"))
            
            if valid_urls:
                self.bot.rand.shuffle(valid_urls)
                for url in valid_urls:
                    if len(collected_media) >= num_requested: break
                    if url not in self.bot.sent_media[channel_id]:
                        self.bot.sent_media[channel_id].add(url)
                        collected_media.append(url)
            else:
                tried_subreddits.add(subreddit)
            
            attempt += 1

        if collected_media:
            for media_url in collected_media:
                try:
                    await self.bot.send_and_clean(message.channel, media_url)
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"failed to send media {media_url} {e}")
        else:
            await self.bot.send_and_clean(message.channel, "could not find valid media after several attempts try again later")

    async def cmd_redgif(self, message, command_args):
        args = message.content.strip().split()

        if len(args) < 3:
            return await self.bot.send_and_clean(message.channel, "usage nux redgif <search term(s)> [number]")

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
            return await self.bot.send_and_clean(message.channel, "this command can only be used in nsfw channels or direct messages")

        api = RedGifsAPI()
        api.login()

        try:
            search_result = api.search(search_term, count=50)
            gifs = search_result.gifs

            if not gifs:
                return await self.bot.send_and_clean(message.channel, f"no results found for '{search_term}'")

            channel_id = message.channel.id
            if channel_id not in self.bot.sent_media:
                self.bot.sent_media[channel_id] = set()

            valid_gifs = [gif.urls.hd for gif in gifs if gif.urls.hd not in self.bot.sent_media[channel_id]]

            if not valid_gifs:
                return await self.bot.send_and_clean(message.channel, "couldn't find new media, try again later")

            self.bot.rand.shuffle(valid_gifs)

            sent_count = 0
            for gif_url in valid_gifs:
                if sent_count >= num_requested:
                    break
                try:
                    await self.bot.send_and_clean(message.channel, gif_url)
                    self.bot.sent_media[channel_id].add(gif_url)
                    sent_count += 1
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"failed to send media {gif_url} {e}")

            if sent_count == 0:
                await self.bot.send_and_clean(message.channel, "failed to send media, please try again")

        except Exception as e:
            print(f"redgifs api error {e}")
            await self.bot.send_and_clean(message.channel, "an error occurred while fetching redgifs content")
        finally:
            pass

    async def _nekobot_image_command(self, message, image_types, command_args=""):
        num_requested = 1
        if command_args.strip():
            try:
                num_requested = int(command_args.strip())
                if num_requested <= 0:
                    num_requested = 1
                elif num_requested > 10:
                    num_requested = 10
            except ValueError:
                pass
        
        channel_id = message.channel.id
        if channel_id not in self.bot.sent_media:
            self.bot.sent_media[channel_id] = set()
        
        sent_count = 0
        max_attempts = num_requested * 10
        attempts = 0
        
        while sent_count < num_requested and attempts < max_attempts:
            attempts += 1
            image_type = self.bot.rand.choice(image_types) if isinstance(image_types, list) else image_types
            try:
                r = requests.get(f"https://nekobot.xyz/api/image?type={image_type}")
                data = r.json()
                url = data.get("message", "")
                if url and url not in self.bot.sent_media[channel_id]:
                    self.bot.sent_media[channel_id].add(url)
                    if len(self.bot.sent_media[channel_id]) > 500:
                        self.bot.sent_media[channel_id] = set(list(self.bot.sent_media[channel_id])[-400:])
                    await self.bot.send_and_clean(message.channel, url)
                    sent_count += 1
                    if sent_count < num_requested:
                        await asyncio.sleep(1)
            except Exception as e:
                print(f"nekobot error: {e}")
        
        if sent_count == 0:
            await self.bot.send_and_clean(message.channel, "no new images found")

    async def cmd_hentai(self, message, command_args=""):
        await self._nekobot_image_command(message, ['hentai', 'hboobs', 'hthigh'], command_args)

    async def cmd_thighs(self, message, command_args=""):
        await self._nekobot_image_command(message, "thigh", command_args)

    async def cmd_ass(self, message, command_args=""):
        await self._nekobot_image_command(message, "ass", command_args)

    async def cmd_boobs(self, message, command_args=""):
        await self._nekobot_image_command(message, "boobs", command_args)

    async def cmd_pussy(self, message, command_args=""):
        await self._nekobot_image_command(message, "pussy", command_args)

    async def cmd_pgif(self, message, command_args=""):
        await self._nekobot_image_command(message, "pgif", command_args)

    async def cmd_neko(self, message, command_args=""):
        await self._nekobot_image_command(message, "neko", command_args)

    async def _nekos_life_image_command(self, message, image_type, command_args=""):
        num_requested = 1
        if command_args.strip():
            try:
                num_requested = int(command_args.strip())
                if num_requested <= 0:
                    num_requested = 1
                elif num_requested > 10:
                    num_requested = 10
            except ValueError:
                pass
        
        channel_id = message.channel.id
        if channel_id not in self.bot.sent_media:
            self.bot.sent_media[channel_id] = set()
        
        sent_count = 0
        max_attempts = num_requested * 10
        attempts = 0
        
        async with aiohttp.ClientSession() as session:
            while sent_count < num_requested and attempts < max_attempts:
                attempts += 1
                try:
                    async with session.get(f'https://nekos.life/api/v2/img/{image_type}') as resp:
                        if resp.status != 200:
                            continue
                        data = await resp.json()
                        url = data.get("url", "")
                        if url and url not in self.bot.sent_media[channel_id]:
                            self.bot.sent_media[channel_id].add(url)
                            if len(self.bot.sent_media[channel_id]) > 500:
                                self.bot.sent_media[channel_id] = set(list(self.bot.sent_media[channel_id])[-400:])
                            await self.bot.send_and_clean(message.channel, url)
                            sent_count += 1
                            if sent_count < num_requested:
                                await asyncio.sleep(1)
                except Exception as e:
                    print(f"nekos.life error: {e}")
        
        if sent_count == 0:
            await self.bot.send_and_clean(message.channel, "no new images found")
                    
    async def cmd_ngif(self, message, command_args=""):
        await self._nekos_life_image_command(message, "ngif", command_args)

    async def cmd_nneko(self, message, command_args=""):
        await self._nekos_life_image_command(message, "neko", command_args)

    async def cmd_nfoxgirl(self, message, command_args=""):
        await self._nekos_life_image_command(message, "fox_girl", command_args)

    NIGHT_API_KEY = "lzjXAQDDzT-ohOSlveR0GQkAwL3defr-PBRgQpr4hv"

    async def _night_api_image_command(self, message, image_type, command_args=""):
        num_requested = 1
        if command_args.strip():
            try:
                num_requested = int(command_args.strip())
                if num_requested <= 0:
                    num_requested = 1
                elif num_requested > 10:
                    num_requested = 10
            except ValueError:
                pass
        
        channel_id = message.channel.id
        if channel_id not in self.bot.sent_media:
            self.bot.sent_media[channel_id] = set()
        
        headers = {"authorization": self.NIGHT_API_KEY}
        
        sent_count = 0
        max_attempts = num_requested * 10
        attempts = 0
        
        async with aiohttp.ClientSession() as session:
            while sent_count < num_requested and attempts < max_attempts:
                attempts += 1
                try:
                    async with session.get(f'https://api.night-api.com/images/nsfw/{image_type}', headers=headers) as resp:
                        if resp.status != 200:
                            text = await resp.text()
                            print(f"night api error: status {resp.status}, response: {text}")
                            continue
                        data = await resp.json()
                        content = data.get("content", {})
                        url = content.get("url") if isinstance(content, dict) else None
                        if url and url not in self.bot.sent_media[channel_id]:
                            self.bot.sent_media[channel_id].add(url)
                            if len(self.bot.sent_media[channel_id]) > 500:
                                self.bot.sent_media[channel_id] = set(list(self.bot.sent_media[channel_id])[-400:])
                            await self.bot.send_and_clean(message.channel, url)
                            sent_count += 1
                            if sent_count < num_requested:
                                await asyncio.sleep(1)
                except Exception as e:
                    print(f"night api error: {e}")
        
        if sent_count == 0:
            await self.bot.send_and_clean(message.channel, "no new images found")

    async def cmd_kanal(self, message, command_args=""):
        await self._night_api_image_command(message, "anal", command_args)

    async def cmd_kgonewild(self, message, command_args=""):
        await self._night_api_image_command(message, "gonewild", command_args)

    async def cmd_khanal(self, message, command_args=""):
        await self._night_api_image_command(message, "hanal", command_args)

    async def cmd_khass(self, message, command_args=""):
        await self._night_api_image_command(message, "hass", command_args)

    async def cmd_khkitsune(self, message, command_args=""):
        await self._night_api_image_command(message, "hkitsune", command_args)

    async def cmd_khmidriff(self, message, command_args=""):
        await self._night_api_image_command(message, "hmidriff", command_args)

    async def cmd_khneko(self, message, command_args=""):
        await self._night_api_image_command(message, "hneko", command_args)

    async def cmd_kpaizuri(self, message, command_args=""):
        await self._night_api_image_command(message, "paizuri", command_args)

    async def cmd_ktentacle(self, message, command_args=""):
        await self._night_api_image_command(message, "tentacle", command_args)

    async def cmd_kyaoi(self, message, command_args=""):
        await self._night_api_image_command(message, "yaoi", command_args)

    async def cmd_thighcalc(self, message, command_args=""):
        args = command_args.strip().split()
        if len(args) < 2:
            return await self.bot.send_and_clean(message.channel, "usage nux thighcalc <height_cm> <weight_kg>")

        try:
            height_cm = float(args[0])
            weight_kg = float(args[1])
        except ValueError:
            return await self.bot.send_and_clean(message.channel, "please provide valid numbers for height and weight")

        if height_cm <= 0 or weight_kg <= 0:
            return await self.bot.send_and_clean(message.channel, "height and weight must be positive numbers")

        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)

        prompt = f"""Given a person with BMI of {bmi:.2f} (height: {height_cm}cm, weight: {weight_kg}kg),
please provide a detailed, slightly playful but scientific estimate of theoretical thigh squeeze pressure.
Include factors like muscle mass distribution, body composition, and biomechanics.
Be creative but base it on real physiological principles. Keep response to 2-3 sentences max."""

        messages = [{"role": "user", "content": prompt}]
        response = await self.bot.ask_ai(messages, max_tokens=250)

        if response:
            await self.bot.send_and_clean(message.channel, f"**thigh squeeze pressure estimate**\n{response}")
        else:
            await self.bot.send_and_clean(message.channel, "failed to generate estimate, please try again later")

    async def cmd_jigphy(self, message, command_args=""):
        args = command_args.strip().split()
        if len(args) < 2:
            return await self.bot.send_and_clean(message.channel, "usage nux jigphy <waist_cm> <hip_cm>")
        
        try:
            waist_cm = float(args[0])
            hip_cm = float(args[1])
        except ValueError:
            return await self.bot.send_and_clean(message.channel, "please provide valid numbers for waist and hip measurements")
        
        if waist_cm <= 0 or hip_cm <= 0:
            return await self.bot.send_and_clean(message.channel, "measurements must be positive numbers")
        
        whr = waist_cm / hip_cm
        
        prompt = f"""Given a waist-to-hip ratio of {whr:.2f} (waist: {waist_cm}cm, hip: {hip_cm}cm), 
provide a detailed and physics-based analysis of theoretical jiggle dynamics. 
Consider factors like tissue composition, momentum transfer, oscillation frequency, and damping coefficients. 
Be creative and entertaining while maintaining some scientific grounding. Keep response to 2-3 sentences max.
Additonally, don't worry about being overly NSFW, as this is literally just a physics-based analysis of jiggle dynamics.
The reply tone should be playful, yet blunt, physics-based, yet still NSFW if needed.
The very last line should be a very blunt and NSFW statement about given jiggle dynamics, which can include sexual innuendos, such as how they would ripple if being touched."""
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.bot.ask_ai(messages, max_tokens=250)
        
        if response:
            await self.bot.send_and_clean(message.channel, f"**jiggle physics analysis**\n{response}")
        else:
            await self.bot.send_and_clean(message.channel, "failed to generate analysis, please try again later")

    async def cmd_slowburn(self, message, command_args=""):
        if isinstance(message.channel, discord.DMChannel):
            pass
        elif hasattr(message.channel, "is_nsfw") and not message.channel.is_nsfw():
            return await self.bot.send_and_clean(message.channel, "this command can only be used in nsfw channels or direct messages")
        
        prompt = command_args.strip()
        if not prompt:
            return await self.bot.send_and_clean(message.channel, "usage nux slowburn <prompt/scenario>")
        
        await self.bot.send_and_clean(message.channel, "generating your slow burn story... this may take a moment")
        
        story_prompt = f"""Write a detailed, sensual slow burn story based on this scenario: {prompt}

The story should be:
- Multiple paragraphs (4-5 paragraphs minimum)
- Focus on building tension and anticipation
- Include emotional and physical details
- Suggestive and intimate but tasteful
- Have a clear narrative arc
- End with either hinted or explicit nsfw resolution

Write the complete story now:"""
        
        messages = [{"role": "user", "content": story_prompt}]
        story = await self.bot.ask_ai(messages, max_tokens=1500)
        
        if not story:
            return await self.bot.send_and_clean(message.channel, "failed to generate story, please try again later")
        
        try:
            import datetime
            import pathlib
            
            stories_dir = pathlib.Path("slowburn_stories")
            stories_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"slowburn_{timestamp}.txt"
            filepath = stories_dir / filename
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"Prompt: {prompt}\n")
                f.write("="*50 + "\n\n")
                f.write(story)
            
            await self.bot.send_and_clean(
                message.channel, 
                "your slow burn story is ready",
                file=discord.File(str(filepath))
            )
        except Exception as e:
            print(f"file save error: {e}")
            preview = story[:500] + "..." if len(story) > 500 else story
            await self.bot.send_and_clean(message.channel, f"couldn't save story, here's a preview\n{preview}")

    async def cmd_pickup(self, message, command_args=""):
        if isinstance(message.channel, discord.DMChannel):
            pass
        elif hasattr(message.channel, "is_nsfw") and not message.channel.is_nsfw():
            return await self.bot.send_and_clean(message.channel, "this command can only be used in nsfw channels or direct messages")
        
        theme = command_args.strip() if command_args.strip() else "flirty and suggestive"
        
        messages = [
            {"role": "system", "content": f"You are a master of pickup lines. Generate 3 creative, {theme} pickup lines. Make them clever and bold. Number them 1-3."},
            {"role": "user", "content": "Give me your best pickup lines."}
        ]
        pickup_lines = await self.bot.ask_ai(messages, max_tokens=250)
        
        if pickup_lines:
            await self.bot.send_and_clean(message.channel, f"💋 **Pickup Lines**\n{pickup_lines}")
        else:
            await self.bot.send_and_clean(message.channel, "couldn't generate pickup lines")

    async def cmd_lewdify(self, message, command_args):
        if isinstance(message.channel, discord.DMChannel):
            pass
        elif hasattr(message.channel, "is_nsfw") and not message.channel.is_nsfw():
            return await self.bot.send_and_clean(message.channel, "this command can only be used in nsfw channels or direct messages")

        prompt = command_args.strip()
        if not prompt:
            return await self.bot.send_and_clean(message.channel, "provide a prompt to lewdify")

        lewdify_prompt = f"""Take this prompt and create a NSFW/lewd version of it: "{prompt}"

Make it explicit and sexual while keeping the core concept. Be creative and detailed.
Keep the response to 2-3 sentences max. Don't hold back on the NSFW content."""

        messages = [{"role": "user", "content": lewdify_prompt}]
        lewdified = await self.bot.ask_ai(messages, max_tokens=250)

        if lewdified:
            await self.bot.send_and_clean(message.channel, f"🔞 **Lewdified**\n{lewdified}")
        else:
            await self.bot.send_and_clean(message.channel, "failed to lewdify, please try again later")

    async def cmd_nsfwmix(self, message, command_args=""):
        args = message.content.strip().split()

        if len(args) < 4:
            return await self.bot.send_and_clean(message.channel, "usage nux nsfwmix <category1> <category2> [number]")

        categories = []
        num_requested = 1

        for arg in args[2:]:
            if arg.lower() in nsfw_categories:
                categories.append(arg.lower())
            else:
                try:
                    num_requested = int(arg)
                    if num_requested <= 0:
                        num_requested = 1
                except ValueError:
                    continue

        if len(categories) < 2:
            return await self.bot.send_and_clean(message.channel, "please provide at least 2 valid categories")

        if isinstance(message.channel, discord.DMChannel):
            pass
        elif hasattr(message.channel, "is_nsfw") and not message.channel.is_nsfw():
            return await self.bot.send_and_clean(message.channel, "this command can only be used in nsfw channels or direct messages")

        channel_id = message.channel.id
        if channel_id not in self.bot.sent_media:
            self.bot.sent_media[channel_id] = set()

        collected_media = []
        all_subreddits = []

        for category in categories:
            all_subreddits.extend(nsfw_categories[category])

        if not all_subreddits:
            return await self.bot.send_and_clean(message.channel, "no valid subreddits found for the selected categories")

        async def fetch_posts(subreddit, sort="hot"):
            url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit=100"
            headers = {"user-agent": "mozilla/5.0"}
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return data.get("data", {}).get("children", [])
            except:
                pass
            return []

        def is_valid_media(post_data):
            url = post_data.get("url", "")
            if post_data.get("stickied", False): return False
            if "redgifs" in url.lower() or "gfycat" in url.lower(): return False

            hint = post_data.get("post_hint", "")
            domain = post_data.get("domain", "")

            is_video = (
                hint in ["hosted:video", "rich:video"] or
                domain == "v.redd.it" or
                url.endswith(('.mp4', '.webm', '.mov'))
            )

            is_image = url.endswith(('.jpg', '.jpeg', '.png', '.gif'))

            return (is_video or is_image) and url not in self.bot.sent_media[channel_id]

        max_attempts = 20
        attempt = 0
        tried_subreddits = set()

        while attempt < max_attempts and len(collected_media) < num_requested:
            available_subreddits = [sub for sub in all_subreddits if sub not in tried_subreddits]
            if not available_subreddits:
                break

            subreddit = self.bot.rand.choice(available_subreddits)
            posts = await fetch_posts(subreddit)

            if not posts:
                tried_subreddits.add(subreddit)
                attempt += 1
                continue

            valid_urls = []
            for post in posts:
                if is_valid_media(post.get("data", {})):
                    valid_urls.append(post.get("data", {}).get("url"))

            if valid_urls:
                self.bot.rand.shuffle(valid_urls)
                for url in valid_urls:
                    if len(collected_media) >= num_requested: break
                    if url not in self.bot.sent_media[channel_id]:
                        self.bot.sent_media[channel_id].add(url)
                        collected_media.append(url)
            else:
                tried_subreddits.add(subreddit)

            attempt += 1

        if collected_media:
            for media_url in collected_media:
                try:
                    await self.bot.send_and_clean(message.channel, media_url)
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"failed to send media {media_url} {e}")
        else:
            await self.bot.send_and_clean(message.channel, "could not find valid media after several attempts try again later")

    async def cmd_nsfwrandom(self, message, command_args=""):
        args = message.content.strip().split()

        num_requested = 1
        if len(args) >= 3:
            try:
                num_requested = int(args[2])
                if num_requested <= 0:
                    num_requested = 1
            except ValueError:
                pass

        if isinstance(message.channel, discord.DMChannel):
            pass
        elif hasattr(message.channel, "is_nsfw") and not message.channel.is_nsfw():
            return await self.bot.send_and_clean(message.channel, "this command can only be used in nsfw channels or direct messages")

        channel_id = message.channel.id
        if channel_id not in self.bot.sent_media:
            self.bot.sent_media[channel_id] = set()

        all_subreddits = []
        for category, subreddits in nsfw_categories.items():
            all_subreddits.extend(subreddits)

        if not all_subreddits:
            return await self.bot.send_and_clean(message.channel, "no nsfw categories available")

        collected_media = []

        async def fetch_posts(subreddit, sort="hot"):
            url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit=100"
            headers = {"user-agent": "mozilla/5.0"}
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return data.get("data", {}).get("children", [])
            except:
                pass
            return []

        def is_valid_media(post_data):
            url = post_data.get("url", "")
            if post_data.get("stickied", False): return False
            if "redgifs" in url.lower() or "gfycat" in url.lower(): return False

            hint = post_data.get("post_hint", "")
            domain = post_data.get("domain", "")

            is_video = (
                hint in ["hosted:video", "rich:video"] or
                domain == "v.redd.it" or
                url.endswith(('.mp4', '.webm', '.mov'))
            )

            is_image = url.endswith(('.jpg', '.jpeg', '.png', '.gif'))

            return (is_video or is_image) and url not in self.bot.sent_media[channel_id]

        max_attempts = 20
        attempt = 0
        tried_subreddits = set()

        while attempt < max_attempts and len(collected_media) < num_requested:
            available_subreddits = [sub for sub in all_subreddits if sub not in tried_subreddits]
            if not available_subreddits:
                break

            subreddit = self.bot.rand.choice(available_subreddits)
            posts = await fetch_posts(subreddit)

            if not posts:
                tried_subreddits.add(subreddit)
                attempt += 1
                continue

            valid_urls = []
            for post in posts:
                if is_valid_media(post.get("data", {})):
                    valid_urls.append(post.get("data", {}).get("url"))

            if valid_urls:
                self.bot.rand.shuffle(valid_urls)
                for url in valid_urls:
                    if len(collected_media) >= num_requested: break
                    if url not in self.bot.sent_media[channel_id]:
                        self.bot.sent_media[channel_id].add(url)
                        collected_media.append(url)
            else:
                tried_subreddits.add(subreddit)

            attempt += 1

        if collected_media:
            for media_url in collected_media:
                try:
                    await self.bot.send_and_clean(message.channel, media_url)
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"failed to send media {media_url} {e}")
        else:
            await self.bot.send_and_clean(message.channel, "could not find valid media after several attempts try again later")

    async def cmd_nsfwsearch(self, message, command_args=""):
        args = message.content.strip().split()

        if len(args) < 3:
            return await self.bot.send_and_clean(message.channel, "usage nux nsfwsearch <query> [number]")

        num_requested = 1
        if len(args) >= 4:
            try:
                num_requested = int(args[3])
                if num_requested <= 0:
                    num_requested = 1
            except ValueError:
                pass

        search_query = args[2].lower()

        if isinstance(message.channel, discord.DMChannel):
            pass
        elif hasattr(message.channel, "is_nsfw") and not message.channel.is_nsfw():
            return await self.bot.send_and_clean(message.channel, "this command can only be used in nsfw channels or direct messages")

        channel_id = message.channel.id
        if channel_id not in self.bot.sent_media:
            self.bot.sent_media[channel_id] = set()

        all_subreddits = []
        for category, subreddits in nsfw_categories.items():
            all_subreddits.extend(subreddits)

        if not all_subreddits:
            return await self.bot.send_and_clean(message.channel, "no nsfw categories available")

        collected_media = []

        async def search_subreddit(subreddit, query):
            url = f"https://www.reddit.com/r/{subreddit}/search.json?q={query}&sort=relevance&limit=100"
            headers = {"user-agent": "mozilla/5.0"}
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return data.get("data", {}).get("children", [])
            except:
                pass
            return []

        def is_valid_media(post_data):
            url = post_data.get("url", "")
            if post_data.get("stickied", False): return False
            if "redgifs" in url.lower() or "gfycat" in url.lower(): return False

            hint = post_data.get("post_hint", "")
            domain = post_data.get("domain", "")

            is_video = (
                hint in ["hosted:video", "rich:video"] or
                domain == "v.redd.it" or
                url.endswith(('.mp4', '.webm', '.mov'))
            )

            is_image = url.endswith(('.jpg', '.jpeg', '.png', '.gif'))

            return (is_video or is_image) and url not in self.bot.sent_media[channel_id]

        max_attempts = 15
        attempt = 0
        tried_subreddits = set()

        while attempt < max_attempts and len(collected_media) < num_requested:
            available_subreddits = [sub for sub in all_subreddits if sub not in tried_subreddits]
            if not available_subreddits:
                break

            subreddit = self.bot.rand.choice(available_subreddits)
            posts = await search_subreddit(subreddit, search_query)

            if not posts:
                tried_subreddits.add(subreddit)
                attempt += 1
                continue

            valid_urls = []
            for post in posts:
                if is_valid_media(post.get("data", {})):
                    valid_urls.append(post.get("data", {}).get("url"))

            if valid_urls:
                self.bot.rand.shuffle(valid_urls)
                for url in valid_urls:
                    if len(collected_media) >= num_requested: break
                    if url not in self.bot.sent_media[channel_id]:
                        self.bot.sent_media[channel_id].add(url)
                        collected_media.append(url)
            else:
                tried_subreddits.add(subreddit)

            attempt += 1

        if collected_media:
            for media_url in collected_media:
                try:
                    await self.bot.send_and_clean(message.channel, media_url)
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"failed to send media {media_url} {e}")
        else:
            await self.bot.send_and_clean(message.channel, f"could not find media matching '{search_query}' after several attempts try again later")

    async def cmd_nsfwblacklist(self, message, command_args=""):
        args = message.content.strip().split()

        if len(args) < 3:
            return await self.bot.send_and_clean(message.channel, "usage nux nsfwblacklist <category1> <category2> ...")

        categories_to_blacklist = []
        for arg in args[2:]:
            if arg.lower() in nsfw_categories:
                categories_to_blacklist.append(arg.lower())
            else:
                return await self.bot.send_and_clean(message.channel, f"invalid category: {arg}. use 'nux nsfwlist' to see available categories")

        if not categories_to_blacklist:
            return await self.bot.send_and_clean(message.channel, "no valid categories provided")

        if not hasattr(self.bot, 'nsfw_blacklist'):
            self.bot.nsfw_blacklist = set()

        for category in categories_to_blacklist:
            self.bot.nsfw_blacklist.add(category)

        blacklisted = ", ".join(categories_to_blacklist)
        await self.bot.send_and_clean(message.channel, f"blacklisted categories: {blacklisted}")

def setup(bot):
    return NSFW(bot), nsfwhelp_msg
