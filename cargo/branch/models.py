from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Branch(models.Model):
    name = models.CharField(max_length=250)
    code = models.CharField()
    address = models.TextField()
    
    class Meta:
        verbose_name = 'Филиал'
        verbose_name_plural = 'Филиалы'

    def save(self, *args, **kwargs):
        old_branch = Branch.objects.get(pk=self.pk) if self.pk else None
        super().save(*args, **kwargs)
        
        if old_branch and old_branch.code != self.code:
            for client in self.clients.all():
                client.code = f"{self.code}{client.numeric_code}"
                client.save(update_fields=['code'])

    def __str__(self):
        return self.name
    
class EmployeeBranchAccess(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="branch_access")
    branches = models.ManyToManyField(Branch, related_name="employees")

    class Meta:
        verbose_name = 'Доступ к филиалу'
        verbose_name_plural = 'Доступ к филиалам'


    def __str__(self):
        return f"{self.user.username} - Access to branches"
    

class ChinaAddress(models.Model):
    name1 = models.CharField(max_length=500)
    name2 = models.CharField(max_length=500)
    name3 = models.CharField(max_length=500)

    def save(self, *args, **kwargs):
        self.pk = 1  # Всегда используем один и тот же первичный ключ
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # Отключаем удаление, чтобы нельзя было удалить последнюю запись

    @classmethod
    def get_instance(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    class Meta:
        verbose_name = "Адрес склада китай"
        verbose_name_plural = "Адрес склада китай"

