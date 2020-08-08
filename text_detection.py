import os
import cv2
import json
import pytesseract
import pandas as pd
from io import StringIO

VALID_OUTPUT_FORMAT = ["json", "csv"]

class TextDetection:
    data_image = []

    def __init__(self, image, output=None, **kwargs):
        self.__input_image(image)
        self.__output_directory(output)
        self.__arguments_validation(kwargs)

        self.__output_image = None
        self.__output_results = None

        self.__format_output_files()

    def detect(self):
        self.__load()

        data = self.__image_to_data()
        self.data_image = self.__filter_data(data)
               
        if self.line:
            self.data_image = self.__validate_complete_lines()
        
        self.__save()

    def __load(self):
        """
        Load the image
        Swap color channel from BGR (OpenCV's default) to RGB (compatible
        with Tesseract and pytesseract).
        """

        self.__load_image = cv2.imread(self.__image)
        self.__rgb_image = cv2.cvtColor(self.__load_image, cv2.COLOR_BGR2RGB)
        return self

    def __image_to_data(self):
        """ Use Tesseract to localize each area of text in the image. """

        return pytesseract.image_to_data(
            self.__rgb_image,
            output_type=pytesseract.Output.DICT
        )

    def __filter_data(self, data):
        """ 
        Validate individual localizations.
        Extract the OCR text, Confidence and Text localization
        """

        response = []

        for index, text in enumerate(data["text"]):
            text = text.strip()
            confidence = int(data["conf"][index])

            if not text or self.min_confidence > confidence:
                continue

            response.append({
                "text": text,
                "confidence": confidence,
                **self.localization(data, index)
            })

        return response

    def __save(self):
        self.__save_image()
        self.__save_results()

    def __save_image(self):
        for localization in self.data_image:
            cv2.rectangle(
                self.__load_image,
                (localization['left'], localization['top']),
                (localization['left'] + localization['width'], localization['top'] + localization['height']),
                (0, 255, 0),
                1
            )

        cv2.imwrite(self.__output_image, self.__load_image)

    def __save_results(self):
        df = pd.read_json(StringIO(json.dumps(self.data_image)))
        if self.file_format == "csv":
            df.to_csv(self.__output_results, index=False)
        
        elif self.file_format == "json":
            df.to_json(self.__output_results, orient='records')
    
    def __validate_complete_lines(self):
        response = []
        complete_text = []
        last_top = self.data_image[0]['top']
        last_left = self.data_image[0]['left']
        last_width = self.data_image[0]['width']
        last_height = self.data_image[0]['height']

        for localization in self.data_image:
            distance = localization['left'] - (last_left + last_width)
            if localization['top'] == last_top and distance < self.word_distance:
                last_width += localization['width'] + distance
                complete_text.append(localization['text'])
                continue
            
            response.append({
                "top": last_top,
                "left": last_left,
                "width": last_width,
                "height": last_height,
                "text": " ".join(complete_text)
            })

            complete_text = []
            last_top = localization['top']
            last_left = localization['left']
            last_width = localization['width']
            last_height = localization['height']

        return response

    def __input_image(self, image):
        if not os.path.isfile(image):
            raise FileNotFoundError
        
        image = os.path.abspath(image)

        self.__image = image
        path, filename = os.path.split(image)
        filename, extension = os.path.splitext(filename)
        
        self.image_path = path
        self.image_name = filename
        self.image_extension = extension.strip(".")

    def __output_directory(self, output):
        if not output:
            output = self.image_path

        if not os.path.isdir(output):
            raise ValueError

        self.__output_dir = output.rstrip("/")

    def __arguments_validation(self, args):
        self.line = bool(args.get("line", False))

        # Output File Format
        self.file_format = args.get("file_format")
        if self.file_format not in VALID_OUTPUT_FORMAT:
            self.file_format = "json"

        # Word Distance
        word_distance = args.get("word_distance", 10)
        self.word_distance = self.validate_word_distance(word_distance)
        
        # Min Confidence
        min_confidence = args.get("min_confidence", 0)
        self.min_confidence = self.validate_min_confidence(min_confidence)

    def __format_output_files(self):
        base = f"{self.__output_dir}/{self.image_name}_output."
        self.__output_results = f"{base}{self.file_format}"
        self.__output_image = f"{base}{self.image_extension}"

    @staticmethod
    def validate_word_distance(word_distance):
        if not isinstance(word_distance, int):
            word_distance = 10

        if word_distance < 0:
            word_distance = 0

        elif word_distance > 20:
            word_distance = 20

        return word_distance

    @staticmethod
    def validate_min_confidence(min_confidence):
        if not isinstance(min_confidence, int):
            min_confidence = 10

        if min_confidence < 0:
            min_confidence = 0

        elif min_confidence > 100:
            min_confidence = 100

        return min_confidence

    @staticmethod
    def localization(data, index):
        """ Coordinates of the text from the current index """

        return {
            "top": data["top"][index],
            "left": data["left"][index],
            "width": data["width"][index],
            "height": data["height"][index],
        }

