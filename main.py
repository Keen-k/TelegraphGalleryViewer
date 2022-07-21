import pyperclip
import requests
import os
from tkinter import *
from PIL import Image
from PIL import ImageTk
import re
import threading
from plyer import notification

x = 0


def getAllImagesFromURL(url):
    if not os.path.exists(os.getcwd() + '\\temp'):
        os.mkdir('temp')
    if len(os.listdir(os.getcwd()+'\\temp')) > 0:
        for file in os.listdir(os.getcwd()+'\\temp'):
            os.remove(os.getcwd() + '\\temp\\' + file)
    print(url)
    try:
        html = requests.get(url)
    except requests.exceptions.InvalidSchema as e:
        print(e)
        return 1
    except requests.exceptions.MissingSchema as e:
        print(e)
        return 1
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
        thread = threading.Thread(target=getImage(src, srcs[src]))
        thread.start()


def getImage(src, srcssrc):
    file = open(os.getcwd() + '\\temp\\' + str('{:02d}').format(src+1) +
                str(re.search('[.].*?$', srcssrc[-6:], ).group()), 'wb')
    try:
        file.write(requests.get(srcssrc).content)
    except requests.exceptions.SSLError as e:
        print(e)
        file.close()
        os.remove(file.name)
    file.close()


def playSlideshow():
    if len(os.listdir(os.getcwd()+'\\temp')) == 0:
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
    images = os.listdir(os.getcwd()+'\\temp')
    print(images)

    imgs = []
    # for image in range(len(images)):
    #     imgs.append(ImageTk.PhotoImage(Image.open("temp\\{}".format(images[image]))))
    for image in range(len(images)):
        im = Image.open("temp\\{}".format(images[image]))
        w, h = im.size
        percent = root.winfo_screenheight() / h
        imgs.append(ImageTk.PhotoImage(im.resize((int(w * percent), int(h * percent)))))

    l = Label(root, image=imgs[0])
    l.pack()

    print(len(imgs))

    def moveforward(event):
        global x
        x = x+1
        print(x)
        if x == len(imgs):
            root.destroy()
            x = 0
            return 0
        root.title('{:02d}/{:02d}'.format(x+1, len(imgs)))
        l.config(image=imgs[x])

    def moveback(event):
        global x
        x = x-1
        print(x)
        if x < 0:
            root.destroy()
            x = 0
            return 0
        root.title('{:02d}/{:02d}'.format(x+1, len(imgs)))
        l.config(image=imgs[x])

    def close(event):
        root.destroy()
        global x
        x = 0
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
