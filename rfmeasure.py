# This script automatically calculates the site RF noise based on given parameters
# Input : CSV file from Agilent FieldFox


# TODOs:
# DONE: Import data from CSV
# DONE: Plot data, colour according to bands
# DONE: Apply median threshold to the "flatter" bands
# DONE: Input : XML File that describes equipment setup during measurement, from .sta file
# DONE: Make bands NOT hardcoded, array based instead of individual variables names b1,b2,b3,b4,b5
# DONE: Plot median values for each band [03 DEC]
# TODO: Replace print statements with logging.
# DONE : SOLVED - Band 18MHz to 30MHz get nulled!!! when using 100M wide CSV file [SOLVED 03 DEC]\ solved : median filter applied took out most of the data between 18MHZ and 30MHz
# DONE: Add save figures to files [03 DEC]
# DONE: Add plot to display original data before banding [03 DEC]
# DONE: Add plot to display banded data [03 DEC]
# TODO: Add plot to display banded and thresholded data together in one plot
# TODO: Add plot maximized when showing
# TODO: Add plot size specified when saving plot to disk
# TODO: Add median filter that have some leeway (think deviations). Original apply_median is too strict
# DONE: Feed a list of files to analyse not only one [03 DEC]
# TODO: Bug, handle missing STA data associated with CSV file
# TODO: Testing framework to test integrity of the module
# TODO: Extract time stamp from CSV/STA file for usage in Figure Title

import zipfile
import os
import numpy as np
import glob


# Constants
# CSV_INPUT_FILE = './data/SITE_VG2-NB1.csv'
# CSV_INPUT_FILE = './data/SITE_VG2-WB2.csv'
# CSV_INPUT_FILE = './data/SITE_VG2-100M2.csv'
# STA_FILE = '.'.join([CSV_INPUT_FILE[:-4], 'sta'])

# These value are pre-calculated based on the above constants
# CSV_FILENAME = CSV_INPUT_FILE[CSV_INPUT_FILE.rfind('/'):][1:]


def get_timestamp_from_csv(fpath):
    # Returns a string containing the timestamp extracted from inside CSV located at fpath

    # TODO: Return better timestamp YYYYMMDD-HHMM, use better 3rd party library
    print(f'Opening {fpath}')
    with open(fpath, mode='r') as f:
        for line in f:
            # print(line.lower())
            if line.lower().find('timestamp') > 0:
                # print('timestamp found')
                break
    # print(line)
    timestamp = "".join([line[line.find(',') + 2:-3].replace(':', '')])
    print(timestamp)
    return timestamp


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
    print(f'Length of bands {len(band)}')

    for i in range(len(bands_limits)):
        # print(f'band {i}')
        if i == 0:
            band[0] = datain[datain[:, 0] <= bands_limits[0]]
        else:
            band[i] = datain[datain[:, 0] <= bands_limits[i]]
            band[i] = band[i][band[i][:, 0] >= bands_limits[i - 1]]
    return band


# def plot_scatter_graph_bands(b1, b2, b3, b4, b5, csvfilename):
def plot_scatter_graph_bands(bands, x_axis_label='insert uom', chart_title='Insert chart title', filename=None,
                             plotmedian=True, prevmediums=None):
    # Plots individual bands
    import matplotlib.pyplot as plt
    print('Plotting graph with bands')
    for b in bands:
        plt.plot(b[:, 0], b[:, 1], '-o')

    # Plot median values in each band
    if plotmedian:
        band_median = []
        print(f'Plotting medians')
        for index, b in enumerate(bands):
            # check if previous medians have been provided
            if prevmediums is None:
                # previous median is not provided calculate fresh
                band_median.append(np.median(b[:, 1]))
            else:
                # previous median provided copy in
                band_median.append(prevmediums[index])

            print(f'Median band {index} = {band_median[-1]}')
            # FIX, use np.copy do not directly reference
            m = np.copy(b[:, 1])
            m[:] = band_median[-1]
            print(m)
            # m[:] = np.median(m)
            plt.plot(b[:, 0], m, linewidth=5)

    print(f'Plot axis are as follows {plt.axis()}')

    plt.title(f'{chart_title}')
    plt.ylabel('Level [dBm]')
    plt.xlabel(f'Frequency [{x_axis_label}]')

    # Change the Y-Axis to something constant
    axis_scale = list(plt.axis())
    axis_scale[2] = -120
    axis_scale[3] = -40

    # Apply the new axis to the plot
    plt.axis(axis_scale)
    plt.grid()
    if filename:
        print(f'Plotting {filename}')
        print(f'Saving plot to file {filename}')
        # TODO : include timestamp in the filename
        plt.savefig(fname=filename, format='SVG', dpi='figure')
    plt.show()
    plt.close()
    # plt.show


def apply_threshold(datain, threshold):
    data_threshed = datain[datain[:, 1] <= threshold]
    return data_threshed


def apply_median(datain):
    # Change input data by filtering out any value smaller or equal to the median
    data_threshed = datain[datain[:, 1] <= np.median(datain[:, 1])]
    return data_threshed


def analyse_data(csvfilename, sta_file_path):
    # Load data from CSV
    # data = np.loadtxt(csvfilename, skiprows=17, delimiter=',', usecols=(0, 1))
    data = None
    data = np.genfromtxt(csvfilename, skip_header=17, skip_footer=1, delimiter=',', usecols=(0, 1))
    x_axis_uom_text = 'MHz'
    x_axis_uom_factor = 1 / 1000000

    # Scale the frequency data from Hz to MHz
    data = data * np.array([x_axis_uom_factor, 1])

    # Load metadata from XML file to set certain

    print(f'Path for STA = {sta_file_path}')

    csv_metadata = get_csv_metadata_from_sta(sta_file_path)

    csv_metadata['startfrequency'] = csv_metadata['startfrequency'] * x_axis_uom_factor
    csv_metadata['stopfrequency'] = csv_metadata['stopfrequency'] * x_axis_uom_factor

    print(csv_metadata)

    resBW = csv_metadata['resolutionbandwidth']

    timestamp = get_timestamp_from_csv(csvfilename)

    title_str = f'RF Level Measurements for VG, resolution BW={resBW}, {timestamp}'

    # These value are pre-calculated based on the above constants
    CSV_FILENAME = csvfilename[csvfilename.rfind('/'):][1:]

    print(CSV_FILENAME)

    # Set bands
    band_lim = [1, 3, 9, 18, 40, csv_metadata['stopfrequency']]

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

    fpath = "".join(["./figs/before/", CSV_FILENAME[:-4], '.SVG'])

    # Plot original data
    plot_scatter_graph_bands(band, x_axis_label=x_axis_uom_text, chart_title=title_str,
                             filename=fpath,
                             plotmedian=True)

    # Apply destructive thresholding on data. NOTE THIS CHANGES FOR EACH AND EVERY MEASUREMENT!!!!
    band[0] = apply_threshold(band[0], -60)
    band[1] = band[1]
    band[2] = apply_median(band[2])
    band[3] = apply_median(band[3])
    band[4] = apply_median(band[4])
    band[5] = apply_median(band[5])

    # Calculate individual band medians after thresholds applied
    medians_after_threshold = []
    print(f'Medians after thresholding')
    for index, b in enumerate(band):
        medians_after_threshold.append(np.median(b[:, 1]))
        print(f'Median band {index} = {medians_after_threshold[-1]}')

    fpath = "".join(["./figs/after/", CSV_FILENAME[:-4], '.SVG'])

    plot_scatter_graph_bands(band, x_axis_label=x_axis_uom_text, chart_title=title_str,
                             filename=fpath,
                             plotmedian=True, prevmediums=medians_before_threshold)


def main():
    print(f'Analysing RF Level Data')
    # get_csv_metadata_from_sta(STA_FILE

    # Analyse one CSV file and save to disk
    # analyse_data(CSV_INPUT_FILE)

    # Analyse all CSV file found in specified folder
    target_folder_match_string = './data/*.csv'

    print(f'Finding all CSV files using the following match pattern {target_folder_match_string}')

    for p in glob.glob(target_folder_match_string):
        print(f'Found : {p}')
        CSV_INPUT_FILEPATH = p
        STA_FILE = '.'.join([CSV_INPUT_FILEPATH[:-4], 'sta'])
        # get_timestamp_from_csv(CSV_INPUT_FILEPATH)
        # return None
        analyse_data(CSV_INPUT_FILEPATH, STA_FILE)
        # break


if __name__ == "__main__":
    main()
