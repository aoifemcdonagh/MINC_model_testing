"""
Script containing all plotting functions
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import os
from datetime import datetime
from material_segmentation import plotting_utils

#  Global dictionary containing class number : name pairs
CLASS_LIST = {0: "brick",
              1: "carpet",
              2: "ceramic",
              3: "fabric",
              4: "foliage",
              5: "food",
              6: "glass",
              7: "hair",
              8: "leather",
              9: "metal",
              10: "mirror",
              11: "other",
              12: "painted",
              13: "paper",
              14: "plastic",
              15: "polishedstone",
              16: "skin",
              17: "sky",
              18: "stone",
              19: "tile",
              20: "wallpaper",
              21: "water",
              22: "wood"}


def get_class_names(class_numbers):
    """
    Function generating the corresponding class name for a class number outputted by network
    """
    class_names = []
    for number in class_numbers:
        class_names.append(CLASS_LIST.get(number))

    print(class_names)

    if len(class_names) == 1:  # If only one number is passed to function, we should return a string value
        return class_names[0]
    else:  # Otherwise return a list of strings
        return class_names


def get_tick_labels(class_numbers):
    """
    Function generating tick labels appropriate to each classified image
    """
    class_names = get_class_names(class_numbers)
    tick_labels = []
    for (number, name) in zip(class_numbers, class_names):
        tick_labels.append(str(number) + ": " + name)

    return tick_labels


def modify_class_map(class_map):
    """
    Function converting a matrix of numbers (corresponding to discrete, numerically unrelated class values) to a
    matrix of numbers which can be plotted.
    Need to assign numerical values of 0-len(unique_classes) in order to properly plot a class map
        - if len(unique_classes) = 5 for example, instead of a prob_map containing a mix of numbers [0,4,16,19,21]
          we would plot a modified_prob_map containing ndarray of numbers [0,1,2,3,4]
        - Important to use the original unique_classes when generating tick labels! (in this case number corresponds
          to a fixed class name)
    """
    unique_values = np.unique(class_map).tolist()  # list of unique values in class_map
    modified_values = range(0, len(unique_values))  # list in range 0 - len(unique_values)
    value_dict = {a: b for (a, b) in zip(unique_values, modified_values)}

    modified_class_map = np.array([[value_dict.get(class_map[i][j]) for j in range(0, class_map.shape[1])] for i in
                          range(0, class_map.shape[0])])

    return modified_class_map


def plot_confidence_map(network_output, save=False, path=None):
    """
    Function for plotting the confidence map from classified image
    :param network_output:
    :param save:
    :param path:
    :return:
    """

    if type(network_output) is dict:  # If the input value is an unmodified 'network output'
        confidence_map = network_output['prob'][0].max(axis=0)  # Get highest probability class at each location
    else:  # if average probability maps are passed in in case of upsampling & averaging
        confidence_map = network_output.max(axis=0)

    fig, ax = plt.subplots(figsize=(15,8))

    ax.set_title("highest probability at each location (irrespective of class)")
    hb = ax.imshow(confidence_map)
    cb = fig.colorbar(hb, ax=ax)
    cb.set_label('Probability')

    if save is True:  # If user chooses to save plot, do so
        if path is None:  # If no path is specified, create one for storing probability maps
            path = os.path.join(os.getcwd(), "plots", datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
            os.makedirs(path)

        plt.savefig(path + "/confidence_map.jpg")

    else:  # Just show the plot
        plt.show()


def plot_class_map(network_output, save=False, path=None):
    """
    Function for plotting only the class map from classification output
    :param network_output:
    :param save:
    :param path:
    :return:
    """

    if type(network_output) is dict:  # If the input value is an unmodified 'network output'
        class_map = network_output['prob'][0].argmax(axis=0)  # Get highest probability class at each location
    else:  # if average probability maps are passed in in case of upsampling & averaging
        class_map = network_output.argmax(axis=0)

    unique_classes = np.unique(class_map).tolist()  # Get unique classes for plot
    class_map = modify_class_map(class_map)  # Modify class_map for plotting


    fig, ax = plt.subplots(figsize=(15,8))

    ax.set_title("Class at each location")
    hb = ax.imshow(class_map, cmap=plt.get_cmap("gist_rainbow", len(unique_classes)))

    step_length = float(len(unique_classes) - 1) / float(
        len(unique_classes))  # Define the step length between ticks for colorbar.
    loc = np.arange(step_length / 2, len(unique_classes), step_length) if len(unique_classes) > 1 else [
        0.0]  # Shift each tick location so that the label is in the middle
    cb = fig.colorbar(hb, ticks=loc)
    cb.set_ticklabels(get_tick_labels(unique_classes))
    cb.set_label('Class Numbers')


    if save is True:  # If user chooses to save plot, do so
        if path is None:  # If no path is specified, create one for storing probability maps
            path = os.path.join(os.getcwd(), "plots", datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
            os.makedirs(path)

        plt.savefig(path + "/class_map.jpg")

    else:  # Just show the plot
        plt.show()


def plot_probability_maps(probability_maps, path=None):
    """
    Function for plotting probability maps
    Inputs:
        - probability_maps: probability maps for all classes
        - path: optional path to save plots to. Default is in folder 'plots' in current directory

    This function is called from outside this script
    """

    if path is None:  # If no path is specified, create one for storing probability maps
        path = os.path.join(os.getcwd(), "plots", datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        os.makedirs(path)
    else:
        path = os.path.join(path, "plots")
        os.makedirs(path)

    class_num = 0  # start at class 0
    for prob_map in probability_maps:

        fig, ax = plt.subplots()
        hb = ax.imshow(prob_map, cmap='gray')
        ax.set_title("Probability of class " + CLASS_LIST.get(class_num))
        cb = fig.colorbar(hb, ax=ax)
        cb.set_label('Probability')

        plt.savefig(path + "/" + str(class_num) + ".jpg")
        plt.close()
        class_num += 1


def plot_abs_map(network_output, save=False, path=None, band=1000):
    """
    Function for plotting absporption coefficient maps
    :param network_output:
    :param save:
    :param path:
    :param band: frequency band in Hz
    :return:
    """

    if type(network_output) is dict:  # If the input value is an unmodified 'network output'
        class_map = network_output['prob'][0].argmax(axis=0)  # Get highest probability class at each location
    else:  # if average probability maps are passed in in case of upsampling & averaging
        class_map = network_output.argmax(axis=0)

    unique_classes = np.unique(class_map).tolist()  # Get unique classes for plot
    class_map = modify_class_map(class_map)  # Modify class_map for plotting

    engine = plotting_utils.PlottingEngine()
    engine.set_colormap("absorption", freq=band)
    #greyscale_map = engine.generate_grayscale_map(band=band)  # Generate greyscale map given frequency band
    pixels, colorbar = engine.process(network_output)

    fig, ax = plt.subplots(figsize=(15, 8))

    ax.set_title("Absorption Coefficients at " + str(band) + " Hz")
    hb = ax.imshow(pixels)

    if save is True:  # If user chooses to save plot, do so
        if path is None:  # If no path is specified, create one for storing probability maps
            path = os.path.join(os.getcwd(), "plots", datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
            os.makedirs(path)

        plt.savefig(path + "/abs_map.jpg")

    else:  # Just show the plot
        plt.show()

def plot_output(network_output, image=None, path=None, aspect=None):
    """
    Function for plotting and saving the output of classification model
        - Class map
        - Confidence map
        - All probability maps

    :param network_output: raw output from classification model
    :param image: pre-loaded image to plot alongside classmap
    :param path: path to save plots to
    :param aspect: aspect of output figures
    :return:
    """

    if path is None:  # If no path is specified, create one for storing probability maps
        path = os.path.join(os.getcwd(), "plots", datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        os.makedirs(path)
    else:
        path = os.path.join(path, "plots")
        os.makedirs(path)

    log = open((path + "/test_log.txt"), "w+")  # Open log file

    log.write("path: " + path + "\n")

    if type(network_output) is dict:  # If the input value is an unmodified 'network output'
        class_map = network_output['prob'][0].argmax(axis=0)  # Get highest probability class at each location
        prob_map = network_output['prob'][0].max(axis=0)

        # Convert network_output to format which can be used to plot probability maps
        network_output = [network_output['prob'][0][class_num] for class_num in CLASS_LIST.keys()]

        log.write("network_output is dict" + "\n")

    else:  # if average probability maps are passed in in case of upsampling & averaging
        class_map = network_output.argmax(axis=0)
        prob_map = network_output.max(axis=0)

        log.write("\'network_output\' is average prob maps" + "\n")

    if aspect is None:
        aspect = (30, 10)

    log.write("plot aspect: " + str(aspect) + "\n")
    log.write("image aspect: " + str(image.shape[1]) + ", " + str(image.shape[0]) + "\n")

    unique_classes = np.unique(class_map).tolist()  # Get unique classes for plot
    class_map = modify_class_map(class_map)  # Modify class_map for plotting

    ## Plot image and class map ##
    fig, axs = plt.subplots(ncols=2, figsize=aspect)
    ax = axs[0]
    hb = ax.imshow(image)
    ax.set_title("Input image")

    ax = axs[1]
    ax.set_title("Class at each location")
    hb = ax.imshow(class_map, cmap=plt.get_cmap("gist_rainbow", len(unique_classes)))

    step_length = float(len(unique_classes) - 1) / float(
        len(unique_classes))  # Define the step length between ticks for colorbar.
    loc = np.arange(step_length / 2, len(unique_classes), step_length) if len(unique_classes) > 1 else [
        0.0]  # Shift each tick location so that the label is in the middle
    cb = fig.colorbar(hb, ticks=loc)
    cb.set_ticklabels(get_tick_labels(unique_classes))
    cb.set_label('Class Numbers')

    plt.savefig(path + "/class_map.jpg")
    plt.close()

    ## Plot image and confidence map (i.e. highest prob at each location, irrespective of class) ##
    fig, axs = plt.subplots(ncols=2, figsize=aspect)
    ax = axs[0]
    hb = ax.imshow(image)
    ax.set_title("Input image")

    ax = axs[1]
    hb = ax.imshow(prob_map)
    ax.set_title("highest probability at each location (irrespective of class)")
    cb = fig.colorbar(hb, ax=ax)
    cb.set_label('Probability')

    plt.savefig(path + "/confidence_map.jpg")
    plt.close()

    # Plot probability maps for all classes
    for class_num in CLASS_LIST.keys():
        prob_map = network_output[class_num]

        fig, ax = plt.subplots()
        hb = ax.imshow(prob_map, cmap='gray')
        ax.set_title("Probability of class " + CLASS_LIST.get(class_num))
        cb = fig.colorbar(hb, ax=ax)
        cb.set_label('Probability')

        plt.savefig(path + "/" + str(class_num) + ".jpg")
        plt.close()

    log.close()  # close log file


def get_class_plot(network_output):
    """
    Function for plotting only the class map from classification output
    :param network_output:
    """

    if type(network_output) is dict:  # If the input value is an unmodified 'network output'
        class_map = network_output['prob'][0].argmax(axis=0)  # Get highest probability class at each location
    else:  # if average probability maps are passed in in case of upsampling & averaging
        class_map = network_output.argmax(axis=0)

    unique_classes = np.unique(class_map).tolist()  # Get unique classes for plot
    class_map = modify_class_map(class_map)  # Modify class_map for plotting

    fig = Figure(figsize=(15, 8))
    a = fig.add_subplot(111)

    a.set_title("Class at each location")
    hb = a.imshow(class_map, cmap=plt.get_cmap("gist_rainbow", len(unique_classes)))

    step_length = float(len(unique_classes) - 1) / float(
        len(unique_classes))  # Define the step length between ticks for colorbar.
    loc = np.arange(step_length / 2, len(unique_classes), step_length) if len(unique_classes) > 1 else [
        0.0]  # Shift each tick location so that the label is in the middle
    cb = fig.colorbar(hb, ticks=loc)
    cb.set_ticklabels(get_tick_labels(unique_classes))
    cb.set_label('Class Numbers')

    return fig

