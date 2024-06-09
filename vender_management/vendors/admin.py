from django.contrib import admin
from .models import Vendor, PurchaseOrder, HistoricalPerformance


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Vendor._meta.fields]


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PurchaseOrder._meta.fields]


@admin.register(HistoricalPerformance)
class HistoricalPerformanceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in HistoricalPerformance._meta.fields]
