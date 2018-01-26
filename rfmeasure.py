# This script automatically calculates the site RF noise based on given parameters
# Input : CSV file from Agilent FieldFox


# TODOs:
# DONE: Import data from CSV
# DONE: Plot data, colour according to bands
# DONE: Apply median threshold to the "flatter" bands
# TODO: Input : XML File that describes equipment setup during measurement, from .sta file
# DONE: Make bands NOT hardcoded, array based instead of individual variables names b1,b2,b3,b4,b5


import zipfile
import os
import matplotlib.pyplot as plt
import numpy as np

# Constants
CSV_INPUT_FILE = './data/SITE_VG2-NB1.csv'
STA_FILE = './data/SITE_VG2-NB1.sta'


def my_open_zipfile(zipfilename):
    print(f'Trying to open ZipFile {zipfilename}')
    # Try to open Zip file
    with zipfile.ZipFile(zipfilename) as zf:
        with zf.open('Temp/SA') as f:
            print(f.read())

    # with zipfile.ZipFile(zipfilename, ) as z:
    #     z.open()
    #     print(f'Opened ZipFile {zipfilename}')
    #     for filename in z.namelist():
    #         print(filename)
    #         # print(os.path.isfile(filename))
    #         print(os.path.split(filename))

    # Read contents of ZipFileRoot/Temp/SA into XML object / JSON?

    # Extract specific parameters and return


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
        print(f'band {i}')
        if i == 0:
            band[0] = datain[datain[:, 0] <= bands_limits[0]]
        else:
            band[i] = datain[datain[:, 0] <= bands_limits[i]]
            band[i] = band[i][band[i][:, 0] >= bands_limits[i-1]]
    return band


# def plot_scatter_graph_bands(b1, b2, b3, b4, b5, csvfilename):
def plot_scatter_graph_bands(bands, csvfilename):
    # Plots individual bands
    for b in bands:
        plt.plot(b[:, 0], b[:, 1], '-o')
    # plt.plot(b1[:, 0], b1[:, 1], '-o')
    # plt.plot(b2[:, 0], b2[:, 1], '-o')
    # plt.plot(b3[:, 0], b3[:, 1], '-o')
    # plt.plot(b4[:, 0], b4[:, 1], '-o')
    # plt.plot(b5[:, 0], b5[:, 1], '-o')
    plt.title(f'{csvfilename}')
    plt.ylabel('Level [dBm]')
    plt.xlabel('Frequency [MHz]')
    plt.grid()
    plt.show()


def apply_threshold(datain, threshold):
    data_threshed = datain[datain[:, 1] <= threshold]
    return data_threshed


def apply_median(datain):
    # data_threshed = datain[datain[:, 1] <= threshold]
    data_threshed = datain[datain[:, 1] <= np.median(datain[:, 1])]
    return data_threshed


def plot_scatter_graph(datain, csvfilename):
    plt.scatter(datain[:, 0], datain[:, 1], color='red')
    plt.scatter(datain[:, 0], datain[:, 1], color='yellow')
    plt.title(f'{csvfilename}')
    plt.ylabel('Level [dBm]')
    plt.xlabel('Frequency [MHz]')
    plt.grid()
    plt.show()


def plot_data(csvfilename):
    data = np.loadtxt(csvfilename, skiprows=17, delimiter=',', usecols=(0, 1))

    data = data * np.array([1/1000000, 1])

    # print(data[0:10])
    print(data[data[:, 0] < 0.1])

    # plot_normal_graph(data, csvfilename)

    # plot_scatter_graph(data, csvfilename)

    # band = return_bands(data)
    band = return_bands(data, bands_limits=[1, 3, 9, 18, 30])

    for b in band:
        print(f'Median b {np.median(b[:,1])}')
    # print(f'Median b2 {np.median(b2[:,1])}')
    # print(f'Median b3 {np.median(b3[:,1])}')
    # print(f'Median b4 {np.median(b4[:,1])}')
    # print(f'Median b5 {np.median(b5[:,1])}')
    # plot_scatter_graph_bands(b1, b2, b3, b4, b5, csvfilename)

    if len(band) == 4:
        plot_scatter_graph_bands([apply_threshold(band[0], -60), band[1], apply_median(band[2]), apply_median(band[3])], csvfilename)
    elif len(band) == 5:
        plot_scatter_graph_bands([apply_threshold(band[0], -60), band[1], apply_median(band[2]), apply_median(band[3]), apply_median(band[4])], csvfilename)


def main():
    print(f'Hello World')

    # with open(CSV_INPUT_FILE, mode='r') as f:
    #     print(f.read())

    # get_csv_metadata_from_sta(STA_FILE)

    plot_data(CSV_INPUT_FILE)


if __name__ == "__main__":
    main()
