from glob import glob
from os import remove
from pathlib import Path

import pytest

from ..internal import data_prep as dp
from ..internal.meta import get_meta


METADATA = get_meta()

# contains a NODES list from the CVE 2012-0010 which serves as input for iterate_nodes()
NODES = [{'operator': 'AND', 'children': [{'operator': 'OR', 'cpe_match': [{'vulnerable': True, 'cpe23Uri':
                                                                            'cpe:2.3:a:microsoft:ie:6:*:*:*:*:*:*:*'}]},
                                          {'operator': 'OR', 'cpe_match': [{'vulnerable': False,
                                                                            'cpe23Uri': 'cpe:2.3:o: microsoft:windows_'
                                                                                        'xp:*:sp3:*:*:*:*:*:*'},
                                                                           {'vulnerable': False,
                                                                            'cpe23Uri': 'cpe:2.3:o:microsoft:windows_xp'
                                                                                        ':-:sp2:x64:*:*:*:*:*'}]}]},
         {'operator': 'AND', 'children': [{'operator': 'OR', 'cpe_match': [{'vulnerable': True, 'cpe23Uri':
                                                                            'cpe:2.3:a:microsoft:ie:9:*:*:*:*:*:*:*'}]},
                                          {'operator': 'OR', 'cpe_match': [{'vulnerable': False,
                                                                            'cpe23Uri': 'cpe:2.3:o:microsoft:windows_7:'
                                                                                        '*:*:x64:*:*:*:*:*'},
                                                                           {'vulnerable': False,
                                                                            'cpe23Uri': 'cpe:2.3:o:microsoft:windows_7:'
                                                                                        '*:*:x86:*:*:*:*:*'},
                                                                           {'vulnerable': False,
                                                                            'cpe23Uri': 'cpe:2.3:o:microsoft:windows_7:'
                                                                                        '*:sp1:x64:*:*:*:*:*'},
                                                                           {'vulnerable': False,
                                                                            'cpe23Uri': 'cpe:2.3:o:microsoft:windows_7:'
                                                                                        '*:sp1:x86:*:*:*:*:*'},
                                                                           {'vulnerable': False,
                                                                            'cpe23Uri': 'cpe:2.3:o:microsoft:windows_'
                                                                                        'vista:*:sp2:*:*:*:*:*:*'},
                                                                           {'vulnerable': False,
                                                                            'cpe23Uri': 'cpe:2.3:o:microsoft:windows_'
                                                                                        'vista:*:sp2:x64:*:*:*:*:*'},
                                                                           {'vulnerable': False,
                                                                            'cpe23Uri': 'cpe:2.3:o:microsoft:windows_xp'
                                                                                        ':*:sp3:*:*:*:*:*:*'}]}]},
         {'operator': 'AND', 'children': [{'operator': 'OR', 'cpe_match': [{'vulnerable': True, 'cpe23Uri':
                                                                            'cpe:2.3:a:microsoft:ie:7:*:*:*:*:*:*:*'}]},
                                          {'operator': 'OR', 'cpe_match': [{'vulnerable': False, 'cpe23Uri':
                                                                            'cpe:2.3:o:microsoft:windows_vista:*:sp2:*:'
                                                                            '*:*:*:*:*'},
                                                                           {'vulnerable': False, 'cpe23Uri':
                                                                            'cpe:2.3:o:microsoft:windows_vista:*:sp2:'
                                                                            'x64:*:*:*:*:*'},
                                                                           {'vulnerable': False, 'cpe23Uri':
                                                                            'cpe:2.3:o:microsoft:windows_xp:*:sp3:*:*:*'
                                                                            ':*:*:*'},
                                                                           {'vulnerable': False, 'cpe23Uri':
                                                                            'cpe:2.3:o:microsoft:windows_xp:-:sp2:x64:*'
                                                                            ':*:*:*:*'}]}]},
         {'operator': 'AND', 'children': [{'operator': 'OR', 'cpe_match': [{'vulnerable': True, 'cpe23Uri':
                                                                            'cpe:2.3:a:microsoft:ie:8:*:*:*:*:*:*:*'}]},
                                          {'operator': 'OR', 'cpe_match':
                                           [{'vulnerable': False, 'cpe23Uri': 'cpe:2.3:o:microsoft:windows_7:*:*:'
                                                                              'x64:*:*:*:*:*'},
                                            {'vulnerable': False,
                                             'cpe23Uri': 'cpe:2.3:o:microsoft:windows_7:*:*:x86:*:*:*:*:*'},
                                            {'vulnerable': False,
                                             'cpe23Uri': 'cpe:2.3:o:microsoft:windows_7:*:sp1:x64:*:*:*:*:*'},
                                            {'vulnerable': False,
                                             'cpe23Uri': 'cpe:2.3:o:microsoft:windows_7:*:sp1:x86:*:*:*:*:*'},
                                            {'vulnerable': False,
                                             'cpe23Uri': 'cpe:2.3:o:microsoft:windows_vista:*:sp2:*:*:*:*:*:*'},
                                            {'vulnerable': False,
                                             'cpe23Uri': 'cpe:2.3:o:microsoft:windows_vista:*:sp2:x64:*:*:*:*:*'},
                                            {'vulnerable': False, 'cpe23Uri': 'cpe:2.3:o:microsoft:windows_xp:*:sp3'
                                                                              ':*:*:*:*:*:*'}]}]}]
# contain the expected result from the extract_cve function
CVE_CPE_LIST = ['CVE-2012-0001', 'cpe:2.3:o:microsoft:windows_7:-:*:*:*:*:*:*:*',
                'cpe:2.3:o:microsoft:windows_7:-:sp1:x64:*:*:*:*:*',
                'cpe:2.3:o:microsoft:windows_7:-:sp1:x86:*:*:*:*:*',
                'cpe:2.3:o:microsoft:windows_server_2003:*:sp2:*:*:*:*:*:*',
                'cpe:2.3:o:microsoft:windows_server_2008:*:sp2:x32:*:*:*:*:*',
                'cpe:2.3:o:microsoft:windows_server_2008:*:sp2:x64:*:*:*:*:*',
                'cpe:2.3:o:microsoft:windows_server_2008:-:sp2:itanium:*:*:*:*:*',
                'cpe:2.3:o:microsoft:windows_server_2008:r2:*:itanium:*:*:*:*:*',
                'cpe:2.3:o:microsoft:windows_server_2008:r2:*:x64:*:*:*:*:*',
                'cpe:2.3:o:microsoft:windows_server_2008:r2:sp1:itanium:*:*:*:*:*',
                'cpe:2.3:o:microsoft:windows_server_2008:r2:sp1:x64:*:*:*:*:*',
                'cpe:2.3:o:microsoft:windows_vista:*:sp2:*:*:*:*:*:*',
                'cpe:2.3:o:microsoft:windows_vista:*:sp2:x64:*:*:*:*:*',
                'cpe:2.3:o:microsoft:windows_xp:*:sp2:professional_x64:*:*:*:*:*',
                'CVE-2012-0010', 'cpe:2.3:a:microsoft:ie:6:*:*:*:*:*:*:*', 'cpe:2.3:a:microsoft:ie:9:*:*:*:*:*:*:*',
                'cpe:2.3:a:microsoft:ie:7:*:*:*:*:*:*:*', 'cpe:2.3:a:microsoft:ie:8:*:*:*:*:*:*:*']

SUMMARY_EXTRACT_LIST = ['CVE-2018-20229', 'GitLab Community and Enterprise Edition before 11.3.14, '
                                          '11.4.x before 11.4.12, and 11.5.x before 11.5.5 allows Directory Traversal.',
                        'CVE-2018-8825', 'Google TensorFlow 1.7 and below is affected by: Buffer Overflow. '
                                         'The impact is: execute arbitrary code (local).']
# contains the expected result from the iterate_node function
NODE_LIST = ['cpe:2.3:a:microsoft:ie:6:*:*:*:*:*:*:*', 'cpe:2.3:a:microsoft:ie:9:*:*:*:*:*:*:*',
             'cpe:2.3:a:microsoft:ie:7:*:*:*:*:*:*:*', 'cpe:2.3:a:microsoft:ie:8:*:*:*:*:*:*:*']
# contains the expected CPE format string result from the extract_cpe function
CPE_EXTRACT_LIST = ['cpe:2.3:a:\\$0.99_kindle_books_project:\\$0.99_kindle_books:6:*:*:*:*:android:*:*',
                    'cpe:2.3:a:1000guess:1000_guess:-:*:*:*:*:*:*:*', 'cpe:2.3:a:1024cms:1024_cms:0.7:*:*:*:*:*:*:*',
                    'cpe:2.3:a:1024cms:1024_cms:1.2.5:*:*:*:*:*:*:*', 'cpe:2.3:a:1024cms:1024_cms:1.3.1:*:*:*:*:*:*:*']

# contain input and expected results of the setup_cve_format function
CVE_LIST = ['CVE-2012-0001', 'cpe:2.3:a:\\$0.99_kindle_bo\\:oks_project:\\$0.99_kindle_books:6:*:*:*:*:android:*:*',
            'cpe:2.3:a:1000guess:1000_guess:-:*:*:*:*:*:*:*', 'cpe:2.3:a:1024cms:1024_cms:0.7:*:*:*:*:*:*:*',
            'cpe:2.3:a:1024cms:1024_cms:1.2.5:*:*:*:*:*:*:*', 'CVE-2012-0002',
            'cpe:2.3:a:1024cms:1024_cms:1.3.1:*:*:*:*:*:*:*']
SUMMARY_LIST = ['CVE-2018-20229', 'GitLab Community and Enterprise Edition before 11.3.14, 11.4.x before 11.4.12, '
                                  'and 11.5.x before 11.5.5 allows Directory Traversal.', 'CVE-2018-0010',
                'Microsoft Internet Explorer 6 through 9 does not properly perform copy-and-paste operations, '
                'which allows user-assisted remote attackers to read content from a different (1) domain or (2) '
                'zone via a crafted web site, aka \'Copy and Paste Information Disclosure Vulnerability.\'']
CVE_TABLE = [('CVE-2012-0001', '2012',
              'cpe:2.3:a:\\$0.99_kindle_bo\\:oks_project:\\$0.99_kindle_books:6:*:*:*:*:android:*:*', 'a',
              '\\$0\\.99_kindle_bo\\:oks_project', '\\$0\\.99_kindle_books', '6', 'ANY', 'ANY', 'ANY', 'ANY',
              'android', 'ANY', 'ANY'),
             ('CVE-2012-0001', '2012', 'cpe:2.3:a:1000guess:1000_guess:-:*:*:*:*:*:*:*', 'a', '1000guess',
              '1000_guess', 'NA', 'ANY', 'ANY', 'ANY', 'ANY', 'ANY', 'ANY', 'ANY'),
             ('CVE-2012-0001', '2012', 'cpe:2.3:a:1024cms:1024_cms:0.7:*:*:*:*:*:*:*', 'a', '1024cms', '1024_cms',
              '0\\.7', 'ANY', 'ANY', 'ANY', 'ANY', 'ANY', 'ANY', 'ANY'),
             ('CVE-2012-0001', '2012', 'cpe:2.3:a:1024cms:1024_cms:1.2.5:*:*:*:*:*:*:*', 'a', '1024cms', '1024_cms',
              '1\\.2\\.5', 'ANY', 'ANY', 'ANY', 'ANY', 'ANY', 'ANY', 'ANY'),
             ('CVE-2012-0002', '2012', 'cpe:2.3:a:1024cms:1024_cms:1.3.1:*:*:*:*:*:*:*', 'a', '1024cms', '1024_cms',
              '1\\.3\\.1', 'ANY', 'ANY', 'ANY', 'ANY', 'ANY', 'ANY', 'ANY')]
SUMMARY_TABLE = [('CVE-2018-20229', '2018', 'GitLab Community and Enterprise Edition before 11.3.14, 11.4.x before '
                                            '11.4.12, and 11.5.x before 11.5.5 allows Directory Traversal.'),
                 ('CVE-2018-0010', '2018', 'Microsoft Internet Explorer 6 through 9 does not properly perform '
                                           'copy-and-paste operations, which allows user-assisted remote attackers '
                                           'to read content from a different (1) domain or (2) zone via a crafted '
                                           'web site, aka \'Copy and Paste Information Disclosure Vulnerability.\'')]
# contain input and expected results of the setup_cpe_format function
CPE_LIST = ['cpe:2.3:a:\\$0.99_kindle_books_project:\\$0.99_kindle_books:6:*:*:*:*:android:*:*',
            'cpe:2.3:a:1000guess:1000_guess:-:*:*:*:*:*:*:*', 'cpe:2.3:a:1024cms:1024_cms:0.7:*:*:*:*:*:*:*',
            'cpe:2.3:a:1024cms:1024_cms:1.2.5:*:*:*:*:*:*:*', 'cpe:2.3:a:1024cms:1024_cms:1.3.1:*:*:*:*:*:*:*']
CPE_TABLE = [('cpe:2.3:a:\\$0.99_kindle_books_project:\\$0.99_kindle_books:6:*:*:*:*:android:*:*', 'a',
              '\\$0\\.99_kindle_books_project', '\\$0\\.99_kindle_books', '6', 'ANY', 'ANY', 'ANY', 'ANY',
              'android', 'ANY', 'ANY'),
             ('cpe:2.3:a:1000guess:1000_guess:-:*:*:*:*:*:*:*', 'a', '1000guess', '1000_guess', 'NA', 'ANY', 'ANY',
              'ANY', 'ANY', 'ANY', 'ANY', 'ANY'),
             ('cpe:2.3:a:1024cms:1024_cms:0.7:*:*:*:*:*:*:*', 'a', '1024cms', '1024_cms', '0\\.7', 'ANY', 'ANY',
              'ANY', 'ANY', 'ANY', 'ANY', 'ANY'),
             ('cpe:2.3:a:1024cms:1024_cms:1.2.5:*:*:*:*:*:*:*', 'a', '1024cms', '1024_cms', '1\\.2\\.5', 'ANY',
              'ANY', 'ANY', 'ANY', 'ANY', 'ANY', 'ANY'),
             ('cpe:2.3:a:1024cms:1024_cms:1.3.1:*:*:*:*:*:*:*', 'a', '1024cms', '1024_cms', '1\\.3\\.1', 'ANY',
              'ANY', 'ANY', 'ANY', 'ANY', 'ANY', 'ANY')]

GET_CVE_LINKS_EXPECTED_OUTPUT = list()
for i in range(2002, 2020):
    GET_CVE_LINKS_EXPECTED_OUTPUT.append(METADATA['source_urls']['cve_source'].format(i))

DOWNLOAD_DATA_YEAR_INPUT = [2018, 2019]

DOWNLOAD_DATA_EXPECTED_OUTPUT = ['official-cpe-dictionary_v2.3.xml', 'nvdcve-1.0-2018.json', 'nvdcve-1.0-2019.json',
                                 'nvdcve-1.0-modified.json']


@pytest.fixture(scope='module', autouse=True)
def setup() -> None:
    yield None
    try:
        remove('official-cpe-dictionary_v2.3.xml')
        for file in glob('nvdcve-1.0-*.json'):
            remove(file)
    except OSError:
        pass


def test_get_cve_links():
    result = dp.get_cve_links(METADATA['source_urls']['cve_source'])
    assert GET_CVE_LINKS_EXPECTED_OUTPUT == result


def test_download_data():
    result = list()
    dp.download_data(cpe=True, cve=True, update=True, path='.', years=DOWNLOAD_DATA_YEAR_INPUT)
    result.extend(glob('official-cpe-dictionary_v2.3.xml'))
    result.extend(glob('nvdcve-1.0-*.json'))
    assert set(DOWNLOAD_DATA_EXPECTED_OUTPUT) == set(result)


def test_download_cve():
    pass


def test_iterate_urls():
    pass


def test_extract_cve():
    cve_data, summary_data = dp.extract_cve(str(Path(__file__).parent.parent) + '/test/test_resources/'
                                                                                'test_cve_extract.json')
    test_cve_list, test_summary_list = cve_data, summary_data
    assert CVE_CPE_LIST.sort() == test_cve_list.sort()
    assert SUMMARY_EXTRACT_LIST.sort() == test_summary_list.sort()


def test_iterate_nodes():
    test_node_list = []
    test_node_list = dp.iterate_nodes(NODES, test_node_list)
    assert test_node_list == NODE_LIST


def test_extract_cpe():
    test_cpe_list = dp.extract_cpe(str(Path(__file__).parent.parent) + '/test/test_resources/'
                                                                       'test_cpe_extract.xml')
    assert test_cpe_list == CPE_EXTRACT_LIST


def test_setup_cve_table():
    cve_result, sum_result = dp.setup_cve_table(CVE_LIST, SUMMARY_LIST)
    assert CVE_TABLE == cve_result
    assert SUMMARY_TABLE.sort() == sum_result.sort()


def test_setup_cpe_table():
    cpe_result = dp.setup_cpe_table(CPE_LIST)
    assert CPE_TABLE == cpe_result