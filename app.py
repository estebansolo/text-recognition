import click
from text_detection import TextDetection

@click.command()
@click.option('-i', '--image', required=True, help='path to input image to be OCR\'d')
@click.option('-o', '--output', help='')
@click.option('-f', '--file_format', help='')
@click.option('-m', '--min-conf', default=0, help='mininum confidence value to filter weak text detection')
@click.option('-c', '--complete-row', default=False, help='')
@click.option('-d', '--distance', default=10, help='')
def ocr(image, output, file_format, min_conf, complete_row, distance):

    detection = TextDetection(
        image,
        output,
        file_format=file_format,
        min_confidence=min_conf,
        complete_row=complete_row,
        distance=distance
    )
    
    detection.detect()

if __name__ == '__main__':
    ocr()
