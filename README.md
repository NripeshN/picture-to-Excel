# Optical Character Recognition (OCR) for Image Files

This Python script uses Optical Character Recognition (OCR) to extract text from image files. The images are preprocessed to enhance the text's visibility and are then processed with Tesseract, an OCR engine. This program supports multiple image formats, including PNG, JPG, JPEG, BMP, and TIFF.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Usage](#usage)
- [Support](#support)
- [Contributing](#contributing)
- [License](#license)

## Features

- Image preprocessing to enhance text visibility
- Parallel processing for efficiency
- Skipped row tracking for data verification
- Extracted data output to an Excel file

## Prerequisites

To run this script, you need Python 3.6+ and the following libraries:

- OpenCV
- Tesseract
- pytesseract
- pandas
- numpy
- concurrent.futures (built-in)
- shutil (built-in)
- os (built-in)
- warnings (built-in)

You also need to have Tesseract OCR installed on your machine. You can download it [here](https://github.com/UB-Mannheim/tesseract/wiki).

## Usage

1. Clone this repository:

```bash
git clone https://github.com/NripeshN/picture-to-df.git
cd repository
```

2. Run the script:

```bash
python script_name.py
```

Ensure you have the correct directory path and necessary configuration details set in the `config` dictionary in the `if __name__ == '__main__'` block. The configuration dictionary includes settings for image dilation, blur, the path for saving preprocessed images, Tesseract commands, and the directory for storing processed files.

The script scans the specified directory for image files, preprocesses them, and then uses Tesseract to extract text from the images. The extracted text is then converted into a DataFrame and written to an Excel file. Any rows of text that the script cannot process are noted in a 'skipped' DataFrame, which is also written to the Excel file. The images are moved to a processed files directory once the text has been extracted.

The script outputs an Excel file (`output.xlsx` by default) containing the extracted data and any skipped rows.

## Support

If you encounter any issues, please open an issue in this repository.

## Contributing

Pull requests are welcome. Please make sure to update tests as appropriate.

## License

This project is licensed under the terms of the MIT license. See [LICENSE](LICENSE) for more details.
