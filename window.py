import os
from tkinter import Tk, Label

from PIL import ImageTk, Image
from plyer import notification


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
        image = Image.  open(os.path.join(directory, image))
        image_width, image_height = image.size
        # insignificant error in size may occur
        resize_coefficient = root.winfo_screenheight() / image_height
        image_resized = image.resize(
            (int(image_width * resize_coefficient),
             int(image_height * resize_coefficient),
             )
        )
        image.close()
        return ImageTk.PhotoImage(image_resized)

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
