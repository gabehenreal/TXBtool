# TXBtool
A Python tool that converts DXT5 DDS files to Yakuza 1&2 (PS3 ONLY) TXB's and .PNG's to PS2 Yakuza 1&2 TXB's.

### Supported Input files:
1) DDS (DXT5)
2) PNG

### Supported Input TXB filetypes:
1) Flag 11 (DXT5 DDS)
2) Flag 21 (8bpp {256 color} CLUT based TXB)
3) Flag 20 (4bpp {16 color} CLUT based TXB)

### Usage:

1) Creating PS3/PS2 txbs from image files:\
    To select images your images to drag and drop or via the explorer window, select:\
    a) one image if its a TXB haiving one image, or\
    b) the last image and then shift- click to the first image if its a TXB having more than one image\
        (ie. if you have 5 images, select the last one and then the first ),\
    and then select your TXB file.
          
    For PS3 TXBS, accepted image input is ALWAYS DDS, for PS2 TXBS it is PNG files. \
    Make sure you DDS file are of DXT5 format, with mipmaps, when making PS3 TXB files.\
    Make sure your .PNG files have alpha channel component, when making PS2 TXB files.

          
2) Creating PS2/PS3 TXBs from a text file.\
    Select both the TXB file and the .TXT file having a format like:
    > path-to-image_1,weight_1\
    > path-to-image_2,weight_2\
    > .\
    > .\
    > path-to-image_n,weight_n
    
    The program will automatically exit after this.

3) Creating a "imagelist" from a collection of images:\
    Select just the images to get a .txt file, you will then be prompted to save it to a location.\
    Make sure the format is like how it is in Usage step 2, and image selection is based from the selection "quirk" in 1,\
    otherwise image order WILL not be like how you intended.
   
### Note:
  1) Alpha weights\
     Alpha weights dont actually "alter" your export image's alpha but rather is used by the algortithm for handling pixel comparison for PS2 image export and by default is set to 0.3.\
     A value of 1 means alpha is considered in color comparisons , whereas if the value is 0, the alpha is not considered as much as the R,G,B components (alpha is just 0).\
     Any value in between just affects or "weights" the alpha during comparison.\
     If you see repeating or inccorect colors, try setting the value lower than 0.3.\
     
     **Alpha weights can only be set with TXB-TXT combo.**
     
### Credits
   Special thanks goes to:\
  -[SutandoTsukai](https://github.com/mosamadeeb) for his [binary reader](https://github.com/mosamadeeb/PyBinaryReader)!\
  -[SamuraiOndo](https://github.com/SamuraiOndo), for helping me with setting up 4bpp indexing code!\
  -[EdnessP](https://github.com/EdnessP), for allowing me to use his Noesis TXB script as a base!

## Suggested Tools:
   -Use [DATman](https://github.com/SamuraiOndo/DATMan) by [SamuraiOndo](https://github.com/SamuraiOndo) for extraction of DAT files and other archives like arc,bin etc.\
   -Use [EdnessP](https://github.com/EdnessP)'s [Noesis TXB script](https://github.com/EdnessP/scripts/blob/main/other/tex_Yakuza.py) for extracting images from TXB's.
  
### Code citations
  https://stackoverflow.com/questions/57025836/how-to-check-if-a-given-number-is-a-power-of-two \
  Algorithim for exporting PS2 256 color and 16 color image is based off from Paul Heckbert's Median cut image quatization.

