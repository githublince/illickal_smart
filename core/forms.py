from django import forms
from .models import Agent, Store, BillDate, Bill, Product
from django.forms import modelformset_factory
from django.contrib.auth.models import User
import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import transaction

class AgentForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    same_as_phone = forms.BooleanField(required=False, label="WhatsApp same as phone")

    class Meta:
        model = Agent
        fields = [
            'username', 'password', 'name', 'phone_number', 'whatsapp_number',
            'address', 'pincode', 'is_active', 'same_as_phone'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('same_as_phone'):
            phone_number = cleaned_data.get('phone_number')
            cleaned_data['whatsapp_number'] = phone_number
        return cleaned_data

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if not phone_number:
                raise forms.ValidationError("Phone number is required !")
        return phone_number

    def clean_whatsapp_number(self):
        whatsapp_number = self.cleaned_data['whatsapp_number']
        return whatsapp_number

    def clean_pincode(self):
        pincode = self.cleaned_data['pincode']
        if not re.match(r'^\d{6}$', pincode):
            raise forms.ValidationError("Pincode must be exactly 6 digits.")
        return pincode

    def clean_password(self):
        password = self.cleaned_data['password']
        try:
            validate_password(password)
        except forms.ValidationError as error:
            raise forms.ValidationError(error)
        return password

    def save(self, commit=True):
        with transaction.atomic():
            try:
                user = User.objects.create_user(
                    username=self.cleaned_data['username'],
                    password=self.cleaned_data['password']
                )
            except Exception as e:
                raise forms.ValidationError(f"Failed to create user: {str(e)}")
            
            agent = super().save(commit=False)
            agent.user = user
            if commit:
                agent.save()
        return agent



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



