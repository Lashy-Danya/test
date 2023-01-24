from django import forms
from django.forms import inlineformset_factory

from .models import (Product, Category, ProductType, 
                    Manufacturer, ProductTechnicalDataValue)

class AddProductForm(forms.Form):
    """Форма добавления товара"""
    name = forms.CharField(label='Название' ,widget=forms.TextInput(
        attrs={
            'class': 'form-control', 'placeholder': 'Название', 'id': 'product_name'
        }
    ))
    description = forms.CharField(label='Описание' ,widget=forms.Textarea(
        attrs={
            'class': 'form-control', 'placeholder': 'Описание', 
            'id': 'product_description', 'rows': '3'
        }
    ))
    product_type = forms.ModelChoiceField(
        label='Тип товара', queryset=ProductType.objects.all(),
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }
        )
    )
    category = forms.ModelChoiceField(
        label='Категория', queryset=Category.objects.all(),
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }
        )
    )
    manufacturer = forms.ModelChoiceField(
        label='Производитель', queryset=Manufacturer.objects.all(),
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }
        )
    )
    price = forms.IntegerField(label='Цена', widget=forms.NumberInput(
        attrs={
            'class': 'form-control', 'placeholder': "Цена"
        }
    ))
    warranty = forms.IntegerField(label='Гарантия', widget=forms.NumberInput(
        attrs={
            'class': 'form-control', 'placeholder': "Гарантия"
        }
    ))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = 'Категория не выбрана'
        self.fields['product_type'].empty_label = 'Тип товара не выбран'
        self.fields['manufacturer'].empty_label =  'Производитель не выбран'
    

class EditProductForm(forms.ModelForm):
    """Форма для редактирования товара"""

    class Meta:
        model = Product
        fields = ('name', 'description', 'price', 'warranty')

class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = (
            'name', 'description', 'price', 'warranty', 
            'product_type', 'category', 'manufacturer', 'count'
        )

        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control', 'placeholder': 'Описание товара',
                    'rows': '3'
                }
            ),
            'price': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'warranty': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'product_type': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),
            'category': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),
            'manufacturer': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),
            'count': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = 'Категория не выбрана'
        self.fields['product_type'].empty_label = 'Тип товара не выбран'
        self.fields['manufacturer'].empty_label =  'Производитель не выбран'

class TechnicalDataValueForm(forms.ModelForm):
    """Форма для характеристик"""

    class Meta:
        model = ProductTechnicalDataValue
        fields = ['technical_data', 'value']

        widgets = {
            'technical_data': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'value': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            )
            
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['technical_data'].empty_label = 'Параметр не выбран'

TechnicalDataValueFormSet = inlineformset_factory(
    Product, ProductTechnicalDataValue, form=TechnicalDataValueForm, extra=1,
    can_delete=True, can_delete_extra=True
)

class ManufacturerForm(forms.Form):
    """Форма для производителя"""

    name = forms.CharField(label='Название' ,widget=forms.TextInput(
        attrs={
            'class': 'form-control', 'placeholder': 'Название'
        }
    ))
    country = forms.CharField(label='Страна' ,widget=forms.TextInput(
        attrs={
            'class': 'form-control', 'placeholder': 'Страна'
        }
    ))