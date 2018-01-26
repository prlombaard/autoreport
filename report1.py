# This script will generate a report of the noise level measurements transposing charts ontop of each other
# The chart should display the level measurements for the morning midday and afternoon

import zipfile
import os
import numpy as np
import glob


def adjust_time(incorrect_datetime, datetimeformat="DD MMMM YYYY HHmm"):
    """Device read and stored the date incorrectly"""
    """The real time was 27 November 2017 10:25 the device recorded 28 November 2018 13:58"""
    """Therefore the device time as read from all CSV and STA files must be adjusted back in time"""
    """by 1 day, 3hours and 33minutes or 27.55 hours"""
    import maya
    import arrow

    # print(f'Incorrect datetime: {incorrect_datetime}')

    # parse date from string into datetime object
    date1 = arrow.get(maya.parse("27 nov 2017 13:58").datetime())
    date2 = arrow.get(maya.parse("28 nov 2017 13:58").datetime())
    diff = date2 - date1
    # print(f'Difference: {diff}')
    corrected_date = arrow.get(maya.parse(incorrect_datetime).datetime()).shift(seconds=(-1*diff.total_seconds()))
    return str(corrected_date.format(datetimeformat))


def get_timestamp_from_csv(fpath):
    # Returns a string containing the timestamp extracted from inside CSV located at fpath

    # TODO: Return better timestamp YYYYMMDD-HHMM, use better 3rd party library
    # print(f'Opening {fpath}')
    with open(fpath, mode='r') as f:
        for line in f:
            # print(line.lower())
            if line.lower().find('timestamp') > 0:
                # print('timestamp found')
                break
    # print(line)
    timestamp = "".join([line[line.find(',') + 2:-3].replace(':', '')])
    # print(f'Before corrected  : {timestamp}')
    timestamp = adjust_time(timestamp)
    # print(f'Returning       : {timestamp}')
    return timestamp


def get_xml_data(xmldata):
    # print(f'Trying to parse XML data')
    # from BeautifulSoup import BeautifulSoup
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(xmldata, "lxml")
    # print(f'Parsing of XML data complete, lets see if it worked')
    find_str = ['StartFrequency', 'StopFrequency', 'ResolutionBandwidth']
    # print(soup.prettify())
    my_dict = {'startfrequency': -999, 'stopfrequency': -999, 'resolutionbandwidth': -999}
    for fstr in find_str:
        # print(f'Trying to find {fstr.lower()}')
        s = soup.find(fstr.lower())
        if s:
            # print(f'Found {fstr} with value {s.string}')
            my_dict[fstr.lower()] = int(s.string)
    return my_dict


def get_csv_metadata_from_sta(zipfilename):
    # print(f'Trying to open ZipFile {zipfilename}')
    # Try to open Zip file
    with zipfile.ZipFile(zipfilename) as zf:
        # Try to open SA file inside of ZipFile object
        with zf.open('Temp/SA') as f:
            # Read contents of ZipFileRoot/Temp/SA into XML object / JSON?
            return get_xml_data(f.read())


def plot_normal_graph(datain, csvfilename):
    from matplotlib import pyplot as plt
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
    # import matplotlib.pyplot as plt
    from matplotlib import pyplot as plt
    plt.figure(1)
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
    axis_scale[3] = -30

    # Apply the new axis to the plot
    plt.axis(axis_scale)
    plt.grid()
    if filename:
        print(f'Plotting {filename}')
        print(f'Saving plot to file {filename}')
        file_format = filename[-3:]
        # TODO : include timestamp in the filename

        #DONE: Maximize the figure to be bigger before saving to disk
        figure = plt.gcf()
        figure.set_size_inches(16, 9)

        plt.savefig(fname=filename, format=file_format, dpi=100)
        # plt.savefig(fname=filename, format='SVG', dpi='figure')
    # plt.show()
    plt.close()


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

    timestamp_for_filename = "".join(["201711", timestamp[:2], timestamp[-4:]])

    print(timestamp_for_filename)

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

    fpath = "".join(["./figs/before/", "b", timestamp_for_filename, "-", CSV_FILENAME[:-4], '.PNG'])

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

        fpath = "".join(["./figs/after/", "a", timestamp_for_filename, "-", CSV_FILENAME[:-4], '.PNG'])

    plot_scatter_graph_bands(band, x_axis_label=x_axis_uom_text, chart_title=title_str,
                             filename=fpath,
                             plotmedian=True, prevmediums=medians_after_threshold)

    # Calculate once more just the median do not apply and plot


def main():
    import time
    start = time.time()
    # print(f'Analysing RF Level Data')

    # print(adjust_time("28 November 2017 13:58"))
    # print(adjust_time("28 November 2017 13:58", datetimeformat="DD MMMM YYYY"))
    # print(adjust_time("28 November 2017 13:58", datetimeformat="YYYYMMDDHHmm"))

    NNB_CSV_INPUT_FILE = ['./data/VG2/SITE_VG2-NNB1.csv', './data/VG2/SITE_VG2-NNB2.csv', './data/VG2/SITE_VG2-NNB3.csv']
    WB_CSV_INPUT_FILE = ['./data/VG2/SITE_VG2-WB1.csv', './data/VG2/SITE_VG2-WB2.csv', './data/VG2/SITE_VG2-WB3.csv']
    NB_CSV_INPUT_FILE = ['./data/VG2/SITE_VG2-NB1.csv', './data/VG2/SITE_VG2-NB3.csv']

    # files = NNB_CSV_INPUT_FILE
    files = WB_CSV_INPUT_FILE
    # files = NB_CSV_INPUT_FILE

    timestamp = []
    metadata = []

    for f in files:
        timestamp.append(get_timestamp_from_csv(f))
        print(timestamp[-1])
        sta_file = '.'.join([f[:-4], 'sta'])
        metadata.append(get_csv_metadata_from_sta(sta_file))
        print(metadata[-1])

    # Read data from CSV files for separate charts


    # Plot all data on one chart


    end = time.time()
    duration = end - start
    print()
    print()
    print('============================================')
    print(f"TOOK {duration} seconds to run script")


if __name__ == "__main__":
    main()
