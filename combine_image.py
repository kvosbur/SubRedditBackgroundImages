import os
from PIL import Image
from util import base_directory, get_screen_aspect_ratio, get_file_from_url, average_pixel_color, do_gradient
from util import RIGHT, LEFT

HEIGHT = 1
WIDTH = 0

urls = ['https://i.redd.it/d3rcv2shyid41.png',
        'https://i.redd.it/50bw2q84bgd41.jpg',
        'https://i.redd.it/3sf6lkuvwid41.png' ]


# have a gradient in between the photos using the edge pixel average to decide the two sides of the gradient.
# will have to do gradient calculations manually though I can use ImageDraw from pil to help the process go nicer


# another idea is to always add a kind of picture frame around all photos that are combined
# have program return a non-zero error code when failure occurs (only do this when shitty internet)
# add logging of program so that it logs its output/ errors
# if error occurs have default image to set as desktop background (or take from weekly in this case)
# idea to possibly combine the weekly portrait photos together into landscape photos since not all are being used right now.
# Fix up file names and project setup
# add command line argument to rerun daily ignoring the last one that was run (will need to keep track of those to be ignored)
# make better stat files in better locations.


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
    return get_total_size(image_data, WIDTH) / get_max_size(image_data, HEIGHT)


def combine_images(image_data, final_image_path):
    width_diff = 0
    if get_current_aspect_ratio(image_data) > get_screen_aspect_ratio():
        # need to add more height to the image
        image_width = get_total_size(image_data, WIDTH)
        image_height = int(image_width // get_screen_aspect_ratio())
    else:
        # need to add more width to the image

        image_height = get_max_size(image_data, HEIGHT)
        combined_width = get_total_size(image_data, WIDTH)
        image_width = int(image_height * get_screen_aspect_ratio())
        width_diff = (image_width - combined_width) // (len(image_data) - 1)

    temp = Image.new("RGB", (image_width, image_height))


    print("Start Image Combining Process")
    beg_x = 0
    nextColor = None
    for pic in image_data:
        n = Image.open(pic[0])
        if nextColor is not None:
            currColor = average_pixel_color(n, LEFT)
            do_gradient(temp, (beg_x - width_diff, 0), (beg_x, image_height - 1), nextColor, currColor)
        nextColor = average_pixel_color(n, RIGHT)
        height_factor = (image_height - get_size_data(pic, HEIGHT)) // 2
        temp.paste(n, (beg_x, height_factor))
        beg_x += get_size_data(pic, WIDTH) + width_diff

    print("Save Resulting Image")
    temp.save(final_image_path, format="PNG")
    print("Combined Image Saved")


target_aspect = get_screen_aspect_ratio()


def closer_to_target(first, second):
    firstDiff = abs(first - target_aspect)
    secondDiff = abs(second - target_aspect)
    return firstDiff < secondDiff


def get_good_aspect(image_data, width, maxHeight, startIndex):
    # iterate through all image_data to find best aspect
    bestAspect = width / maxHeight
    bestArr = []

    for index in range(startIndex, len(image_data)):
        current_image = image_data[index]
        nextWidth = width + get_size_data(current_image, WIDTH)
        nextHeight = max(maxHeight, get_size_data(current_image, HEIGHT))
        new_aspect = nextWidth / nextHeight
        if closer_to_target(new_aspect, bestAspect):
            bestAspect = new_aspect
            bestArr = [index]
        if new_aspect <= target_aspect and index + 1 < len(image_data):
            bestFound = get_good_aspect(image_data, nextWidth, nextHeight, index + 1)
            if closer_to_target(bestFound[1], bestAspect):
                bestAspect = bestFound[1]
                bestArr = bestFound[0] + [index]

    return [bestArr, bestAspect]


def find_images_to_combine(image_data):
    ids = sorted(image_data, reverse=True, key=lambda x: x[-1][1])
    height = get_size_data(ids[0], HEIGHT)
    bestSolution = [[], 0]
    beginIndex = 0
    index = 1
    while index < len(ids):
        nextHeight = get_size_data(ids[index], HEIGHT)
        if nextHeight < (height * 0.8):
            solution = get_good_aspect(ids[beginIndex:index], 0, 1, 0)
            if closer_to_target(solution[1], bestSolution[1]):
                bestSolution = solution
            beginIndex = index
            height = nextHeight
        index += 1

    if index - 1 != beginIndex:
        sol = get_good_aspect(ids[beginIndex:index], 0, 1, 0)
        if closer_to_target(solution[1], bestSolution[1]):
            bestSolution = solution
        print(sol)

    return bestSolution


def substitute_data(chosen_indices, image_data, dest_directory):
    final_data = []
    for index in chosen_indices:
        temp = get_file_from_url(dest_directory, "image" + str(index), image_data[index][0], check_correct_aspect=False)
        temp = list(temp)
        temp[1] = image_data[index][0]
        final_data.append(temp)
    return final_data


def remove_image_files(image_data):
    for pic in image_data:
        os.remove(pic[0])


def write_image_statistics(image_data, file_path):
    with open(file_path, "w") as f:
        for pic in image_data:
            f.write(pic[1] + "\n")



def do_combine_landscape_process(image_data):
    dest_directory = os.path.join(base_directory, "PictureSource")
    final = os.path.join(dest_directory, "final.png")

    chosen_images, image_aspect = find_images_to_combine(image_data)
    final_data = substitute_data(chosen_images, image_data, dest_directory)

    combine_images(final_data, final)
    remove_image_files(final_data)

    stat_file_path = os.path.join(dest_directory, "tempStat.txt")
    write_image_statistics(final_data, stat_file_path)





if __name__ == "__main__":


    # test data
    a = [['https://i.redd.it/ew47fvqvrqd41.png', '/r/Animewallpaper/comments/evp08d/megumin_konosuba_2250x4000/', (2250, 4000)],
        ['https://i.redd.it/73k8un5iiqd41.png', '/r/Animewallpaper/comments/evo6oj/gudas_ritsuka_and_mashu_fategrand_order2250x4000/', (2250, 4000)],
        ['https://i.redd.it/e4bptn0tumd41.jpg', '/r/Animewallpaper/comments/evgp0u/kurumi_tokisawadate_a_live_2250x4000/', (2250, 4000)],
        ['https://i.redd.it/mnab4a3gbqd41.png', '/r/Animewallpaper/comments/evnonz/marnie_and_gloria_pokémon_sword_shield_2250x4000/', (2250, 4000)],
        ['https://i.redd.it/jd8g5coqqmd41.jpg', '/r/Animewallpaper/comments/evgeeq/pop_style_bunny_girloriginal_2250x4000/', (4250, 4000)],
        ['https://i.redd.it/xs3ts5c46od41.png', '/r/Animewallpaper/comments/evjmnb/sunset_original_1262x2246/', (1262, 2246)],
        ['https://i.redd.it/u3xj8s52tmd41.jpg', '/r/Animewallpaper/comments/evgkmc/chika_fujiwarakaguyasama_love_is_war_2250x4000/', (2250, 4000)]]

    do_combine_landscape_process(a)

    exit(0)
    test = Image.new("RGB", (1000, 1000), (0, 0, 0))

    do_gradient(test, (0, 0), (1000, 1000), (117, 103, 108), (178, 156, 111))

    path = os.path.join(base_directory, "test.PNG")
    test.save(path, "PNG")


