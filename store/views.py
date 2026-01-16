from django.shortcuts import render , get_object_or_404
from category.models import Category
from .models import product
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
# Create your views here.
def store(request , category_slug=None):
    categories = None
    products=None
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = product.objects.filter(category=categories, is_available=True).order_by('id')
        paginator= Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = product.objects.all().filter(is_available=True).order_by('id')
        paginator= Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    context = { 'products': paged_products, 'product_count': product_count }

    return render(request, 'store/store.html' , context=context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = product.objects.get(category__slug=category_slug, slug=product_slug)
        cart_in = CartItem.objects.filter(cart__cart_id=_cart_id(request), prod=single_product).exists()
    except Exception as e:
        raise e
    context = {
        'cart_in':cart_in,
        'single_product': single_product,
    }
    return render(request, 'store/productdetail.html', context)


def search(request):
    return render(request, 'store/store.html')


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword) )
            
    context = {
        'products': products,
    }
    return render(request, 'store/store.html', context)
