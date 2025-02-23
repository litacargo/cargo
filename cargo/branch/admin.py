from django.contrib import admin
from .models import Branch, EmployeeBranchAccess, ChinaAddress
# Register your models here.

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code')
    search_fields = ('name', 'code')

@admin.register(EmployeeBranchAccess)
class EmployeeBranchAccessAdmin(admin.ModelAdmin):
    list_display = ("user",)
    filter_horizontal = ("branches",)

@admin.register(ChinaAddress)
class ChinaAddress(admin.ModelAdmin):
    pass