import asyncio
import os
import re

import aiohttp
import pyperclip
import requests
from plyer import notification


# TODO Refactor get_all_images_from_url() it seems too long and conplex
async def get_all_images_from_url(telegraph_url: str, temp_dir: str) -> None:
    if len(temp_dir_list := os.listdir(temp_dir)) > 0:
        for file in temp_dir_list:
            os.remove(os.path.join(temp_dir, file))
    print(telegraph_url)
    try:
        html = requests.get(telegraph_url)
    except requests.exceptions.InvalidSchema as e:
        print(e)
        return None
    except requests.exceptions.MissingSchema as e:
        print(e)
        return None
    finally:
        pyperclip.copy('')
    notification.notify(
        title='Telegra.ph Gallery Viewer',
        message='Telegra.ph URL detected. Downloading gallery.',
        app_icon=None,  # e.g. 'C:\\icon_32x32.ico'
        timeout=3,  # seconds
    )
    articles = re.findall('<article.*</article>', html.text)
    print(articles)
    srcs = re.findall('src=.*?>', articles[0])
    print(srcs)
    for string_index in range(len(srcs)):
        srcs[string_index] = srcs[string_index][5:-2]
        if srcs[string_index].startswith('/'):
            srcs[string_index] = "https://telegra.ph" + srcs[string_index]

        # TODO Write module with rules.

        if 'mult.club' in srcs[string_index]:
            srcs[string_index] = srcs[string_index].replace('club', 'press')
    print(srcs)
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            *[get_image(source_index, source_url, temp_dir, session) for
              source_index, source_url in enumerate(srcs)]
        )
    return None


async def get_image(
        src_index: int,
        src_string: str,
        gallery_dir: str,
        session: aiohttp.ClientSession,
        ) -> None:
    print(src_index, end=' ')
    file = open(os.path.join(gallery_dir,
                             str('{:05d}').format(src_index + 1) +
                             str(re.search('[.].*?$', src_string[-6:]).group())
                             ),
                'wb',
                )
    try:
        async with session.get(src_string) as image_source:
            content = await image_source.content.read()
            file.write(content)
    except Exception as e:
        print(e)
        file.close()
        os.remove(file.name)
        return None
    file.close()
    print(src_index, end=' ')
    return None
