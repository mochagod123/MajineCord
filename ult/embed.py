import aiohttp

class Embed():
    def __init__(self, title, desc, color = "#5440ba", url = "https://api.sharkbot.xyz/"):
        self.title = title
        self.desc = desc
        self.color = color
        self.url = url
        pass

    async def build(self):
        payload = {"title": self.title, "description": self.desc, "color": self.color, "url": self.url}

        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.sharkbot.xyz/embed/make", json=payload) as resp:
                data = await resp.json()

                embed = data['url']

                return f"[⁠︎]({embed})"