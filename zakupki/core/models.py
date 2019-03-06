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
    date_added = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

    def __str__(self):
        return self.name


class Organization(models.Model):
    reg_num = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    post_address = models.CharField(max_length=255, blank=True, null=True)
    fact_address = models.CharField(max_length=255, blank=True, null=True)
    inn = models.CharField(max_length=255)
    kpp = models.CharField(max_length=255)
    email = models.EmailField(max_length=254, blank=True, null=True)
    site = models.URLField(max_length=200, blank=True, null=True)
    date_added = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

    def __str__(self):
        return self.full_name


class FinanceSource(models.Model):
    name = models.CharField(max_length=255)
    date_added = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

    def __str__(self):
        return self.name


class Purchase(models.Model):
    description = models.CharField(max_length=255, blank=True, null=True)
    purchase_number = models.CharField(max_length=255, blank=True, null=True)
    placing_way = models.ForeignKey(PlacingWay, on_delete=models.CASCADE, blank=True, null=True)
    max_price = models.IntegerField(blank=True, null=True)
    responsible = models.ForeignKey(Organization, on_delete=models.CASCADE, blank=True, null=True)
    customer = models.ForeignKey(Organization, on_delete=models.CASCADE, blank=True, null=True)
    finance_source = models.ForeignKey(FinanceSource, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.purchase_number


class OKPD(models.Model):
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    date_added = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

    def __str__(self):
        return self.name


class OKEI(models.Model):
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    date_added = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

    def __str__(self):
        return self.name


class PurchaseObject(models.Model):
    okpd = models.ForeignKey(OKPD, on_delete=models.CASCADE)
    okei = models.ForeignKey(OKEI, on_delete=models.CASCADE)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    price = models.IntegerField(blank=True, null=True)
    date_added = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)


class Archive(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255)
    date_added = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

    def __str__(self):
        return self.name


class File(models.Model):
    name = models.CharField(max_length=255)
    archive = models.ForeignKey(Archive, on_delete=models.CASCADE)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, blank=True, null=True)
    type_control = models.ForeignKey(PurchaseTypeControl, on_delete=models.CASCADE, blank=True, null=True)
    date_added = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

    def __str__(self):
        return self.name
