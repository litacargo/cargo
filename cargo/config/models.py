import json
from django.db import models

class Configuration(models.Model):
    name = models.CharField(max_length=255) 
    description = models.TextField(null=True, blank=True) 
    key = models.CharField(max_length=255, unique=True) # Уникальный ключ
    value = models.TextField()  # Универсальное поле для хранения любых значений

    def __str__(self):
        return f"{self.name}: {self.key}"

    def get_value(self):
        """Декодировать значение из строки в нужный тип."""
        try:
            return json.loads(self.value)  # Попытка преобразовать в Python-объект
        except json.JSONDecodeError:
            return self.value  # Если это просто строка

    def set_value(self, new_value):
        """Установить значение и сохранить в строковом формате."""
        if isinstance(new_value, (dict, list, int, float, bool)):
            self.value = json.dumps(new_value)  # Преобразовать в JSON-строку
        else:
            self.value = str(new_value)  # Сохранить как строку
        self.save()

    @staticmethod
    def get_config(key, default=None):
        """Получить значение по ключу с поддержкой типа."""
        config = Configuration.objects.filter(key=key).first() 
        return config.get_value() if config else default 

    @staticmethod
    def set_config(key, new_value):
        """Установить значение для ключа."""
        config, _ = Configuration.objects.get_or_create(key=key) 
        config.set_value(new_value)

    @staticmethod
    def get_unit_price():
        """Fetch unit price from configuration, defaulting to 3 if not set."""
        unit_price = Configuration.get_config("unit_price", default=3) # Получить значение по ключу
        try:
            # Убедимся, что возвращается числовое значение
            print(unit_price)
            return float(unit_price)
        except (ValueError, TypeError):
            return 3  # Если значение некорректное, вернуть значение по умолчанию