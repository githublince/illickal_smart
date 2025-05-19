from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.db import models
from django.contrib.auth.models import User

from django.db import models
import base64

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.db import transaction
from django.db import IntegrityError
import base64

import base64
from django.db import models, transaction


class Product(models.Model):
    product_id = models.CharField(max_length=20, primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    rr_price = models.DecimalField(max_digits=10, decimal_places=2)
    mr_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_photo = models.BinaryField(blank=True, null=True)
    product_photo_mime = models.CharField(max_length=50, blank=True)
    _base64_image = models.TextField(blank=True, null=True)  # Cache for base64 string

    def save(self, *args, **kwargs):
        if not self.product_id:
            max_attempts = 10
            for attempt in range(max_attempts):
                try:
                    with transaction.atomic():
                        last = Product.objects.order_by('-product_id').first()
                        next_id = int(last.product_id[2:]) + 1 if last else 1
                        self.product_id = f'PR{next_id:08d}'
                        # Set _base64_image before the first save
                        if self.product_photo:
                            self._base64_image = base64.b64encode(self.product_photo).decode('utf-8')
                        else:
                            self._base64_image = None
                        super().save(*args, **kwargs)
                        break
                except IntegrityError:
                    if attempt == max_attempts - 1:
                        raise ValueError("Unable to generate a unique product_id after multiple attempts.")
                    continue
        else:
            # Update _base64_image before saving
            if self.product_photo:
                self._base64_image = base64.b64encode(self.product_photo).decode('utf-8')
            else:
                self._base64_image = None
            super().save(*args, **kwargs)

    def get_image_data(self):
        if self._base64_image and self.product_photo_mime:
            return f"data:{self.product_photo_mime};base64,{self._base64_image}"
        return '/static/no-image.png'

    def get_mobile_image_data(self):
        if self.product_photo:
            return f"data:{self.product_photo_mime};base64,{base64.b64encode(self.product_photo).decode('utf-8')}"
        return '/static/no-image.png'

class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    manager_id = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    whatsapp_number = models.CharField(max_length=20)
    address = models.TextField()
    pincode = models.CharField(max_length=10)

    def save(self, *args, **kwargs):
        if not self.manager_id:
            last = Manager.objects.order_by('-manager_id').first()
            if last and last.manager_id:
                last_id = int(last.manager_id.replace('MGR', ''))
            else:
                last_id = 0
            self.manager_id = f"MGR{last_id + 1:07d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    agent_id = models.CharField(max_length=20, primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    whatsapp_number = models.CharField(max_length=15)
    address = models.TextField()
    pincode = models.CharField(max_length=6)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.agent_id:
            last = Agent.objects.order_by('agent_id').first()
            next_id = int(last.agent_id[3:]) + 1 if last else 1
            self.agent_id = f'AGT{next_id:07d}'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_agent_id(self):
        return self.agent_id




class Store(models.Model):
    store_id = models.CharField(max_length=20, primary_key=True, editable=False)
    store_name = models.CharField(max_length=100)
    store_owner = models.CharField(max_length=100)
    gst_number = models.CharField(max_length=20)
    block = models.CharField(max_length=100)
    address = models.TextField()
    nearby = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    phone_number = models.CharField(max_length=15)
    whatsapp_number = models.CharField(max_length=15)
    location = models.CharField(max_length=100)  # GPS coords
    photo = models.ImageField(upload_to='store_photos/')
    email = models.EmailField()

    def save(self, *args, **kwargs):
        if not self.store_id:
            last = Store.objects.order_by('-store_id').first()
            next_id = int(last.store_id[3:]) + 1 if last else 1
            self.store_id = f'STR{next_id:08d}'
        super().save(*args, **kwargs)

class AgentBalance(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)


class Transaction(models.Model):
    TRANSACTION_TYPE = (
        ('credit', 'credit'),
        ('return', 'return')
    )
    transaction_id = models.CharField(max_length=20, primary_key=True, editable=False)
    transaction_date = models.DateField(default=now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            last = Transaction.objects.order_by('-transaction_id').first()
            next_id = int(last.transaction_id[3:]) + 1 if last else 1
            self.transaction_id = f'TRN{next_id:011d}'
        super().save(*args, **kwargs)

class BillDate(models.Model):
    billno = models.CharField(max_length=25, primary_key=True, editable=False)
    date = models.DateField(default=now)

    def save(self, *args, **kwargs):
        if not self.billno:
            last = BillDate.objects.order_by('-billno').first()
            next_id = int(last.billno[4:]) + 1 if last else 1
            self.billno = f'BILL{next_id:015d}'
        super().save(*args, **kwargs)

class Bill(models.Model):
    billno = models.ForeignKey(BillDate, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.PositiveIntegerField()
    
    @property
    def total_price(self):
        return self.count * self.product.rr_price
    

from django.db import models
from django.utils.timezone import now

class ManagerAgentTransaction(models.Model):
    transaction = models.ForeignKey('Transaction', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    manager = models.ForeignKey('Manager', on_delete=models.CASCADE)
    agent = models.ForeignKey('Agent', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    transaction_date = models.DateField(default=now)

    class Meta:
        verbose_name = 'Manager-Agent Transaction'
        verbose_name_plural = 'Manager-Agent Transactions'
        unique_together = ('transaction', 'product')  # Ensure each transaction-product pair is unique

    def __str__(self):
        return f"{self.transaction.transaction_id} - {self.product.name} (Qty: {self.quantity})"

    @property
    def total_price(self):
        return self.quantity * self.product.rr_price
