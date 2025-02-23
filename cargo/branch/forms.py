from django import forms
from .models import ChinaAddress

class ChinaAddressForm(forms.ModelForm):
    class Meta:
        model = ChinaAddress
        fields = ['name1', 'name2', 'name3']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Пример: добавить классы Bootstrap к каждому полю
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
