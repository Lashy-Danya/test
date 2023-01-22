from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Category, Product
from .forms import AddProductForm


def product_all(request):
    products = Product.products.all()

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        'page_obj': page_obj
    }

    return render(request, 'store/index.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)

    context = {'product': product}

    return render(request, 'store/product_single.html', context)

def category_list(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    products = Product.products.filter(category=category)

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        'category': category, 
        'page_obj': page_obj
    }

    return render(request, 'store/category.html', context)

def add_product(request):

    if request.method == 'POST':
        form_product = AddProductForm(request.POST)
        if form_product.is_valid():
            # print(form_product.cleaned_data)

            try:
                Product.objects.create(**form_product.cleaned_data)
                return redirect('store:product_all')
            except:
                form_product.add_error(None, 'Ошибка добавления продукта')
    else:
        form_product = AddProductForm()

    context = {'form_product': form_product}

    return render(request, 'store/product_add.html', context)