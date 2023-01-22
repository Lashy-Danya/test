from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.forms import formset_factory

from .models import Category, Product
from .forms import AddProductForm, AddTechnicalDataValueForm, EditProductForm, EditTechnicalDataValueForm

@login_required
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

@login_required
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)

    # Получение характеристик товара и их значений 
    # вызывая функцию sql
    id_product = product.pk

    c = connection.cursor()
    try:
        c.callproc('data_value_product', (id_product,))
        data_value = c.fetchall()
    finally:
        c.close()

    context = {
        'product': product,
        'data_value': data_value
    }

    return render(request, 'store/product_single.html', context)

@login_required
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

@login_required
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

@login_required
def edit_product(request, id):

    product = get_object_or_404(Product, id=id)

    product_form = EditProductForm(request.POST, instance=product)

    data_value_form = EditTechnicalDataValueForm(request.POST)

    context = {
        'product_form': product_form,
        'data_value_form': data_value_form,
        'product': product
    }

    if all([product_form.is_valid(), data_value_form.is_valid()]):
        parent = product_form.save(commit=False)
        parent.save()

        child = data_value_form.save(commit=False)
        child.product = parent
        child.save()

        print(product_form.cleaned_data)
        print(data_value_form.cleaned_data)
        

    return render(request, 'store/product_edit.html', context)


# вызовать сохр. процедуру удаления
@login_required
def delete_product(request, id):

    product = get_object_or_404(Product, id=id)

    product.delete()

    return redirect('store:product_all')