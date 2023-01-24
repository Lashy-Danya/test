from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class ProductManager(models.Manager):
    def get_queryset(self):
        return super(ProductManager, self).get_queryset().filter(is_active=True)

class Category(models.Model):
    """Таблица категорий"""
    name = models.CharField(
        verbose_name="Название категории", 
        max_length=255,
        unique=True
    )
    slug = models.SlugField(
        verbose_name="URL категории",
        max_length=255, 
        unique=True
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'categorys'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:category_list', args=[self.slug])

class Manufacturer(models.Model):
    """Таблица производители"""
    name = models.CharField(verbose_name='Название бренда', max_length=255)
    country = models.CharField(verbose_name='Страна', max_length=255)

    class Meta:
        db_table = 'manufacturers'
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'

    def __str__(self):
        return self.name

class Discount(models.Model):
    amount = models.IntegerField(verbose_name='Размер скидки')
    reason = models.TextField(verbose_name='Причина скидки')

    class Meta:
        db_table = 'discount'
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'

    def __str__(self):
        return f'{self.amount}'

class ProductType(models.Model):
    """Таблица представления различных типов товара"""
    name = models.CharField(
        verbose_name="Название типа продукта",
        max_length=255,
        unique=True
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'product_type'
        verbose_name = 'Тип продукта'
        verbose_name_plural = 'Типы продуктов'

    def __str__(self):
        return self.name

class ProductTechnicalData(models.Model):
    """Таблица технических параметров товара"""
    name = models.CharField(
        verbose_name='Название',
        max_length=255,
    )
    product_type = models.ForeignKey(ProductType, on_delete=models.RESTRICT)

    class Meta:
        db_table = 'product_technical_data'
        verbose_name = 'Технические параметры продукта'
        verbose_name_plural = 'Технические параметры продуктов'

    def __str__(self):
        return self.name

class Product(models.Model):
    """Таблица товара"""
    product_type = models.ForeignKey(
        ProductType, on_delete=models.RESTRICT, verbose_name='Тип товара'
    )
    category = models.ForeignKey(
        Category, on_delete=models.RESTRICT, verbose_name='Категория'
    )
    name = models.CharField(verbose_name='Наименование', max_length=255)
    description = models.TextField(verbose_name='Описание', blank=True)
    slug = models.SlugField(
        verbose_name='URL товара', max_length=255, unique=True
    )
    price = models.DecimalField(
        verbose_name="Цена", 
        max_digits=8, 
        decimal_places=2,
        help_text='Максимум 999999.99'
    )
    is_active = models.BooleanField(
        verbose_name="Наличие товара", 
        default=True
    )
    manufacturer = models.ForeignKey(
        Manufacturer, on_delete=models.RESTRICT, verbose_name='Производитель'
    )
    warranty = models.IntegerField(verbose_name='Гарантия')
    created_in = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name='Создан'
    )
    updated_in = models.DateTimeField(auto_now=True, verbose_name='Обнавлен')
    discount = models.ForeignKey(
        Discount, on_delete=models.CASCADE, verbose_name='Скидка', blank=True, null=True
    )
    count = models.IntegerField(verbose_name='Количество товара')
    objects = models.Manager()
    products = ProductManager()

    class Meta:
        db_table = 'products'
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ('-created_in',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)

class ProductTechnicalDataValue(models.Model):
    """Таблица значений технических параметров товара"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    technical_data = models.ForeignKey(
        ProductTechnicalData, on_delete=models.CASCADE
    )
    value = models.CharField(
        verbose_name='Значение',
        max_length=255,
        help_text='Значение технического параметра товара (максимум 255 символов)'
    )

    class Meta:
        db_table = 'product_technical_data_value'
        verbose_name = 'Значение технических параметров продукта'
        verbose_name_plural = 'Значения технических параметров продуктов'

    def __str__(self):
        return self.value

class ProductImage(models.Model):
    """Таблица изображений товара"""
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='image_product'
    )
    image = models.ImageField(verbose_name='Изображение', upload_to='images/')
    desc_image = models.CharField(
        verbose_name='Описания изображения',
        max_length=255,
        blank=True
    )
    created_in = models.DateTimeField(auto_now_add=True, editable=False)
    updated_in = models.DateTimeField(auto_now=True)
    main_image = models.BooleanField(default=False)

    class Meta:
        db_table = 'product_image'
        verbose_name = 'Изображения продукта'
        verbose_name_plural = 'Изображения продуктов'
