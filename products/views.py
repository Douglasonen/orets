from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProductForm, CategoryForm
from django.shortcuts import render
from .forms import ProductForm
from django.contrib import messages
from .models import Product, Category
from .forms import ProductForm, CategoryForm
from django.shortcuts import render, get_object_or_404


@login_required
def dashboard(request):
    products = Product.objects.filter(business=request.user).order_by('-created_at')
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'products': products,
        'categories': categories,
        'total_products': products.count(),
        'active_products': products.filter(is_available=True).count(),
    }
    return render(request, 'products/dashboard.html', context)
@login_required
def add_product(request):
    # No profile checks - any authenticated business can add products
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.business = request.user
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('business_dashboard')
    else:
        form = ProductForm()
    
    return render(request, 'products/add_product.html', {'form': form})

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            # Create but don't save yet
            category = form.save(commit=False)
            # Set the business/user relationship
            category.business = request.user  
            # Now save to database
            category.save()
            messages.success(request, 'Category added successfully!')
            return redirect('products:dashboard')  # Redirect to products dashboard
        else:
            # Show form errors
            messages.error(request, 'Please correct the errors below.')
    else:
        # GET request - show empty form
        form = CategoryForm()
    
    return render(request, 'products/add_category.html', {
        'form': form,
        'title': 'Add New Category'
    })

@login_required
def edit_product(request, product_id):
    # Get the product or return 404
    product = get_object_or_404(Product, id=product_id, business=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('business_dashboard')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'products/edit_product.html', {
        'form': form,
        'product': product
    })