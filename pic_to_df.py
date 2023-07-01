import time
import cv2
import pytesseract
import pandas as pd
import re
import os
import concurrent.futures
import shutil
import warnings
import numpy as np
import argparse
import sys

# print (sys.platform)

if sys.platform=="win32":
    pytesseract.pytesseract.tesseract_cmd = r'tesseract\tesseract.exe'

warnings.filterwarnings("ignore")

def read_image(file, config, skipped):
    im = cv2.imread(file)
    
    # Preprocess the image using the provided configuration
    im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    dilated_img = cv2.dilate(im_gray, np.ones(config["dilation"], np.uint8))
    bg_img = cv2.medianBlur(dilated_img, config["blur"])
    im_no_shadow = 255 - cv2.absdiff(im_gray, bg_img)
    im_thresh = cv2.threshold(im_no_shadow, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
    # Output the preprocessed image
    cv2.imwrite(config["preprocessed_image_path"], im_thresh)
    
    # Extract text with pytesseract
    text = pytesseract.image_to_string(im_thresh, config=config["tesseract"])
    
    # Process the text and create a DataFrame
    rows = text.strip().split('\n')
    header, data = rows[0].split(), rows[1:]
    
    df = pd.DataFrame(columns=header)
    for row in data:
        values = re.split(r'\s+', row)  
        if len(values) == len(header):
            df.loc[len(df)] = values
        else:
            skipped_row = pd.DataFrame({'skipped': [row]})
            skipped = pd.concat([skipped, skipped_row], ignore_index=True)
            
    df['file'] = file
    return df, skipped


def read_images_in_folder(folder, config):
    skipped = pd.DataFrame(columns=['skipped'])
    df = pd.DataFrame()
    
    # Supported image file formats
    valid_extensions = [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]
    files = [os.path.join(folder, file) for file in os.listdir(folder) if any(file.endswith(ext) for ext in valid_extensions)]
    
    processed_files_folder = os.path.join(config["processed_files_folder"])
    if not os.path.exists(processed_files_folder):
        os.makedirs(processed_files_folder)
        
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = executor.map(read_image, files, [config]*len(files), [skipped]*len(files))
        
    for file, result in zip(files, results):
        dataframe, new_skipped = result
        df = pd.concat([df, dataframe], ignore_index=True)
        skipped_row = pd.DataFrame(new_skipped, columns=['skipped'])
        skipped = pd.concat([skipped, skipped_row], ignore_index=True)
        destination = os.path.join(processed_files_folder, os.path.basename(file))
        shutil.move(file, destination)
    return df, skipped

if __name__ == '__main__':
    # pytesseract.pytesseract.tesseract_cmd = r'tesseract\tesseract.exe'
    config = {
        "dilation": (7,7),
        "blur": 21,
        "preprocessed_image_path": "preprocessed.png",
        "tesseract": r'--oem 3 --psm 6',
        "processed_files_folder": 'processed_files'
    }
    
    # folder = 'new_images'
    # df, skipped = read_images_in_folder(folder, config)
    
    # with pd.ExcelWriter('output.xlsx') as writer:
    #     df.to_excel(writer, sheet_name='data', index=False)
    #     skipped.to_excel(writer, sheet_name='skipped', index=False)

    ''' [1:48 PM] Niketan, Nripesh

python file.py [-f folder-name] [-o output-excel-name] [-onefile file-name]
'''

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--foldername", help = "Specify path of folder that contain the images. Will use new_images folder if not specified", default='new_images')
    parser.add_argument("-o", "--outputfile", help="Specify name (and destination) of the output file to be created. Will appear in base directory if location is not specified.", default='output.xlsx')
    parser.add_argument("-of", "--onefile", dest = "onefile", help = "One file")

    args = parser.parse_args()

    folder= args.foldername
    file = args.outputfile

    df, skipped = read_images_in_folder(folder, config)

    with pd.ExcelWriter(file) as writer:
        df.to_excel(writer, sheet_name='data' , index=False)
        skipped.to_excel(writer, sheet_name='skipped', index=False)
