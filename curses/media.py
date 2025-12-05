import discord
import aiohttp
import io
import os
import urllib.parse
import qrcode
import yt_dlp
import subprocess
import numpy as np
import scipy.signal as sp_signal
import soundfile as sf
import random
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont

HELP_TEXT = {
    "media": {
        "nux qr <text/url>": "generate a qr code",
        "nux tts <text>": "convert text to speech (sends mp3)",
        "nux dlmedia <url>": "download videos or audio from youtube, tiktok, pinterest, twitter (fuck x), instagram, and reddit (more websites supported soon)",
        "nux pornhub <white> - <orange>": "make a image with your text in the pornhub logo style",
        "nux didyou mean <search> - <dym>": "make a google result image that has the <search> text in the text bar, and <dym> being the blue text that would correct you",
        "nux facts <text>": "make an image with the fact book from ed, edd n eddy using your text",
        "nux scroll <text>": "make an image with the scroll meme format",
        "nux freq <freq hz> <waveform>": "sends back an audio file with the requested hz and waveform, useful for clean frequencies",
        "nux font <fontname> <text>": "renders text using a specific font from dmfonts",
        "nux vintage": "add VHS effects to last image in chat",
    }
}


class Media:
    def __init__(self, bot):
        self.bot = bot
    
    async def cmd_qr(self, message, command_args):
        text = command_args
        if not text:
            return await self.bot.send_and_clean(message.channel, "send me some text or a link to make a qr code")
        
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
            await self.bot.send_and_clean(message.channel, file=discord.File(fp=image_binary, filename="qr.png"))

    async def cmd_tts(self, message, command_args):
        text = command_args.strip()
        if not text:
            return await self.bot.send_and_clean(message.channel, "speak what, darling")
        
        try:
            tts = gTTS(text=text, lang="en")
            buffer = io.BytesIO()
            tts.write_to_fp(buffer)
            buffer.seek(0)
            await self.bot.send_and_clean(message.channel, file=discord.File(buffer, "tts.mp3"))
        except Exception as e:
            return await self.bot.send_and_clean(message.channel, f"failed to generate tts: {e}")

    async def cmd_pornhub(self, message, command_args):
        args = command_args.split(" - ")
        
        if len(args) != 2:
            await self.bot.send_and_clean(message.channel, "usage nux pornhub <text1> - <text2>")
            return
        
        text1, text2 = args
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.bot.af_api}/pornhub?text={urllib.parse.quote(text1)}&text2={urllib.parse.quote(text2)}"
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await self.bot.send_and_clean(message.channel, "couldn't generate image")
                    img_bytes = await resp.read()
            buffer = io.BytesIO(img_bytes)
            await self.bot.send_and_clean(message.channel, file=discord.File(buffer, filename="pornhub.png"))
        except Exception as e:
            await self.bot.send_and_clean(message.channel, "couldn't generate image")

    async def cmd_didyoumean(self, message, command_args):
        args = command_args.split(" - ")
        
        if len(args) != 2:
            await self.bot.send_and_clean(message.channel, "usage nux didyoumean <text1> - <text2>")
            return
        
        text1, text2 = args
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.bot.af_api}/didyoumean?top={urllib.parse.quote(text1)}&bottom={urllib.parse.quote(text2)}"
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await self.bot.send_and_clean(message.channel, "couldn't generate image")
                    img_bytes = await resp.read()
            buffer = io.BytesIO(img_bytes)
            await self.bot.send_and_clean(message.channel, file=discord.File(buffer, filename="didyoumean.png"))
        except Exception as e:
            await self.bot.send_and_clean(message.channel, "couldn't generate image")

    async def cmd_facts(self, message, command_args):
        text = command_args
        if not text:
            await self.bot.send_and_clean(message.channel, "usage nux facts <text>")
            return
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.bot.af_api}/facts?text={urllib.parse.quote(text)}"
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await self.bot.send_and_clean(message.channel, "couldn't generate facts")
                    img_bytes = await resp.read()
            buffer = io.BytesIO(img_bytes)
            await self.bot.send_and_clean(message.channel, file=discord.File(buffer, filename="facts.png"))
        except Exception as e:
            await self.bot.send_and_clean(message.channel, "couldn't generate facts")

    async def cmd_scroll(self, message, command_args):
        text = command_args
        if not text:
            await self.bot.send_and_clean(message.channel, "usage nux scroll <text>")
            return
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.bot.af_api}/scroll?text={urllib.parse.quote(text)}"
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await self.bot.send_and_clean(message.channel, "couldn't generate scroll")
                    img_bytes = await resp.read()
            buffer = io.BytesIO(img_bytes)
            await self.bot.send_and_clean(message.channel, file=discord.File(buffer, filename="scroll.png"))
        except Exception as e:
            await self.bot.send_and_clean(message.channel, "couldn't generate scroll")

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

    async def cmd_font(self, message, command_args=""):
        args = command_args.split()
        if len(args) < 1:
            await self.bot.send_and_clean(message.channel, "usage nux font... *breath...* <arathos|berosong|betterfields|brunoblack|hanah|krondos|maskneyes|maytorm|onerock|rockaura|roomach|spider|thunder> <text>")
            return
        
        font_name = args[0].lower()
        text = ' '.join(args[1:])
        
        font_dir = 'dmfonts'
        available_fonts = {f.split('.')[0].lower(): f for f in os.listdir(font_dir) if f.endswith(('.ttf', '.otf'))}
        
        if font_name not in available_fonts:
            await self.bot.send_and_clean(message.channel, f"font '{font_name}' not found available fonts {', '.join(available_fonts.keys())}")
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

    async def cmd_dlmedia(self, message, command_args):
        url = command_args.strip()
        
        if not url:
            await self.bot.send_and_clean(message.channel, "usage: nux dlmedia <url>")
            return
        
        platform = "unknown"
        
        if "tiktok.com" in url:
            platform = "tiktok"
        elif "pinterest.com" in url or "pin.it" in url:
            platform = "pinterest"
        elif "youtube.com" in url or "youtu.be" in url:
            platform = "youtube"
        elif "twitter.com" in url or "x.com" in url:
            platform = "twitter"
        elif "instagram.com" in url:
            platform = "instagram"
        elif "reddit.com" in url or "v.redd.it" in url:
            platform = "reddit"
        elif "facebook.com" in url:
            platform = "facebook"
        elif "soundcloud.com" in url:
            platform = "soundcloud"
        elif "twitch.tv" in url:
            platform = "twitch"
        else:
            await self.bot.send_and_clean(message.channel, "unsupported url - supported: tiktok, pinterest, youtube, twitter, instagram, reddit, facebook, soundcloud, twitch")
            return
        
        ydl_opts = {
            'quiet': True,
            'noplaylist': True,
            'skip_download': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                
                video_url = None
                audio_url = None
                
                if 'formats' in info:
                    for f in reversed(info['formats']):
                        if f.get('vcodec') != 'none' and not video_url:
                            video_url = f.get('url')
                        if f.get('acodec') != 'none' and f.get('vcodec') == 'none' and not audio_url:
                            audio_url = f.get('url')
                
                if not video_url:
                    video_url = info.get('url')
                
                response = f"**{platform}** - {title}\n"
                if duration:
                    mins, secs = divmod(duration, 60)
                    response += f"duration: {int(mins)}:{int(secs):02d}\n"
                response += f"\n**video:** {video_url}"
                if audio_url:
                    response += f"\n**audio:** {audio_url}"
                
                await self.bot.send_and_clean(message.channel, response)
        
        except Exception as e:
            await self.bot.send_and_clean(message.channel, f"error extracting media: {e}")
    
    async def cmd_vintage(self, message, command_args):
        async for msg in message.channel.history(limit=50):
            if msg.attachments:
                for attachment in msg.attachments:
                    if attachment.content_type and attachment.content_type.startswith('image/'):
                        try:
                            async with aiohttp.ClientSession() as session:
                                async with session.get(attachment.url) as resp:
                                    if resp.status == 200:
                                        img_data = await resp.read()
                                        img = Image.open(io.BytesIO(img_data))
                                        
                                        img = img.convert('RGB')
                                        pixels = np.array(img)
                                    
                                        noise = np.random.randint(-30, 30, pixels.shape, dtype=np.int16)
                                        pixels = np.clip(pixels.astype(np.int16) + noise, 0, 255).astype(np.uint8)
                                    
                                        for i in range(0, pixels.shape[0], 4):
                                            pixels[i:i+2] = pixels[i:i+2] * 0.7
                                        
                                        shift = 3
                                        red = np.roll(pixels[:,:,0], shift, axis=1)
                                        blue = np.roll(pixels[:,:,2], -shift, axis=1)
                                        pixels[:,:,0] = red
                                        pixels[:,:,2] = blue
                                        
                                        vintage_img = Image.fromarray(pixels.astype(np.uint8))
                                        
                                        output = io.BytesIO()
                                        vintage_img.save(output, format='PNG')
                                        output.seek(0)
                                        
                                        await self.bot.send_and_clean(message.channel, "", file=discord.File(output, 'vintage.png'))
                                        return
                        except Exception as e:
                            await self.bot.send_and_clean(message.channel, f"failed to apply vintage effect: {e}")
                            return
        
        await self.bot.send_and_clean(message.channel, "no image found in recent messages")

def setup(bot):
    return Media(bot), HELP_TEXT
