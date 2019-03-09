import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zakupki.settings")
os.environ["DJANGO_SETTINGS_MODULE"] = "zakupki.settings"
import django
django.setup()

from xml.dom import minidom
from zakupki.settings import BASE_DIR
from core import models
from django.utils.dateparse import parse_datetime, parse_date


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


def __parse_notification_ef_child_by_args(node, tag, *args):
    tag_node = None
    for _node in node.childNodes:
        if _node.localName == tag:
            tag_node = _node
    if not tag_node:
        return [None for arg in args]
    data = []
    for arg in args:
        _node = tag_node.getElementsByTagName(arg)
        if _node:
            data.append(_node[0].firstChild.data)
        else:
            data.append(None)
    return data


def __parse_notification_ef_purchase_objects(nodes):
    purchase_objects = []
    for _node in nodes:
        okpd_code, okpd_name = __parse_notification_ef_child_by_args(_node, 'OKPD', 'code', 'name')
        okpd2_code, okpd2_name = __parse_notification_ef_child_by_args(_node, 'OKPD2', 'code', 'name')
        okei_code, okei_national_code, okei_full_name = __parse_notification_ef_child_by_args(_node, 'OKEI',
                                                                                              'code', 'nationalCode',
                                                                                              'fullName')
        price = __parse_node_data_by_tag(_node, 'price')
        quantity = __parse_notification_ef_child_by_args(_node, 'quantity', 'value')[0]
        purchase_objects.append({'okpd_code': okpd_code, 'okpd_name': okpd_name,
                                 'okpd2_code': okpd2_code, 'okpd2_name': okpd2_name,
                                 'okei_code': okei_code, 'okei_national_code': okei_national_code,
                                 'okei_full_name': okei_full_name, 'price': price,
                                 'quantity': quantity})
    return purchase_objects


def __parse_notification_ef_placing_way(node):
    element = node.getElementsByTagName('placingWay')
    if element:
        return element[0].getElementsByTagName('code')[0].firstChild.data,\
               element[0].getElementsByTagName('name')[0].firstChild.data
    else:
        return None, None


def __get_minidom_by_file_object(file):
    path_unzipped = os.path.join(BASE_DIR, 'unzipped')
    archive = models.Archive.objects.get(id=file.archive_id)
    resource = models.Resource.objects.get(id=archive.resource_id)
    file_path = os.path.join(path_unzipped, resource.code, archive.name.split('.')[0], file.name)
    return minidom.parse(file_path)


def parse_notification_ef(file):
    document = __get_minidom_by_file_object(file)
    purchase_number = __parse_node_data_by_tag(document, 'purchaseNumber')
    purchase_object_info = __parse_node_data_by_tag(document, 'purchaseObjectInfo')
    purchase_responsible = __parse_notification_ef_purchase_responsible(document)
    placing_way_code, placing_way_name = __parse_notification_ef_placing_way(document)
    max_price = __parse_node_data_by_tag(document, 'maxPrice')
    direct_date = __parse_node_data_by_tag(document, 'directDate')
    if direct_date:
        direct_date = parse_datetime(direct_date)
    doc_publish_date = __parse_node_data_by_tag(document, 'docPublishDate')
    if doc_publish_date:
        doc_publish_date = parse_datetime(doc_publish_date)
    finance_source = __parse_node_data_by_tag(document, 'financeSource')
    purchase_object_nodes = document.getElementsByTagName('purchaseObject')
    purchase_objects = __parse_notification_ef_purchase_objects(purchase_object_nodes)
    return {'purchase_number': purchase_number, 'purchase_object_info': purchase_object_info,
            'purchase_responsible': purchase_responsible, 'placing_way_code': placing_way_code,
            'placing_way_name': placing_way_name, 'max_price': max_price,
            'direct_date': direct_date, 'doc_publish_date': doc_publish_date,
            'finance_source': finance_source, 'purchase_objects': purchase_objects}


def __parse_contract_ef_suppliers(nodes):
    suppliers = []
    for _node in nodes:
        suppliers.append({'inn': __parse_node_data_by_tag(_node, 'inn'),
                          'kpp': __parse_node_data_by_tag(_node, 'kpp'),
                          'name': __parse_node_data_by_tag(_node, 'organizationName'),
                          'fact_address': __parse_node_data_by_tag(_node, 'factualAddress'),
                          'post_address': __parse_node_data_by_tag(_node, 'postAddress')})
    return suppliers


def parse_contract_ef(file):
    document = __get_minidom_by_file_object(file)
    purchase_number = __parse_node_data_by_tag(document, 'purchaseNumber')
    price = __parse_node_data_by_tag(document, 'price')
    sign_date = __parse_node_data_by_tag(document, 'signDate')
    if sign_date:
        sign_date = parse_date(sign_date.split('+')[0])
    protocol_date = __parse_node_data_by_tag(document, 'protocolDate')
    if protocol_date:
        protocol_date = parse_date(protocol_date.split('+')[0])
    supplier_nodes = document.getElementsByTagName('supplier')
    suppliers = __parse_contract_ef_suppliers(supplier_nodes)
    return {'purchase_number': purchase_number, 'price': price, 'suppliers': suppliers,
            'sign_date': sign_date, 'protocol_date': protocol_date}


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
    purchase_type_control = models.PurchaseTypeControl.objects.get_or_create(code=type_control_name)[0]
    file = models.File.objects.get_or_create(name=_filename, archive=archive)[0]
    if not file.archive:
        file.archive = archive
        file.save()
    if not file.purchase_type_control:
        file.purchase_type_control = purchase_type_control
        file.save()


def collect_file_descriptions():
    __paths_by_dir = _get_paths_by_dir()
    for _dir in __paths_by_dir:
        for _path in __paths_by_dir[_dir]:
            filenames = get_filenames(_path)
            for _filename in filenames:
                collect_file_description(_dir, _path, _filename)


def __save_purchase_objects_to_database(purchase, objects):
    for object in objects:
        if object['okpd_code'] and object['okpd2_code']:
            okpd = models.OKPD.objects.get_or_create(code=object['okpd_code'])[0]
            okpd2 = models.OKPD2.objects.get_or_create(code=object['okpd2_code'])[0]
            purchase_object = models.PurchaseObject.objects.get_or_create(purchase=purchase,
                                                                          okpd=okpd,
                                                                          okpd2=okpd2)[0]
        elif object['okpd_code']:
            okpd = models.OKPD.objects.get_or_create(code=object['okpd_code'])[0]
            okpd.name = object['okpd_name']
            okpd.save()
            purchase_object = models.PurchaseObject.objects.get_or_create(purchase=purchase,
                                                                          okpd=okpd)[0]
        elif object['okpd2_code']:
            okpd2 = models.OKPD2.objects.get_or_create(code=object['okpd2_code'])[0]
            okpd2.name = object['okpd2_name']
            okpd2.save()
            purchase_object = models.PurchaseObject.objects.get_or_create(purchase=purchase,
                                                                          okpd2=okpd2)[0]
        else:
            continue
        if object['okei_code'] and object['okei_national_code'] and object['okei_full_name']:
            okei = models.OKEI.objects.get_or_create(code=object['okei_code'],
                                                     national_code=object['okei_national_code'],
                                                     full_name=object['okei_full_name'])[0]
            purchase_object.okei = okei
        purchase_object.price = object['price']
        purchase_object.quantity = object['quantity']
        purchase_object.save()


def __save_suppliers_to_database(purchase, objects):
    for object in objects:
        organization = models.Organization.objects.get_or_create(inn=object['inn'])[0]
        organization.name = object['name']
        organization.fact_address = object['fact_address']
        organization.post_address = object['post_address']
        organization.save()
        organization_role = models.OrganizationRole.objects.get_or_create(name='supplier')[0]
        obj, created = models.OrganizationPurchase.objects.get_or_create(organization=organization,
                                                                         purchase=purchase,
                                                                         organization_role=organization_role)


def save_contract_sign_to_database():
    contract_sign = models.PurchaseTypeControl.objects.get(code='fcsContractSign')
    files = models.File.objects.filter(purchase_type_control_id=contract_sign.id)
    for file in files:
        data = parse_contract_ef(file)
        purchase = models.Purchase.objects.get_or_create(purchase_number=data['purchase_number'])[0]
        file.purchase = purchase
        file.save()
        purchase.price = data['price']
        purchase.sign_date = data['sign_date']
        purchase.protocol_date = data['protocol_date']
        purchase.save()
        __save_suppliers_to_database(purchase, data['suppliers'])


def save_notification_ef_to_database():
    purchase_type_control = models.PurchaseTypeControl.objects.get(code='fcsNotificationEF')
    files = models.File.objects.filter(purchase_type_control_id=purchase_type_control.id)
    for file in files:
        data = parse_notification_ef(file)
        purchase = models.Purchase.objects.get_or_create(purchase_number=data['purchase_number'])[0]
        file.purchase = purchase
        file.save()
        purchase.object_info = data['purchase_object_info']
        purchase.max_price = data['max_price']
        purchase.direct_date = data['direct_date']
        purchase.doc_publish_date = data['doc_publish_date']
        finance_source = models.FinanceSource.objects.get_or_create(name=data['finance_source'])[0]
        purchase.finance_source = finance_source
        if data['placing_way_code'] and data['placing_way_name']:
            placing_way = models.PlacingWay.objects.get_or_create(code=data['placing_way_code'],
                                                                  name=data['placing_way_name'])[0]
            purchase.placing_way = placing_way
        organization = models.Organization.objects.get_or_create(inn=data['purchase_responsible']['inn'])[0]
        organization.reg_num = data['purchase_responsible']['reg_num']
        organization.kpp = data['purchase_responsible']['kpp']
        organization.post_address = data['purchase_responsible']['post_address']
        organization.fact_address = data['purchase_responsible']['fact_address']
        organization.cons_registry_num = data['purchase_responsible']['cons_registry_num']
        organization.full_name = data['purchase_responsible']['full_name']
        organization.save()
        purchase.save()
        organization_role = models.OrganizationRole.objects.get_or_create(name='responsible')[0]
        obj, created = models.OrganizationPurchase.objects.get_or_create(organization=organization,
                                                                         purchase=purchase,
                                                                         organization_role=organization_role)
        __save_purchase_objects_to_database(purchase, data['purchase_objects'])


# collect_file_descriptions()
# save_notification_ef_to_database()
save_contract_sign_to_database()
