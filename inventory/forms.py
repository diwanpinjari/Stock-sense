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


class DeliveryCreateForm(forms.Form):
    source_location = forms.ModelChoiceField(
        queryset=Location.objects.filter(location_type='internal'),
        label="Source Storage Location",
        empty_label="Select Storage Location",
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    destination_location = forms.ModelChoiceField(
        queryset=Location.objects.filter(location_type='customer'),
        label="Customer Destination",
        empty_label="Select Customer Location",
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        label="Product to Deliver",
        empty_label="Select Product",
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    quantity = forms.DecimalField(
        min_value=0.01,
        max_digits=10,
        decimal_places=2,
        label="Quantity to Ship",
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 10.00'})
    )
    notes = forms.CharField(
        required=False,
        label="Delivery Notes / Customer Order #",
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Optional reference details'})
    )


class TransferCreateForm(forms.Form):
    source_location = forms.ModelChoiceField(
        queryset=Location.objects.filter(location_type='internal'),
        label="Source Storage Location",
        empty_label="Select Origin Location",
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    destination_location = forms.ModelChoiceField(
        queryset=Location.objects.filter(location_type='internal'),
        label="Destination Storage Location",
        empty_label="Select Destination Location",
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        label="Product to Transfer",
        empty_label="Select Product",
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    quantity = forms.DecimalField(
        min_value=0.01,
        max_digits=10,
        decimal_places=2,
        label="Quantity to Move",
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 15.00'})
    )
    notes = forms.CharField(
        required=False,
        label="Transfer Notes",
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Optional movement details'})
    )

    def clean(self):
        cleaned_data = super().clean()
        src = cleaned_data.get('source_location')
        dest = cleaned_data.get('destination_location')
        if src and dest and src == dest:
            self.add_error('destination_location', "Source and destination locations cannot be identical.")
        return cleaned_data


class AdjustmentCreateForm(forms.Form):
    location = forms.ModelChoiceField(
        queryset=Location.objects.filter(location_type='internal'),
        label="Counted Storage Location",
        empty_label="Select Location",
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        label="Audited Product",
        empty_label="Select Product",
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    counted_quantity = forms.DecimalField(
        min_value=0.00,
        max_digits=10,
        decimal_places=2,
        label="Real Physical Counted Quantity",
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Actual counted units on shelf'})
    )