
import os
import random
import shutil

# Validation split ratio.
VALID_SPLIT = 0.17

IMAGES_FOLDER = os.path.join('data', 'images')
XML_FOLDER = os.path.join('data', 'annotations')

TRAIN_IMAGES_DEST = os.path.join('data', 'train_images')
TRAIN_XML_DEST = os.path.join('data', 'train_xmls')
VALID_IMAGES_DEST = os.path.join('data', 'valid_images')
VALID_XMLS_DEST = os.path.join('data', 'valid_xmls')

os.makedirs(TRAIN_IMAGES_DEST, exist_ok=True)
os.makedirs(TRAIN_XML_DEST, exist_ok=True)
os.makedirs(VALID_IMAGES_DEST, exist_ok=True)
os.makedirs(VALID_XMLS_DEST, exist_ok=True)

all_src_images = sorted(os.listdir(IMAGES_FOLDER))
all_src_xmls = sorted(os.listdir(XML_FOLDER))



temp = list(zip(all_src_images, all_src_xmls))
random.shuffle(temp)
res1, res2 = zip(*temp)
temp_images, temp_xmls = list(res1), list(res2)

print(temp_images[:3])
print(temp_xmls[:3])

num_training_images = int(len(temp_images)*(1-VALID_SPLIT))
num_valid_images = int(len(temp_images)-num_training_images)

print(num_training_images, num_valid_images)

train_images = temp_images[:num_training_images]
train_xmls = temp_xmls[:num_training_images]

valid_images = temp_images[num_training_images:len(all_src_images)]
valid_xmls = temp_xmls[num_training_images:len(all_src_images)]

print(train_images[:3])
print(valid_images[:3])

for i in range(len(train_images)):
    shutil.copy(
        os.path.join(IMAGES_FOLDER, train_images[i]),
        os.path.join(TRAIN_IMAGES_DEST, train_images[i])
    )
    shutil.copy(
        os.path.join(XML_FOLDER, train_xmls[i]),
        os.path.join(TRAIN_XML_DEST, train_xmls[i])
    )

for i in range(len(valid_images)):
    shutil.copy(
        os.path.join(IMAGES_FOLDER, valid_images[i]),
        os.path.join(VALID_IMAGES_DEST, valid_images[i])
    )
    shutil.copy(
        os.path.join(XML_FOLDER, valid_xmls[i]),
        os.path.join(VALID_XMLS_DEST, valid_xmls[i])
    )