import asyncio
import os

import pyperclip

from downloader import get_all_images_from_url
from window import play_slideshow


async def main():
    pyperclip.copy('')
    temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    while True:
        url = pyperclip.waitForNewPaste()
        print('Wait for telegra.ph URL in clipboard.')
        if 'telegra' in url:
            await get_all_images_from_url(url, temp_dir)
            play_slideshow(temp_dir)
        else:
            print('Clipboard content changed, but no URL in there.')


if __name__ == '__main__':
    asyncio.run(main())
