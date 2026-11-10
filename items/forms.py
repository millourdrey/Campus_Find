from django import forms
from .models import Item


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            'title',
            'description',
            'category',
            'report_type',
            'location',
            'date_lost_found',
            'photo',
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter item name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the item'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'report_type': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Where was it lost or found?'
            }),
            'date_lost_found': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }


class ClaimRequestForm(forms.Form):
    message = forms.CharField(
        label='Why is this item yours?',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Describe identifying details to help verify ownership.'
        })
    )
