from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', '保留中'),
        ('Paid', '支払い済み'),
        ('Shipped', '発送済み'),
        ('Cancelled', 'キャンセル'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='ユーザー')
    order_number = models.CharField('注文番号', max_length=100, unique=True)
    first_name = models.CharField('名', max_length=50)
    last_name = models.CharField('姓', max_length=50)
    email = models.EmailField('メールアドレス', max_length=100)
    phone = models.CharField('電話番号', max_length=20)
    address = models.CharField('住所', max_length=255)
    postal_code = models.CharField('郵便番号', max_length=10)
    total_price = models.IntegerField('合計金額')
    status = models.CharField('注文ステータス', max_length=20, choices=STATUS_CHOICES, default='Pending')
    stripe_payment_intent_id = models.CharField('Stripe Payment Intent ID', max_length=255, blank=True)
    created_at = models.DateTimeField('注文日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = '注文'
        verbose_name_plural = '注文一覧'
        ordering = ['-created_at']

    def full_name(self):
        return f"{self.last_name} {self.first_name}"

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='注文')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品')
    price = models.IntegerField('単価')
    quantity = models.PositiveIntegerField('数量')
    created_at = models.DateTimeField('作成日時', auto_now_add=True)

    class Meta:
        verbose_name = '注文明細'
        verbose_name_plural = '注文明細一覧'

    def sub_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"
