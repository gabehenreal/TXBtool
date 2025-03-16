import os
import csv
from tkinter import filedialog
from binary_reader import BinaryReader
from median_cut_alpha import median_cut_quantize_rgba_256,median_cut_quantize_rgba_16
from dds_reader import read_dds_file

def get_txb_data(txbfilepath):
    f = open(txbfilepath,"rb")
    reader = BinaryReader(f.read())

    if reader.read_str(4) == "TXBP":
        print("\nValid TXB file")
    else:
        raise Exception("Invalid TXB file")
    
    imagecounts = reader.read_uint32()
    unoff_filesize = reader.read_uint32()
    reader.seek(0)
    headerdata = reader.read_bytes(32)

    skipbytes = 32
    subheader_datas = []
    mipmapcounts = []
    flags = []
    ddscount = 0
    ps2count = 0
    ps2_16count = 0
    for i in range(imagecounts):
        reader.seek(skipbytes)
        headerfilesize = reader.read_uint32()
        resolution = reader.read_uint32() ## dds txbs have only 1 res component
        txb_ddsmmc = reader.read_uint32() ## mipmap count IF this is a dds txb, in ps2 this wouldve been another res component
        txbflag = reader.read_uint32()
        mipmapcounts.append(txb_ddsmmc)

        if txbflag == 11 or txbflag == 21 or txbflag == 20:
            if txbflag == 11:
                ddscount += 1
                flags.append(0)
            if txbflag == 21:
                ps2count += 1
                flags.append(1)
            if txbflag == 20:
                ps2_16count += 1
                flags.append(2)
        else:
            raise Exception(f"Unsupported TXB version {txbflag}")

        reader.seek(skipbytes)    
        header_data_s = reader.read_bytes(32)
        subheader_datas.append(header_data_s)
        skipbytes += 32+headerfilesize

    print(f"DDS images:{ddscount}")
    print(f"PS2(8bpp) images:{ps2count}")    
    print(f"PS2(4bpp) images:{ps2_16count}")  
    
    f.close()
    return headerdata, imagecounts, subheader_datas, mipmapcounts, flags
 
# MAIN
#filepaths = sys.argv[1:]
print("TXBtool Ver 1.0")
filepaths = filedialog.askopenfilenames()

export_txb_path = ""                                                    
input_txt_path = ""                                                     
inputpaths = []
alphaweights = []
for path in filepaths:
    if "txb" in path[-3:].lower() and os.path.exists(path) == True:
        export_txb_path = path
    elif "txt" in path[-3:].lower() and os.path.exists(path) == True:
        input_txt_path = path
    else:
        inputpaths.append(path)
        alphaweights.append(0.3)

if export_txb_path != "":
    print("TXB:",export_txb_path)
    print("TXT:",input_txt_path)
    print("Input paths:")
    for k in inputpaths:
        print(k)
else:
    print("No TXB file was given")

if len(inputpaths) != 0 and export_txb_path == "":
    writepath = ""
    print("Saving info to:",os.path.join(os.path.dirname(inputpaths[-1]),"imagelists.txt"))

    ask = input("Do you wish to save data at this path? (y/n)\n")
    if ask == "y" or ask == "Y":
        writepath = os.path.join(os.path.dirname(inputpaths[-1]),"imagelists.txt")
    else:
        writepath = input("Give the directory path to the .txt file you wish to save at.\n")

    f = open(writepath,"w",newline="")
    csv_w = csv.writer(f)
    for i in inputpaths:
        csv_w.writerow([i, 0.3])
    f.close()
    print(f"Wrote file to:{writepath}")

### if we do have a txt, take the inputfiles as well as alphaweights if applicable
if export_txb_path != "" and input_txt_path != "" :
    inputpaths.clear()
    alphaweights.clear()

    f=open(input_txt_path,'r',newline='')
    csv_r=csv.reader(f)
    for i in csv_r:
        path = i[0]
        weight = i[1]
        print(path,weight)
        inputpaths.append(path)
        alphaweights.append(float(weight))

    f.close()

headerdata, count, subheader_datas, mipmapcounts, flags = get_txb_data(export_txb_path)
if count == len(inputpaths):
    pass
else:
    raise Exception(f"Mismatch in image count, needed {count}, got {len(inputpaths)}")

### now we can start writing data
writer = BinaryReader()
writer.write_bytes(headerdata)
curpos = writer.pos()
txb_main_size = 0

for k in range(count):
    cur_flag = flags[k]
    if cur_flag == 0:               #dds
            filepath_dds = inputpaths[k]
            print(filepath_dds,cur_flag)
            if filepath_dds[-3:].lower() == "dds":
                pass
            else:
                raise Exception(f"Expected a .DDS image, not a .{filepath_dds[-3:].lower()}")

            exportdata,mipmap_count,res = read_dds_file(filepath_dds,mipmapcounts[k])
            writer.seek(curpos,0)

            if k == 0:
                txb_main_size = len(exportdata)
            
            writer.write_bytes(subheader_datas[k])
            writer.seek(curpos,0)
            writer.write_uint32(len(exportdata))
            writer.write_uint32(res)
            writer.write_uint32(mipmap_count)
            writer.seek(curpos+32,0)
            writer.write_bytes(exportdata)
            curpos = writer.pos()

    if cur_flag == 1:           # ps2 8
            filepath_png = inputpaths[k]
            print(filepath_png,cur_flag)
            if filepath_png[-3:].lower() == "png":
                pass
            else:
                raise Exception(f"Expected a .PNG image, not a .{filepath_png[-3:].lower()}")

            indices,pallete,resx,resy = median_cut_quantize_rgba_256(filepath_png,alphaweights[k])
            writer.seek(curpos,0)

            thisfilesize = len(indices)+len(pallete)*4
            if k == 0:
                txb_main_size = len(indices)+len(pallete)*4

            writer.write_bytes(subheader_datas[k])
            writer.seek(curpos,0)
            writer.write_uint32(thisfilesize)
            writer.write_uint32(resx)
            writer.write_uint32(resy)
            writer.seek(curpos+32,0)           
            for clr in pallete:
                writer.write_uint8(clr[0])
                writer.write_uint8(clr[1])
                writer.write_uint8(clr[2])
                writer.write_uint8(clr[3])
            for inx in indices:
                writer.write_uint8(inx)
            curpos = writer.pos()
            
    if cur_flag == 2:           # ps2 4
            filepath_png = inputpaths[k]
            print(filepath_png,cur_flag)
            if filepath_png[-3:].lower() == "png":
                pass
            else:
                raise Exception(f"Expected a .PNG image, not a .{filepath_png[-3:].lower()}")

            indices,pallete,resx,resy = median_cut_quantize_rgba_16(filepath_png,alphaweights[k])
            writer.seek(curpos,0)

            thisfilesize = len(pallete)*4+ (resx*resy)//2
            if k == 0:
                txb_main_size = thisfilesize

            writer.write_bytes(subheader_datas[k])
            writer.seek(curpos,0)
            writer.write_uint32(thisfilesize)
            writer.write_uint32(resx)
            writer.write_uint32(resy)
            writer.seek(curpos+32,0)           
            for clr in pallete:
                writer.write_uint8(clr[0])
                writer.write_uint8(clr[1])
                writer.write_uint8(clr[2])
                writer.write_uint8(clr[3])

            # masterpiece by violet
            for inx in range(0,resx*resy,2):
                indexByte = (indices[inx+1] << 4) | (indices[inx] & 0xF)
                writer.write_bytes(bytes([indexByte]))
            curpos = writer.pos()

writer.seek(8,0)
writer.write_uint32(txb_main_size)

### overwrites files on default
file = open(export_txb_path,'wb')
file.write(writer.buffer())
file.close()

print("Done")