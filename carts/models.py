from django.db import models
from products.models import Product


class Cart(models.Model):
    cart_id = models.CharField('カートID', max_length=250, blank=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)

    class Meta:
        verbose_name = 'カート'
        verbose_name_plural = 'カート一覧'
        ordering = ['-created_at']

    def __str__(self):
        return self.cart_id or f"Cart {self.id}"


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品')
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name='カート')
    quantity = models.PositiveIntegerField('数量', default=1)
    is_active = models.BooleanField('有効フラグ', default=True)

    class Meta:
        verbose_name = 'カート明細'
        verbose_name_plural = 'カート明細一覧'

    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
