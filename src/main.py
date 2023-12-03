from PIL import Image
import collections
import itertools
import turtle
from colormath.color_objects import LabColor
from colormath.color_diff import delta_e_cie2000
import numpy
from collections import namedtuple


# This is a quick fix for an issue of a deprecated function within NumPy
def patch_asscalar(a):
    return a.item()


setattr(numpy, "asscalar", patch_asscalar)


# This function takes a list of RGBs ([r, g, b]) and converting them to the LAB Color Space
def convert_rgb_to_lab(rgb_list):
    num = 0
    # created list RGB and initialized with 0
    rgb = [0, 0, 0]
    for value in rgb_list:
        value = float(value) / 255
        if value > 0.04045:
            value = ((value + 0.055) / 1.055) ** 2.4
        else:
            value = value / 12.92
        rgb[num] = value * 100
        num = num + 1

    XYZ = [
        0,
        0,
        0,
    ]

    # converted all the three R, G, B to X, Y, Z
    X = rgb[0] * 0.4124 + rgb[1] * 0.3576 + rgb[2] * 0.1805
    Y = rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722
    Z = rgb[0] * 0.0193 + rgb[1] * 0.1192 + rgb[2] * 0.9505
    # rounded off the values upto 4 decimal digit
    XYZ[0] = round(X, 4)
    XYZ[1] = round(Y, 4)
    XYZ[2] = round(Z, 4)
    XYZ[0] = float(XYZ[0]) / 95.047  # ref_X =  95.047   Observer= 2°, Illuminant= D65
    XYZ[1] = float(XYZ[1]) / 100.0  # ref_Y = 100.000
    XYZ[2] = float(XYZ[2]) / 108.883  # ref_Z = 108.883

    num = 0
    for value in XYZ:
        if value > 0.008856:
            value = value ** (0.3333333333333333)
        else:
            value = (7.787 * value) + (16 / 116)
        XYZ[num] = value
        num = num + 1

    # formed Lab list and initialize with 0
    Lab = [0, 0, 0]
    # found L, A, and B
    L = (116 * XYZ[1]) - 16
    a = 500 * (XYZ[0] - XYZ[1])
    b = 200 * (XYZ[1] - XYZ[2])
    # rounded off to 4 decimal digit
    Lab[0] = round(L, 4)
    Lab[1] = round(a, 4)
    Lab[2] = round(b, 4)
    # return the list (variable: Lab) after having created the conversion
    return Lab


# This function runs the code which calculates the Delta E between two colors using the CIE2000 calculation.
# ....Input for this function are two RGB colors: rgbColor1, rgbColor2 = [r, g, b]
def calculate_deltaE_CIE2000(rgb_color1, rgb_color2):
    # first convert the two input RGB[r, g, b] to LAB[l, a, b]
    labList1 = convert_rgb_to_lab(rgb_color1)
    labColor1 = LabColor(lab_l=labList1[0], lab_a=labList1[1], lab_b=labList1[2])

    labList2 = convert_rgb_to_lab(rgb_color2)
    labColor2 = LabColor(lab_l=labList2[0], lab_a=labList2[1], lab_b=labList2[2])

    # return the calculated Delta E CIE2000 value
    return delta_e_cie2000(labColor1, labColor2)


# This function is used to iterate through the colors of an input image -> output is a map variable
def iterate_image_colors(img):
    coordinates = itertools.product(range(img.size[0]), range(img.size[1]))
    return map(img.getpixel, coordinates)


# This function is used to draw swatches of the most common RGBs of an image to the screen
def draw_common_rgb_swatches(list_common_rgbs):
    # initialize the various variables needed for creating the window for the swatches
    window = turtle.Screen()
    window.setup(525, 250)
    window.colormode(255)
    # settings for how things are drawn on the newly created window
    turtle.speed(0)
    turtle.hideturtle()
    turtle.tracer(False)
    turtle.penup()
    # variables used to keep track of the location of where new squares will be drawn
    sqr_start_position_x = -(window.window_width() / 2) + 35
    sqr_start_position_y = -25

    # loop through each item in the RGB list and draw a new swatch
    for current_color_index, squareI in enumerate(list_common_rgbs):
        # get current color from the list
        current_color = list_common_rgbs[current_color_index]
        # go to the start location of where to draw the individual swatch
        turtle.goto(sqr_start_position_x, sqr_start_position_y)
        # change pen size for the outline of each swatch
        turtle.pensize(2)
        # tell the function that it wants to apply a fill color, using the current color, to the newly created swatch
        turtle.fillcolor(current_color)
        turtle.begin_fill()
        # draw the current color swatch using configured settings
        for square_side in range(4):
            turtle.pendown()
            turtle.forward(75)
            turtle.left(90)
            turtle.penup()
        # tell teh function to stop applying a fill color to the shape
        turtle.end_fill()
        # advance the location variable of where the next swatch will be drawn
        sqr_start_position_x += 90

    # setting use to show the drawing process
    turtle.pendown()
    # main loop -> used to keep the swatches on the screen
    turtle.mainloop()


# Main Function
def main():
    # variable to keep track of the image used in ther various calculations
    current_image = Image.open("../res/batman.png").convert("RGB")
    # find the number of unique colors within the input image
    unique_colors = set(iterate_image_colors(current_image))
    # calculate the frequencies of each unique color
    rgb_frequencies = collections.Counter(
        (rgb for rgb in iterate_image_colors(current_image) if rgb in unique_colors))
    # Create new list of most common RGBs
    list_most_common_rgbs = []
    for x in rgb_frequencies.most_common(n=5):
        list_most_common_rgbs.append((x[0]))

    # list of RGB values along with their Delta E CIE2000 value
    tupleDeltaE = namedtuple("RGB", "Delta_E")

    # iterate through the listMostCommonRGBs[]
    for counter, frequentColor in enumerate(list_most_common_rgbs):
        # make sure this isn't the first run of the loop
        while not (counter == 0):
            # clear list deltaE_calculations
            tempClearTuple = list(tupleDeltaE)
            tempClearTuple.clear()
            tupleDeltaE = tuple(tempClearTuple)

        # iterate through the rest of the colors in listMostCommonRGBs
        for otherColor in list_most_common_rgbs:
            # if items are the same (frequentColor == otherColors) then skip
            # ... otherwise calculate the
            while not (frequentColor == otherColor):
                # convert frequentColor and otherColors to list[]: [r, g, b]
                listRGB1 = list(frequentColor)
                listRGB2 = list(otherColor)

                # calculate the Delta E CIE2000 using listRGB1 * listRGB2
                _deltaE = calculate_deltaE_CIE2000(listRGB1, listRGB2)

                tempString = str(listRGB2[0]) + ", " + str(listRGB2[1]), ", " + str(
                    listRGB2[1]
                )
                # append the values to tupleDeltaE named tuple
                print(type(tupleDeltaE))

                tupleDeltaE(str(tempString), str(_deltaE))

        # print out the name of the First Colors
        # ... then print out the delta E values for every other color in the list
        print("Main Color: ", str(frequentColor), "\n")
        # cycle through the tupleDeltaE namedtupel
        for currItem in tupleDeltaE:
            print("....", str(currItem[0]), ": ", str(currItem[1], "\n"))

    # Call outputMostCommonRGBs function
    display_common_rgb_swatches(list_most_common_rgbs)

    # Cycle through the most common RGB values -> n = number of RGB frequencies to show
    # for i in rgbFrequencies.most_common(n=5):
    #      print("Frequency: " + str(i))


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    main()
