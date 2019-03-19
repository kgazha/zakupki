import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zakupki.settings")
os.environ["DJANGO_SETTINGS_MODULE"] = "zakupki.settings"
import django
django.setup()

from downloader import Downloader


def download_files(downloader, path, foldername, file_names):
    for name in file_names:
        downloader.download_file_if_exist(path, foldername, name)


downloader = Downloader()
# resources = ['sketchplans', 'notifications', 'contracts']
resources = ['notifications']

for resource in resources:
    paths = ['/fcs_regions/Cheljabinskaja_obl/' + resource + '/',
             '/fcs_regions/Cheljabinskaja_obl/' + resource + '/currMonth/',
             '/fcs_regions/Cheljabinskaja_obl/' + resource + '/prevMonth/']
    foldername = resource
    for path in paths:
        file_names = downloader.get_file_names(path, '.+\.xml\.zip')
        file_names = [name for name in file_names if 'obl_2019' in name]
        download_files(downloader, path, foldername, file_names)
