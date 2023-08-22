from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from .models import Customer, Product, Cart, OrderePlaced
from .forms import CustomerRegistrationForm, CustomerProfileForm, LoginForm
from django.views import View
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from math import ceil
from django.views.generic import View, TemplateView
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login


# def home(request):
# return render(request, 'app/home.html')
class ProductView(View):
    def get(self, request):
        vegetables = Product.objects.filter(category='V')
        fruits = Product.objects.filter(category='F')
        grains = Product.objects.filter(category='G')
        speices = Product.objects.filter(category='S')
        user = request.user
        my_object = [p for p in Cart.objects.all() if p.user == user]
        object_size = len(my_object)
        return render(request, 'app/home.html',
                      {'vegetables': vegetables, 'fruits': fruits, 'grains': grains, 'speices': speices,
                       'object_size': object_size})


@csrf_protect
def profile(request):
    user = request.user
    my_object = [p for p in Cart.objects.all() if p.user == user]
    object_size = len(my_object)
    return render(request, 'app/profile.html', {'object_size': object_size})


@csrf_exempt
def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')  # Redirect to a success page
        else:
            # Handle invalid login credentials
            error_message = "Invalid username or password."
            return render(request, 'app/login.html', {'error_message': error_message})

    form = LoginForm()
    return render(request, 'app/login.html', {'form': form})


# class my_view(View):
#   def get(self, request):
#     user = request.user
#     my_object = [p for p in Cart.objects.all() if p.user==user]
#     object_size = sys.getsizeof(my_object)

#     return render(request, 'app/base.html', {'object_size': object_size})
# def product_detail(request):
#  return render(request, 'app/productdetail.html')

class ProductDetailView(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)

        item_already_in_cart = False
        my_object = [p for p in Cart.objects.all() if p.user == request.user]
        object_size = len(my_object)
        if request.user.is_authenticated:
            item_already_in_cart = Cart.objects.filter(Q(Product=product.id) & Q(user=request.user)).exists()
        return render(request, 'app/productdetail.html',
                      {'product': product, 'item_already_in_cart': item_already_in_cart, 'object_size': object_size})



def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount = 0.0
    shipping_amount = 70.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for p in cart_product:
            tempamount = (p.quantity * p.Product.discounted_price)
            amount += tempamount
        totalamount = amount + shipping_amount

    return render(request, 'app/checkout.html', {'add': add, 'totalamount': totalamount, 'cart_items': cart_items})


@login_required()
def buy_now(request, pk):
    user = request.user
    p = Product.objects.get(pk=pk)
    add = Customer.objects.filter(user=user)

    amount = 0.0
    shipping_amount = 70.0
    tempamount = p.discounted_price
    amount += tempamount
    totalamount = amount + shipping_amount

    return render(request, 'app/buynow.html', {'add': add, 'totalamount': totalamount, 'p': p})


@login_required()
def add_to_cart(request):
    user = request.user
    item_already_in_cart1 = False
    product = request.GET.get('prod_id')
    item_already_in_cart1 = Cart.objects.filter(Q(Product=product) & Q(user=request.user)).exists()
    if item_already_in_cart1 == False:
        product_title = Product.objects.get(id=product)
        Cart(user=user, Product=product_title).save()
        messages.success(request, 'Product Added to Cart Successfully !!')
        return redirect('/cart')
    else:
        return redirect('/cart')


# def add_to_cart(request):
#     user = request.user
#     product_id = request.GET.get('prod_id')
#     product = Product.objects.get(id=product_id)
#     Cart(user=user, Product=product).save()
#     user = request.user
#     my_object = [p for p in Cart.objects.all() if p.user == user]
#     object_size = len(my_object)
#     return redirect('/cart', {'object_size': object_size})


def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(Product=prod_id) & Q(user=request.user))
        c.delete()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.Product.discounted_price)
            # print("Quantity", p.quantity)
            # print("Selling Price", p.product.discounted_price)
            # print("Before", amount)
            amount += tempamount
            # print("After", amount)
        # print("Total", amount)
        data = {
            'amount': amount,
            'totalamount': amount + shipping_amount
        }
        return JsonResponse(data)
    else:
        return HttpResponse("")


def show_cart(request):
    if (request.user.is_authenticated):
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        if cart_product:
            for p in cart_product:
                temp_amount = (p.quantity * p.Product.discounted_price)
                amount += temp_amount
                total_amount = amount + shipping_amount
            user = request.user
            my_object = [p for p in Cart.objects.all() if p.user == user]
            object_size = len(my_object)
            return render(request, 'app/addtocart.html',
                          {'carts': cart, 'totalamount': total_amount, 'amount': amount, 'object_size': object_size})
        else:
            return render(request, 'app/emptycart.html')


def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(Product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.Product.discounted_price)
            # print("Quantity", p.quantity)
            # print("Selling Price", p.product.discounted_price)
            # print("Before", amount)
            amount += tempamount
            # print("After", amount)
        # print("Total", amount)
        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': amount + shipping_amount
        }
        return JsonResponse(data)
    else:
        return HttpResponse("")


def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(Product=prod_id) & Q(user=request.user))
        c.quantity -= 1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.Product.discounted_price)
            # print("Quantity", p.quantity)
            # print("Selling Price", p.product.discounted_price)
            # print("Before", amount)
            amount += tempamount
            # print("After", amount)
        # print("Total", amount)
        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': amount + shipping_amount
        }
        return JsonResponse(data)
    else:
        return HttpResponse("")



@login_required
def address(request):
    user = request.user
    my_object = [p for p in Cart.objects.all() if p.user == user]
    object_size = len(my_object)
    add = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html', {'add': add, 'active': 'btn-primary', 'object_size': object_size})


@login_required()
def orders(request):
    op = OrderePlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html', {'order_placed': op})


@login_required()
def about(request):
    user = request.user
    my_object = [p for p in Cart.objects.all() if p.user == user]
    object_size = len(my_object)
    return render(request, 'app/about.html', {'object_size': object_size})


# def login(request):
#  return render(request, 'app/login.html')

# def customerregistration(request):
#  return render(request, 'app/customerregistration.html')
@method_decorator(csrf_exempt, name='dispatch')
class CustomerRegistration(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form': form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Congratulations!! Registered Successfully')
            form.save()
        return render(request, 'app/customerregistration.html', {'form': form})


@login_required()
def payment_done(request):
    user = request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderePlaced(user=user, customer=customer, product=c.Product, quantity=c.quantity).save()
        c.delete()
    return redirect("orders")


@method_decorator(csrf_exempt, name='dispatch')
class ProfileView(View):

    def get(self, request):
        form = CustomerProfileForm()
        user = request.user
        my_object = [p for p in Cart.objects.all() if p.user == user]
        object_size = len(my_object)
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary', 'object_size': object_size})

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=usr, name=name, locality=locality, city=city, state=state, zipcode=zipcode)
            reg.save()
            messages.success(request, 'Congratulations!! Profile Updated Successfully')
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary'})


class SearchView(TemplateView):
    template_name = "app/search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kw = self.request.GET["keyword"]
        results = Product.objects.filter(Q(title__contains=kw) | Q(description__contains=kw))
        context["results"] = results
        return context



