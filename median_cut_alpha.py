from PIL import Image
import numpy as np

def encode_ps2_shift_to_pallete(palette_int):
    sliced_palette_int = palette_int[8:]                ### skips the first 8 entries
    temp_buffer =[]
    for i in range(8):
        chunk = sliced_palette_int[(32*i):32+(32*i)]    ## contains both the swap chunk and a normal chunk
        edit_chunk = chunk[:16]
        og_chunk = chunk[16:] 

                                                        #swaps done within "one" line
        temp_buffer.append(            [edit_chunk[8],edit_chunk[9],edit_chunk[10],edit_chunk[11],
                                        edit_chunk[12],edit_chunk[13],edit_chunk[14],edit_chunk[15],
                                        edit_chunk[0],edit_chunk[1],edit_chunk[2],edit_chunk[3],
                                        edit_chunk[4],edit_chunk[5],edit_chunk[6],edit_chunk[7]  ]
                          )
        temp_buffer.append(og_chunk)                    #retain the other original part

    final_palette = []                                  #make final palette
    for i in palette_int[:8]:                           #appends the excluded 8 entries
        final_palette.append(i)
    
    for k in temp_buffer:
        for j in k:
            final_palette.append(j)     
    return final_palette

def sort_pixels_by_highest_variance_channel(pixels):

    pixel_array = np.array(pixels)                                          
    variances = np.var(pixel_array, axis=0)                                   
    var_list = [variances[0],variances[1],variances[2]]                     
    dominant_channel = np.argmax(var_list)                                  
    sorted_pixels = sorted(pixels, key=lambda p: p[dominant_channel])       
    return sorted_pixels

def obtaineightmorefromthisbin(colorbin):
    ## this couldve been written a bit better....
    sorted_bin = colorbin
    morebins = [sorted_bin[:len(sorted_bin)//2],sorted_bin[len(sorted_bin)//2:] ]

    while len(morebins) < 8:
        temp = []
        for i in morebins:
            s_i = i
            temp.append(s_i[:len(s_i)//2])
            temp.append(s_i[len(s_i)//2:])
        morebins.clear()
        for k in temp:
            morebins.append(k)

    exp = []
    for i in range(8):
        bin_alt = morebins[i] 
        tot_r = 0
        tot_g = 0
        tot_b = 0
        tot_a = 0
        for j in bin_alt:
            tot_r += j[0]
            tot_g += j[1]
            tot_b += j[2]
            tot_a += j[3]
        if len(bin_alt) != 0:
            centroid = ( tot_r//len(bin_alt), tot_g//len(bin_alt), tot_b//len(bin_alt) ,tot_a//len(bin_alt))
        else:
            centroid = ( tot_r//1, tot_g//1, tot_b//1 ,tot_a//1)
        exp.append(centroid)

    return exp

def obtainfourmorefromthisbin(colorbin):
    ## this couldve been written a bit better.... and is a copy ...
    sorted_bin = colorbin
    morebins = [sorted_bin[:len(sorted_bin)//2],sorted_bin[len(sorted_bin)//2:] ]

    while len(morebins) < 4:
        temp = []
        for i in morebins:
            s_i = i
            temp.append(s_i[:len(s_i)//2])
            temp.append(s_i[len(s_i)//2:])
        morebins.clear()
        for k in temp:
            morebins.append(k)

    exp = []
    for i in range(4):
        bin_alt = morebins[i] 
        tot_r = 0
        tot_g = 0
        tot_b = 0
        tot_a = 0
        for j in bin_alt:
            tot_r += j[0]
            tot_g += j[1]
            tot_b += j[2]
            tot_a += j[3]
        centroid = ( tot_r//len(bin_alt), tot_g//len(bin_alt), tot_b//len(bin_alt) ,tot_a//len(bin_alt))
        exp.append(centroid)

    return exp


def assign_colors(pixels, centroids, alpha_influence):
        
        pixel_array = np.array(pixels, dtype=np.float32)        # Shape (num_pixels, 4)
        centroid_array = np.array(centroids, dtype=np.float32)  # Shape (num_centroids, 4)
        alpha_weights = pixel_array[:, 3:4] / 255.0             # Normalize alpha between 0-1
        alpha_weights = alpha_weights * alpha_influence         # Scale by user-defined influence

        # Compute squared Euclidean distance for RGB
        rgb_distances = np.sum((pixel_array[:, None, :3] - centroid_array[:, :3]) ** 2, axis=2)
        # Compute weighted alpha distance
        alpha_distances = ((pixel_array[:, None, 3] - centroid_array[:, 3]) ** 2) * alpha_weights
        total_distances = rgb_distances + alpha_distances
        closest_indices = np.argmin(total_distances, axis=1)
        closest_colors = [tuple(map(int, centroid_array[idx])) for idx in closest_indices]

        return closest_colors, closest_indices.tolist()

### main defintions
def median_cut_quantize_rgba_256(image_path,alpha_influence=0.3):

    img = Image.open(image_path).convert("RGBA")                    
    pixels = []

    width, height = img.size
    print( width, height)

    for y in range(width):                                          ##probably could be done in 1 line rather than this
        for x in range(height):          
            r, g, b, a = img.getpixel((x, y))
            pixels.append((r, g, b, a))
    sorted_pixels = sort_pixels_by_highest_variance_channel(pixels)

    avg = []
    bins = [sorted_pixels[:len(sorted_pixels)//2],sorted_pixels[len(sorted_pixels)//2:] ]
    while len(bins) < 256:
        temp = []
        for i in bins:
            s_i = sort_pixels_by_highest_variance_channel(i)    # very important that this is done
            temp.append(s_i[:len(s_i)//2])
            temp.append(s_i[len(s_i)//2:])
        bins.clear()
        for k in temp:
            bins.append(k)

    avg1 ,avg2 ,avg3 ,avg4 ,avg5 ,avg6 ,avg7 ,avg8 = [],[],[],[],[],[],[],[], 
    for i in range(256):

        clrbin = bins[i]  
        tot_r = 0
        tot_g = 0
        tot_b = 0
        tot_a = 0
        for j in clrbin:
            tot_r += j[0]
            tot_g += j[1]
            tot_b += j[2]
            tot_a += j[3]
        centroid = ( tot_r//len(clrbin), tot_g//len(clrbin), tot_b//len(clrbin) ,tot_a//len(clrbin))
        
        potentialcolors = obtaineightmorefromthisbin(clrbin)
        
        ### could be written better?
        c1 = potentialcolors[0]
        c2 = potentialcolors[1]
        c3 = potentialcolors[2]
        c4 = potentialcolors[3]
        c5 = potentialcolors[4]
        c6 = potentialcolors[5]
        c7 = potentialcolors[6]
        c8 = potentialcolors[7]

        avg1.append(c1)
        avg2.append(c2)
        avg3.append(c3)
        avg4.append(c4)
        avg5.append(c5)
        avg6.append(c6)
        avg7.append(c7)
        avg8.append(c8)

        if centroid not in avg:
            avg.append(centroid)
        
    ## fill up unused spots with colors from those avg bins
    extra_clr_list = []
    listoflists = [avg8,avg7,avg6,avg5,avg4,avg3,avg2,avg1]
    count = 0
    for i in range(8):
        parselist = []

        # alternate where the colors are being taken from
        if i%2 == 0:
            parselist = listoflists[i][::-1]
        else:
            parselist = listoflists[i]
        if i == 7:
            print(count)
            for j in range((256-len(avg))-count):
                extra_clr_list.append(parselist[j])
        else:
            count += ((256-len(avg))//8 ) + 1
            for j in range(((256-len(avg))//8 ) + 1):
                extra_clr_list.append(parselist[j])

    print(len(avg), 256-len(avg),len(extra_clr_list) )
    for j in range (256-len(avg)):
        avg.append(extra_clr_list[-1*(j+1)])

    image_final, actualfinal = assign_colors(pixels, avg, alpha_influence) ##image_final was used to directly export it to png for preview
    return actualfinal, encode_ps2_shift_to_pallete(avg), height, width


def median_cut_quantize_rgba_16(image_path,alpha_influence=0.3):

    # a literal reuse of the 256 one, but now for 16, i will rewrite one day
    img = Image.open(image_path).convert("RGBA")                    
    pixels = []

    width, height = img.size
    print( width, height)

    for y in range(width):                                          ## obtain la pixels, probably can be done in 1 line rather than this
        for x in range(height):          
            r, g, b, a = img.getpixel((x, y))
            pixels.append((r, g, b, a))
    sorted_pixels = sort_pixels_by_highest_variance_channel(pixels)

    avg = []
    bins = [sorted_pixels[:len(sorted_pixels)//2],sorted_pixels[len(sorted_pixels)//2:] ]

    while len(bins) < 16:
        temp = []
        for i in bins:
            s_i = sort_pixels_by_highest_variance_channel(i)    # very important that this is done
            temp.append(s_i[:len(s_i)//2])
            temp.append(s_i[len(s_i)//2:])
        bins.clear()
        for k in temp:
            bins.append(k)

    avg1 ,avg2 ,avg3 ,avg4 = [],[],[],[]

    for i in range(16):

        clrbin = bins[i]   
        tot_r = 0
        tot_g = 0
        tot_b = 0
        tot_a = 0
        for j in clrbin:
            tot_r += j[0]
            tot_g += j[1]
            tot_b += j[2]
            tot_a += j[3]
        centroid = ( tot_r//len(clrbin), tot_g//len(clrbin), tot_b//len(clrbin) ,tot_a//len(clrbin))
        
        potentialcolors = obtainfourmorefromthisbin(clrbin)
        
        ### could be written better?
        c1 = potentialcolors[0]
        c2 = potentialcolors[1]
        c3 = potentialcolors[2]
        c4 = potentialcolors[3]

        avg1.append(c1)
        avg2.append(c2)
        avg3.append(c3)
        avg4.append(c4)

        if centroid not in avg:
            avg.append(centroid)
        
    ## fill up unused spots with colors from those avg bins
    extra_clr_list = []
    listoflists = [avg4,avg3,avg2,avg1]
    count = 0
    for i in range(4):
        parselist = []

        # alternate where the colors are being taken from
        if i%2 == 0:
            parselist = listoflists[i][::-1]
        else:
            parselist = listoflists[i]
        if i == 3:
            print(count)
            for j in range((16-len(avg))-count):
                extra_clr_list.append(parselist[j])
        else:
            count += ((16-len(avg))//4 ) + 1
            for j in range(((16-len(avg))//4 ) + 1):
                extra_clr_list.append(parselist[j])

    print(len(avg), 16-len(avg),len(extra_clr_list) )
    for j in range (16-len(avg)):
        avg.append(extra_clr_list[-1*(j+1)])

    image_final, actualfinal = assign_colors(pixels, avg, alpha_influence) ##image_final was used to directly export it to png for previe
    return actualfinal, avg, height, width