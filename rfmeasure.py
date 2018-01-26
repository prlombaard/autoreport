# This script automatically calculates the site RF noise based on given parameters
# Input : CSV file from Agilent FieldFox


# TODOs:
# DONE: Import data from CSV
# DONE: Plot data, colour according to bands
# DONE: Apply median threshold to the "flatter" bands

import zipfile
import os
import matplotlib as plt
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
    import matplotlib.pyplot as plt
    import numpy as np
    plt.plot(datain[:, 0], datain[:, 1])
    plt.title(f'{csvfilename}')
    plt.ylabel('Level [dBm]')
    plt.xlabel('Frequency [MHz]')
    plt.grid()
    plt.show()


def return_bands(datain, bands_lims=[1, 3, 9, 18, 30]):
    band1 = []
    band2 = []
    band3 = []
    band4 = []
    band5 = []
    band1 = datain[datain[:, 0] <= bands_lims[0]]
    band2 = datain[datain[:, 0] <= bands_lims[1]]
    band2 = band2[band2[:, 0] >= bands_lims[0]]
    band3 = datain[datain[:, 0] <= bands_lims[2]]
    band3 = band3[band3[:, 0] >= bands_lims[1]]
    band4 = datain[datain[:, 0] <= bands_lims[3]]
    band4 = band4[band4[:, 0] >= bands_lims[2]]
    band5 = datain[datain[:, 0] <= bands_lims[4]]
    band5 = band5[band5[:, 0] >= bands_lims[3]]

    return band1, band2, band3, band4, band5


def plot_scatter_graph_bands(b1, b2, b3, b4, b5, csvfilename):
    import matplotlib.pyplot as plt
    import numpy as np

    plt.plot(b1[:, 0], b1[:, 1], '-o')
    plt.plot(b2[:, 0], b2[:, 1], '-o')
    plt.plot(b3[:, 0], b3[:, 1], '-o')
    plt.plot(b4[:, 0], b4[:, 1], '-o')
    plt.plot(b5[:, 0], b5[:, 1], '-o')
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
    import matplotlib.pyplot as plt
    import numpy as np
    plt.scatter(datain[:, 0], datain[:, 1], color='red')
    plt.scatter(datain[:, 0], datain[:, 1], color='yellow')
    plt.title(f'{csvfilename}')
    plt.ylabel('Level [dBm]')
    plt.xlabel('Frequency [MHz]')
    plt.grid()
    plt.show()


def plot_data(csvfilename):
    import matplotlib.pyplot as plt
    import numpy as np

    data = np.loadtxt(csvfilename, skiprows=17, delimiter=',', usecols=(0, 1))

    data = data * np.array([1/1000000, 1])

    # print(data[0:10])
    print(data[data[:, 0] < 0.1])

    # plot_normal_graph(data, csvfilename)

    # plot_scatter_graph(data, csvfilename)

    b1, b2, b3, b4, b5 = return_bands(data)

    print(f'Median b1 {np.median(b1[:,1])}')
    print(f'Median b2 {np.median(b2[:,1])}')
    print(f'Median b3 {np.median(b3[:,1])}')
    print(f'Median b4 {np.median(b4[:,1])}')
    print(f'Median b5 {np.median(b5[:,1])}')
    # plot_scatter_graph_bands(b1, b2, b3, b4, b5, csvfilename)

    plot_scatter_graph_bands(b1, b2, apply_median(b3), apply_median(b4), apply_median(b5), csvfilename)



def main():
    print(f'Hello World')

    # with open(CSV_INPUT_FILE, mode='r') as f:
    #     print(f.read())

    # get_csv_metadata_from_sta(STA_FILE)

    plot_data(CSV_INPUT_FILE)


if __name__ == "__main__":
    main()
