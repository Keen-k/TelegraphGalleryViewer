import pyperclip
import requests
import os
from tkinter import *
from PIL import Image
from PIL import ImageTk
import re
import threading

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
    file.write(requests.get(srcssrc).content)
    file.close()


def playSlideshow():
    if len(os.listdir(os.getcwd()+'\\temp')) == 0:
        print('There is nothing to see now.')
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

    def move(event):
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
    root.bind("<Right>", move)
    root.bind("<Left>", moveback)

    root.mainloop()


if __name__ == '__main__':
    while True:
        url = pyperclip.waitForNewPaste()
        print('Wait for telegra.ph URL in clipboard.')
        if 'telegra' in url:
            getAllImagesFromURL(url)
            playSlideshow()
        else:
            print('Clipboard content changed, but no URL in there.')
