import csv
import urllib.request as ur
import imghdr
import os
from PIL import Image


def reading_file():
    with open('train_products.csv', 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        rows = []
        for row in csv_reader:
            # First line in the file is not useful information
            if line_count == 0:
                line_count += 1
            else:
                # Do not use line if it does not have all information to avoid out of bounds error
                if len(row) == 5:
                    # Add information to the array
                    rows.append(row)
                    line_count += 1
        print(f'Processed {line_count} lines.')
    return rows


def download_files(rows):
    download_size = 51
    counter_download_fail = 0
    counter_resize_fail = 0
    counter_downloading = 0
    abs_path = os.path.dirname("Inception.py")
    dest_path = 'data/train/'
    length_validation = 0

    # Passing through each line in the file
    for row in rows:
        filename = str(row[4])
        counter_downloading = counter_downloading + 1

        # Checking the number of files in the corresponding folder, required for the next step
        try:
            length_validation = len(os.listdir(str(abs_path) + 'data/validation/' + str(row[0])))
        except:
            length_validation = 0
            pass
        try:
            length_train = len(os.listdir(str(abs_path) + 'data/train/' + str(row[0])))
        except:
            length_train = 0
            pass

        # Saving image to data/validation instead of data/train for every 5 image to create ratio of validation data 4:1
        if (length_train + length_validation + 1) % 5 == 0:
            dest_path = 'data/validation/'
        else:
            dest_path = 'data/train/'

        # Showing progress of downloaded files
        if (counter_downloading % 10) == 0:
            print('Number of downloaded files: ' + str(counter_downloading))

        try:
            # Trying to download an image
            ur.urlretrieve(row[3], filename)
            img = Image.open(filename)

            try:
                # Resizing image to the chosen size
                image_small = img.resize((256, 256), Image.ANTIALIAS)
                # Creating a folder if it has not been created
                os.makedirs(os.path.dirname(abs_path + dest_path + row[0] + '/'), exist_ok=True)
                # Save downloaded image to the corresponding folder of the category
                image_small.save(abs_path + dest_path + row[0] + '/' + filename + '.jpg')
                # Remove temporary file
                os.remove(filename)
            except:
                try:
                    # If failed saving or file was in different format, so it requires reformatting and repeating other two steps
                    image_small = image_small.convert('RGB')
                    image_small.save(abs_path + dest_path + row[0] + '/' + filename + '.jpg', 'JPEG')
                    os.remove(filename)
                except:
                    # If resize/converting failed
                    counter_resize_fail = counter_resize_fail + 1
                    print('Failed to resize an image: ID - ' + str(row[item_number]) + ' , link - ' + str(row[link]))
                    pass
        except:
            # Show links, which failed to download
            print('Failed link of the image: ID - ' + str(row[item_number]) + ' , link - ' + str(row[link]))
            counter_download_fail = counter_download_fail + 1
            pass

    # Printing failed to download or resize files
    print("Number of failed downloads: ", counter_download_fail)
    print("Number of failed resizing of images: ", counter_resize_fail)


# Reading the file into an array
file = reading_file()

print("Starting downloading...")

# Downloading files from the list
download_files(file)
