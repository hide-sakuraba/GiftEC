from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Category


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True)
    keyword = request.GET.get('keyword', '').strip()
    sort = request.GET.get('sort', 'newest')

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    if keyword:
        products = products.filter(
            Q(name__icontains=keyword) | Q(description__icontains=keyword)
        )

    products = products.order_by({
        'price_asc': 'price',
        'price_desc': '-price',
        'newest': '-created_at',
    }.get(sort, '-created_at'))

    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'product_count': products.count(),
        'keyword': keyword,
        'sort': sort,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, category_slug, product_slug):
    product = get_object_or_404(Product, category__slug=category_slug, slug=product_slug, is_available=True)
    related_products = Product.objects.filter(category=product.category, is_available=True).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)
