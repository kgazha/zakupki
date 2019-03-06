import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zakupki.settings")
os.environ["DJANGO_SETTINGS_MODULE"] = "zakupki.settings"
import django
django.setup()

from zakupki.settings import BASE_DIR
import zipfile
import pathlib


def unzip_file(_from_dirname, _to_dirname, filename):
    if not os.path.exists(os.path.join(BASE_DIR, 'unzipped', _to_dirname, filename.split('.')[0])):
        zip_ref = zipfile.ZipFile(os.path.join(_from_dirname, filename), 'r')
        folder = os.path.join(BASE_DIR, 'unzipped', _to_dirname, filename.split('.')[0])
        pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
        zip_ref.extractall(folder)
        zip_ref.close()


subdirs = []
for dirname, dirnames, filenames in os.walk('.\\downloaded'):
    for subdirname in dirnames:
        subdirs.append(subdirname)
    for filename in filenames:
        for _dir in subdirs:
            if _dir in dirname:
                try:
                    unzip_file(dirname, _dir, filename)
                except:
                    pass
