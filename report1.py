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
    corrected_date = arrow.get(maya.parse(incorrect_datetime).datetime()).shift(seconds=(-1 * diff.total_seconds()))
    return str(corrected_date.format(datetimeformat))


def get_timestamp_from_csv(fpath, datetimeformat="DD MMMM YYYY HHmm"):
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


def generate_report1(csv_file_paths, sta_file_paths):
    # Load data from CSVs
    data = []
    timestamp = []

    for csv_f in csv_file_paths:
        # data = np.loadtxt(csvfilename, skiprows=17, delimiter=',', usecols=(0, 1))
        data.append(None)
        data[-1] = np.genfromtxt(csv_f, skip_header=17, skip_footer=1, delimiter=',', usecols=(0, 1))

        timestamp.append(adjust_time(get_timestamp_from_csv(csv_f, datetimeformat="DD MMMM YYYY HH:mm")))

        x_axis_uom_text = 'MHz'
        x_axis_uom_factor = 1 / 1000000

        # Scale the frequency data from Hz to MHz
        data[-1] = data[-1] * np.array([x_axis_uom_factor, 1])

    csv_metadata = []

    for sta_f in sta_file_paths:
        # Load metadata from XML file to set certain

        print(f'Path for STA = {sta_f}')
        csv_metadata.append(get_csv_metadata_from_sta(sta_f))
        csv_metadata[-1]['startfrequency'] = csv_metadata[-1]['startfrequency'] * x_axis_uom_factor
        csv_metadata[-1]['stopfrequency'] = csv_metadata[-1]['stopfrequency'] * x_axis_uom_factor

        print(csv_metadata[-1])

        resBW = csv_metadata[-1]['resolutionbandwidth']

    title_str = f'RF Level Measurements for VG, resolution BW={resBW}, {timestamp}'

    fpath = "".join(["./figs/report01", '.PNG'])

    # Plot original data
    from matplotlib import pyplot as plt
    for i, chart_data in enumerate(data):
        plt.plot(chart_data[:, 0], chart_data[:, 1], alpha=0.8, linewidth=1, label=timestamp[i])
    plt.legend(loc='upper right')
    plt.title(f'Noise measurements')
    plt.ylabel('Level [dBm]')
    plt.xlabel('Frequency [MHz]')
    # DONE: Maximize the figure to be bigger before saving to disk
    # figure = plt.gcf()
    # figure.set_size_inches(16, 9)

    plt.savefig(fname=fpath, format="PNG", dpi=100)
    plt.grid()
    plt.show()


def main():
    import time
    start = time.time()
    # print(f'Analysing RF Level Data')

    # print(adjust_time("28 November 2017 13:58"))
    # print(adjust_time("28 November 2017 13:58", datetimeformat="DD MMMM YYYY"))
    # print(adjust_time("28 November 2017 13:58", datetimeformat="YYYYMMDDHHmm"))

    NNB_CSV_INPUT_FILE = ['./data/VG2/SITE_VG2-NNB1.csv', './data/VG2/SITE_VG2-NNB2.csv',
                          './data/VG2/SITE_VG2-NNB3.csv']
    WB_CSV_INPUT_FILE = ['./data/VG2/SITE_VG2-WB1.csv', './data/VG2/SITE_VG2-WB2.csv', './data/VG2/SITE_VG2-WB3.csv']
    NB_CSV_INPUT_FILE = ['./data/VG2/SITE_VG2-NB1.csv', './data/VG2/SITE_VG2-NB3.csv']

    # csv_files = NNB_CSV_INPUT_FILE
    # csv_files = WB_CSV_INPUT_FILE
    csv_files = NB_CSV_INPUT_FILE

    timestamp = []
    sta_files = []

    for f in csv_files:
        timestamp.append(get_timestamp_from_csv(f))
        print(timestamp[-1])
        sta_files.append('.'.join([f[:-4], 'sta']))

    # Read and plot data from CSV files for separate charts
    generate_report1(csv_files, sta_files)

    end = time.time()
    duration = end - start
    print()
    print()
    print('============================================')
    print(f"TOOK {duration} seconds to run script")


if __name__ == "__main__":
    main()
