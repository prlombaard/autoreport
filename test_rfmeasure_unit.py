import pytest
import rfmeasure


# rfmeasure.analyse_data()
# rfmeasure.apply_median()
# rfmeasure.apply_threshold()
# rfmeasure.get_csv_metadata_from_sta()
# rfmeasure.get_timestamp_from_csv()
# rfmeasure.get_xml_data()
# rfmeasure.main()
# rfmeasure.plot_normal_graph()
# rfmeasure.plot_scatter_graph_bands()


@pytest.mark.parametrize('csv_file_path,expected',
                         [('./data/VG2/SITE_VG2-NB1.csv', '28 November 2017 1317'),
                          ('./data/VG2/SITE_VG2-NB3.csv', '29 November 2017 1049')])
def test_get_timestamp_from_csv_default(csv_file_path, expected):
    assert rfmeasure.get_timestamp_from_csv(csv_file_path) == expected


@pytest.mark.parametrize('sta_file_path,expected',
                         [('./data/VG2/SITE_VG2-NB1.sta',
                           {'resolutionbandwidth': 30, 'startfrequency': 100000, 'stopfrequency': 30000000}),
                          ('./data/VG2/SITE_VG2-NB3.sta',
                           {'resolutionbandwidth': 30, 'startfrequency': 100000, 'stopfrequency': 30000000}),
                          ('./data/VG2/SITE_VG2-WB1.sta',
                           {'resolutionbandwidth': 1000, 'startfrequency': 100000, 'stopfrequency': 30000000})])
def test_get_timestamp_from_csv_default(sta_file_path, expected):
    assert rfmeasure.get_csv_metadata_from_sta(sta_file_path) == expected


@pytest.mark.skip(reason="Skipping test because this function is actually deprecated")
def test_plot_normal_graph_default_values():
    rfmeasure.plot_normal_graph([0, 1, 2], "./data/VG2/SITE_VG2-NB1.sta")
    assert True == True



def test_always_true():
    assert True == 1
