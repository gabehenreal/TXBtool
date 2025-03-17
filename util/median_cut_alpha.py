from PIL import Image
import numpy as np


def encode_ps2_shift_to_pallete(palette_int):
    sliced_palette_int = palette_int[8:]  ### skips the first 8 entries
    temp_buffer = []
    for i in range(8):
        chunk = sliced_palette_int[
            (32 * i) : 32 + (32 * i)
        ]  ## contains both the swap chunk and a normal chunk
        edit_chunk = chunk[:16]
        og_chunk = chunk[16:]

        # swaps done within "one" line
        temp_buffer.append(
            [
                edit_chunk[8], edit_chunk[9], edit_chunk[10], edit_chunk[11],
                edit_chunk[12], edit_chunk[13], edit_chunk[14], edit_chunk[15],
                edit_chunk[0], edit_chunk[1], edit_chunk[2], edit_chunk[3],
                edit_chunk[4], edit_chunk[5], edit_chunk[6], edit_chunk[7]
            ]
        )
        temp_buffer.append(og_chunk)  # retain the other original part

    final_palette = []  # make final palette
    for i in palette_int[:8]:  # appends the excluded 8 entries
        final_palette.append(i)

    for k in temp_buffer:
        for j in k:
            final_palette.append(j)
    return final_palette


def sort_pixels_by_highest_variance_channel(pixels):
    pixel_array = np.array(pixels)
    variances = np.var(pixel_array, axis=0)
    var_list = [variances[0], variances[1], variances[2]]
    dominant_channel = np.argmax(var_list)
    sorted_pixels = sorted(pixels, key=lambda p: p[dominant_channel])
    return sorted_pixels


def obtain_from_bin(color_bin, count):
    # this couldve been written a bit better....
    sorted_bin = color_bin
    more_bins = [sorted_bin[: len(sorted_bin) // 2], sorted_bin[len(sorted_bin) // 2 :]]

    while len(more_bins) < count:
        temp = []
        for i in more_bins:
            s_i = i
            temp.append(s_i[: len(s_i) // 2])
            temp.append(s_i[len(s_i) // 2 :])
        more_bins.clear()
        for k in temp:
            more_bins.append(k)

    exp = []
    for i in range(count):
        bin_alt = more_bins[i]
        rgba = [[0]] * 4
        for j in bin_alt:
            for o in j:
                rgba[o] += j[o]

        if len(bin_alt) != 0:
            centroid = (
                rgba[0] // len(bin_alt),
                rgba[1] // len(bin_alt),
                rgba[2] // len(bin_alt),
                rgba[3] // len(bin_alt),
            )
        else:
            centroid = (rgba[0], rgba[1], rgba[2], rgba[3])
        exp.append(centroid)

    return exp


def assign_colors(pixels, centroids, alpha_influence):

    pixel_array = np.array(pixels, dtype=np.float32)  # Shape (num_pixels, 4)
    centroid_array = np.array(centroids, dtype=np.float32)  # Shape (num_centroids, 4)
    alpha_weights = pixel_array[:, 3:4] / 255.0  # Normalize alpha between 0-1
    alpha_weights = alpha_weights * alpha_influence  # Scale by user-defined influence

    # Compute squared Euclidean distance for RGB
    rgb_distances = np.sum(
        (pixel_array[:, None, :3] - centroid_array[:, :3]) ** 2, axis=2
    )
    # Compute weighted alpha distance
    alpha_distances = (
        (pixel_array[:, None, 3] - centroid_array[:, 3]) ** 2
    ) * alpha_weights
    total_distances = rgb_distances + alpha_distances
    closest_indices = np.argmin(total_distances, axis=1)
    closest_colors = [tuple(map(int, centroid_array[idx])) for idx in closest_indices]

    return closest_colors, closest_indices.tolist()


### main defintions
def median_cut_quantize_rgba(image_path, size, alpha_influence=0.3):

    img = Image.open(image_path).convert("RGBA")
    pixels = []

    width, height = img.size
    print(width, height)

    for y in range(width):  # probably could be done in 1 line rather than this
        for x in range(height):
            r, g, b, a = img.getpixel((x, y))
            pixels.append((r, g, b, a))
    sorted_pixels = sort_pixels_by_highest_variance_channel(pixels)

    avg = []
    bins = [
        sorted_pixels[: len(sorted_pixels) // 2],
        sorted_pixels[len(sorted_pixels) // 2 :],
    ]
    while len(bins) < size:
        temp = []
        for i in bins:
            s_i = sort_pixels_by_highest_variance_channel(
                i
            )  # very important that this is done
            temp.append(s_i[: len(s_i) // 2])
            temp.append(s_i[len(s_i) // 2 :])
        bins.clear()
        for k in temp:
            bins.append(k)

    averages = [[]] * (8 if size == 256 else 4)
    for i in range(size):
        clrbin = bins[i]
        rgba = [[0]] * 4
        for j in clrbin:
            for o in j:
                rgba[o] += j[o]

        centroid = (
            rgba[0] // len(clrbin),
            rgba[1] // len(clrbin),
            rgba[2] // len(clrbin),
            rgba[3] // len(clrbin),
        )

        potential_colors = obtain_from_bin(clrbin, len(averages))

        for i in range(len(potential_colors)):
            averages[i].append(potential_colors[i])

        if centroid not in avg:
            avg.append(centroid)

    ## fill up unused spots with colors from those avg bins
    extra_clr_list = []
    averages.reverse()
    count = 0
    for i in range(len(averages)):
        parselist = []
        # alternate where the colors are being taken from
        if i % 2 == 0:
            parselist = averages[i][::-1]
        else:
            parselist = averages[i]
        if i == 7:
            print(count)
            for j in range((size - len(avg)) - count):
                extra_clr_list.append(parselist[j])
        else:
            count += ((size - len(avg)) // 8) + 1
            for j in range(((size - len(avg)) // 8) + 1):
                extra_clr_list.append(parselist[j])

    print(len(avg), size - len(avg), len(extra_clr_list))
    for j in range(size - len(avg)):
        avg.append(extra_clr_list[-1 * (j + 1)])
    image_final, actualfinal = assign_colors(
        pixels, avg, alpha_influence
    )  ##image_final was used to directly export it to png for preview
    return actualfinal, encode_ps2_shift_to_pallete(avg), height, width
