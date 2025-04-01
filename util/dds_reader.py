from binary_reader import BinaryReader


def get_valid_mipmapcount(res):
    actualcount = 0
    while res != 1:
        actualcount += 1
        res = res // 2
    actualcount += 1
    return actualcount


def read_dds_file(filepath, mipmap_count):

    with open(filepath, "rb") as f:
        reader = BinaryReader(f.read())

    dds_total_filesize = reader.size()

    magic = reader.read_str(4)
    if magic != "DDS ":
        raise Exception("Invalid DDS file")

    reader.seek(4)
    image_data_pointer = reader.read_uint32()

    reader.seek(12)
    image_x = reader.read_uint32()
    image_y = reader.read_uint32()

    reader.seek(28)
    dds_mipmap_count = reader.read_uint32()

    # https://stackoverflow.com/questions/57025836/how-to-check-if-a-given-number-is-a-power-of-two
    # funk for power of 2 checks
    if (
        image_x == image_y
        and ((image_x & (image_x - 1) == 0) and image_x != 0)
        and ((image_y & (image_y - 1) == 0) and image_y != 0)
    ):
        if (
            dds_mipmap_count >= mipmap_count
            and dds_mipmap_count >= 0
            and mipmap_count >= 0
        ):
            pass
        else:
            print(
                f"Got a mipmap count greater than original, snapping to export limit \nOriginal mipmap count:{dds_mipmap_count}, Got:{mipmap_count}"
            )
            mipmap_count = get_valid_mipmapcount(image_x)
            # raise Exception(f"Not enough mipmaps exist! \nOriginal mipmap count:{ddsmipmap_count}, Got:{mipmap_count}")
    else:
        raise Exception(
            f"Image has either unequal dimensions or is not a power of 2! \n{image_x,image_y}"
        )

    bytes_to_copy = 0
    compres_x = image_x
    compres_y = image_y
    for i in range(mipmap_count):
        if i == 0:
            bytes_to_copy += image_x * image_y
        else:
            bytes_to_copy += (compres_x // 2) * (compres_y // 2)
            compres_x = compres_x // 2
            compres_y = compres_y // 2

    if mipmap_count != dds_mipmap_count:
        reader.seek(image_data_pointer + 4)

        # its to prevent non uniformity, next block is "aligned" by 16 bytes
        if bytes_to_copy % 16 != 0:
            bytes_to_copy = (bytes_to_copy // 16 + 1) * 16

        export_data = reader.read_bytes(bytes_to_copy)
        print(len(export_data), dds_total_filesize, len(export_data) / 16,end=" ")
        print("[DONE]")
        return export_data, mipmap_count, image_x

    elif mipmap_count == dds_mipmap_count:
        reader.seek(image_data_pointer + 4)
        bytesize = dds_total_filesize - (image_data_pointer + 4)
        export_data = reader.read_bytes(bytesize)
        print(len(export_data), dds_total_filesize, len(export_data) / 16,end=" ")
        print("[DONE]")
        return export_data, mipmap_count, image_x
    else:
        raise Exception("Could not retrieve image data")
