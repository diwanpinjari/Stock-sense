from django import forms
from .models import Location, Product


class ReceiptCreateForm(forms.Form):
    source_location = forms.ModelChoiceField(
        queryset=Location.objects.filter(location_type='vendor'),
        label="Vendor / Supplier Location",
        empty_label="Select Vendor",
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    destination_location = forms.ModelChoiceField(
        queryset=Location.objects.filter(location_type='internal'),
        label="Destination Warehouse Location",
        empty_label="Select Destination Storage",
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        label="Product to Receive",
        empty_label="Select Product",
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    quantity = forms.DecimalField(
        min_value=0.01,
        max_digits=10,
        decimal_places=2,
        label="Quantity Received",
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 50.00'})
    )
    notes = forms.CharField(
        required=False,
        label="Operation Notes / Vendor Bill #",
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Optional reference details'})
    )