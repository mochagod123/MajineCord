import aiohttp
import json

class YTDL():
    def __init__(self, url: str):
        self.url = url
        pass

    async def build(self):
        async with aiohttp.ClientSession() as session:
            headers = {
                'accept': '*/*',
                'accept-language': 'ja,en-US;q=0.9,en;q=0.8',
                'content-type': 'text/plain;charset=UTF-8',
                'origin': 'https://transkriptor.com',
                'priority': 'u=1, i',
                'referer': 'https://transkriptor.com/',
                'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'cross-site',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            }

            data = '{"url":"' + self.url +'","app":"transkriptor","is_only_download":true}'
            async with session.post("https://oo6o8y6la6.execute-api.eu-central-1.amazonaws.com/default/Upload-DownloadYoutubeLandingPage", headers=headers, data=data) as resp:
                try:
                    response_text = await resp.text()
                    url_data = json.loads(response_text)
                    return url_data["download_url"]
                except json.JSONDecodeError as e:
                    print(f"JSON デコードエラー: {e}")
                    print(f"レスポンス内容: {response_text}")
                    return None
                except KeyError as e:
                    print(f"キーエラー: '{e}' がレスポンスにありませんでした。")
                    print(f"レスポンス内容: {response_text}")
                    return None