import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zakupki.settings")
os.environ["DJANGO_SETTINGS_MODULE"] = "zakupki.settings"
import django
django.setup()

from xml.dom import minidom
from zakupki.settings import BASE_DIR
from core import models


def get_dirnames(path):
    _subdirnames = []
    for dirname, dirnames, filenames in os.walk(path):
        for subdirname in dirnames:
            _subdirnames.append(subdirname)
    return _subdirnames


def get_filenames(path):
    _filenames = []
    for dirname, dirnames, filenames in os.walk(path):
        for filename in filenames:
            _filenames.append(filename)
    return _filenames


def _get_paths_by_dir():
    path_unzipped = os.path.join(BASE_DIR, 'unzipped')
    dirs = next(os.walk(path_unzipped))[1]
    paths_by_dir = {}
    for _dir in dirs:
        dirnames = get_dirnames(os.path.join(path_unzipped, _dir))
        paths = []
        for dirname in dirnames:
            paths.append(os.path.join(path_unzipped, _dir, dirname))
        paths_by_dir.update({_dir: paths})
    return paths_by_dir


def __parse_node_data_by_tag(node, tag):
    element = node.getElementsByTagName(tag)
    if element:
        return element[0].firstChild.data
    else:
        return None


def __parse_notification_ef_purchase_responsible(node):
    responsible_org = dict()
    responsible_org_node = node.getElementsByTagName('responsibleOrg')[0]
    from_tags = ['regNum', 'consRegistryNum', 'fullName', 'postAddress', 'factAddress', 'INN', 'KPP']
    to_tags = ['reg_num', 'cons_registry_num', 'full_name', 'post_address', 'fact_address', 'inn', 'kpp']
    for idx, _tag in enumerate(from_tags):
        responsible_org[to_tags[idx]] = __parse_node_data_by_tag(responsible_org_node, _tag)
    return responsible_org


def __parse_notification_ef_placing_way(node):
    placing_way_node = node.getElementsByTagName('placingWay')[0]
    code = placing_way_node.getElementsByTagName('code')[0].firstChild.data
    name = placing_way_node.getElementsByTagName('name')[0].firstChild.data
    return code, name


def parse_notification_ef(file):
    path_unzipped = os.path.join(BASE_DIR, 'unzipped')
    archive = models.Archive.objects.get(id=file.archive_id)
    resource = models.Resource.objects.get(id=archive.resource_id)
    file_path = os.path.join(path_unzipped, resource.code, archive.name.split('.')[0], file.name)
    document = minidom.parse(file_path)
    purchase_number = __parse_node_data_by_tag(document, 'purchaseNumber')
    purchase_object_info = __parse_node_data_by_tag(document, 'purchaseObjectInfo')
    purchase_responsible = __parse_notification_ef_purchase_responsible(document)
    placing_way_code, placing_way_name = __parse_notification_ef_placing_way(document)
    print(purchase_number,
          purchase_object_info,
          purchase_responsible,
          placing_way_code,
          placing_way_name)
    return (purchase_number,
            purchase_object_info,
            purchase_responsible)


def collect_file_description(_dir, _path, _filename):
    if _filename.split('.')[-1] != 'xml':
        return
    archive = models.Archive.objects.get(name__contains=_path.split(_dir)[-1].strip('\\'))
    document = minidom.parse(os.path.join(_path, _filename))
    type_control_node = document.childNodes[0]
    if type_control_node.localName == 'export':
        for node in type_control_node.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                type_control_name = node.localName
    else:
        type_control_name = type_control_node.localName
    type_control = models.PurchaseTypeControl.objects.get_or_create(code=type_control_name)[0]
    file = models.File.objects.get_or_create(name=_filename, archive=archive)[0]
    if not file.archive:
        file.archive = archive
        file.save()
    if not file.type_control:
        file.type_control = type_control
        file.save()
    # purchase_number = document.getElementsByTagName('purchaseNumber')
    # if purchase_number:
    #     purchase_number = purchase_number[0].firstChild.data
    # else:
        # return
    # purchase = models.Purchase.objects.get_or_create(purchase_number=purchase_number)[0]
    # file = models.File.objects.get(name=_filename, archive=archive)
    # file.purchase = purchase
    # file.save()


def collect_file_descriptions():
    __paths_by_dir = _get_paths_by_dir()
    for _dir in __paths_by_dir:
        for _path in __paths_by_dir[_dir]:
            filenames = get_filenames(_path)
            for _filename in filenames:
                collect_file_description(_dir, _path, _filename)


# collect_file_descriptions()
files = models.File.objects.filter(id__lte=40)
for file in files:
    parse_notification_ef(file)
