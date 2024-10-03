import razorpay
import logging
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from owner.models import Client, ContactPage, AboutUs
from .forms import BookingForm
from .models import Ad, AdType, AdSize, Booking

logger = logging.getLogger(__name__)
def index(request):
    return render(request, 'office360degree/index.html')
def about(request):
    about_details = AboutUs.objects.first()
    return render(request, 'office360degree/about.html', {'about_details': about_details})
def clients(request):
    client_list = Client.objects.all()  # Fetch all client data
    return render(request, 'office360degree/clients.html', {'client_list': client_list})
def booking(request):
    return render(request, 'office360degree/booking.html')
def epaper(request):
    return render(request, 'office360degree/epaper.html')
def knowledgebase(request):
    return render(request, 'office360degree/knowledgebase.html')
def contact(request):
    contact_details = ContactPage.objects.first()  # Fetch the first entry or use filters as needed
    return render(request, 'office360degree/contact.html', {'contact_details': contact_details})


# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=("rzp_test_9e4v9FchUNaCuZ", "rzp_test_9e4v9FchUNaCuZ"))

def payment_success(request):
    return render(request, 'office360degree/payment_success.html')

def payment_failure(request):
    return render(request, 'office360degree/payment_failure.html')


def ad_list(request):
    ads = Ad.objects.filter(is_available=True)
    ad_types = AdType.objects.all()

    # Get the adType parameter from the query string
    selected_ad_type_name = request.GET.get('adType')

    if selected_ad_type_name and selected_ad_type_name != 'all':
        try:
            # Find the AdType by name
            selected_ad_type = AdType.objects.get(name=selected_ad_type_name)
            ads = ads.filter(ad_type=selected_ad_type)
        except AdType.DoesNotExist:
            ads = Ad.objects.none()  # No ads if AdType doesn't exist

    context = {
        'ads': ads,
        'ad_types': ad_types,
        'selected_ad_type_name': selected_ad_type_name  # Pass selected type to template
    }

    return render(request, 'office360degree/ad_list.html', context)

def ad_detail(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)
    return render(request, 'office360degree/ad_detail.html', {'ad': ad})


def book_ad(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)

    if request.method == 'POST':
        form = BookingForm(request.POST, request.FILES)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.ad = ad
            booking.save()

            # Integrate Razorpay payment gateway here
            razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            payment = razorpay_client.order.create({
                "amount": int(ad.price * 100),  # Razorpay accepts paise (i.e., 100 rupees = 10000 paise)
                "currency": "INR",
                "payment_capture": 1
            })

            # Redirect to the payment page with payment details
            return render(request, 'office360degree/payment_page.html', {
                'payment_id': payment['id'],  # Correctly pass payment ID
                'booking': booking,
                'ad': ad,
                'upi_number': '+917878474764',  # UPI payment option
                'amount_in_paise': int(ad.price * 100),  # Pass amount in paise
                'razorpay_key_id': settings.RAZORPAY_KEY_ID  # Pass the Razorpay key
            })
    else:
        form = BookingForm()

    return render(request, 'office360degree/book_ad.html', {'form': form, 'ad': ad})

def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    # Update the payment status here (either through Razorpay webhook or manual verification)
    booking.payment_status = 'Completed'
    booking.save()

    return render(request, 'office360degree/success.html', {'booking': booking})