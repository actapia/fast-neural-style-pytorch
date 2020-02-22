import argparse
import cv2
import os
import transformer
import torch
import utils

import sys

import multiprocessing

import yaml

STYLE_TRANSFORM_PATH = "transforms/mosaic.pth"
PRESERVE_COLOR = False
WIDTH = 1280
HEIGHT = 720

class Style:
    def __init__(self,title,path,artist=None):
        self.title = title
        self.artist = artist
        self.path = path
        
    def __str__(self):
        style_str = '"{}"'.format(self.title)
        if self.artist:
            style_str = "{0} by {1}".format(style_str,self.artist)
        return '{0} ({1})'.format(style_str,self.path)

def webcam(styles, current_style, width=1280, height=720):
    """
    Captures and saves an image, perform style transfer, and again saves the styled image.
    Reads the styled image and show in window. 
    """
    # Device
    device = ("cuda" if torch.cuda.is_available() else "cpu")
    
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
    cam = cv2.VideoCapture(0)
    cam.set(3, width)
    cam.set(4, height)

    cv2.namedWindow("style")
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
            
            cv2.setWindowTitle('style',styles[current_style.value].title)

            # Show webcam
            cv2.imshow('style', generated_image)
            if cv2.waitKey(1) == 27: 
                break  # esc to quit
            
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c","--camera",type=int,default=0)
    parser.add_argument("-S","--styles-dir",default=os.path.join(os.path.dirname(os.path.realpath(__file__)),"transforms"))
    args = parser.parse_args()
    #print(args.styles_dir)
    styles = []
    for style_dir in os.listdir(args.styles_dir):
        style_dir_path = os.path.join(args.styles_dir,style_dir)
        if os.path.isdir(style_dir_path):
            try:
                with open(os.path.join(style_dir_path,"style.yml"),"r") as style_file:
                    style_contents = style_file.read()
                style_dict = yaml.load(style_contents,Loader=yaml.Loader)
                styles.append(Style(**style_dict,path=os.path.join(style_dir_path,"{}.pth".format(style_dir))))
                print(str(styles[-1]))
            except FileNotFoundError:
                print("bad dir")
    #sys.exit(0)
    current_style = multiprocessing.Value('i',0)
    job = multiprocessing.Process(target=webcam,args=(styles,current_style,WIDTH,HEIGHT,))
    job.start()
    style_options = [s.title for s in styles]
    while True:
        print("Source style")
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
