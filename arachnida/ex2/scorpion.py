import argparse
from PIL import Image
from pathlib import Path

# https://www.pythonforall.com/modules/pillow/pwmeta
def get_tags(filenames):
    # md_tags = piexif.load(filename)
    # print(md_tags["0th"])
    # print(md_tags["Exif"])
    # print(md_tags["GPS"])
    # print(md_tags["Interop"])
    # print(md_tags["1st"])
    # print(md_tags["thumbnail"])
    # return md_tags
    for filename in filenames:
        img = Image.open(filename)
        print(f"########## {filename} ##########")
        exif_data = img.getexif()
        if not exif_data:
            print("no exif data")
            continue
        for tag_id, value in exif_data.items():
            tag_name = Image.ExifTags.TAGS.get(tag_id, tag_id)
            print(tag_name, ":", value)


def collect_images(args) -> list:
    filter = (".jpg", ".jpeg", ".png", ".gif", ".bmp")
    images = []
    for image in args.files:
        img_path = Path(image)
        if not img_path.is_file():
            print(f"{image} not found")
            continue
        extension = img_path.suffix.lower()
        if extension not in filter:
            print(f"{image} unsupported")
            continue
        images.append(image)
    # print(images)
    return (images)


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
    images = collect_images(args)
    get_tags(images)


if __name__ == "__main__":
    scorpion()
