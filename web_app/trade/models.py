from django.db import models, connections


class City(models.Model):
    name = models.CharField(max_length=32)


class Maker(models.Model):
    name = models.CharField(max_length=64)
    city = models.ForeignKey(City, on_delete=models.DO_NOTHING)
    address = models.CharField(max_length=124)
    phone = models.CharField(max_length=11)


class Tovar(models.Model):
    name = models.CharField(max_length=32)
    maker = models.ForeignKey(Maker, on_delete=models.DO_NOTHING)
    sort = models.PositiveSmallIntegerField()
    price = models.IntegerField()
    material = models.CharField(max_length=64)


class Client(models.Model):
    last_name = models.CharField(max_length=64)
    city = models.ForeignKey(City, on_delete=models.DO_NOTHING, null=True)
    phone = models.CharField(max_length=11)


class Sale(models.Model):
    tovar = models.ForeignKey(Tovar, on_delete=models.DO_NOTHING)
    client = models.ForeignKey(Client, on_delete=models.DO_NOTHING)
    date = models.DateField()
    quantity = models.SmallIntegerField()
