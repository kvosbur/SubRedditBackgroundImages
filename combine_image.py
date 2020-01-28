from reddit_attempt import base_directory, get_file_from_url, get_screen_size, get_screen_aspect_ratio
import os
from PIL import Image

HEIGHT = 1
WIDTH = 0

urls = ['https://i.redd.it/d3rcv2shyid41.png',
        'https://i.redd.it/50bw2q84bgd41.jpg',
        'https://i.redd.it/3sf6lkuvwid41.png',
        'https://i.redd.it/ocycpx6j5gd41.jpg']


def get_size_data(single_image_data, index):
    return single_image_data[2][index]


def get_max_size(image_data, size_type):
    max_item = get_size_data(image_data[0], size_type)
    for image in image_data[1:]:
        max_item = max(max_item, get_size_data(image, size_type))
    return max_item

def get_total_size(image_data, size_type):
    item = 0
    for image in image_data:
        item += get_size_data(image, size_type)
    return item


def get_current_aspect_ratio(image_data):
    return get_total_size(image_data, WIDTH) / get_total_size(image_data, HEIGHT)


def combine_images(image_data, final_image_path):
    width_diff = 0
    if get_current_aspect_ratio(image_data) > get_screen_aspect_ratio():
        # need to add more height to the image
        image_width = get_total_size(image_data, WIDTH)
        max_height = get_max_size(image_data, HEIGHT)
        image_height = int(image_width * get_screen_aspect_ratio())
        print("add height")
    else:
        # need to add more width to the image
        print("add width")
        image_height = get_max_size(image_data, HEIGHT)
        combined_width = get_total_size(image_data, WIDTH)
        image_width = int(image_height * get_screen_aspect_ratio())
        width_diff = (image_width - combined_width) // (len(image_data) - 1)

    temp = Image.new("RGB", (image_width, image_height))


    print("Start Image Combining Process")
    beg_x = 0
    for pic in info:
        n = Image.open(pic[0])
        height_factor = (image_height - get_size_data(pic, HEIGHT)) // 2
        print("height_fac", height_factor)
        temp.paste(n, (beg_x, height_factor))
        beg_x += get_size_data(pic, WIDTH) + width_diff
        print(beg_x)

    print("Save Resulting Image")
    temp.save(final_image_path, format="PNG")
    print("Combined Image Saved")

if __name__ == "__main__":

    dest_directory = os.path.join(base_directory, "PictureSource")
    info = []
    i = 0
    for url in urls:
        info.append(get_file_from_url(dest_directory, "image" + str(i), url, check_correct_aspect=False))
        i+= 1

    print(info)
    final = os.path.join(dest_directory, "final.png")

    combine_images(info, final)


