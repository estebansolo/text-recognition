import click
from text_detection import TextDetection

@click.command()
@click.option(
    '-i', '--image',
    prompt=True, required=True,
    type=click.Path(dir_okay=False, exists=True),
    help='Input image to be OCR\'d.')
@click.option(
    '-o', '--output',
    type=click.Path(file_okay=False, exists=True),
    help='Path to the output image and its content.')
@click.option(
    '-f', '--file_format',
    default="csv",
    show_default=True,
    type=click.Choice(["json", "csv"]),
    help='Format type to the result content.')
@click.option(
    '-m', '--min-conf',
    default=0,
    show_default=True,
    type=click.IntRange(min=0, max=100),
    help='Mininum confidence value to filter weak text detection.')
@click.option(
    '--line/--word',
    default=False,
    show_default=True,
    help='Determines whether to extract words or rows of text.')
@click.option(
    '-d', '--distance',
    default=10,
    show_default=True,
    type=click.IntRange(min=0, max=20),
    help='Max distance between words in the same row, it\'s used if --line is used.')
def ocr(image, output, file_format, min_conf, line, distance):
    word_detection = TextDetection(
        image,
        output,
        file_format=file_format,
        min_confidence=min_conf,
        line=line, distance=distance
    )
    
    word_detection.detect()

if __name__ == '__main__':
    ocr()
