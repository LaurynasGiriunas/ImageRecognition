# Downloads images to be tested, resizes them to the single size and saves them
import csv
import urllib.request as ur
import imghdr
import os
from PIL import Image


def reading_file():
    # Opening file
    with open('test_products.csv', 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        rows = []
        # Passing through each line in the file
        for row in csv_reader:
            # First line in the file is not useful information
            if line_count == 0:
                line_count += 1
            else:
                # Do not use line if it does not have all information to avoid out of bounds error
                if len(row) == 4:
                    # Add information to the array
                    rows.append(row)
                    line_count += 1
        print(f'Processed {line_count} lines.')
    return rows


def download_files(rows):
    # Initialising variables
    image_size = 256
    destination_path = 'data/test/'
    absolute_path = os.path.dirname("Inception.py")
    counter_download_fail = 0
    counter_resize_fail = 0
    counter_downloading = 0
    link = 2
    item_number = 3

    # If required to download part of files
    for row in rows:
        filename = str(row[item_number])
        counter_downloading = counter_downloading + 1

        # Print progress
        if (counter_downloading % 10) == 0:
            print('Number of downloaded files: ' + str(counter_downloading))

        try:
            # Trying to download an image
            ur.urlretrieve(row[link], filename)
            img = Image.open(filename)

            try:
                # Resizing image to the chosen size
                image_small = img.resize((image_size, image_size), Image.ANTIALIAS)
                # Creating a folder if it has not been created
                os.makedirs(os.path.dirname(absolute_path + destination_path + '/'), exist_ok=True)
                # Save downloaded image
                image_small.save(absolute_path + destination_path + '/' + filename + '.jpg')
                # Remove temporary file
                os.remove(filename)
            except:
                try:
                    # If failed saving or file was in different format, so it requires reformatting and repeating other two steps
                    image_small = image_small.convert('RGB')
                    image_small.save(absolute_path + destination_path + '/' + filename + '.jpg', 'JPEG')
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
