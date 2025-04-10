import aiohttp
import requests
from urllib import parse
from functools import partial
import io
import mimetypes
import asyncio
from bs4 import BeautifulSoup

class Upload():
    def __init__(self, io_: io.BytesIO, filename: str):
        self.io_ = io_
        self.filename = filename
        pass

    def UploadFile(self, io, filename: str):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://firestorage.jp/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        params = {
            'act': 'flashupjs',
            'type': 'flash10b',
            'photo': '1',
            'talk': '1',
            'json': '1',
            'eid': '',
        }

        uploadfolder = requests.get('https://firestorage.jp/flashup.cgi', params=params, headers=headers)

        uploadid = uploadfolder.json()

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Origin': 'https://firestorage.jp',
            'Referer': 'https://firestorage.jp/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        mime_type, _ = mimetypes.guess_type(filename)

        files = [
                ('folder_id', (None, f'{uploadid["folder_id"]}')),
                ('ppass', (None, '')),
                ('dpass', (None, '')),
                ('thumbnail', (None, 'nomal')),
                ('top', (None, '1')),
                ('jqueryupload', (None, '1')),
                ('max_size', (None, '2147483648')),
                ('max_sized', (None, '2')),
                ('max_size_photo', (None, '15728640')),
                ('max_size_photod', (None, '15')),
                ('max_size_photo', (None, '150')),
                ('max_count', (None, '20')),
                ('max_count_photo', (None, '150')),
                ('jqueryupload', (None, '1')),
                ('eid', (None, '')),
                ('processid', (None, f'{uploadid["folder_id"]}')),
                ('qst', (None, 'n1=Mozilla&n2=Netscape&n3=Win32&n4=Mozilla/5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit/537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome/131.0.0.0%20Safari/537.36')),
                ('comments', (None, '')),
                ('comment', (None, '')),
                ('arc', (None, '')),
                ('zips', (None, '')),
                ('file_queue', (None, '1')),
                ('pc', (None, '1')),
                ('exp', (None, '7')),
                ('Filename', (f"{filename}", io, mime_type)),
        ]

        response = requests.post('https://server73.firestorage.jp/upload.cgi', headers=headers, files=files)

        decoded_str = parse.unquote(response.text)

        soup = BeautifulSoup(decoded_str, 'html.parser')

        download_url = soup.find('a', {'id': 'downloadlink'})['href']

        return download_url
    
    async def upload(self):
        loop = asyncio.get_event_loop()
        url = await loop.run_in_executor(None, partial(self.UploadFile, self.io_, self.filename))
        return url