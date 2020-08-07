import os
import cv2
import pytesseract

class TextDetection:
    data_image = []

    def __init__(self, image, output=None, **kwargs):
        self.__input_image(image)

        self.__output_directory(output)
        self.__output_image(output)
        
        self.file_format = kwargs.get("file_format", "json")
        self.word_distance = kwargs.get("word_distance", 10)
        self.complete_row = kwargs.get("complete_row", False)
        self.min_confidence = kwargs.get("min_confidence", 0)

    def detect(self):
        self.__load()
        data = self.__image_to_data()

        self.data_image = self.__filter_data(data)

        # exit()

        if self.complete_row:
            self.data_image = self.__validate_complete_rows()
        
        # Save found texts json, csv?
        self.__save_image()

    def __input_image(self, image):
        if not os.path.isfile(image):
            raise FileNotFoundError
        
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

    def __output_image(self):
        if not output:
            output = self.image_path

        if not os.path.isdir(output):
            raise ValueError

        output_name = f"{self.image_name}_output.{self.image_extension}"
        self.__output = f"{self.image_path}/{output_name}"

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

    @staticmethod
    def localization(data, index):
        """ Coordinates of the text from the current index """

        return {
            "top": data["top"][index],
            "left": data["left"][index],
            "width": data["width"][index],
            "height": data["height"][index],
        }




    

    def __save_image(self):
        for localization in self.data_image:
            cv2.rectangle(
                self.__load_image,
                (localization['left'], localization['top']),
                (localization['left'] + localization['width'], localization['top'] + localization['height']),
                (0, 255, 0),
                1
            )

        cv2.imwrite(self.__output, self.__load_image)

    def __validate_complete_rows(self):
        response = []
        complete_text = []
        last_top = self.data_image[0]['top']
        last_left = self.data_image[0]['left']
        last_width = self.data_image[0]['width']
        last_height = self.data_image[0]['height']

        for localization in self.data_image:
            distance = localization['left'] - (last_left + last_width)
            if localization['top'] == last_top and distance < 10:
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

    
