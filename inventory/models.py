# inventory/models.py

from django.db import models
from django.utils import timezone

class Medicine(models.Model):
    """
    Represents a medicine item in the inventory with detailed attributes.
    """
    CATEGORY_CHOICES = [
        ('Tablet', 'Tablet'),
        ('Syrup', 'Syrup'),
        ('Injection', 'Injection'),
        ('Ointment', 'Ointment'),
        ('Capsule', 'Capsule'),
        ('Other', 'Other'),
    ]

    # Core Info
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Pricing
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price at which the item was purchased.")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price at which the item is sold.")

    # Stock & Batch Info
    quantity = models.PositiveIntegerField(default=0)
    batch_number = models.CharField(max_length=50, blank=True, help_text="Unique code for each batch.")

    # Dates
    purchase_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField()
    added_date = models.DateTimeField(auto_now_add=True)

    # Categorization & Details
    brand_name = models.CharField(max_length=100, blank=True, help_text="Name of the brand or manufacturer.")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    dosage_form = models.CharField(max_length=100, blank=True, help_text="e.g., 500mg tablet, 5ml/5mg syrup")

    # Supplier & Storage
    supplier_name = models.CharField(max_length=100, blank=True, help_text="Name of the supplier.")
    storage_info = models.TextField(blank=True, help_text="e.g., Keep refrigerated, Store away from sunlight")
    location = models.CharField(max_length=100, blank=True, help_text="e.g., Shelf 3, Box A, Fridge")

    def __str__(self):
        return f"{self.name} ({self.brand_name})"

    class Meta:
        ordering = ['name']


class Sale(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Sale #{self.pk} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def update_total(self):
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        self.save()

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price_at_sale = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantity * self.price_at_sale

    def __str__(self):
        return f"{self.quantity} x {self.medicine.name} @ ${self.price_at_sale}"
