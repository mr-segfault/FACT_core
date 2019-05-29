import re
import xml.etree.ElementTree as Et
from datetime import datetime
from io import BytesIO
from json import load
from zipfile import ZipFile
from typing import Tuple

import requests

from .meta import get_meta
from .meta import unbinding


def get_cve_links(url: str) -> list:
    '''
    generates all years from 2002 to the recent year and put each
    in a separate CVE URL which is added to a cve_urls list
    :param url: contains blue print of CVE URL
    :return list of CVE URLs
    '''
    cve_urls = list()
    current = datetime.today().year
    for year in range(2002, current+1):
        cve_urls.append(url.format(year))

    return cve_urls


def iterate_urls(dl_urls: list, path: str) -> None:
    '''
    Iterates through all specified download urls and downloads files to specified path
    :param dl_urls: list of download urls
    :param path: destination path for downloaded files
    :return: None
    '''
    request = None
    for url in dl_urls:
        try:
            request = requests.get(url, allow_redirects=True)
        except requests.exceptions.RequestException as err:
            exit('Error: URLs are invalid. URL format might have been changed or website might have moved. ' + str(err))

        zipped_data = ZipFile(BytesIO(request.content))
        zipped_data.extractall(path)


def download_cve(dl_urls: list, years: list, meta: dict) -> list:
    '''
    Prepares download urls from all specified years if available
    :param dl_urls: list of specified download links
    :param years: specifies which CVE feeds should be downloaded
    :param meta: contains the link structure for a CVE link
    :return: dl_urls
    '''
    cve_candidates = get_cve_links(meta['source_urls']['cve_source'])
    if cve_candidates is None:
        exit('Error: No CVE links are provided')
    if years is None:
        exit('Error: The required years of CVE feeds are not specified')
    for candidate in cve_candidates:
        for year in years:
            if str(year) in candidate:
                dl_urls.append(candidate)

    return dl_urls


def download_data(cpe: bool = False, cve: bool = False, update: bool = False, path: str = None,
                  years: list = None) -> None:
    '''

    :param cpe: boolean specifying if CPE should be downloaded
    :param cve: boolean specifying if CVE should be downloaded
    :param update: boolean specifying if CVE should be updated
    :param path: destination path for downloaded files
    :param years: specified CVE years
    :return: None
    '''
    dl_urls = list()
    meta = get_meta()
    if meta is None:
        exit('Error: No source URLs provided. Check metadata.json if required URL is set.')
    # if the download options cpe, cve or update are not set, nothing can be downloaded
    if not cpe and not cve and not update:
        exit('Error: No file specified for download.')
    # a list of URLs is declared and the URLs are appended depending on the download options chosen
    if cpe:
        dl_urls.append(meta['source_urls']['cpe_source'])
    if update:
        dl_urls.append(meta['source_urls']['cve_source'].format('modified'))
    # in contrast to cpe or update the CVE feed links are resolved dynamically because each year new feeds are added
    # and the user is able to chose which years should be downloaded
    if cve:
        dl_urls.extend(download_cve(dl_urls, years, meta))

    iterate_urls(dl_urls, path)


def iterate_nodes(nodes: list, cpe_entries: list) -> list:
    '''
    helper function which iterates recursively through
    the dictionary nodes and checks if CPE is vulnerable and a duplicate. It then adds the entry to a list.
    :param nodes: contains CPE entries with logical operators
    :param cpe_entries: contains previously added cpe entries since function is recursive
    :return list of CPE entries
    '''
    for dicts in nodes:
        if 'cpe_match' in dicts.keys():
            for cpe in dicts['cpe_match']:
                if cpe['vulnerable'] is True:
                    cpe_entries.append(cpe['cpe23Uri'])
        elif 'children' in dicts.keys():
            iterate_nodes(dicts['children'], cpe_entries)

    return cpe_entries


def extract_cve(file: str) -> Tuple[list, list]:
    '''
    gets the path to a CVE file and retrieves all CVE ids and the corresponding CPE entries.
    If a CVE feed does not contain CPE entries and is not a rejected feed, the summary of the feeds is saved.
    :param file: contains path to CVE feed
    :return two lists containing CVE entries and summaries
    '''
    feeds = None
    cve_list = list()
    summary_list = list()
# get all json feeds from the directory
    try:
        feeds = open(file)
        root = load(feeds)
        items = root['CVE_Items']
        for vuln in items:
            cpe_entries = []
            # for each vulnerability in the feeds get the CVE id and the summary
            cve_id = vuln['cve']['CVE_data_meta']['ID']
            summary = vuln['cve']['description']['description_data'][0]['value']
            # if no CPE ids are contained and if the vulnerability has not been rejected, put the summary into
            # a separate list
            if not vuln['configurations']['nodes'] and not summary.startswith('** REJECT **'):
                summary_list.append(cve_id)
                summary_list.append(summary)
            # else put CVE id and the software products into the CVE list
            elif vuln['configurations']['nodes']:
                cve_list.append(cve_id)
                # conversion between list and set because duplicate cpe values in feeds
                cpe_entries = list(set(iterate_nodes(vuln['configurations']['nodes'], cpe_entries)))
                cve_list.extend(cpe_entries)
                del cpe_entries
    except IOError as err:
        exit(err)
    finally:
        feeds.close()

    return cve_list, summary_list


def extract_cpe(file: str) -> list:
    '''
    gets the path to the CPE dictionary and returns all CPE 2.3 format strings
    :param file: contains path to CPE dictionary file
    :return list with CPE entries
    '''
    cpe_list = []
    tree = None
    # parse the XML file and get the root of the DOM tree
    try:
        tree = Et.parse(file)
    except Et.ParseError as err:
        exit(err)
    root = tree.getroot()

    for entry in root:
        for item in entry:
            if 'cpe23-item' in item.tag:
                cpe_list.append(item.attrib['name'])

    return cpe_list


def setup_cve_table(cve_list: list, summary_list: list) -> Tuple[list, list]:
    '''
    gets the cve and summary list returned from extract_cve() and transforms them into the appropriate table format.
    :param cve_list: contains extracted list of CVE feeds
    :param summary_list: contains extracted list of CVE summaries
    :return two lists containing CVE feeds and summaries in the appropriate table format
    '''
    cve_table, summary_table = [], []
    ident = ''
    row = []
    for entry in cve_list:
        if re.match(r'CVE-[0-9]{4}-[0-9]', entry):
            ident = entry
        else:
            row.append(ident)
            year = ident.split('-')[1]
            row.append(year)
            row.append(entry)
            row.extend(unbinding(re.split(r'(?<!\\)[:]', entry)[2:]))
            cve_table.append(tuple(row))
            row = []

    if summary_list:
        for entry in summary_list:
            if re.match(r'CVE-[0-9]{4}-[0-9]', entry):
                row.append(entry)
                year = entry.split('-')[1]
                row.append(year)
            else:
                row.append(entry)
                summary_table.append(tuple(row))
                row = []

    return cve_table, summary_table


def setup_cpe_table(cpe_list: list) -> list:
    '''
    gets the CPE list returned from extract_cpe() and transforms the entries into a appropriate table format.
    :param cpe_list: contains extracted list of CPE entries
    :return list containing appropriate CPE table format
    '''
    cpe_table = []
    for cpe in cpe_list:
        row = unbinding(re.split(r'(?<!\\)[:]', cpe)[2:])
        row.insert(0, cpe)
        cpe_table.append(tuple(row))

    return cpe_table