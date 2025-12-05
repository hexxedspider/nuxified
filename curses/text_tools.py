import aiohttp, base64, hashlib, uuid, random, asyncio
from pyfiglet import figlet_format

zalgo_up = [chr(i) for i in range(0x0300, 0x036F)]
flip_map = str.maketrans(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890",
    "ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz∀𐐒ƆᗡƎℲ⅁HIſʞ˥WՈΌԀΌᴚS⊥ՈΛMX⅄Z⇂ᄅƐㄣϛ9ㄥ860"
)
MORSE_CODE_DICT = {
'a': '.-', 'b': '-...', 'c': '-.-.', 'd': '-..', 'e': '.', 'f': '..-.',
'g': '--.', 'h': '....', 'i': '..', 'j': '.---', 'k': '-.-', 'l': '.-..',
'm': '--', 'n': '-.', 'o': '---', 'p': '.--.', 'q': '--.-', 'r': '.-.',
's': '...', 't': '-', 'u': '..-', 'v': '...-', 'w': '.--', 'x': '-..-',
'y': '-.--', 'z': '--..',
'0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
'5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
' ': '/'
}

MORSE_CODE_REVERSE = {v: k for k, v in MORSE_CODE_DICT.items()}

class text_tools_commands:

    def __init__(self, client):

        self.client = client

    async def cmd_define(self, message, command_args):
        term = command_args.strip()
        if not term:
            return await self.client.send_and_clean(message.channel, "define what")
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{term}"
        async with aiohttp.ClientSession() as s:
            resp = await s.get(url)
            if resp.status != 200:
                return await self.client.send_and_clean(message.channel, f"no proper definition found for {term}")
            try:
                data = await resp.json()
                if not data or len(data) == 0:
                    return await self.client.send_and_clean(message.channel, f"no proper definition found for {term}")
                entry = data[0]
                if "meanings" not in entry or not entry["meanings"]:
                    return await self.client.send_and_clean(message.channel, f"no proper definition found for {term}")
                meanings = entry["meanings"]
                if not meanings[0].get("definitions"):
                    return await self.client.send_and_clean(message.channel, f"no proper definition found for {term}")
                defs = meanings[0]["definitions"][0]
                definition = defs.get("definition", "—")
                example = defs.get("example")
                out = f"{term} {definition}"
                if example:
                    out += f"\n» {example}"
                await self.client.send_and_clean(message.channel, out)
            except Exception:
                await self.client.send_and_clean(message.channel, f"couldn't process definition for {term}")

    async def cmd_udefine(self, message, command_args):
        term = command_args.strip()
        if not term:
            return await self.client.send_and_clean(message.channel, "give me a word")
        url = f"http://api.urbandictionary.com/v0/define?term={term}"
        async with aiohttp.ClientSession() as s:
            resp = await s.get(url)
            data = await resp.json()
        lst = data.get("list", [])
        if not lst:
            return await self.client.send_and_clean(message.channel, f"no slang found for {term}")
        top = max(lst, key=lambda x: x.get("thumbs_up", 0))
        definition = top.get("definition", "").replace("[", "").replace("]", "")
        example = top.get("example", "").replace("[", "").replace("]", "")
        await self.client.send_and_clean(message.channel, f"{term} (ud) {definition}\n» {example}\n{top.get('thumbs_up',0)} | {top.get('thumbs_down',0)}")

    async def cmd_zalgo(self, message, command_args):
        text = command_args
        if not text:
            return await self.client.send_and_clean(message.channel, "zalgo what")
        corrupted = ''.join(c + ''.join(self.client.rand.choices(zalgo_up, k=self.client.rand.randint(1, 3))) for c in text)
        await self.client.send_and_clean(message.channel, corrupted)

    async def cmd_flip(self, message, command_args):
        text = command_args
        if not text:
            return await self.client.send_and_clean(message.channel, "what the flip")
        flipped = text[::-1].translate(flip_map)
        await self.client.send_and_clean(message.channel, flipped)

    async def cmd_ascii(self, message, command_args):
        text = command_args
        if not text:
            return await self.client.send_and_clean(message.channel, "ascii needs a soul to shape")

        try:
            output = figlet_format(text)
            if len(output) > 1900:
                output = output[:1900] + "..."
            await self.client.send_and_clean(message.channel, f"```{output}```")
        except Exception as e:
            await self.client.send_and_clean(message.channel, "couldn't ascii-fy that")

    async def cmd_mock(self, message, command_args):
        text = command_args
        if not text:
            return await self.client.send_and_clean(message.channel, "mock what, genius")
            return

        mocked = ''.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(text))
        await self.client.send_and_clean(message.channel, mocked)

    async def cmd_emc(self, message, command_args):
        text = command_args
        if not text:
            return await self.client.send_and_clean(message.channel, "please provide the text to encode")
        words = text.lower().split(' ')
        encoded_words = []
        for word in words:
            encoded_chars = []
            for char in word:
                morse = MORSE_CODE_DICT.get(char, '?')
                encoded_chars.append(morse)
            if encoded_chars:
                encoded_words.append(" ".join(encoded_chars))
        result = " / ".join(encoded_words)
        await self.client.send_and_clean(message.channel, f"```{result}```")

    async def cmd_dmc(self, message, command_args):
        code = command_args
        if not code:
            return await self.client.send_and_clean(message.channel, "please provide the morse code to decode")
        words = code.split(" / ")
        decoded_words = []
        for word in words:
            chars = word.split()
            decoded_chars = [MORSE_CODE_REVERSE.get(c, '?') for c in chars]
            decoded_words.append("".join(decoded_chars))
        await self.client.send_and_clean(message.channel, " ".join(decoded_words))

    async def cmd_base64(self, message, command_args):
        content = message.content.strip()
        args = content[len("nux base64"):].strip().split(maxsplit=1)

        if len(args) < 2 or args[0] not in ["encode", "decode"]:
            return await self.client.send_and_clean(message.channel, "usage nux base64 <encode|decode> <text>")

        action = args[0]
        text = args[1]

        try:
            if action == "encode":
                result = base64.b64encode(text.encode()).decode()
            else:
                result = base64.b64decode(text.encode()).decode()

            await self.client.send_and_clean(message.channel, result)
        except Exception:
            await self.client.send_and_clean(message.channel, "invalid input")

    async def cmd_hash(self, message, command_args):
        content = message.content.strip()
        args = content[len("nux hash"):].strip().split(maxsplit=1)

        if len(args) < 1:
            return await self.client.send_and_clean(message.channel, "usage nux hash <algorithm> <text>\n\n-# supported algorithms: md5, sha1, sha256, sha512. type \"nux hash help\" for the help page.")

        algorithm = args[0].lower()

        if algorithm == "help":
            return await self.client.send_and_clean(message.channel, "hashes **cannot** be reversed, so you cannot get the original text back. however, if you run it again (e.g. ```nux hash md5 test```) it will always return the same hash, but that's the only thing you could do.\n\n-# test in md5 hash is \"098f6bcd4621d373cade4e832627b4f6\" by the way.")

        if len(args) < 2:
            return await self.client.send_and_clean(message.channel, "usage nux hash <algorithm> <text>\n\n-# supported algorithms: md5, sha1, sha256, sha512. type \"nux hash help\" for the help page.")

        text = args[1]

        try:
            if algorithm == "md5":
                hashed = hashlib.md5(text.encode()).hexdigest()
            elif algorithm == "sha1":
                hashed = hashlib.sha1(text.encode()).hexdigest()
            elif algorithm == "sha256":
                hashed = hashlib.sha256(text.encode()).hexdigest()
            elif algorithm == "sha512":
                hashed = hashlib.sha512(text.encode()).hexdigest()
            else:
                return await self.client.send_and_clean(message.channel, "unsupported algorithm use md5, sha1, sha256, or sha512")

            await self.client.send_and_clean(message.channel, f"hash ({algorithm}) {hashed}")
        except Exception as e:
            await self.client.send_and_clean(message.channel, f"hashing failed {e}")

    async def cmd_wordcount(self, message, command_args):
        text = command_args
        if not text:
            return await self.client.send_and_clean(message.channel, "usage nux wordcount <text>")

        words = text.split()
        await self.client.send_and_clean(message.channel, f"word count {len(words)}")

    async def cmd_charfreq(self, message, command_args):
        text = command_args
        if not text:
            return await self.client.send_and_clean(message.channel, "usage nux charfreq <text>")

        freq = {}
        for char in text:
            freq[char] = freq.get(char, 0) + 1

        freq_str = "\n".join([f"'{c}': {count}" for c, count in sorted(freq.items())])
        await self.client.send_and_clean(message.channel, f"character frequency\n```{freq_str}```")

    async def cmd_anagram(self, message, command_args):
        text = command_args.strip()
        if not text:
            return await self.client.send_and_clean(message.channel, "usage nux anagram <text>")
        words = text.split()
        anagram_words = []
        for word in words:
            char_list = list(word)
            self.client.rand.shuffle(char_list)
            anagram_words.append(''.join(char_list))
        result = ' '.join(anagram_words)
        await self.client.send_and_clean(message.channel, result)

    async def cmd_uuid(self, message, command_args=""):
        generated_uuid = str(uuid.uuid4())
        await self.client.send_and_clean(message.channel, f"generated uuid: {generated_uuid}")

    async def cmd_piglatin(self, message, command_args):
        content = message.content.strip()
        args = content[len("nux piglatin"):].strip().split(maxsplit=1)

        if len(args) < 1 or args[0] not in ["encode", "decode"]:
            return await self.client.send_and_clean(message.channel, "usage nux piglatin <encode|decode> <text>")

        action = args[0]
        text = args[1] if len(args) > 1 else ""
        
        if not text:
            return await self.client.send_and_clean(message.channel, "usage nux piglatin <encode|decode> <text>")

        if action == "encode":
            def piglatinify(word):
                vowels = "aeiouAEIOU"
                if word[0] in vowels:
                    return word + "yay"
                else:
                    for i, letter in enumerate(word):
                        if letter in vowels:
                            return word[i:] + word[:i] + "ay"
                    return word + "ay"
            
            result = ' '.join([piglatinify(word) for word in text.split()])
        else:
            def unpiglatinify(word):
                if word.endswith("yay"):
                    return word[:-3]
                elif word.endswith("ay"):
                    word = word[:-2]
                    for i in range(len(word)):
                        rotated = word[i:] + word[:i]
                        vowels = "aeiouAEIOU"
                        if rotated[0] in vowels or i == len(word) - 1:
                            return rotated
                    return word
                return word
            
            result = ' '.join([unpiglatinify(word) for word in text.split()])
        
        await self.client.send_and_clean(message.channel, result)

    async def cmd_rot13(self, message, command_args):
        content = message.content.strip()
        args = content[len("nux rot"):].strip().split(maxsplit=1)

        if len(args) < 1 or args[0] not in ["encode", "decode"]:
            return await self.client.send_and_clean(message.channel, "usage nux rot <encode|decode> <text>")

        action = args[0]
        text = args[1] if len(args) > 1 else ""
        
        if not text:
            return await self.client.send_and_clean(message.channel, "usage nux rot <encode|decode> <text>")

        rot13_map = str.maketrans(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "nopqrstuvwxyzabcdefghijklmNOPQRSTUVWXYZABCDEFGHIJKLM"
        )
        
        result = text.translate(rot13_map)
        await self.client.send_and_clean(message.channel, result)

    async def cmd_rvowel(self, message, command_args):
        text = command_args.strip()
        if not text:
            return await self.client.send_and_clean(message.channel, "usage nux rvowel <text>")

        vowels = "aeiouAEIOU"
        result = ''.join([char for char in text.lower() if char not in vowels])
        await self.client.send_and_clean(message.channel, result)

    async def cmd_vapor(self, message, command_args):
        text = command_args.strip()
        if not text:
            return await self.client.send_and_clean(message.channel, "provide text to vaporwave")
        vaporwave = "".join(chr(0xFF00 + ord(c) - 0x20) if 0x20 <= ord(c) <= 0x7E else c for c in text)
        await self.client.send_and_clean(message.channel, vaporwave)

    async def cmd_typo(self, message, command_args):
        text = command_args.strip()
        if not text:
            return await self.client.send_and_clean(message.channel, "provide text to typo")
        typo_map = {'a': 'q', 'e': 'w', 'i': 'o', 'o': 'p', 'u': 'y', 't': 'r', 'y': 't'}
        result = list(text)
        for i in range(len(result)):
            if self.client.rand.random() < 0.15 and result[i].lower() in typo_map:
                result[i] = typo_map[result[i].lower()]
        await self.client.send_and_clean(message.channel, ''.join(result))

    async def cmd_bypass(self, message, command_args):
        text = command_args.strip()
        if not text:
            return await self.client.send_and_clean(message.channel, "provide text to bypass")
        bypass_chars = ['\u200b', '\u200c', '\u200d', '\ufeff']
        result = ''.join(c + self.client.rand.choice(bypass_chars) for c in text)
        await self.client.send_and_clean(message.channel, result)

    async def cmd_echoplus(self, message, command_args):
        parts = command_args.strip().split(maxsplit=1)
        if len(parts) < 2:
            return await self.client.send_and_clean(message.channel, "usage: nux echoplus <number> <text>")
        try:
            count = int(parts[0])
            if count < 1 or count > 20:
                return await self.client.send_and_clean(message.channel, "number must be between 1 and 20")
            text = parts[1]
            for _ in range(count):
                await message.channel.send(text)
                await asyncio.sleep(1.2)
        except ValueError:
            await self.client.send_and_clean(message.channel, "first argument must be a number")

    async def cmd_uwu(self, message, command_args):
        text = command_args.strip()
        if not text:
            return await self.client.send_and_clean(message.channel, "pwease pwovide text to uwu-ify")
        uwu = text.replace('r', 'w').replace('l', 'w').replace('R', 'W').replace('L', 'W')
        uwu = uwu.replace('n', 'ny').replace('N', 'NY')
        await self.client.send_and_clean(message.channel, uwu + " uwu")

    async def cmd_shakespeare(self, message, command_args):
        text = command_args.strip()
        if not text:
            return await self.client.send_and_clean(message.channel, "provide text to shakespearify")
        old_map = {'you': 'thou', 'your': 'thy', 'are': 'art', 'is': 'be', 'yes': 'aye', 'no': 'nay'}
        words = text.split()
        result = [old_map.get(w.lower(), w) for w in words]
        await self.client.send_and_clean(message.channel, ' '.join(result))

    async def cmd_bottomsup(self, message, command_args):
        text = command_args.strip()
        if not text:
            return await self.client.send_and_clean(message.channel, "provide text to reverse")
        words = text.split()
        await self.client.send_and_clean(message.channel, ' '.join(reversed(words)))

    async def cmd_t9(self, message, command_args):
        text = command_args.strip().lower()
        if not text:
            return await self.client.send_and_clean(message.channel, "provide text to convert")
        t9_map = {'abc': '2', 'def': '3', 'ghi': '4', 'jkl': '5', 'mno': '6', 'pqrs': '7', 'tuv': '8', 'wxyz': '9', ' ': '0'}
        result = []
        for char in text:
            for keys, digit in t9_map.items():
                if char in keys:
                    result.append(digit * (keys.index(char) + 1))
                    break
        await self.client.send_and_clean(message.channel, '-'.join(result))

    async def cmd_smokeymirror(self, message, command_args):
        text = command_args.strip()
        if not text:
            return await self.client.send_and_clean(message.channel, "provide text to distort")
        distort_chars = ['~', '≈', '≋', '∼', '⋍', '≃']
        result = []
        for i, char in enumerate(text):
            distortion_level = int((i / len(text)) * len(distort_chars))
            if distortion_level > 0 and self.client.rand.random() < (distortion_level / len(distort_chars)):
                result.append(self.client.rand.choice(distort_chars[:distortion_level]))
            else:
                result.append(char)
        await self.client.send_and_clean(message.channel, ''.join(result))

def setup(client):
    instance = text_tools_commands(client)
    help_dict = {
        "text tools": {
            "nux define": "official dictionary definition, usage: nux define <word>",
            "nux udefine": "urban dictionary definition, usage: nux udefine <word>",
            "nux zalgo": "turn text into glitched text, usage: nux zalgo <text>",
            "nux flip": "flip your text upside-down, usage: nux flip <text>",
            "nux ascii": "turn your text into ascii art, usage: nux ascii <text>",
            "nux mock": "alternate your text casing, usage: nux mock <text>",
            "nux emc": "encode morse code, usage: nux emc <text>",
            "nux dmc": "decode morse code, usage: nux dmc <text>",
            "nux base64": "encode or decode base64, usage: nux base64 <encode|decode> <text>",
            "nux rot": "converts text into rot13, usage: nux rot <encode|decode> <text>",
            "nux rvowel": "removes vowels from the given text, usage: nux rvowel <text>",
            "nux piglatin": "converts text into piglatin, usage: nux piglatin <encode|decode> <text>",
            "nux hash": "hashes text using md5, sha1, sha256, or sha512, usage: nux hash <algorithm> <text>",
            "nux wordcount": "counts words in the provided text, usage: nux wordcount <text>",
            "nux charfreq": "displays the frequency of each character in the text, usage: nux charfreq <text>",
            "nux anagram": "rearranges letters to create an anagram, usage: nux anagram <text>",
            "nux uuid": "generates a unique identifier, usage: nux uuid",
            "nux vapor": "convert text to vaporwave aesthetic, usage: nux vapor <text>",
            "nux typo": "generate believable typos in text, usage: nux typo <text>",
            "nux bypass": "corrupt text with unicode to bypass filters, usage: nux bypass <text>",
            "nux echoplus": "echo text multiple times, usage: nux echoplus <number> <text>",
            "nux uwu": "convert text to uwu-speak, usage: nux uwu <text>",
            "nux shakespeare": "convert to old english style, usage: nux shakespeare <text>",
            "nux bottomsup": "reverse word order, usage: nux bottomsup <text>",
            "nux t9": "convert to phone keypad input, usage: nux t9 <text>",
            "nux smokeymirror": "progressively distort text, usage: nux smokeymirror <text>",
        }
    }
    return instance, help_dict
