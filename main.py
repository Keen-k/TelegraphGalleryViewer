import asyncio
import os
from tkinter import *
import re

import aiohttp
import pyperclip
import requests
from PIL import Image
from PIL import ImageTk
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


def play_slideshow(slides_dir: str) -> None:
    if len(images := os.listdir(slides_dir)) == 0:
        print('There is nothing to see now.')
        notification.notify(
            title='Telegra.ph Gallery Viewer',
            message='There is nothing to see now.',
            app_icon=None,  # e.g. 'C:\\icon_32x32.ico'
            timeout=3,  # seconds
        )
        return None

    root = Tk()
    root.attributes('-fullscreen', True)
    root.configure(bg='black')

    images.sort()
    print(images)
    root.page_number = 0

    def resize_image(directory: str, image: str) -> ImageTk.PhotoImage:
        image = Image.open(os.path.join(directory, image))
        image_width, image_height = image.size
        print(root.winfo_height())
        # insignificant error in size may occur
        resize_coefficient = root.winfo_screenheight() / image_height
        image_resized = image.resize(
            (int(image_width * resize_coefficient),
             int(image_height * resize_coefficient),
             )
        )
        tk_image = ImageTk.PhotoImage(image_resized)
        return tk_image

    root.title('{:02d}/{:02d}'.format(1, len(images)))
    root.resized_image = resize_image(slides_dir, images[root.page_number])
    label = Label(root, image=root.resized_image)
    label.pack()

    print(len(images))

    def close_viewer(event) -> None:
        root.destroy()
        return None

    def show_next_page(event) -> None:
        root.page_number += 1
        print(root.page_number)
        if root.page_number == len(images):
            close_viewer(None)
            return None
        root.title('{:02d}/{:02d}'.format(root.page_number + 1, len(images)))
        root.resized_image = resize_image(slides_dir, images[root.page_number])
        label.config(image=root.resized_image)
        return None

    def show_previous_page(event) -> None:
        root.page_number -= 1
        print(root.page_number)
        if root.page_number < 0:
            close_viewer(None)
            return None
        root.title('{:02d}/{:02d}'.format(root.page_number + 1, len(images)))
        root.resized_image = resize_image(slides_dir, images[root.page_number])
        label.config(image=root.resized_image)
        return None

    root.bind("<Escape>", close_viewer)
    root.bind("<KeyPress-q>", close_viewer)
    root.bind("<Right>", show_next_page)
    root.bind("<Left>", show_previous_page)

    root.mainloop()
    return None


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
