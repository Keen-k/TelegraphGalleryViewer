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
    for string in range(len(srcs)):
        srcs[string] = srcs[string][5:-2]
        if srcs[string][0] == '/':
            srcs[string] = "https://telegra.ph" + srcs[string]
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
    if len(os.listdir(slides_dir)) == 0:
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
    images = os.listdir(slides_dir)
    images.sort()
    print(images)

    imgs = []
    # for image in range(len(images)):
    #     imgs.append(ImageTk.PhotoImage(Image.open("temp\\{}".format(images[image]))))
    for image in range(len(images)):
        im = Image.open(os.path.join(slides_dir, images[image]))
        w, h = im.size
        percent = root.winfo_screenheight() / h
        imgs.append(ImageTk.PhotoImage(im.resize((int(w * percent), int(h * percent)))))

    label = Label(root, image=imgs[0])
    label.pack()

    print(len(imgs))

    def moveforward(event):
        global page_number
        page_number = page_number + 1
        print(page_number)
        if page_number == len(imgs):
            root.destroy()
            page_number = 0
            return 0
        root.title('{:02d}/{:02d}'.format(page_number + 1, len(imgs)))
        label.config(image=imgs[page_number])

    def moveback(event):
        global page_number
        page_number = page_number - 1
        print(page_number)
        if page_number < 0:
            root.destroy()
            page_number = 0
            return 0
        root.title('{:02d}/{:02d}'.format(page_number + 1, len(imgs)))
        label.config(image=imgs[page_number])

    def close(event):
        root.destroy()
        global page_number
        page_number = 0
        return 0

    root.bind("<Escape>", close)
    root.bind("<Right>", moveforward)
    root.bind("<Left>", moveback)

    root.mainloop()


def main():
    global page_number
    page_number = 0
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
