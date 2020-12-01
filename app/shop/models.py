from django.db import models
from django.contrib.auth.models import User
from pathlib import Path
from django.shortcuts import reverse
from django.core.validators import MinValueValidator


class Category(models.Model):
    """Категория"""
    name = models.CharField('Наименование категории', max_length=255)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['-id']

    def get_absolute_url(self):
        return reverse('category_detail', args=[self.slug])

    def __str__(self):
        return self.name


def get_path_category(instance, filename):
    return '{0}/{1}{2}'.format(instance.category, instance.slug, Path(filename).suffix)


class Product(models.Model):
    """Продукт"""
    name = models.CharField('Наименование', max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    description = models.TextField(verbose_name='Описание', blank=True)
    slug = models.SlugField(unique=True)
    image = models.ImageField('Изображение', upload_to=get_path_category)
    qty = models.PositiveIntegerField(verbose_name='Количество')
    price = models.DecimalField(validators=[MinValueValidator(0)], max_digits=9, decimal_places=2, verbose_name='Цена')

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['-id']

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def save(self, *args, **kwargs):
        for item in self.cartproduct_set.all():
            if not item.cart.in_order:
                item.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CartProduct(models.Model):
    """Корзина продукта"""
    customer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт')
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, verbose_name='Корзина')
    qty = models.PositiveIntegerField(default=1, verbose_name='Общее количество')
    final_price = models.DecimalField(default=0, max_digits=9, decimal_places=2, verbose_name='Общая цена')

    class Meta:
        verbose_name = 'Корзина продукта'
        verbose_name_plural = 'Корзины продуктов'

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.product.price
        super().save(*args, **kwargs)

    def __str__(self):
        return "Продукт: {} (для корзины)".format(self.product.name)


class Cart(models.Model):
    """Корзина"""
    customer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', null=True, blank=True)
    total_product = models.PositiveIntegerField(default=0, verbose_name='Количество продуктов')
    final_price = models.DecimalField(max_digits=9, default=0, decimal_places=2, verbose_name='Общая цена')
    in_order = models.BooleanField(default=False, verbose_name='В заказе')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return 'Пользователь: {0} | Корзина({1}) | Продукты: {2}'.format(
            self.customer.username if self.customer else '-', self.id, ', '.join(
                [f'{item.product.name}({item.qty})' for item in self.cartproduct_set.all()]))


class Order(models.Model):
    """Заказ"""
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    PAYMENT_TYPE_CASH = 'cash'
    PAYMENT_TYPE_CARD = 'card'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ выполнен')
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Самовывоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка')
    )

    PAYMENT_TYPE_CHOICES = (
        (PAYMENT_TYPE_CASH, 'Наличные'),
        (PAYMENT_TYPE_CARD, 'Карта')
    )

    customer = models.ForeignKey(User, verbose_name='Покупатель',
                                 on_delete=models.CASCADE, blank=True, null=True)
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=1024, verbose_name='Адрес', null=True, blank=True)
    status = models.CharField(
        max_length=100,
        verbose_name='Статус заказ',
        choices=STATUS_CHOICES,
        default=STATUS_NEW
    )
    buying_type = models.CharField(
        max_length=100,
        verbose_name='Тип заказа',
        choices=BUYING_TYPE_CHOICES,
        default=BUYING_TYPE_SELF
    )
    payment_type = models.CharField(
        max_length=100,
        verbose_name='Тип оплаты',
        choices=PAYMENT_TYPE_CHOICES,
        default=PAYMENT_TYPE_CASH
    )
    comment = models.TextField(verbose_name='Комментарий к заказу', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания заказа')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-id']

    def __str__(self):
        if self.customer:
            return 'Заказ({0}): {1}'.format(self.id, self.customer.username)
        else:
            return 'Заказ({0}): {1} {2}'.format(self.id, self.first_name, self.last_name)
