import os
from PIL import Image
from util import base_directory, get_screen_aspect_ratio, average_pixel_color, do_gradient, print_list
from util import RIGHT, LEFT, readConfigFile
from reddit_image import RedditImage

urls = ['https://i.redd.it/d3rcv2shyid41.png',
        'https://i.redd.it/50bw2q84bgd41.jpg',
        'https://i.redd.it/3sf6lkuvwid41.png']


class CombineImages:
    target_aspect = get_screen_aspect_ratio()

    def __init__(self, allImageObjects, destDirectory):
        self.allImageObjects = allImageObjects
        self.destDirectory = destDirectory
        config = readConfigFile()
        general = config["GENERAL"]
        self.allowedAspectDiff = general.getfloat("ALLOWED_ASPECT_DIFF")
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

    def acceptable_difference(self, givenAspect):
        diff = abs(givenAspect - CombineImages.target_aspect)
        if diff < self.allowedAspectDiff:
            return True
        else:
            return False

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

                # fix issue that came up that solution gives slice index and not overall list index
                for indexA in range(len(solution[0])):
                    solution[0][indexA] += beginIndex
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

        # update list of image objects to possibly be used for further combinations
        temp = sorted(chosen_indices, reverse=True)
        for index in temp:
            del self.allImageObjects[index]

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
        temp.save(final_image_path, format="JPEG")
        print("Combined Image Saved")

    def write_image_statistics(self, file_path):
        with open(file_path, "w") as f:
            for pic in self.selectedImages:
                f.write(pic.submissionUrl + "\n")

    def do_combine_landscape_process(self, dest_file_name="final.jpg"):
        final = os.path.join(self.destDirectory, dest_file_name)

        chosen_images, image_aspect = self.find_images_to_combine()
        self.substitute_data(chosen_images)
        if not self.acceptable_difference(image_aspect):
            return ""

        try:
            self.combine_images(final)
        except Exception:
            print_list(self.selectedImages)
            raise

        stat_file_path = os.path.join(self.destDirectory, "tempStat.txt")
        self.write_image_statistics(stat_file_path)
        return final

    def iterate_combine_landscape(self):
        iterate = 0
        print("start Combining")
        while len(self.allImageObjects) > 0:
            b = self.do_combine_landscape_process(dest_file_name="final" + str(iterate) + ".jpg")
            if b == "":
                # this means that there isn't a good match now, which means that no
                break
            print(b)
            iterate += 1


if __name__ == "__main__":


    # test data
    urls = ["https://i.redd.it/jo7eoqh9gue41.jpg",
         "https://i.imgur.com/EutiMfe.jpg",
         "https://i.redd.it/99qky2zx6ve41.png",
         "https://i.redd.it/fszcdofojue41.jpg",
         "https://i.redd.it/wwt28ys8lue41.jpg",
         "https://i.redd.it/bmdk44wvmxe41.png",
         "https://i.redd.it/slraqbhomxe41.png",
         "https://i.redd.it/lzitvr0hxue41.jpg",
         "https://i.redd.it/olcckyd4iue41.jpg"]

    imageObjects = []
    # get image objects for urls
    dest_directory = os.path.join(base_directory, "PictureSource")
    for url in urls:
        print(url)
        imageObj = RedditImage(url, "")
        imageObj.get_image_from_url(dest_directory)
        imageObj.image_is_landscape()
        imageObjects.append(imageObj)

    ci = CombineImages(imageObjects, dest_directory)
    pathOfResult = ci.do_combine_landscape_process()
    for imageObj in imageObjects:
        imageObj.cleanup()
    print(pathOfResult)

    exit(0)
    # test gradient util method
    test = Image.new("RGB", (1000, 1000), (0, 0, 0))

    do_gradient(test, (0, 0), (1000, 1000), (117, 103, 108), (178, 156, 111))

    path = os.path.join(base_directory, "test.PNG")
    test.save(path, "PNG")


