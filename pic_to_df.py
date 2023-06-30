
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

warnings.filterwarnings("ignore")

# Set the path to the tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'tesseract\tesseract.exe'

global skipped
skipped = pd.DataFrame(columns=['skipped'])

def read_image(file, skipped=skipped):
    im = cv2.imread(file)
    # Preprocess the image
    im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    
    # Remove shadows
    dilated_img = cv2.dilate(im_gray, np.ones((5,5), np.uint8))
    bg_img = cv2.medianBlur(dilated_img, 21)
    im_no_shadow = 255 - cv2.absdiff(im_gray, bg_img)
    
    im_thresh = cv2.threshold(im_no_shadow, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
    # Output the preprocessed image
    cv2.imwrite('preprocessed.png', im_thresh)
    
    
    
    # Extract text with pytesseract
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(im_thresh, config=custom_config)
    
    # # Detect text blocks
    # d = pytesseract.image_to_data(im_thresh, config=custom_config, output_type=pytesseract.Output.DICT)
    # n_boxes = len(d['level'])
    # for i in range(n_boxes):
    #     (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
    #     cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
    # # Show image with detected text
    # cv2.imshow('img', im)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
    
    # Process the text and create a DataFrame
    rows = text.strip().split('\n')
    header, data = rows[0].split(), rows[1:]
    print(header)
    locators, lines, item_codes, qtys = [], [], [], []
    for row in data:
        values = re.split(r'\s+', row)  # Split on one or more whitespace characters
        if len(values) == 4:
            locator, line, item_code, qty = values
            locators.append(locator)
            lines.append(line)
            item_codes.append(item_code)
            qtys.append(qty)
        # if len(values) == 3:
        #     locator, item_code, qty = values
        #     locators.append(locator)
        #     lines.append(None)
        #     item_codes.append(item_code)
        #     qtys.append(qty)
        else:
            # append the skipped rows to the skipped dataframe
            skipped = skipped.append({'skipped': row}, ignore_index=True)
    df = pd.DataFrame({'Locator': locators, 'item_code': item_codes, 'qty': qtys, 'line': lines, 'file': file})
    return df, skipped



def read_images_in_folder(folder):
    global skipped
    df = pd.DataFrame()
    files = [os.path.join(folder, file) for file in os.listdir(folder) if file.endswith(".png") or file.endswith(".jpg")]
    processed_files_folder = os.path.join('processed_files')
    if not os.path.exists(processed_files_folder):
        os.makedirs(processed_files_folder)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = executor.map(read_image, files)
    for file, result in zip(files, results):
        dataframe, new_skipped = result
        df = df.append(dataframe, ignore_index=True)
        skipped = skipped.append(new_skipped, ignore_index=True)
        destination = os.path.join(processed_files_folder, os.path.basename(file))
        shutil.move(file, destination)
    return df

if __name__ == '__main__':
    folder = r'new_images'
    df = read_images_in_folder(folder)
    with pd.ExcelWriter('output.xlsx') as writer:
        df.to_excel(writer, sheet_name='data', index=False)
        skipped.to_excel(writer, sheet_name='skipped', index=False)
