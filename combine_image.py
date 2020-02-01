import os
from PIL import Image
from util import base_directory, get_screen_aspect_ratio, average_pixel_color, do_gradient, print_list
from util import RIGHT, LEFT
from reddit_image import RedditImage

urls = ['https://i.redd.it/d3rcv2shyid41.png',
        'https://i.redd.it/50bw2q84bgd41.jpg',
        'https://i.redd.it/3sf6lkuvwid41.png']



# another idea is to always add a kind of picture frame around all photos that are combined (prob not going to do)
# have program return a non-zero error code when failure occurs (only do this when shitty internet)
# add logging of program so that it logs its output / errors
# if error occurs have default image to set as desktop background (or take from weekly in this case)
# idea to possibly combine the weekly portrait photos together into landscape photos since not all are being used right now.
# Fix up file names and project setup
# add command line argument to rerun daily ignoring the last one that was run (will need to keep track of those to be ignored)
# make better stat files in better locations.

class CombineImages:
    target_aspect = get_screen_aspect_ratio()

    def __init__(self, allImageObjects, destDirectory):
        self.allImageObjects = allImageObjects
        self.destDirectory = destDirectory
        self.selectedImages = []

    @staticmethod
    def get_good_aspect(image_objects, width, maxHeight, startIndex):
        # iterate through all image_data to find best aspect
        bestAspect = width / maxHeight
        bestArr = []

        for index in range(startIndex, len(image_objects)):
            current_image = image_objects[index]
            nextWidth = width + current_image.imageWidth
            nextHeight = max(maxHeight, current_image.imageHeight)
            new_aspect = nextWidth / nextHeight
            if CombineImages.closer_to_target(new_aspect, bestAspect):
                bestAspect = new_aspect
                bestArr = [index]
            if new_aspect <= CombineImages.target_aspect and index + 1 < len(image_objects):
                bestFound = CombineImages.get_good_aspect(image_objects, nextWidth, nextHeight, index + 1)
                if CombineImages.closer_to_target(bestFound[1], bestAspect):
                    bestAspect = bestFound[1]
                    bestArr = bestFound[0] + [index]

        return [bestArr, bestAspect]

    @staticmethod
    def closer_to_target(first, second):
        firstDiff = abs(first - CombineImages.target_aspect)
        secondDiff = abs(second - CombineImages.target_aspect)
        return firstDiff < secondDiff

    def find_images_to_combine(self):
        self.allImageObjects = sorted(self.allImageObjects, reverse=True, key=lambda x: x.imageHeight)
        height = self.allImageObjects[0].imageHeight
        bestSolution = [[], 0]
        beginIndex = 0
        index = 1
        while index < len(self.allImageObjects):
            nextHeight = self.allImageObjects[index].imageHeight
            if nextHeight < (height * 0.9):
                solution = CombineImages.get_good_aspect(self.allImageObjects[beginIndex:index], 0, 1, 0)
                if CombineImages.closer_to_target(solution[1], bestSolution[1]):
                    bestSolution = solution
                beginIndex = index
                height = nextHeight
            index += 1

        if index - 1 != beginIndex:
            sol = CombineImages.get_good_aspect(self.allImageObjects[beginIndex:index], 0, 1, 0)
            if CombineImages.closer_to_target(sol[1], bestSolution[1]):
                bestSolution = sol

        return bestSolution

    def substitute_data(self, chosen_indices):
        self.selectedImages = []
        for index in chosen_indices:
            self.selectedImages.append(self.allImageObjects[index])

    def get_max_size(self,  size_type):
        max_item = RedditImage.get_size_data(self.selectedImages[0], size_type)
        for image in self.selectedImages[1:]:
            max_item = max(max_item, RedditImage.get_size_data(image, size_type))
        return max_item

    def get_total_size(self, size_type):
        item = 0
        for image in self.selectedImages:
            item += RedditImage.get_size_data(image, size_type)
        return item

    def get_current_aspect_ratio(self):
        return self.get_total_size(RedditImage.WIDTH) / self.get_max_size(RedditImage.HEIGHT)

    def combine_images(self, final_image_path):
        width_diff = 0
        if self.get_current_aspect_ratio() > get_screen_aspect_ratio():
            # need to add more height to the image
            image_width = self.get_total_size(RedditImage.WIDTH)
            image_height = int(image_width // get_screen_aspect_ratio())
        else:
            # need to add more width to the image

            image_height = self.get_max_size(RedditImage.HEIGHT)
            combined_width = self.get_total_size(RedditImage.WIDTH)
            image_width = int(image_height * get_screen_aspect_ratio())
            width_diff = (image_width - combined_width) // (len(self.selectedImages) - 1)

        temp = Image.new("RGB", (image_width, image_height))

        print("Start Image Combining Process")
        beg_x = 0
        nextColor = None
        for pic in self.selectedImages:
            portrait = Image.open(pic.imagePath)
            if nextColor is not None:
                # make gradient for in between images
                currColor = average_pixel_color(portrait, LEFT)
                do_gradient(temp, (beg_x - width_diff, 0), (beg_x, image_height - 1), nextColor, currColor)
            nextColor = average_pixel_color(portrait, RIGHT)
            height_factor = (image_height - RedditImage.get_size_data(pic, RedditImage.HEIGHT)) // 2
            temp.paste(portrait, (beg_x, height_factor))
            beg_x += RedditImage.get_size_data(pic, RedditImage.WIDTH) + width_diff

        print("Save Resulting Image")
        temp.save(final_image_path, format="PNG")
        print("Combined Image Saved")

    def write_image_statistics(self, file_path):
        with open(file_path, "w") as f:
            for pic in self.selectedImages:
                f.write(pic.submissionUrl + "\n")

    def do_combine_landscape_process(self):
        final = os.path.join(self.destDirectory, "final.png")

        chosen_images, image_aspect = self.find_images_to_combine()
        self.substitute_data(chosen_images)

        try:
            self.combine_images(final)
        except Exception:
            print_list(self.selectedImages)
            raise

        stat_file_path = os.path.join(self.destDirectory, "tempStat.txt")
        self.write_image_statistics(stat_file_path)
        return final


if __name__ == "__main__":


    # test data
    a = [['https://i.redd.it/ew47fvqvrqd41.png', '/r/Animewallpaper/comments/evp08d/megumin_konosuba_2250x4000/', (2250, 4000)],
        ['https://i.redd.it/73k8un5iiqd41.png', '/r/Animewallpaper/comments/evo6oj/gudas_ritsuka_and_mashu_fategrand_order2250x4000/', (2250, 4000)],
        ['https://i.redd.it/e4bptn0tumd41.jpg', '/r/Animewallpaper/comments/evgp0u/kurumi_tokisawadate_a_live_2250x4000/', (2250, 4000)],
        ['https://i.redd.it/mnab4a3gbqd41.png', '/r/Animewallpaper/comments/evnonz/marnie_and_gloria_pokémon_sword_shield_2250x4000/', (2250, 4000)],
        ['https://i.redd.it/jd8g5coqqmd41.jpg', '/r/Animewallpaper/comments/evgeeq/pop_style_bunny_girloriginal_2250x4000/', (4250, 4000)],
        ['https://i.redd.it/xs3ts5c46od41.png', '/r/Animewallpaper/comments/evjmnb/sunset_original_1262x2246/', (1262, 2246)],
        ['https://i.redd.it/u3xj8s52tmd41.jpg', '/r/Animewallpaper/comments/evgkmc/chika_fujiwarakaguyasama_love_is_war_2250x4000/', (2250, 4000)]]

    ci = CombineImages(a, os.path.join(base_directory, "PictureSource"))
    ci.do_combine_landscape_process()


    exit(0)
    test = Image.new("RGB", (1000, 1000), (0, 0, 0))

    do_gradient(test, (0, 0), (1000, 1000), (117, 103, 108), (178, 156, 111))

    path = os.path.join(base_directory, "test.PNG")
    test.save(path, "PNG")


