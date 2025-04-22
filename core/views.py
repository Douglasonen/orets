from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from .models import BusinessProfile
from .forms import BusinessProfileForm
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib import messages
from . import models
from django.db import transaction
from django.conf import settings
from products.models import Product, Category # Only import from products app
from .models import business  # Your Business model
 # Import from products app only
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import BusinessRegistrationForm, BusinessProfileForm, BusinessSignupForm

@login_required
def dashboard(request):
    # Get filter parameters
    category_id = request.GET.get('category')
    status = request.GET.get('status')
    search = request.GET.get('search')
    
    # Base queryset
    products = Product.objects.filter(business=request.user).order_by('-created_at')
    
    # Apply filters
    if category_id:
        products = products.filter(categories__id=category_id)
    
    if status == 'active':
        products = products.filter(is_available=True)
    elif status == 'inactive':
        products = products.filter(is_available=False)
    
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Get categories used by this business's products
    category_ids = products.values_list('categories__id', flat=True).distinct()
    categories = Category.objects.filter(
        is_active=True,
        id__in=category_ids
    ).distinct()
    
    # Pagination
    paginator = Paginator(products, 10)
    page = request.GET.get('page')
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    context = {
        'products': products_page,
        'categories': categories,
        'total_products': products.count(),
        'active_products': products.filter(is_available=True).count(),
    }
    return render(request, 'products/dashboard.html', context)


def resend_activation(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = business.objects.get(email=email, is_active=False)
            # Resend activation email (same code as in register view)
            messages.success(request, 'Activation email resent!')
            return redirect('registration_sent')
        except business.DoesNotExist:
            messages.error(request, 'No pending registration found with this email.')
    return render(request, 'registration/resend_activation.html')
###### resend activation up
def register(request):
    if request.method == 'POST':
        form = BusinessRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User inactive until email verification
            user.save()
            
            # Send verification email
            current_site = get_current_site(request)
            mail_subject = 'Activate your account'
            message = render_to_string('registration/activate_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            send_mail(
                mail_subject,
                message,
                'noreply@yourdomain.com',
                [user.email],
                fail_silently=False,
            )
            
            return redirect('registration_sent')
    else:
        form = BusinessRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = business.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, business.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('business_profile')
    else:
        return render(request, 'registration/activation_invalid.html')
############ registration up
def register_Business(request):
    if request.method == 'POST':
        form = BusinessRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('business_dashboard')
    else:
        form = BusinessRegistrationForm()
    return render(request, 'core/register.html', {'form': form})

@login_required
@transaction.atomic
def edit_profile(request):
    try:
        profile = request.user.profile
    except BusinessProfile.DoesNotExist:
        profile = BusinessProfile(business=request.user)

    if request.method == 'POST':
        form = BusinessProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Explicitly save all fields
            business_profile = form.save(commit=False)
            
            # Ensure WhatsApp number is properly formatted
            whatsapp_num = form.cleaned_data['whatsapp_number']
            business_profile.whatsapp_number = whatsapp_num
            
            # Save to database
            business_profile.save()
            
            # Update the associated business record
            request.user.whatsapp_number = whatsapp_num
            request.user.save()
            
            messages.success(request, "Profile updated successfully!")
            return redirect('profile_view')
    else:
        form = BusinessProfileForm(instance=profile)

    return render(request, 'core/edit_profile.html', {'form': form})
###########################################

@transaction.atomic
def business_signup(request):
    if request.method == 'POST':
        form = BusinessSignupForm(request.POST)
        if form.is_valid():
            try:
                # Save the user (business) first
                user = form.save()
                
                # Create the business profile with all required fields
                BusinessProfile.objects.create(
                    business=user,
                    business_name=form.cleaned_data.get('company_name', ''),
                    phone_number=form.cleaned_data.get('phone_number', ''),
                    whatsapp_number=form.cleaned_data.get('whatsapp_number', ''),
                    industry=form.cleaned_data.get('industry', ''),
                    address=form.cleaned_data.get('address', ''),
                    email=form.cleaned_data.get('email', '')
                )
                
                login(request, user)
                messages.success(request, "Account created successfully!")
                return redirect('dashboard')
                
            except Exception as e:
                messages.error(request, f"Error creating account: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below")
    else:
        form = BusinessSignupForm()
    
    return render(request, 'core/signup.html', {'form': form})

####################
class BusinessSignupView(CreateView):
    model = business
    form_class = BusinessSignupForm
    template_name = 'core/signup.html'
    success_url = reverse_lazy('dashboard')
    
    def form_valid(self, form):
        # Add any additional processing here
        user = form.save(commit=False)
        user.is_active = True  # Activate immediately or verify email first
        user.save()
@login_required
def business_profile(request):
    try:
        profile = request.user.profile
    except BusinessProfile.DoesNotExist:
        profile = BusinessProfile(business=request.user)
        profile.save()  # Save the new profile immediately
    
    if request.method == 'POST':
        form = BusinessProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('business_profile')  # Redirect back to same page
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = BusinessProfileForm(instance=profile)
    
    return render(request, 'core/business_profile.html', {'form': form})
@login_required
def home(request):
    return render(request, 'core/home.html')
def register(request):
    if request.method == 'POST':
        form = BusinessRegistrationForm(request.POST)
        if form.is_valid():
            business = form.save()
            login(request, business)
            return redirect('complete_profile')
    else:
        form = BusinessRegistrationForm()
    return render(request, 'core/register.html', {'form': form})

def complete_profile(request):
    if request.method == 'POST':
        form = BusinessProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.business = request.user
            profile.save()
            return redirect('dashboard')
    else:
        form = BusinessProfileForm()
    return render(request, 'core/complete_profile.html', {'form': form})
def custom_logout(request):
    logout(request)
    return redirect('login')  # Or your homepage