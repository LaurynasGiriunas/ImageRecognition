# Makes prediction of the test item category
from keras.applications.inception_v3 import InceptionV3
from keras.preprocessing import image
from keras.models import Model
from keras.layers import Dense, GlobalAveragePooling2D
from keras.applications.inception_v3 import preprocess_input, decode_predictions
import numpy as np
import csv
import os

# Download testing images
#import download_test.py


def recreating_model():
    base_model = InceptionV3(weights=None, include_top=False)
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(1024, activation='relu')(x)
    predictions = Dense(5, activation='softmax')(x)
    model = Model(inputs=base_model.input, outputs=predictions)
    return model


def image_preparation(file):
    loaded_image = image.load_img('data/test/'+file.decode(), target_size=(256, 256))
    temporary_image = image.img_to_array(loaded_image)
    temporary_image = np.expand_dims(temporary_image, axis=0)
    temporary_image = preprocess_input(temporary_image)
    return temporary_image


def predicting():
    # Initializing variables
    results = []
    file_counter = 0

    # Iterating through all files in the folder
    for file in os.listdir(test_directory):

        # Image preparation for prediction
        prepared_image = image_preparation(file)
        filename = os.fsdecode(file)

        preds = model.predict(prepared_image)
        result = prediction_label(preds)

        # Adding results to the single array
        results.append([str(filename.replace('.jpg', '')), str(result)])

        # Printing current prediction file
        if file_counter % 50 == 0:
            print("Number of completed predictions: " + str(file_counter))
        # Limiting amount of the predicted files for test purposes
        #if file_counter == 100:
        #    break
        file_counter = file_counter + 1
    return results


def prediction_label(preds):
    if np.argmax(preds) == 0:
        result = 'Apparel & Accesories'
    elif np.argmax(preds) == 1:
        result = 'Electronics'
    elif np.argmax(preds) == 2:
        result = 'Health & Beauty'
    elif np.argmax(preds) == 3:
        result = 'Home & Garden'
    else:
        result = 'Sporting Goods'
    return result


def save_to_file(results):
    with open("test_products_predictions.csv", "w+") as my_csv:
        csv_writer = csv.writer(my_csv, delimiter=',', lineterminator='\n')
        csv_writer.writerows(results)

# Choosing directory of test files
test_directory = os.fsencode("data/test/")

# Recreating trained model
model = recreating_model()

# Loading learnt weights
model.load_weights("model_weights.h5")

print('Finished recreating model and loading weights')
print('Starting predictions...')

# making predictions
results = predicting()

# Save predictions into file
save_to_file(results)