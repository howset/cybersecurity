import argparse
from PIL import Image, ExifTags, TiffTags
from pathlib import Path


# https://www.pythonforall.com/modules/pillow/pwmeta
# def get_tags(filenames):
#     # md_tags = piexif.load(filename)
#     # print(md_tags["0th"])
#     # print(md_tags["Exif"])
#     # print(md_tags["GPS"])
#     # print(md_tags["Interop"])
#     # print(md_tags["1st"])
#     # print(md_tags["thumbnail"])
#     # return md_tags
#     for filename in filenames:
#         img = Image.open(filename)
#         # for key, value in img.info.items():
#         #     print(f"{key}: {value}")
#         # print(img.getxmp())
#         print(f"########## {filename} ##########")
#         print("format:", img.format, "| size:", img.size, "| mode:", img.mode)
#         exif_data = img.getexif()  # only exif (IFD0), there may be others (img.info, img.getxmp())
#         if not exif_data:
#             print("no exif data")
#         # main details (make model etc)
#         for tag_id, value in exif_data.items():
#             tag_name = Image.ExifTags.TAGS.get(tag_id, tag_id)
#             print(tag_name, ":", value)
#         # other details
#         # exif_ifd = exif_data.get_ifd(ExifTags.IFD.Exif)  # exif ifd. exposure, etc
#         # exif_ifd = exif_data.get_ifd(0x8825) # gps ifd
#         # for tag_id, value in exif_ifd.items():
#         #     tag_name = ExifTags.TAGS.get(tag_id, tag_id)
#         #     print(f"{tag_name}: {value}")

TYPE_SIZE = {
    1: 1,  # byte
    2: 1,  # ascii
    3: 2,  # short
    4: 4,  # long
    5: 8,  # rational
    7: 1,  # undefined
    9: 4,  # slong
    10: 8,  # srational
    129: 1  # utf8
}

def get_tags2(filenames):
    for filename in filenames:
        img = Image.open(filename)
        exif_bytes = img.info.get("exif")  # get raw exif data
        print(f"########## {filename} ##########")
        print("format:", img.format, "| size:", img.size, "| mode:", img.mode)
        if exif_bytes is None:
            print("no EXIF data")
            return
        # print(f"{filename}: {exif_bytes.hex(' ')}")  # print only hex
        # print(f"{filename}: {exif_bytes}")  # print readable

        start = 6 if exif_bytes.startswith(b"Exif\x00\x00") else 0
        tiff = exif_bytes[start:]

        if len(tiff) < 8:  # 2 for byte order, 2 for tiff marker, 4 for offset
            raise ValueError("EXIF block is too short")

        byte_order = tiff[:2]
        if byte_order == b"II":
            endian = "little"
        elif byte_order == b"MM":
            endian = "big"
        else:
            raise ValueError("invalid byte-order marker")
        print(f"endian: {endian}")

        magic = int.from_bytes(tiff[2:4], endian)
        print(f"magic: {magic}")
        if magic != 42:
            raise ValueError("invalid TIFF marker")

        ifd0_offset = int.from_bytes(tiff[4:8], endian)
        print(f"ifd0_offset: {ifd0_offset}")

        count = int.from_bytes(tiff[ifd0_offset:ifd0_offset + 2], endian)
        print(f"tags count: {count}")

        for i in range(count):
            entry = ifd0_offset + 2 + i * 12  # @ entry is 12 bytes long
            tag_id = int.from_bytes(tiff[entry:entry + 2], endian)
            val_type = int.from_bytes(tiff[entry + 2:entry + 4], endian)
            value = int.from_bytes(tiff[entry + 4:entry + 8], endian)
            # offset = int.from_bytes(tiff[entry + 8:entry + 12], endian)
            print("---------------------------------")
            # print(f"tag: {tag_id}")
            # print(f"valuetype: {val_type}")
            # print(f"value: {value}")
            # print(f"offset: {offset}")
            print(f"tag: {ExifTags.TAGS.get(tag_id, f'Unknown tag ({tag_id})')}")
            print(f"valuetype: {TiffTags.TYPES.get(val_type, f'Unknown type ({val_type})')}")

            field = tiff[entry + 8:entry + 12]
            value_length = TYPE_SIZE[val_type] * value

            if value_length <= 4:
                real_value = field[:value_length]
            else:
                value_offset = int.from_bytes(field, endian)
                real_value = tiff[value_offset:value_offset + value_length]

            if val_type == 2:  # ASCII
                decoded_value = real_value.rstrip(b"\x00").decode("ascii", errors="replace")
            elif val_type == 3:  # SHORT
                decoded_value = [
                    int.from_bytes(real_value[i:i + 2], endian)
                    for i in range(0, len(real_value), 2)
                ]
                if len(decoded_value) == 1:
                    decoded_value = decoded_value[0]
            elif val_type == 4:  # LONG
                decoded_value = [
                    int.from_bytes(real_value[i:i + 4], endian)
                    for i in range(0, len(real_value), 4)
                ]
                if len(decoded_value) == 1:
                    decoded_value = decoded_value[0]
            else:
                decoded_value = real_value.hex(" ")
            print(f"value: {decoded_value}")

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
    # get_tags(images)
    get_tags2(images)



if __name__ == "__main__":
    scorpion()
