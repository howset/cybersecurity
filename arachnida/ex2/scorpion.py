import argparse
from PIL import Image, ExifTags
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
        # for key, value in img.info.items():
        #     print(f"{key}: {value}")
        # print(img.getxmp())
        print(f"########## {filename} ##########")
        print("format:", img.format, "| size:", img.size, "| mode:", img.mode)
        exif_data = img.getexif()  # only exif (IFD0), there may be others (img.info, img.getxmp())
        if not exif_data:
            print("no exif data")
        # main details (make model etc)
        for tag_id, value in exif_data.items():
            tag_name = Image.ExifTags.TAGS.get(tag_id, tag_id)
            print(tag_name, ":", value)
        # other details
        # exif_ifd = exif_data.get_ifd(ExifTags.IFD.Exif)  # exif ifd. exposure, etc
        # exif_ifd = exif_data.get_ifd(0x8825) # gps ifd
        # for tag_id, value in exif_ifd.items():
        #     tag_name = ExifTags.TAGS.get(tag_id, tag_id)
        #     print(f"{tag_name}: {value}")


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
            prog="scorpion.py",
            description="display metadata from image",
        )
    parser.add_argument(
        "files",
        nargs="+",  # accept one/more
        help="image file(s)",
    )
    args = parser.parse_args()
    # print("args:", args)
    images = collect_images(args)
    get_tags(images)


if __name__ == "__main__":
    scorpion()
