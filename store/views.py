from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.forms import inlineformset_factory
from django.db.models import Sum

from django.views.generic.edit import (
    CreateView, UpdateView
)
from django.contrib import messages

from .models import (Category, Product, ProductTechnicalDataValue)
from .forms import (AddProductForm, EditProductForm, 
                    ProductForm, TechnicalDataValueFormSet)

import datetime
from django.utils import timezone

class ProductInline():
    form_class = ProductForm
    model = Product
    template_name = "store/product_create_or_update.html"

    def form_valid(self, form):
        named_formsets = self.get_named_formsets()
        if not all((x.is_valid() for x in named_formsets.values())):
            return self.render_to_response(self.get_context_data(form=form))

        self.object = form.save()

        # for every formset, attempt to find a specific formset save function
        # otherwise, just save.
        for name, formset in named_formsets.items():
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()
        return redirect('store:product_all')

    def formset_variants_valid(self, formset):
        """
        Hook for custom formset saving.Useful if you have multiple formsets
        """
        variants = formset.save(commit=False)  # self.save_formset(formset, contact)
        # add this 2 lines, if you have can_delete=True parameter 
        # set in inlineformset_factory func
        for obj in formset.deleted_objects:
            obj.delete()
        for variant in variants:
            variant.product = self.object
            variant.save()

class ProductCreate(ProductInline, CreateView):

    def get_context_data(self, **kwargs):
        ctx = super(ProductCreate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                'variants': TechnicalDataValueFormSet(prefix='variants'),
            }
        else:
            return {
                'variants': TechnicalDataValueFormSet(self.request.POST or None, self.request.FILES or None, prefix='variants'),
            }

class ProductUpdate(ProductInline, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(ProductUpdate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        return {
            'variants': TechnicalDataValueFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='variants'),
        }


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

    up_count = request.POST.get("count_up", '')
    down_count = request.POST.get('count_down', '')

    if up_count != '':
        product.count += int(up_count)

        product.save()

        if down_count == '':

            return redirect(product.get_absolute_url())


    if down_count != '':

        if int(down_count) > product.count:
            product.count = 0
        else:
            product.count -= int(down_count)

        product.save()

        return redirect(product.get_absolute_url())

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


    DataValueInlineFormSet = inlineformset_factory(Product, ProductTechnicalDataValue, fields=('technical_data', 'value'))

    if request.method == 'POST':
        formset = DataValueInlineFormSet(request.POST, instance=product)

        product_form = EditProductForm(request.POST, instance=product)


        if formset.is_valid() and product_form.is_valid():
            formset.save()
            product_form.save()

            return redirect(product.get_absolute_url())

    else:
        product_form = EditProductForm(instance=product)

        formset = DataValueInlineFormSet(instance=product)

    context = {
        'formset': formset,
        'product_form': product_form,
        'product': product
    }

    return render(request, 'store/product_edit.html', context)


# вызовать сохр. процедуру удаления
@login_required
def delete_product(request, id):

    product = get_object_or_404(Product, id=id)

    c = connection.cursor()
    try:
        # c.callproc('del_product', [product.pk,])
        c.execute("CALL del_product(%s::int)", (product.pk,))
    finally:
        c.close()

    # product.delete()

    return redirect('store:product_all')

def sum_count(request):
    products = Product.products.all()

    # общее количество товара
    total_count = Product.objects.aggregate(Sum('count')) 

    total_price = 0

    c = connection.cursor()
    try:
        c.execute("CALL sum_count_price()")
        total_price = c.fetchall()
    finally:
        c.close()

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        'page_obj': page_obj,
        'total_price': total_price,
        'total_count': total_count,
        'products': products
    }

    return render(request, 'store/sum_count.html', context)

def time_product(request):

    time = request.POST.get("lr_action", None)

    if time != '':

        time_now = timezone.now()

        if time == 'one':
            time_now -= datetime.timedelta(weeks=52)

            products = Product.objects.all().exclude(updated_in__gte = time_now)

        elif time == 'two':
            time_now -= datetime.timedelta(minutes=10)

            # вывод товара за последние 10 минут
            # products = Product.objects.all().filter(updated_in__gte = time_now)

            # весь товар не за последние 10 минут
            products = Product.objects.all().exclude(updated_in__gte = time_now)
            
    else:
        print('не выбран')

    if 'products' in dir():

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

    else:

        context = {}

    return render(request, 'store/time_product.html', context)