import sys, csv, StringIO, urlparse, zipfile
from webscraping import download, xpath


def download_locations():
    """Find latitude longitude bounding box for this country
    """
    D = download.Download(proxy_file='proxies.txt', num_retries=1)
    index_url = 'http://download.geonames.org/export/zip/'
    index_html = D.get(index_url)
    for link in xpath.search(index_html, '//pre/a/@href'):
        if link.endswith('.zip') and '_full' not in link and 'allCountries' not in link:
            download_html = D.get(urlparse.urljoin(index_url, link))
            input_zip = StringIO.StringIO()
            input_zip.write(download_html)
            tsv_data = zipfile.ZipFile(input_zip).read(link.replace('.zip', '.txt'))

            output_filename = link.replace('.zip', '_locations.csv')
            writer = csv.writer(open(output_filename, 'w'))
            found = set()
            for row in csv.reader(tsv_data.splitlines(), delimiter='\t'):
                zip_code = row[1] = row[1].split('-')[0]
                lat, lng = row[9:11]
                if lat and lng and zip_code not in found:
                    found.add(zip_code)
                    writer.writerow(row)
            print 'Downloaded to', output_filename


if __name__ == '__main__':
    download_locations()
