from binary_reader import BinaryReader

def get_valid_mipmapcount(res):
    actualcount = 1
    res_buf = res//2
    while True:
        if res_buf == 1:
            actualcount += 1
            break
        else:
            actualcount += 1
            new = res_buf//2
            res_buf = new
    return actualcount

def read_dds_file(filepath,mipmap_count):

    f = open(filepath,"rb")
    reader = BinaryReader(f.read())
    ddstotalfilesize = f.tell()

    magic = reader.read_str(4)
    if magic == "DDS ":
        print("Valid DDS file")
    else:
        raise Exception("Invalid DDS file")
    
    reader.seek(4,0)
    imagedatapointer = reader.read_uint32()

    reader.seek(12,0)
    imagex = reader.read_uint32()
    imagey = reader.read_uint32()

    reader.seek(28,0)
    ddsmipmap_count = reader.read_uint32()

    # https://stackoverflow.com/questions/57025836/how-to-check-if-a-given-number-is-a-power-of-two
    # funk for power of 2 checks
    if imagex == imagey and ((imagex & (imagex-1) == 0) and imagex != 0) and ((imagey & (imagey-1) == 0) and imagey != 0):
        if ddsmipmap_count >= mipmap_count and ddsmipmap_count >=0 and mipmap_count >=0:
            pass
        else:
            print(f"Got a mipmap count greater than original, snapping to export limit \nOriginal mipmap count:{ddsmipmap_count}, Got:{mipmap_count}")
            mipmap_count = get_valid_mipmapcount(imagex)
            #raise Exception(f"Not enough mipmaps exist! \nOriginal mipmap count:{ddsmipmap_count}, Got:{mipmap_count}")
    else:
        raise Exception(f"Image has either unequal dimenstions or is not a power of 2! \n{imagex,imagey}")

    bytestobecopiedamt = 0
    compresx = imagex
    compresy = imagey
    for i in range(mipmap_count):
        if  i == 0:
            bytestobecopiedamt += imagex*imagey
        else:
            bytestobecopiedamt += (compresx//2)*(compresy//2)
            compresx = compresx//2
            compresy = compresy//2
    
    if mipmap_count != ddsmipmap_count:
        reader.seek(imagedatapointer+4 , 0)

        ### its to prevent non uniformity, next block is "aligned" by 16 bytes 
        if bytestobecopiedamt%16 != 0:
            bytestobecopiedamt = (bytestobecopiedamt//16 + 1)*16

        exportdata = reader.read_bytes(bytestobecopiedamt)
        print(len(exportdata),ddstotalfilesize, len(exportdata)/16 )

        f.close()
        return exportdata,mipmap_count,imagex

    elif mipmap_count == ddsmipmap_count:
        reader.seek(imagedatapointer+4 , 0)
        bytesize = ddstotalfilesize -(imagedatapointer+4)
        exportdata = reader.read_bytes(bytesize)
        print(len(exportdata),ddstotalfilesize,len(exportdata)/16)

        f.close()
        return exportdata,mipmap_count,imagex
    else:
        f.close()
        raise Exception("Could not retrive image data")
