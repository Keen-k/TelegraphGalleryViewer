import pyperclip
import requests
import os
from tkinter import *
from PIL import Image
from PIL import ImageTk
import re
import threading
from plyer import notification


def get_all_images_from_url(telegraphurl, temp_dir):
    if len(temp_dir_list := os.listdir(temp_dir)) > 0:
        for file in temp_dir_list:
            os.remove(os.path.join(temp_dir, file))
    print(telegraphurl)
    try:
        html = requests.get(telegraphurl)
    except requests.exceptions.InvalidSchema as e:
        print(e)
        return 1
    except requests.exceptions.MissingSchema as e:
        print(e)
        return 1
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
        if srcs[string_index][0] == '/':
            srcs[string_index] = "https://telegra.ph" + srcs[string_index]

        # TODO Write module with rules.

        if 'mult.club' in srcs[string_index]:
            srcs[string_index] = srcs[string_index].replace('club', 'press')
    print(srcs)
    for src in range(len(srcs)):
        thread = threading.Thread(target=get_image(src, srcs[src], temp_dir))
        thread.start()


def get_image(src_index, src_string, gallery_dir):
    file = open(os.path.join(gallery_dir,
                             str('{:05d}').format(src_index + 1) +
                             str(re.search('[.].*?$', src_string[-6:], ).group())), 'wb')
    try:
        file.write(requests.get(src_string, timeout=3).content)
    except Exception as e:
        print(e)
        file.close()
        os.remove(file.name)
    file.close()


def play_slideshow(slides_dir):
    if len(images := os.listdir(slides_dir)) == 0:
        print('There is nothing to see now.')
        notification.notify(
            title='Telegra.ph Gallery Viewer',
            message='There is nothing to see now.',
            app_icon=None,  # e.g. 'C:\\icon_32x32.ico'
            timeout=3,  # seconds
        )
        return 0
    root = Tk()
    root.attributes('-fullscreen', True)
    root.configure(bg='black')
    images.sort()
    print(images)
    page_number = 0

    resized_images = []

    for image_index in range(len(images)):
        image = Image.open(os.path.join(slides_dir, images[image_index]))
        image_width, image_height = image.size
        percent = root.winfo_screenheight() / image_height
        resized_images.append(ImageTk.PhotoImage(image.resize((int(image_width * percent), int(image_height * percent)))))

    root.title('{:02d}/{:02d}'.format(1, len(resized_images)))
    label = Label(root, image=resized_images[0])
    label.pack()

    print(len(resized_images))

    def close_viewer(event):
        root.destroy()

    def show_next_page(event):
        nonlocal page_number
        page_number += 1
        print(page_number)
        if page_number == len(resized_images):
            close_viewer(None)
            return
        root.title('{:02d}/{:02d}'.format(page_number + 1, len(resized_images)))
        label.config(image=resized_images[page_number])

    def show_previous_page(event):
        nonlocal page_number
        page_number -= 1
        print(page_number)
        if page_number < 0:
            close_viewer(None)
            return
        root.title('{:02d}/{:02d}'.format(page_number + 1, len(resized_images)))
        label.config(image=resized_images[page_number])

    root.bind("<Escape>", close_viewer)
    root.bind("<KeyPress-q>", close_viewer)
    root.bind("<Right>", show_next_page)
    root.bind("<Left>", show_previous_page)

    root.mainloop()


def main():
    pyperclip.copy('')
    temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    while True:
        url = pyperclip.waitForNewPaste()
        print('Wait for telegra.ph URL in clipboard.')
        if 'telegra' in url:
            get_all_images_from_url(url, temp_dir)
            play_slideshow(temp_dir)
        else:
            print('Clipboard content changed, but no URL in there.')


if __name__ == '__main__':
    main()
