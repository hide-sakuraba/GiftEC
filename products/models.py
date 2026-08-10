from django.db import models


class Category(models.Model):
    name = models.CharField('カテゴリ名', max_length=100)
    slug = models.SlugField('スラグ', max_length=100, unique=True)
    description = models.TextField('説明', blank=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)

    class Meta:
        verbose_name = 'カテゴリ'
        verbose_name_plural = 'カテゴリ一覧'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='カテゴリ')
    name = models.CharField('商品名', max_length=200)
    slug = models.SlugField('スラグ', max_length=200, unique=True)
    description = models.TextField('商品説明')
    price = models.IntegerField('価格')
    stock = models.PositiveIntegerField('在庫数', default=0)
    image = models.ImageField('商品画像', upload_to='products/', blank=True, null=True)
    is_available = models.BooleanField('販売可能フラグ', default=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品一覧'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
