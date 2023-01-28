from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.forms import inlineformset_factory
from django.db.models import Sum, Avg
from django.db.models import FloatField

from django.views.generic.edit import (
    CreateView, UpdateView
)

from .models import (Category, Product, ProductTechnicalDataValue)
from .forms import (AddProductForm, EditProductForm, 
                    ProductForm, TechnicalDataValueFormSet,
                    ManufacturerForm, SelectManufacturerForm)

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
                'variants': TechnicalDataValueFormSet(
                    self.request.POST or None, 
                    self.request.FILES or None, prefix='variants'
                ),
            }

class ProductUpdate(ProductInline, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(ProductUpdate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        return {
            'variants': TechnicalDataValueFormSet(
                self.request.POST or None, 
                self.request.FILES or None, instance=self.object, prefix='variants'
            ),
        }


@login_required
# функция для отображения всех товаров
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

# функция для отображения страницы товара
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

# функция для отображения товара по категориям
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

# функция для добавления товара
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

# функция для изменения данных товара
@login_required
def edit_product(request, id):

    product = get_object_or_404(Product, id=id)


    DataValueInlineFormSet = inlineformset_factory(
        Product, ProductTechnicalDataValue, 
        fields=('technical_data', 'value')
    )

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

# функция для удаления товара
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

# функция для получения о общем количестве товара и на какую сумму
@login_required
def sum_count(request):

    # общее количество товара
    total_count = Product.objects.aggregate(Sum('count')) 

    total_price = 0

    c = connection.cursor()
    try:
        c.execute("CALL sum_count_price()")
        total_price = c.fetchall()
    finally:
        c.close()

    c = connection.cursor()
    try:
        c.execute("SELECT * FROM sum_price_view")
        products_view = c.fetchall()
    finally:
        c.close()

    paginator = Paginator(products_view, 10)
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
        'products_view': products_view
    }

    return render(request, 'store/sum_count.html', context)

# функция для выборки товара по времени
@login_required
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

        elif time == 'tree':
            time_now -= datetime.timedelta(days=1)

            products = Product.objects.all().exclude(updated_in__gte = time_now)

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

# функция для добавления производителя
@login_required
def create_manufacturer(request):

    if request.method == 'POST':

        name = request.POST.get('name')
        country = request.POST.get('country')

        c = connection.cursor()
        try:
            c.execute("CALL create_manufacturer(%s, %s)", (name, country))
        finally:
            c.close()

        return redirect('store:product_all')

    else:

        manufacturerform = ManufacturerForm()

    context = {
        'manufacturerform': manufacturerform
    }

    return render(request, 'store/create_manufacturer.html', context)

# функция для выборки товара по производителю
@login_required
def selection_manufacturer(request):

    selectform = SelectManufacturerForm()

    manufacture_id = request.POST.get("manufacturer", None)

    check = request.POST.get('check-box', None)

    if manufacture_id != '':

        products = Product.objects.all().filter(manufacturer = manufacture_id)

        if check == 'check':

            total_count = Product.objects.filter(
                manufacturer = manufacture_id).aggregate(sum = Sum('count')
            )

            avg_price = Product.objects.filter(
                manufacturer = manufacture_id).aggregate(avg = Avg('price', 
                output_field=FloatField())
            )

            c = connection.cursor()
            try:
                c.execute("CALL sum_count_price_manufactur(%s)", (manufacture_id,))
                total_price = c.fetchall()
            finally:
                c.close()

    if 'products' in dir() and 'total_count' in dir():

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
            'selectform': selectform,
            'total_count': total_count,
            'total_price': total_price,
            'avg_price': avg_price
        }

    elif 'products' in dir():

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
            'selectform': selectform,
        }

    else:

        context = {
            'selectform': selectform
        }

    return render(request, 'store/selection_manafacturer.html', context)

# функция для отображения товара со скидкой и без
@login_required
def discount_search(request):

    products = Product.objects.all()
        
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
    }

    return render(request, 'store/discount_search.html', context)