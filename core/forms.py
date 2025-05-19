from django import forms
from django.forms import formset_factory, modelformset_factory
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.utils.timezone import now
import re

from .models import Agent, Store, BillDate, Bill, Product, Transaction, ManagerAgentTransaction

# Agent Form for creating/updating agents
class AgentForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'true'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': 'true'})
    )
    same_as_phone = forms.BooleanField(
        required=False,
        label="WhatsApp same as phone",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Agent
        fields = [
            'username', 'password', 'name', 'phone_number', 'whatsapp_number',
            'address', 'pincode', 'is_active', 'same_as_phone'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'true',
                'pattern': '[0-9]{10}',
                'title': 'Enter a 10-digit phone number'
            }),
            'whatsapp_number': forms.TextInput(attrs={
                'class': 'form-control',
                'pattern': '[0-9]{10}',
                'title': 'Enter a 10-digit WhatsApp number'
            }),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'required': 'true'}),
            'pincode': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'true',
                'pattern': '[0-9]{6}',
                'title': 'Enter a 6-digit pincode'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data:
            raise forms.ValidationError("Please fill out all required fields correctly.")
        if cleaned_data.get('same_as_phone'):
            phone_number = cleaned_data.get('phone_number')
            cleaned_data['whatsapp_number'] = phone_number
        return cleaned_data

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number:
            raise forms.ValidationError("Phone number is required!")
        if not re.match(r'^\d{10}$', phone_number):
            raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return phone_number

    def clean_whatsapp_number(self):
        whatsapp_number = self.cleaned_data.get('whatsapp_number')
        if whatsapp_number and not re.match(r'^\d{10}$', whatsapp_number):
            raise forms.ValidationError("WhatsApp number must be exactly 10 digits.")
        return whatsapp_number

    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if not pincode:
            raise forms.ValidationError("Pincode is required!")
        if not re.match(r'^\d{6}$', pincode):
            raise forms.ValidationError("Pincode must be exactly 6 digits.")
        return pincode

    def clean_password(self):
        password = self.cleaned_data.get('password')
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

# Store Form for creating/updating stores
class StoreForm(forms.ModelForm):
    same_as_phone = forms.BooleanField(
        required=False,
        label="Same as Phone Number",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Store
        exclude = ('store_id',)
        widgets = {
            'store_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'store_owner': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'gst_number': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'block': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'required': 'true'}),
            'nearby': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'pincode': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'true',
                'pattern': '[0-9]{6}',
                'title': 'Enter a 6-digit pincode'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'true',
                'pattern': '[0-9]{10}',
                'title': 'Enter a 10-digit phone number'
            }),
            'whatsapp_number': forms.TextInput(attrs={
                'class': 'form-control',
                'pattern': '[0-9]{10}',
                'title': 'Enter a 10-digit WhatsApp number'
            }),
            'location': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'photo': forms.FileInput(attrs={'accept': 'image/*', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': 'true'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data:
            raise forms.ValidationError("Please fill out all required fields correctly.")
        if cleaned_data.get('same_as_phone'):
            cleaned_data['whatsapp_number'] = cleaned_data.get('phone_number')
        return cleaned_data

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number:
            raise forms.ValidationError("Phone number is required!")
        if not re.match(r'^\d{10}$', phone_number):
            raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return phone_number

    def clean_whatsapp_number(self):
        whatsapp_number = self.cleaned_data.get('whatsapp_number')
        if whatsapp_number and not re.match(r'^\d{10}$', whatsapp_number):
            raise forms.ValidationError("WhatsApp number must be exactly 10 digits.")
        return whatsapp_number

    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if not pincode:
            raise forms.ValidationError("Pincode is required!")
        if not re.match(r'^\d{6}$', pincode):
            raise forms.ValidationError("Pincode must be exactly 6 digits.")
        return pincode

# Bill Date Form
class BillDateForm(forms.ModelForm):
    class Meta:
        model = BillDate
        fields = ['date']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': 'true'}),
        }

# Bill Form
class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['product', 'count']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'count': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'required': 'true'}),
        }

# Manager-Agent Transaction Form (optional, not currently used)
class ManagerAgentTransactionForm(forms.ModelForm):
    class Meta:
        model = ManagerAgentTransaction
        fields = ['agent', 'manager', 'transaction_date', 'product', 'quantity']
        widgets = {
            'agent': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'manager': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'transaction_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': 'true'
            }),
            'product': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'required': 'true'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transaction_date'].initial = now().date()

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('quantity') or cleaned_data['quantity'] < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        return cleaned_data

# Formset for ManagerAgentTransactionForm (optional, not currently used)
ManagerAgentTransactionFormSet = formset_factory(ManagerAgentTransactionForm, extra=1)

from django import forms
from django.forms import formset_factory
from django.utils.timezone import now
from .models import Transaction, ManagerAgentTransaction, Product

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['agent', 'transaction_date']
        widgets = {
            'agent': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'transaction_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': 'true'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transaction_date'].initial = now().date()

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('agent'):
            raise forms.ValidationError("Please select an agent.")
        if not cleaned_data.get('transaction_date'):
            raise forms.ValidationError("Please select a transaction date.")
        return cleaned_data

class ProductForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        widget=forms.HiddenInput(),
        required=False,
        to_field_name='product_id'
    )
    product_search = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control product-search',
            'placeholder': 'Search products by name...',
        }),
        required=False
    )

    class Meta:
        model = ManagerAgentTransaction
        fields = ['product', 'quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'value': 1,
                'required': 'true'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')
        
        if product and (not quantity or quantity < 1):
            raise forms.ValidationError("Quantity must be at least 1 for selected products.")
        if quantity and not product:
            raise forms.ValidationError("Please select a product for the specified quantity.")
        
        return cleaned_data

ProductFormSet = formset_factory(ProductForm, extra=0, can_delete=True)  # extra=0 to prevent additional empty forms

# Product Create Form
class ProductCreateForm(forms.ModelForm):
    product_photo = forms.ImageField(
        required=False,
        label="Product Photo",
        widget=forms.FileInput(attrs={'accept': 'image/*', 'class': 'form-control'})
    )

    class Meta:
        model = Product
        fields = ['name', 'rr_price', 'mr_price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'rr_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'required': 'true',
                'min': '0.01'
            }),
            'mr_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'required': 'true',
                'min': '0.01'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data:
            raise forms.ValidationError("Please fill out all required fields correctly.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('product_photo'):
            image_file = self.cleaned_data['product_photo']
            instance.product_photo = image_file.read()
            instance.product_photo_mime = image_file.content_type
        else:
            instance.product_photo = None
            instance.product_photo_mime = ''
        if commit:
            instance.save()
        return instance