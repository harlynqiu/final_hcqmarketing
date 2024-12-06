from django.contrib import messages

from django.shortcuts import render
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse
from .models import Product
from django.shortcuts import render, get_object_or_404, redirect


from .forms import ProductForm

# Create your views here.
def index(request):
    return render(request, 'products/index.html', {
        'products':Product.objects.all().order_by('id')
    })

def view_product(request, id):
    product = Product.objects.get(pk=id)
    return HttpResponseRedirect(reverse('index'))

def add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            # Create a new product from the form data
            new_product = form.save()
            return render(request, 'products/add.html', {
                'form': ProductForm(),  # Reset the form after successful submission
                'success': True  # Indicate success
            })


            new_product_name = form.cleaned_data['product_name']
            new_product_descript = form.cleaned_data['product_descript']
            new_product_price = form.cleaned_data['product_price']
            new_product_unit = form.cleaned_data['product_unit']
           

            new_product = Product(
                product_name = new_product_name,
                product_descript = new_product_descript, 
                product_price = new_product_price, 
                product_unit = new_product_unit, 
                
            )
            new_product.save()
            return render(request, 'products/add.html',{
                'form' :ProductForm(), 
                'success': True
            })
         
        else:
            return render(request, 'products/add.html',{
                'form': ProductForm()
            }) 
    else:
        form = ProductForm()
        return render(request, 'products/add.html', {
            'form': form
        })
    
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('products_index')  # Updated to match your URL pattern
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/product_edit.html', {'form': form})

def delete_product(request, product_id):
    # Get the product or return a 404 error if not found
    product = get_object_or_404(Product, id=product_id)
    
    # Delete the product
    product.delete()
    
    # Redirect to the product list page with a success message
    messages.success(request, "Product deleted successfully")
    return redirect('products_index')  # Make sure 'products_index' is the name of your product list URL