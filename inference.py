import numpy as np
import cv2
import torch
import glob as glob
import os
import time
import argparse
import yaml
import matplotlib.pyplot as plt

from models.create_fasterrcnn_model import create_model
from utils.annotations import inference_annotations
from utils.general import set_infer_dir
from utils.transforms import infer_transforms

def collect_all_images(dir_test):
   
    test_images = []
    if os.path.isdir(dir_test):
        image_file_types = ['*.jpg', '*.jpeg', '*.png', '*.ppm']
        for file_type in image_file_types:
            test_images.extend(glob.glob(f"{dir_test}/{file_type}"))
    else:
        test_images.append(dir_test)
    return test_images    

def parse_opt():
    # Construct the argument parser.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--input', 
        help='folder path ',
    )
    parser.add_argument(
        '-c', '--config', 
        default=None,
        help='(optional) config file'
    )
    parser.add_argument(
        '-m', '--model', default=None,
        help='model'
    )
    parser.add_argument(
        '-w', '--weights', default=None,
        help='path '
    )
    parser.add_argument(
        '-th', '--threshold', default=0.3, type=float,
        help='detection threshold'
    )
    parser.add_argument(
        '-si', '--show-image', dest='show_image', action='store_true',
        help='visualize '
    )
    parser.add_argument(
        '-mpl', '--mpl-show', dest='mpl_show', action='store_true',
        
    )
    parser.add_argument(
        '-d', '--device', 
        default=torch.device('cuda:0' if torch.cuda.is_available() else 'cpu'),
       
    )
    args = vars(parser.parse_args())
    return args

def main(args):
  
    np.random.seed(42)

  
    data_configs = None
    if args['config'] is not None:
        with open(args['config']) as file:
            data_configs = yaml.safe_load(file)
        NUM_CLASSES = data_configs['NC']
        CLASSES = data_configs['CLASSES']

    DEVICE = args['device']
    OUT_DIR = set_infer_dir()

    # Load the pretrained model
    if args['weights'] is None:
        
       
        if data_configs is None:
            with open(os.path.join('data_configs', 'test_image_config.yaml')) as file:
                data_configs = yaml.safe_load(file)
            NUM_CLASSES = data_configs['NC']
            CLASSES = data_configs['CLASSES']
        try:
            build_model = create_model[args['model']]
        except:
            build_model = create_model['fasterrcnn_resnet50_fpn']
        model = build_model(num_classes=NUM_CLASSES, coco_model=True)
    # Load weights if path provided.
    if args['weights'] is not None:
        checkpoint = torch.load(args['weights'], map_location=DEVICE)
        # If config file is not given, load from model dictionary.
        if data_configs is None:
            data_configs = True
            NUM_CLASSES = checkpoint['config']['NC']
            CLASSES = checkpoint['config']['CLASSES']
        try:
            print('Building from model name arguments...')
            build_model = create_model[str(args['model'])]
        except:
            build_model = create_model[checkpoint['model_name']]
        model = build_model(num_classes=NUM_CLASSES, coco_model=False)
        model.load_state_dict(checkpoint['model_state_dict'])
    model.to(DEVICE).eval()

    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
    if args['input'] == None:
        DIR_TEST = data_configs['image_path']
        test_images = collect_all_images(DIR_TEST)
    else:
        DIR_TEST = args['input']
        test_images = collect_all_images(DIR_TEST)
    print(f"Test instances: {len(test_images)}")

    detection_threshold = args['threshold']

   
    frame_count = 0
   
    total_fps = 0
    for i in range(len(test_images)):
       
        image_name = test_images[i].split(os.path.sep)[-1].split('.')[0]
        image = cv2.imread(test_images[i])
        orig_image = image.copy()
        # BGR to RGB
        image = cv2.cvtColor(orig_image, cv2.COLOR_BGR2RGB)
        image = infer_transforms(image)
        # Add batch dimension.
        image = torch.unsqueeze(image, 0)
        start_time = time.time()
        with torch.no_grad():
            outputs = model(image.to(DEVICE))
        end_time = time.time()

       
        fps = 1 / (end_time - start_time)
       
        total_fps += fps
      
        frame_count += 1
        
        outputs = [{k: v.to('cpu') for k, v in t.items()} for t in outputs]
       
        if len(outputs[0]['boxes']) != 0:
            orig_image = inference_annotations(
                outputs, detection_threshold, CLASSES,
                COLORS, orig_image
            )
            if args['show_image']:
                cv2.imshow('Prediction', orig_image)
                cv2.waitKey(1)
            if args['mpl_show']:
                plt.imshow(orig_image[:, :, ::-1])
                plt.axis('off')
                plt.show()
        cv2.imwrite(f"{OUT_DIR}/{image_name}.jpg", orig_image)
        print(f"Image {i+1} done...")
        print('-'*50)

    print('TEST PREDICTIONS COMPLETE')
    cv2.destroyAllWindows()
    # Calculate and print the average FPS.
    avg_fps = total_fps / frame_count
    print(f"Average FPS: {avg_fps:.3f}")

if __name__ == '__main__':
    args = parse_opt()
    main(args)