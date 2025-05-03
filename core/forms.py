
from django import forms
from .models import Agent, Store, BillDate, Bill, Product
from django.forms import modelformset_factory

class AgentForm(forms.ModelForm):
    same_as_phone = forms.BooleanField(required=False, label="Same as Phone Number")

    class Meta:
        model = Agent
        fields = ['name', 'phone_number', 'whatsapp_number', 'address', 'pincode']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('same_as_phone'):
            cleaned_data['whatsapp_number'] = cleaned_data.get('phone_number')
        return cleaned_data

class StoreForm(forms.ModelForm):
    same_as_phone = forms.BooleanField(required=False, label="Same as Phone Number")

    class Meta:
        model = Store
        exclude = ('store_id',)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('same_as_phone'):
            cleaned_data['whatsapp_number'] = cleaned_data.get('phone_number')
        return cleaned_data

class BillDateForm(forms.ModelForm):
    class Meta:
        model = BillDate
        fields = []

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['product', 'count']
