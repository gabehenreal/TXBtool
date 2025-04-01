import os
import csv
import sys
from tkinter import filedialog
from binary_reader import BinaryReader
from util.median_cut_alpha import median_cut_quantize_rgba
from util.dds_reader import read_dds_file


def get_txb_data(txb_filepath):
    with open(txb_filepath, "rb") as f:
        reader = BinaryReader(f.read())

    if reader.read_str(4) != "TXBP":
        raise Exception("Invalid TXB file")

    imagecounts = reader.read_uint32()
    unoff_filesize = reader.read_uint32()
    reader.seek(0)
    headerdata = reader.read_bytes(32)

    skip_bytes = 32
    subheader_datas = []
    mipmap_counts = []
    flags = []
    ddscount = 0
    ps2count = 0
    ps2_16count = 0
    for i in range(imagecounts):
        reader.seek(skip_bytes)
        header_filesize = reader.read_uint32()
        resolution = reader.read_uint32()  ## dds txbs have only 1 res component
        txb_ddsmmc = reader.read_uint32() ## mipmap count IF this is a dds txb, in ps2 this wouldve been another res component
        txb_flag = reader.read_uint32()
        mipmap_counts.append(txb_ddsmmc)

        if txb_flag == 11 or txb_flag == 21 or txb_flag == 20:
            if txb_flag == 11:
                ddscount += 1
                flags.append(0)
            if txb_flag == 21:
                ps2count += 1
                flags.append(1)
            if txb_flag == 20:
                ps2_16count += 1
                flags.append(2)
        else:
            raise Exception(f"Unsupported TXB version {txb_flag}")

        reader.seek(skip_bytes)
        header_data_s = reader.read_bytes(32)
        subheader_datas.append(header_data_s)
        skip_bytes += 32 + header_filesize

    print(f"DDS images:{ddscount}")
    print(f"PS2(8bpp) images:{ps2count}")
    print(f"PS2(4bpp) images:{ps2_16count}")

    f.close()
    return headerdata, imagecounts, subheader_datas, mipmap_counts, flags


def main():
    print("TXBtool Ver 1.1")
    print("""Usage:

1) Creating PS3/PS2 txbs from image files:
    To select images your images to drag and drop or via the explorer window, select:
    a) one image if its a TXB haiving one image, or
    b) the last image and then shift- click to the first image if its a TXB having more than one image
        (ie. if you have 5 images, select the last one and then the first ),
    and then select your TXB file.
          
    For PS3 TXBS, accepted image input is ALWAYS DDS, for PS2 TXBS it is PNG files. 
    Make sure you DDS file are of DXT5 format, with mipmaps, when making PS3 TXB files.
    Make sure your .PNG files have alpha channel component, when making PS2 TXB files.
          
2) Creating PS2/PS3 TXBs from a text file.
    Select both the TXB file and the .TXT file having a format like:
    path-to-image1,weight1
    path-to-image2,weight2
    .
    .
    ,etc.
    The program will automatically exit after this.
          
3) Creating a "imagelist" from a collection of images:
    Select just the images to get a .txt file, you will then be prompted to save it to a location.
    Make sure the format is like how it is in Usage step 2, and image selection is based from the selection "quirk" in 1,
    otherwise image order WILL not be like how you intended.
    """)
    if len(sys.argv) > 1:
        filepaths = sys.argv[1:]
    else:
        filepaths = filedialog.askopenfilenames()

    export_txb_path = ""
    input_txt_path = ""
    image_paths = []
    alphaweights = []
    for path in filepaths:
        if os.path.exists(path):
            if "txb" in path[-3:].lower():
                export_txb_path = path
            elif "txt" in path[-3:].lower():
                input_txt_path = path
            else:
                image_paths.append(path)
                alphaweights.append(0.3)

    if export_txb_path != "":
        print("TXB:", export_txb_path)
        print("TXT:", input_txt_path)
        print("Input paths:")
        for k in image_paths:
            print(k)
    else:
        print("No TXB file was given")

    if len(image_paths) != 0 and export_txb_path == "":
        writepath = ""
        print(
            "Saving info to:",
            os.path.join(os.path.dirname(image_paths[-1]), "imagelists.txt"),
        )

        ask = input("Do you wish to save this .txt file at this path? (y/n)\n")
        if ask == "y" or ask == "Y":
            writepath = os.path.join(os.path.dirname(image_paths[-1]), "imagelists.txt")
        else:
            writepath = input(
                "Give the directory path to where you want to save the .txt file at.\n"
            )
            writepath = os.path.join(writepath, "imagelists.txt")
                   
        ### validate filetype
        for i in image_paths:
            if i[-3:].lower() not in ("png","dds"):
                print(i)
                raise Exception(
                    f"Expected an image format (.png, .dds, ), got {i[-3:].lower()}"
                )
               
        f = open(writepath, "w", newline="")
        csv_w = csv.writer(f)
        for i in image_paths:
            csv_w.writerow([i, 0.3])
        f.close()
        print(f"Wrote file to: {writepath}")

        sys.exit()

    ### if we do have a txt, take the inputfiles as well as alphaweights if applicable
    if export_txb_path != "" and input_txt_path != "":
        image_paths.clear()
        alphaweights.clear()

        f = open(input_txt_path, "r", newline="")
        csv_r = csv.reader(f)
        for i in csv_r:
            path = i[0]
            weight = i[1]
            print(path, weight)
            image_paths.append(path)
            alphaweights.append(float(weight))
        f.close()

    headerdata, count, subheader_datas, mipmapcounts, flags = get_txb_data(
        export_txb_path
    )
    if count != len(image_paths):
        raise Exception(
            f"Mismatch in image count, needed {count}, got {len(image_paths)}"
        )

    ### now we can start writing data
    writer = BinaryReader()
    writer.write_bytes(headerdata)
    cur_pos = writer.pos()
    txb_main_size = 0

    for k in range(count):
        cur_flag = flags[k]
        if cur_flag == 0:  # dds
            filepath_dds = image_paths[k]
            print(filepath_dds, cur_flag)
            if filepath_dds[-3:].lower() != "dds":
                raise Exception(
                    f"Expected a .DDS image, not a .{filepath_dds[-3:].lower()}"
                )

            exportdata, mipmap_count, res = read_dds_file(filepath_dds, mipmapcounts[k])
            writer.seek(cur_pos)

            if k == 0:
                txb_main_size = len(exportdata)

            writer.write_bytes(subheader_datas[k])
            writer.seek(cur_pos)
            writer.write_uint32(len(exportdata))
            writer.write_uint32(res)
            writer.write_uint32(mipmap_count)
            writer.seek(cur_pos + 32)
            writer.write_bytes(exportdata)
            cur_pos = writer.pos()

        if cur_flag == 1:  # ps2 8
            filepath_png = image_paths[k]
            print(filepath_png, cur_flag)
            if filepath_png[-3:].lower() != "png":
                raise Exception(
                    f"Expected a .PNG image, not a .{filepath_png[-3:].lower()}"
                )

            indices, pallete, resx, resy = median_cut_quantize_rgba(
                filepath_png, 256, alphaweights[k]
            )
            writer.seek(cur_pos)

            filesize = len(indices) + len(pallete) * 4
            if k == 0:
                txb_main_size = len(indices) + len(pallete) * 4

            writer.write_bytes(subheader_datas[k])
            writer.seek(cur_pos)
            writer.write_uint32(filesize)
            writer.write_uint32(resx)
            writer.write_uint32(resy)
            writer.seek(cur_pos + 32)
            for clr in pallete:
                writer.write_uint8(clr)
            writer.write_uint8(indices)
            cur_pos = writer.pos()

        if cur_flag == 2:  # ps2 4
            filepath_png = image_paths[k]
            print(filepath_png, cur_flag)
            if filepath_png[-3:].lower() != "png":
                raise Exception(
                    f"Expected a .PNG image, not a .{filepath_png[-3:].lower()}"
                )

            indices, pallete, resx, resy = median_cut_quantize_rgba(
                filepath_png, 16, alphaweights[k]
            )
            writer.seek(cur_pos)

            filesize = len(pallete) * 4 + (resx * resy) // 2
            if k == 0:
                txb_main_size = filesize

            writer.write_bytes(subheader_datas[k])
            writer.seek(cur_pos)
            writer.write_uint32(filesize)
            writer.write_uint32(resx)
            writer.write_uint32(resy)
            writer.seek(cur_pos + 32)
            for clr in pallete:
                writer.write_uint8(clr)

            # masterpiece by violet
            for inx in range(0, resx * resy, 2):
                indexByte = (indices[inx + 1] << 4) | (indices[inx] & 0xF)
                writer.write_bytes(bytes([indexByte]))
            cur_pos = writer.pos()

    writer.seek(8)
    writer.write_uint32(txb_main_size)

    ### overwrites files on default
    with open(export_txb_path, "wb") as f:
        f.write(writer.buffer())

    print(f"Done.\nWrote to {export_txb_path}\nProgram will automatically close.")

if __name__ == "__main__":
    main()
