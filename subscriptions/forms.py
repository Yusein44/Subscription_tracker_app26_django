from django import forms
from .models import Subscription

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['name', 'company', 'department', 'price', 'currency', 'billing_cycle', 'start_date', 'invoice_file']

        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'


class CompanySettingsForm(forms.Form):
    name = forms.CharField(
        max_length=255, 
        label='Име на компанията', 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Въведи име...'})
    )
    monthly_budget = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        label='Месечен бюджет (BGN)', 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )