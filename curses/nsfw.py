import discord
import aiohttp
import asyncio
import requests
import xml.etree.ElementTree as ET
import os
from redgifs import API as RedGifsAPI

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
        "nux nsfw": "get nsfw images from reddit categories (ass, boobs, hentai, milf, thighs, goth, bwomen, rreverse, femdom, asian), usage: nux nsfw <category> [number]",
        "nux nsfwlist": "show available nsfw categories",
        "nux redgif": "search redgif for nsfw gifs, usage: nux redgif <search> <number>",
        "nux rule34": "search rule34.xxx for nsfw images, usage: nux rule34 <search> <number>",
        "nux thighcalc": "estimate squeeze pressure based on bmi inputs, usage: nux thighcalc <height_cm> <weight_kg>",
        "nux jigphy": "estimate jiggle physics based on waist-to-hip ratio, usage: nux jigphy <waist_cm> <hip_cm>",
        "nux slowburn": "ai-generated slow burn story (requires openrouter), usage: nux slowburn <prompt>",
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
            return await self.bot.send_and_clean(message.channel, "usage nux nsfw <category> [number]\nunsure of the categories use nux nsfwlist")

        category = args[2].strip('<>').lower()

        if category not in nsfw_categories:
            return await self.bot.send_and_clean(message.channel, "invalid category use 'nux nsfwlist' to see available categories")

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
            return await self.bot.send_and_clean(message.channel, "this command can only be used in nsfw channels or direct messages")

        max_attempts = 10
        attempt = 0
        collected_media = []
        tried_subreddits = set()

        channel_id = message.channel.id
        if channel_id not in self.bot.sent_media:
            self.bot.sent_media[channel_id] = set()

        available_subreddits = nsfw_categories[category][:]
        while attempt < max_attempts and len(collected_media) < num_requested:
            possible_subreddits = [sub for sub in available_subreddits if sub not in tried_subreddits]

            if not possible_subreddits:
                print("all subreddits have been tried, stopping early")
                break

            subreddit = self.bot.rand.choice(possible_subreddits)
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
                                if media_url not in self.bot.sent_media[channel_id]:
                                    valid_posts.append(media_url)

                        print(f"found {len(valid_posts)} new valid media posts in r/{subreddit}")

                        if not valid_posts:
                            attempt += 1
                            tried_subreddits.add(subreddit)
                            continue

                        self.bot.rand.shuffle(valid_posts)

                        for media_url in valid_posts:
                            if len(collected_media) >= num_requested:
                                break
                            self.bot.sent_media[channel_id].add(media_url)
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
                    await self.bot.send_and_clean(message.channel, media_url)
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"failed to send media {media_url} {e}")
            return
        else:
            return await self.bot.send_and_clean(message.channel, "could not find valid media after several attempts try again later")

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

    async def cmd_rule34(self, message, command_args):
        args = message.content.strip().split()

        if len(args) < 3:
            return await self.bot.send_and_clean(message.channel, "usage nux rule34 <search term(s)> [number]")

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
            return await self.bot.send_and_clean(message.channel, "this command can only be used in nsfw channels or direct messages")

        url = f"https://rule34.xxx/index.php?page=dapi&s=post&q=index&limit=100&tags={search_tags}"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await self.bot.send_and_clean(message.channel, "failed to fetch results from rule34")

                    text = await resp.text()
                    root = ET.fromstring(text)
                    posts = root.findall('post')

                    if not posts:
                        return await self.bot.send_and_clean(message.channel, f"no results found for '{search_tags.replace('+', ' ')}'")

                    channel_id = message.channel.id
                    if channel_id not in self.bot.sent_media:
                        self.bot.sent_media[channel_id] = []

                    valid_posts = []
                    for post in posts:
                        file_url = post.attrib.get('file_url')
                        if file_url and file_url not in self.bot.sent_media[channel_id]:
                            valid_posts.append(file_url)

                    if not valid_posts:
                        return await self.bot.send_and_clean(message.channel, "couldn't find new media, try again later")

                    self.bot.rand.shuffle(valid_posts)

                    sent_count = 0
                    for file_url in valid_posts:
                        if sent_count >= num_requested:
                            break
                        try:
                            await self.bot.send_and_clean(message.channel, file_url)
                            MAX_TRACKED_URLS = 500
                            self.bot.sent_media[channel_id].append(file_url)
                            if len(self.bot.sent_media[channel_id]) > MAX_TRACKED_URLS:
                                self.bot.sent_media[channel_id].pop(0)
                            sent_count += 1
                            await asyncio.sleep(1)
                        except Exception as e:
                            print(f"failed to send media {file_url} {e}")

                    if sent_count == 0:
                        await self.bot.send_and_clean(message.channel, "failed to send media, please try again")

            except Exception as e:
                print(f"rule34 api error {e}")
                await self.bot.send_and_clean(message.channel, "an error occurred while fetching rule34 content")
                
    async def cmd_hentai(self, message, commands_args=""):
        r = requests.get("https://nekobot.xyz/api/image?type=" + self.bot.rand.choice(['hentai', 'hboobs', 'hthigh']))
        data = r.json()
        await self.bot.send_and_clean(message.channel, data.get("message", "no image found"))

    async def cmd_thighs(self, message, command_args=""):
        r = requests.get("https://nekobot.xyz/api/image?type=thigh")
        data = r.json()
        await self.bot.send_and_clean(message.channel, data.get("message", "no image found"))

    async def cmd_ass(self, message, command_args=""):
        r = requests.get("https://nekobot.xyz/api/image?type=ass")
        data = r.json()
        await self.bot.send_and_clean(message.channel, data.get("message", "no image found"))

    async def cmd_boobs(self, message, command_args=""):
        r = requests.get("https://nekobot.xyz/api/image?type=boobs")
        data = r.json()
        await self.bot.send_and_clean(message.channel, data.get("message", "no image found"))

    async def cmd_pussy(self, message, command_args=""):
        r = requests.get("https://nekobot.xyz/api/image?type=pussy")
        data = r.json()
        await self.bot.send_and_clean(message.channel, data.get("message", "no image found"))

    async def cmd_pgif(self, message, command_args=""):
        r = requests.get("https://nekobot.xyz/api/image?type=pgif")
        data = r.json()
        await self.bot.send_and_clean(message.channel, data.get("message", "no image found"))

    async def cmd_neko(self, message, command_args=""):
        r = requests.get("https://nekobot.xyz/api/image?type=neko")
        data = r.json()
        await self.bot.send_and_clean(message.channel, data.get("message", "no image found"))

    async def _nekos_life_image_command(self, message, image_type):
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://nekos.life/api/v2/img/{image_type}') as resp:
                if resp.status != 200:
                    return await self.bot.send_and_clean(message.channel, f"couldn't fetch {image_type} image")
                data = await resp.json()
                await self.bot.send_and_clean(message.channel, data.get("url", "no image found"))

    async def cmd_thighcalc(self, message, command_args=""):
        """Estimate squeeze pressure based on BMI inputs using AI"""
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
        
        openrouter_key = os.getenv('OpenRouter')
        if not openrouter_key:
            return await self.bot.send_and_clean(message.channel, "openrouter api key not set in .env")
        
        prompt = f"""Given a person with BMI of {bmi:.2f} (height: {height_cm}cm, weight: {weight_kg}kg), 
please provide a detailed, slightly playful but scientific estimate of theoretical thigh squeeze pressure. 
Include factors like muscle mass distribution, body composition, and biomechanics. 
Be creative but base it on real physiological principles. Keep response to 2-3 sentences max."""
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"authorization": f"bearer {openrouter_key}", "content-type": "application/json"}
        
        models = [
            "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
            "nousresearch/hermes-3-llama-3.1-405b:free",
            "meituan/longcat-flash-chat:free"
        ]
        
        for model in models:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "max_tokens": 250
            }
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=payload) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            response = data["choices"][0]["message"]["content"].strip()
                            await self.bot.send_and_clean(message.channel, f"**thigh squeeze pressure estimate**\n{response}")
                            return
                        else:
                            print(f"openrouter error with {model}: {resp.status}")
                            continue
            except Exception as e:
                print(f"error with {model}: {e}")
                continue
        
        await self.bot.send_and_clean(message.channel, "failed to generate estimate, please try again later")

    async def cmd_jigphy(self, message, command_args=""):
        """Estimate jiggle physics based on waist-to-hip ratio using AI"""
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
        
        openrouter_key = os.getenv('OpenRouter')
        if not openrouter_key:
            return await self.bot.send_and_clean(message.channel, "openrouter api key not set in .env")
        
        prompt = f"""Given a waist-to-hip ratio of {whr:.2f} (waist: {waist_cm}cm, hip: {hip_cm}cm), 
provide a detailed and physics-based analysis of theoretical jiggle dynamics. 
Consider factors like tissue composition, momentum transfer, oscillation frequency, and damping coefficients. 
Be creative and entertaining while maintaining some scientific grounding. Keep response to 2-3 sentences max.
Additonally, don't worry about being overly NSFW, as this is literally just a physics-based analysis of jiggle dynamics.
The reply tone should be playful, yet blunt, physics-based, yet still NSFW if needed.
The very last line should be a very blunt and NSFW statement about given jiggle dynamics, which can include sexual innuendos, such as how they would ripple if being touched."""
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"authorization": f"bearer {openrouter_key}", "content-type": "application/json"}
        
        models = [
            "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
            "nousresearch/hermes-3-llama-3.1-405b:free",
            "meituan/longcat-flash-chat:free"
        ]
        
        for model in models:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "max_tokens": 250
            }
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=payload) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            response = data["choices"][0]["message"]["content"].strip()
                            await self.bot.send_and_clean(message.channel, f"**jiggle physics analysis**\n{response}")
                            return
                        else:
                            print(f"openrouter error with {model}: {resp.status}")
                            continue
            except Exception as e:
                print(f"error with {model}: {e}")
                continue
        
        await self.bot.send_and_clean(message.channel, "failed to generate analysis, please try again later")

    async def cmd_slowburn(self, message, command_args=""):
        """Generate a slow burn story with AI and save to local file"""
        if isinstance(message.channel, discord.DMChannel):
            pass
        elif hasattr(message.channel, "is_nsfw") and not message.channel.is_nsfw():
            return await self.bot.send_and_clean(message.channel, "this command can only be used in nsfw channels or direct messages")
        
        prompt = command_args.strip()
        if not prompt:
            return await self.bot.send_and_clean(message.channel, "usage nux slowburn <prompt/scenario>")
        
        openrouter_key = os.getenv('OpenRouter')
        if not openrouter_key:
            return await self.bot.send_and_clean(message.channel, "openrouter api key not set in .env")
        
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
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"authorization": f"bearer {openrouter_key}", "content-type": "application/json"}
        
        models = [
            "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
            "nousresearch/hermes-3-llama-3.1-405b:free",
            "z-ai/glm-4.5-air:free",
            "meituan/longcat-flash-chat:free"
        ]
        
        story = None
        for model in models:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": story_prompt}],
                "stream": False,
                "max_tokens": 1500
            }
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=payload) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            story = data["choices"][0]["message"]["content"].strip()
                            break
                        else:
                            print(f"openrouter error with {model}: {resp.status}")
                            continue
            except Exception as e:
                print(f"error with {model}: {e}")
                continue
        
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

def setup(bot):
    return NSFW(bot), nsfwhelp_msg