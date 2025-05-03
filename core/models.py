from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    product_id = models.CharField(max_length=20, primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    rr_price = models.DecimalField(max_digits=10, decimal_places=2)
    mr_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.product_id:
            last = Product.objects.order_by('-product_id').first()
            next_id = int(last.product_id[2:]) + 1 if last else 1
            self.product_id = f'PR{next_id:08d}'
        super().save(*args, **kwargs)

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
            last = Agent.objects.order_by('-agent_id').first()
            next_id = int(last.agent_id[3:]) + 1 if last else 1
            self.agent_id = f'AGT{next_id:07d}'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
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

class Transaction(models.Model):
    TRANSACTION_TYPE = (
        ('credit', 'Credit'),
        ('return', 'Credit Return')
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
