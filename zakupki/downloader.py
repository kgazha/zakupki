import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zakupki.settings")
os.environ["DJANGO_SETTINGS_MODULE"] = "zakupki.settings"
import django
django.setup()

from core.models import Resource, Archive
from ftplib import FTP
import urllib.request
import re
import pathlib
from zakupki.settings import BASE_DIR


LOGIN = 'free'
PASSWORD = 'free'
DOMAIN = 'ftp.zakupki.gov.ru'


class Downloader:
    def __init__(self):
        self.ftp = FTP(DOMAIN)
        self.ftp.login(LOGIN, PASSWORD)
        self.foldername = None
        self.filename = None

    def get_file_names(self, path, regex):
        self.ftp.cwd(path)
        file_names = self.ftp.nlst()
        return [re.search(regex, file).group(0)
                for file in file_names if re.findall(regex, file)]

    def __download_file(self, path, foldername, filename):
        self.foldername = foldername
        self.filename = filename
        url = "ftp://" + LOGIN + ":" + PASSWORD + "@" + DOMAIN + path + "/" + filename
        folder = os.path.join(BASE_DIR, 'downloaded', foldername)
        pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, folder + "\\" + filename)

    def download_file_if_exist(self, path, foldername, filename):
        resource = Resource.objects.filter(path=path)
        if not resource:
            resource = Resource.objects.create(path=path, code=foldername)
        else:
            resource = resource[0]
        file = Archive.objects.filter(name=filename)
        if not os.path.isfile(os.path.join(BASE_DIR,
                                           'downloaded',
                                           foldername,
                                           filename)):
            self.__download_file(path, foldername, filename)
            if not file:
                Archive.objects.create(resource=resource, name=filename)
            else:
                file = file[0]
                if file.resource != resource:
                    file.resource = resource
                    file.save()


