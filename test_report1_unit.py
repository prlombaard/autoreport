import pytest
import report1


@pytest.mark.parametrize('valid_date_times, expected',
                         [('27 January 2017 12:34', '26 January 2017 1234'),
                          ('01 January 2017 12:34', '31 December 2016 1234')])
def test_adjust_time_default_values(valid_date_times, expected):
    assert report1.adjust_time(valid_date_times) == expected


@pytest.mark.parametrize('valid_date_times, expected,valid_formats',
                         [('27 January 2017 12:34', '2601171234', 'DDMMYYHHmm'),
                          ('01 January 2017 12:34', '1612313412', 'YYMMDDmmHH')])
def test_adjust_time_valid_formats(valid_date_times, expected, valid_formats):
    assert report1.adjust_time(valid_date_times, datetimeformat=valid_formats) == expected


@pytest.mark.parametrize('csv_file_path,expected',
                         [('./data/VG2/SITE_VG2-NB1.csv', '28 November 2017 1317'),
                          ('./data/VG2/SITE_VG2-NB3.csv', '29 November 2017 1049')])
def test_get_timestamp_from_csv_default(csv_file_path, expected):
    assert report1.get_timestamp_from_csv(csv_file_path) == expected


@pytest.mark.parametrize('csv_file_path,expected',
                         [('./data/VG2/SITE_VG2-NB1.csv', '27 November 2017 1317'),
                          ('./data/VG2/SITE_VG2-NB3.csv', '28 November 2017 1049')])
def test_get_timestamp_from_csv_and_adjusted(csv_file_path, expected):
    assert report1.adjust_time(report1.get_timestamp_from_csv(csv_file_path)) == expected

# timestamp = adjust_time(timestamp, datetimeformat=datetimeformat)
