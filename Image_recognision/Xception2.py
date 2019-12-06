from keras.applications.inception_v3 import InceptionV3
from keras.preprocessing import image
from keras.models import Model
from keras.layers import Dense, GlobalAveragePooling2D
from keras.preprocessing.image import ImageDataGenerator
from keras import backend as K
from keras.callbacks import ModelCheckpoint, EarlyStopping
import sys
import os
import numpy as np
import tensorflow as tf
import download_train.py

# hyper parameters for model
nb_classes = 5  # number of classes
based_model_last_block_layer_number = 126  # value is based on based model selected.
img_width, img_height = 256, 256  # change based on the shape/structure of your images
batch_size = 64  # try 4, 8, 16, 32, 64, 128, 256 dependent on CPU/GPU memory capacity (powers of 2 values).
nb_epoch = 15  # number of iteration the algorithm gets trained.
learn_rate = 5e-5  # sgd learning rate
momentum = .9  # sgd momentum to avoid local minimum
train_data_dir = 'data/train'  # training data folder path
validation_data_dir = 'data/validation'  # validation data folder path
transformation_ratio = .05  # how aggressive will be the data augmentation/transformation

# creating the base pre-trained model
base_model = InceptionV3(weights='imagenet', include_top=False)

# adding some extra layers
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(1024, activation='relu')(x)
predictions = Dense(5, activation='softmax')(x)

# this final model will be trained
model = Model(inputs=base_model.input, outputs=predictions)

# firstly only top layers, which were randomly initialized, are trained. All other layers are frozen
for layer in base_model.layers:
    layer.trainable = False

# Data aaugmentation
train_datagen = ImageDataGenerator(rescale=1. / 255,
                                   rotation_range=transformation_ratio,
                                   shear_range=transformation_ratio,
                                   zoom_range=transformation_ratio,
                                   cval=transformation_ratio,
                                   horizontal_flip=True,
                                   vertical_flip=True)

validation_datagen = ImageDataGenerator(rescale=1. / 255)

os.makedirs(os.path.join(os.path.abspath(train_data_dir), '../preview'), exist_ok=True)
train_generator = train_datagen.flow_from_directory(train_data_dir,
                                                    target_size=(img_width, img_height),
                                                    batch_size=batch_size,
                                                    class_mode='categorical')

validation_generator = validation_datagen.flow_from_directory(validation_data_dir,
                                                              target_size=(img_width, img_height),
                                                              batch_size=batch_size,
                                                              class_mode='categorical')

# compiling the model
model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['accuracy'])

#weights file name
top_weights_path = 'model_weights.h5'

callbacks_list = [
    ModelCheckpoint(top_weights_path, monitor='val_acc', verbose=1, save_best_only=True),
    EarlyStopping(monitor='val_acc', patience=5, verbose=0)
]
# the model is trained for a few epochs
model.fit_generator(train_generator,
                        samples_per_epoch=train_generator.samples,
                        nb_epoch=nb_epoch / 5,
                        validation_data=validation_generator,
                        nb_val_samples=validation_generator.samples,
                        callbacks=callbacks_list)

# at this point, the top layers are well trained and we can start fine-tuning
# convolutional layers from inception V3. We will freeze the bottom N layers
# and train the remaining top layers.

# printing the layer list to decide, which layers to retrain
for i, layer in enumerate(base_model.layers):
   print(i, layer.name)

# the last 2 inception blocks are chosen to retrain. Others are frozen
for layer in model.layers[:249]:
   layer.trainable = False
for layer in model.layers[249:]:
   layer.trainable = True

# model has to be recompiled for changes to take place
from keras.optimizers import SGD
model.compile(optimizer=SGD(lr=0.0001, momentum=0.9), loss='categorical_crossentropy', metrics=['accuracy'])

# model is trained again
model.fit_generator(train_generator,
                        samples_per_epoch=train_generator.samples,
                        nb_epoch=nb_epoch,
                        validation_data=validation_generator,
                        nb_val_samples=validation_generator.samples,
                        callbacks=callbacks_list)