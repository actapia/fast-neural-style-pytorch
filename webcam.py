import argparse
import cv2
import os
import transformer
import torch
import utils

import numpy as np

import sys

import multiprocessing

import yaml

from style_picker import StylePicker
from style_button import StyleButton

from PyQt5.QtWidgets import *

from screeninfo import get_monitors

STYLE_TRANSFORM_PATH = "transforms/mosaic.pth"
PRESERVE_COLOR = False
WIDTH = 1280
HEIGHT = 720

def save_img(out_path, img):
    img = np.clip(img, 0, 255).astype(np.uint8)
    imwrite(out_path, img)

from style import Style
def webcam(styles, current_style, width=1280, height=720, cam_num=0, cam_screen=None):
    """
    Captures and saves an image, perform style transfer, and again saves the styled image.
    Reads the styled image and show in window. 
    """
    # Device
    device = ("cuda" if torch.cuda.is_available() else "cpu")
    
    snap_number = 0
    
    style_nets = []

    # Load Transformer Network
    #print("Loading Transformer Networks")
    for style in styles:
        net = transformer.TransformerNetwork()
        net.load_state_dict(torch.load(style.path))
        net = net.to(device)
        style_nets.append(net)
    #print("Done Loading Transformer Networks")

    # Set webcam settings
    cam = cv2.VideoCapture(cv2.CAP_DSHOW+cam_num)
    cam.set(3, width)
    cam.set(4, height)

    cv2.namedWindow("style")
    if cam_screen:
        monitors = get_monitors()
        cv2.moveWindow("style",monitors[cam_screen].x,0)
    # Main loop
    with torch.no_grad():
        while True:
            # Get webcam input
            ret_val, img = cam.read()

            # Mirror 
            img = cv2.flip(img, 1)

            # Free-up unneeded cuda memory
            torch.cuda.empty_cache()
            
            # Generate image
            content_tensor = utils.itot(img).to(device)
            generated_tensor = style_nets[current_style.value](content_tensor)
            generated_image = utils.ttoi(generated_tensor.detach())
            if (PRESERVE_COLOR):
                generated_image = utils.transfer_color(img, generated_image)

            generated_image = generated_image / 255
            generated_image = cv2.resize(generated_image,(1920,1080))
            
            cv2.setWindowTitle('style',styles[current_style.value].title)


            k = cv2.waitKey(1)
            if k == 27: 
                break  # esc to quit
            elif k % 256 == 32:
                cv2.imwrite("snapshot{0}.png".format(snap_number),255*generated_image)
                snap_number = snap_number + 1
                
            # Show webcam
            cv2.imshow('style', generated_image)

            
    # Free-up memories
    cam.release()
    cv2.destroyAllWindows()
    
def show_options(options, first=1, prompt="Selection: ", validate_type=False,validate_range=False):
    for index, option in enumerate(options):
        print("  [{0}] {1}".format(index+first, option))
    valid = False
    response = None
    while not valid:
        response = input(prompt)
        if not validate_type:
            response = int(response)
            break
        try:
            response = int(response)
            if (not validate_range) or (response >= first and response < first+len(options)):
                valid = True
            else:
                print("Invalid choice {0}.".format(response))
        except ValueError:
            print("Invalid choice {0}.".format(response))
    return response

def get_styles(styles_dir):
    styles = []
    for style_dir in os.listdir(styles_dir):
        style_dir_path = os.path.join(styles_dir,style_dir)
        if os.path.isdir(style_dir_path):
            style_dict = None
            try:
                with open(os.path.join(style_dir_path,"style.yml"),"r") as style_file:
                    style_contents = style_file.read()
                style_dict = yaml.load(style_contents,Loader=yaml.Loader)
                #print(str(styles[-1]))
            except FileNotFoundError:
                print("bad dir")                
            if style_dict:
                thumb_path = os.path.join(style_dir_path,"thumb.png")
                if os.path.exists(thumb_path):
                    style_dict["thumb"] = thumb_path
                styles.append(Style(**style_dict,path=os.path.join(style_dir_path,"{}.pth".format(style_dir))))
    return styles
    
def set_current_style(current_style, value):
    current_style.value = value

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c","--camera",type=int,default=0)
    parser.add_argument("-S","--styles-dir",default=os.path.join(os.path.dirname(os.path.realpath(__file__)),"transforms"))
    parser.add_argument("-g","--gui",action='store_true')
    parser.add_argument("-m","--maximize",action='store_true')
    parser.add_argument("-C","--camera-screen",type=int)
    parser.add_argument("-P","--picker-screen",type=int)
    args = parser.parse_args()
    #print(args.styles_dir)
    #sys.exit(0)
    styles = get_styles(args.styles_dir)
    current_style = multiprocessing.Value('i',0)
    job = multiprocessing.Process(target=webcam,args=(styles,current_style,WIDTH,HEIGHT,args.camera,args.camera_screen))
    job.start()
    if args.gui:
        # GUI
        app = QApplication([])
        if not args.maximize:
            StyleButton.default_size = (250,250)
        picker = StylePicker(styles)
        picker.style_picked.connect(lambda s, picked=current_style: set_current_style(picked, s))
        picker.show()
        picker.resize(1200,700)
        if args.picker_screen:
            monitors = get_monitors()
            picker.move(monitors[args.picker_screen].x,0)
        if args.maximize:
            picker.showMaximized()
        app.exec_()
        job.terminate()
    else:
        # Terminal text interface.
        style_options = [s.title for s in styles]
        while True:
            print("Source style")
            # Style index represents ...
            style_index = show_options(style_options,validate_type=True)
            if style_index == 0:
                if job:
                    job.terminate()
                break
            elif style_index >= 1 and style_index <= len(styles):
                current_style.value = style_index - 1
            else:
                print("Invalid choice {0}.".format(style_index))
    #webcam(STYLE_TRANSFORM_PATH, WIDTH, HEIGHT)
