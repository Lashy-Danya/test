from django.db import models
from store.models import Product

class Vendor(models.Model):
    name = models.CharField(verbose_name='Название', max_length=255)

    class Meta:
        db_table = 'vendor'
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'

    def __str__(self):
        return self.name

class ShipmentDetails(models.Model):

    SHIPMENT_TYPE = (
        ("Магазин", "Магазин"),
        ("Склад", "Склад"),
    )

    name = models.CharField(verbose_name='Номер доставки', max_length=255)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    shipment_type = models.CharField(max_length=255, choices=SHIPMENT_TYPE)
    date_shipment = models.DateTimeField(
        auto_now_add=True, 
        editable=False
    )

    class Meta:
        db_table = 'spipment_details'
        verbose_name = 'Поставка'
        verbose_name_plural = 'Поставки'

    def __str__(self):
        return self.name

class ShipmentDetailsData(models.Model):
    shipment = models.ForeignKey(ShipmentDetails, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.IntegerField(verbose_name='Количество')

    class Meta:
        db_table = 'spipment_details_data'
        verbose_name = 'Детали поставки'
        verbose_name_plural = 'Детали поставок'