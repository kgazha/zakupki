from django.db import models


class Resource(models.Model):
    code = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.path


class PurchaseTypeControl(models.Model):
    code = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.code


class PlacingWay(models.Model):
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Organization(models.Model):
    reg_num = models.CharField(max_length=255)
    cons_registry_num = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    full_name = models.TextField(blank=True, null=True)
    post_address = models.CharField(max_length=255, blank=True, null=True)
    fact_address = models.CharField(max_length=255, blank=True, null=True)
    inn = models.CharField(max_length=255, unique=True)
    kpp = models.CharField(max_length=255, blank=True, null=True)
    okato = models.CharField(max_length=255, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name


class FinanceSource(models.Model):
    name = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Purchase(models.Model):
    object_info = models.TextField(blank=True, null=True)
    purchase_number = models.CharField(max_length=255, unique=True)
    placing_way = models.ForeignKey(PlacingWay, on_delete=models.SET_NULL, blank=True, null=True)
    max_price = models.FloatField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    sign_date = models.DateField(blank=True, null=True)
    protocol_date = models.DateField(blank=True, null=True)
    direct_date = models.DateTimeField(blank=True, null=True)
    doc_publish_date = models.DateTimeField(blank=True, null=True)
    finance_source = models.ForeignKey(FinanceSource, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.purchase_number


class OrganizationRole(models.Model):
    name = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class OrganizationPurchase(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, blank=True, null=True)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, blank=True, null=True)
    organization_role = models.ForeignKey(OrganizationRole, on_delete=models.CASCADE, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class OKPD(models.Model):
    code = models.CharField(max_length=255)
    name = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class OKPD2(models.Model):
    code = models.CharField(max_length=255)
    name = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class OKEI(models.Model):
    code = models.CharField(max_length=255)
    national_code = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class PurchaseObject(models.Model):
    okpd = models.ForeignKey(OKPD, on_delete=models.SET_NULL, blank=True, null=True)
    okpd2 = models.ForeignKey(OKPD2, on_delete=models.SET_NULL, blank=True, null=True)
    okei = models.ForeignKey(OKEI, on_delete=models.SET_NULL, blank=True, null=True)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    price = models.FloatField(blank=True, null=True)
    quantity = models.FloatField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)


class Archive(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class File(models.Model):
    name = models.CharField(max_length=255)
    archive = models.ForeignKey(Archive, on_delete=models.CASCADE)
    purchase = models.ForeignKey(Purchase, on_delete=models.SET_NULL, blank=True, null=True)
    purchase_type_control = models.ForeignKey(PurchaseTypeControl, on_delete=models.SET_NULL, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
