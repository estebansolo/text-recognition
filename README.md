# Text Detection with Tesseract OCR

## Installation

First you need to install [Tesseract](https://github.com/tesseract-ocr/tesseract/wiki) on your computer, if you have Ubuntu or its derivatives, below are the installation steps.

### Install Tesseract 4 In Ubuntu

```
sudo apt install tesseract-ocr
```

### Older Ubuntu Versions

```
sudo add-apt-repository ppa:alex-p/tesseract-ocr
sudo apt-get update
sudo apt install tesseract-ocr
```

Once you have Tesseract installed, you will be able to install the necessary project libraries.

```
pip install -r requirements.txt
```

## CLI

This CLI requires at least one image to be processed.

```
python3 app.py --image /path/to/the/image.png
```

### Options:

```
-i/--image                  # (Required) Image to be OCR'd.
-o/--output                 # Path to the output image and its content.
-f/--file_format            # Format type to the result content (json / csv).
-m/--min-conf               # Mininum confidence value to filter weak text detection.
--line/--word               # Determines whether to extract words or rows of text.
-d/--distance               # Max distance between words in the same row, it's used if --line flag is present.
```

## Examples

```
python3 app.py -i examples/images/test.png -o output
python3 app.py -i examples/images/label.jpg -f json -o output
```