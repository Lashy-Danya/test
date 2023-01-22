from django.contrib import admin

from .models import Vendor, ShipmentDetails, ShipmentDetailsData

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['name',]

class ShipmentDetailsDataInline(admin.TabularInline):
    model = ShipmentDetailsData

@admin.register(ShipmentDetails)
class ShipmentDetailsAdmin(admin.ModelAdmin):
    inlines = [ShipmentDetailsDataInline,]