from django import forms
from .models import Booking
from owner.models import Zone

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['user_name', 'business_name', 'contact_number', 'booking_description', 'attachment', 'zone']
        zone = forms.ModelChoiceField(queryset=Zone.objects.all(), empty_label="Select Zone")
        widgets = {
            'user_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'business_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Business Name'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Number'}),
            'booking_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Booking Description'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'zone': forms.Select(attrs={'class': 'form-control'}),  # Widget for Zone field
        }

