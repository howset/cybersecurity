import argparse
import piexif
from pathlib import Path


def get_tags(filename) -> dict:
    md_tags = piexif.load(filename)
    print(md_tags)
    return md_tags


def display_md(args):
    filter = (".jpg", ".jpeg", ".png", ".gif", ".bmp")
    for image in args.files:
        img_path = Path(image)
        if not img_path.is_file():
            print(f"{image} not found")
            continue
        extension = img_path.suffix.lower()
        if extension not in filter:
            print(f"{image} unsupported")
            continue
        get_tags(image)


def scorpion():
    parser = argparse.ArgumentParser(
            prog="./scorpion",
            description="display metadata from image",
            epilog="usage: scorpion file1 [file2 ...]",
        )
    parser.add_argument(
        "files",
        nargs="+",  # accept one/more
        metavar="FILE",
        help="image file(s)",
    )
    args = parser.parse_args()
    # print("args:", args)
    display_md(args)


if __name__ == "__main__":
    scorpion()
