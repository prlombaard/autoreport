# This script automatically calculates the site RF noise based on given parameters
# Input : CSV file from Agilent FieldFox


# TODOs:
# DONE: Import data from CSV
# DONE: Plot data, colour according to bands
# DONE: Apply median threshold to the "flatter" bands
# DONE: Input : XML File that describes equipment setup during measurement, from .sta file
# DONE: Make bands NOT hardcoded, array based instead of individual variables names b1,b2,b3,b4,b5
# TODO: Plot median values for each band
# TODO: Replace print statements with logging.
# TODO : BUG - Band 18MHz to 30MHz get nulled!!! when using 100M wide CSV file


import zipfile
import os
import matplotlib.pyplot as plt
import numpy as np


# Constants
CSV_INPUT_FILE = './data/SITE_VG2-NB1.csv'
# CSV_INPUT_FILE = './data/SITE_VG2-WB2.csv'
# CSV_INPUT_FILE = './data/SITE_VG2-100M2.csv'
STA_FILE = '.'.join([CSV_INPUT_FILE[:-4], 'sta'])


def get_xml_data(xmldata):
    print(f'Trying to parse XML data')
    # from BeautifulSoup import BeautifulSoup
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(xmldata, "lxml")
    print(f'Parsing of XML data complete, lets see if it worked')
    find_str = ['StartFrequency', 'StopFrequency', 'ResolutionBandwidth']
    # print(soup.prettify())
    my_dict = {'startfrequency': -999, 'stopfrequency': -999, 'resolutionbandwidth': -999}
    for fstr in find_str:
        # print(f'Trying to find {fstr.lower()}')
        s = soup.find(fstr.lower())
        if s:
            print(f'Found {fstr} with value {s.string}')
            my_dict[fstr.lower()] = int(s.string)
    return my_dict


def get_csv_metadata_from_sta(zipfilename):
    print(f'Trying to open ZipFile {zipfilename}')
    # Try to open Zip file
    with zipfile.ZipFile(zipfilename) as zf:
        # Try to open SA file inside of ZipFile object
        with zf.open('Temp/SA') as f:
            # Read contents of ZipFileRoot/Temp/SA into XML object / JSON?
            return get_xml_data(f.read())


def plot_normal_graph(datain, csvfilename):
    plt.plot(datain[:, 0], datain[:, 1])
    plt.title(f'{csvfilename}')
    plt.ylabel('Level [dBm]')
    plt.xlabel('Frequency [MHz]')
    plt.grid()
    plt.show()


def return_bands(datain, bands_limits=[1, 3, 9, 18, 30]):
    # Return n amount of arrays based on how many input ranges are provided
    # Each of the band limits are the end of the current band
    # Unit of measure for bands_limits is MHz
    band = [0 for _ in range(len(bands_limits))]
    # print(f'Length of bands {len(band)}')

    for i in range(len(bands_limits)):
        # print(f'band {i}')
        if i == 0:
            band[0] = datain[datain[:, 0] <= bands_limits[0]]
        else:
            band[i] = datain[datain[:, 0] <= bands_limits[i]]
            band[i] = band[i][band[i][:, 0] >= bands_limits[i-1]]
    return band


# def plot_scatter_graph_bands(b1, b2, b3, b4, b5, csvfilename):
def plot_scatter_graph_bands(bands, x_axis_label='insert uom', chart_title='Insert chart title'):
    # Plots individual bands
    for b in bands:
        plt.plot(b[:, 0], b[:, 1], '-o')
    plt.title(f'{chart_title}')
    plt.ylabel('Level [dBm]')
    plt.xlabel(f'Frequency [{x_axis_label}]')
    plt.grid()
    plt.show()


def apply_threshold(datain, threshold):
    data_threshed = datain[datain[:, 1] <= threshold]
    return data_threshed


def apply_median(datain):
    data_threshed = datain[datain[:, 1] <= np.median(datain[:, 1])]
    return data_threshed


def analyse_data(csvfilename):
    # Load data from CSV
    # data = np.loadtxt(csvfilename, skiprows=17, delimiter=',', usecols=(0, 1))
    data = np.genfromtxt(csvfilename, skip_header=17, skip_footer=1, delimiter=',', usecols=(0, 1))
    x_axis_uom_text = 'MHz'
    x_axis_uom_factor = 1/1000000

    # Scale the frequency data from Hz to MHz
    data = data * np.array([x_axis_uom_factor, 1])

    # Load metadata from XML file to set certain

    print(f'Path for STA = {STA_FILE}')

    csv_metadata = get_csv_metadata_from_sta(STA_FILE)

    csv_metadata['stopfrequency'] = csv_metadata['stopfrequency'] * x_axis_uom_factor

    print(csv_metadata)

    resBW = csv_metadata['resolutionbandwidth']

    title_str = f'RF Level Measurements for VG, resolution BW={resBW}'

    # Set bands
    band_lim = [1, 3, 9, 18, csv_metadata['stopfrequency']]

    print(f'Bands:')
    for index, b in enumerate(band_lim):
        print(f'Band {index} End = {b} [{x_axis_uom_text}]')

    # Split data into bands
    band = return_bands(data, bands_limits=band_lim)

    # Calculate individual band medians before applying thresholds
    medians_before_threshold = []
    print(f'Medians before thresholding')
    for index, b in enumerate(band):
        medians_before_threshold.append(np.median(b[:, 1]))
        print(f'Median band {index} = {medians_before_threshold[-1]}')

    # Plot original data

    # Apply destructive thresholding on data. NOTE THIS CHANGES FOR EACH AND EVERY MEASUREMENT!!!!
    band[0] = apply_threshold(band[0], -60)
    band[1] = band[1]
    band[2] = apply_median(band[2])
    band[3] = apply_median(band[3])
    band[4] = apply_median(band[4])

    # Calculate individual band medians after thresholds applied
    medians_after_threshold = []
    print(f'Medians after thresholding')
    for index, b in enumerate(band):
        medians_after_threshold.append(np.median(b[:, 1]))
        print(f'Median band {index} = {medians_after_threshold[-1]}')

    if len(band) == 4:
        plot_scatter_graph_bands(band, x_axis_label=x_axis_uom_text, chart_title=title_str)
    elif len(band) == 5:
        plot_scatter_graph_bands(band, x_axis_label=x_axis_uom_text, chart_title=title_str)


def main():
    print(f'Analysing RF Level Data')
   # get_csv_metadata_from_sta(STA_FILE)

    analyse_data(CSV_INPUT_FILE)


if __name__ == "__main__":
    main()
