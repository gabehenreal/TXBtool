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

To use the tool, just click on the tool and you will be greeted by a windows explorer screen asking you to select files.
There are mainly 2 types of export options:

1) TXB-Image combo:
   Basically, select the TXB and the images (ensure that your images have the same count as in the TXB) and press "ok" in the explorer.
2) TXB-TXT combo:
  If you have a list of imagepaths and their respective alphaweight values , you can just select the TXB and the TXT file for exporting.

If you want to make a "imagelists.txt" file, just select only the images and press "Open" in the explorer window.\
You will then be asked to confirm the path it will save to or else provide a path to an already existing TXT file\
(ie E:/johndoe/New folder/imagelists.txt and NOT E:/johndoe/New folder ). \
You will get a TXT file with filepaths and alphaweights which comes handy when compiling for PS2 256 color or 16 color image.

### Note:
  1) Selection order\
     If you have, for example 5 images named 1-0_0.png to 1-0_4.png and want to do TXB-Image combo, you **MUST** select the last image first (which is 1-0_4.png) and then the TXB or the first image if you are doing TXB-TXT combo, otherwise the order exported will be wrong.

  2) Alpha weights\
     Alpha weights dont actually "alter" your export image's alpha but rather is used by the algortithm for handling pixel comparison for PS2 image export and by default is set to 0.3.\
     If you notice your image has repeating colors/incorrect color, set it to 1 so that more of the alpha component of the image gets considered when comparing pixels.\
     If you set it to 0, more of the RGB component has higher priorty than the alpha component, which is great for color heavy images but will might compromise a bit on your alpha quality.\
     
     **Alpha weights can only be set with TXB-TXT combo.**
     
### Credits
  -SutandoTsukai, for his binary reader!
  -SamuraiOndo, for helping me with setting up 4bpp indexing code!
  -EdnessP, for allowing me to use his Noesis TXB script as a base!
  
### Code citations
  https://stackoverflow.com/questions/57025836/how-to-check-if-a-given-number-is-a-power-of-two \
  Algorithim for exporting PS2 256color and 16color image is based off from Paul Heckbert's Median cut image quatization

