from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponseBadRequest,JsonResponse
from django.views import View
from . models import Product, Customer, Cart
from django.db.models import Count, Q, F , Sum
from . forms import CustomerRegistrationForm,CustomerProfileForm
from django.contrib import messages

# Create your views here.
def home(request):
    return render(request,"app/Home.html")

def about(request):
    return render(request,"app/about.html")

def contact(request):
    return render(request,"app/contact.html")

class CategoryView(View):
    def get(self,request,val):
        product=Product.objects.filter(category=val)
        title=Product.objects.filter(category=val).values('title')
        return render(request,"app/category.html",locals())
    
class CategoryTitle(View):
    def get(self,request,val):
        product=Product.objects.filter(title=val)
        title=Product.objects.filter(category=product[0].category).values('title')
        return render(request,"app/category.html",locals())
    
class ProductDetailView(View):
    def get(self,request,pk):
        product=Product.objects.get(pk=pk)
        return render(request,"app/productdetail.html",locals())
    
class CustomerRegistrationView(View):
    def get(self,request):
        form=CustomerRegistrationForm()
        return render(request,'app/customerregistration.html',locals())
    def post(self,request):
        form=CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Congratulations! User Registered Successfully")
        else:
            messages.warning(request,"Invalid Input Data")
        return render(request,'app/customerregistration.html',locals())
    
class ProfileView(View):
    def get(self,request):
        form=CustomerProfileForm()
        return render(request,'app/profile.html',locals())
    def post(self,request):
        form=CustomerProfileForm(request.POST)
        if form.is_valid():
            user=request.user
            name=form.cleaned_data['name']
            locality=form.cleaned_data['locality']
            city=form.cleaned_data['city']
            mobile=form.cleaned_data['mobile']
            state=form.cleaned_data['state']
            zipcode=form.cleaned_data['zipcode']
            
            reg=Customer(user=user,name=name,locality=locality,city=city,mobile=mobile,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request,"Congratulations! Profile Saved Successfully")
        else:
            messages.warning(request,"Invalid Input Data")
        return render(request,'app/profile.html',locals())
    
def address(request):
    add=Customer.objects.filter(user=request.user)
    return render(request,'app/address.html',locals())

class updateAddress(View):
    def get(self,request,pk):
        add=Customer.objects.get(pk=pk)
        form=CustomerProfileForm(instance=add)
        return render(request,'app/updateAddress.html',locals())
    def post(self,request,pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request,"Congratulations! Profile Updated Successfully")
        else:
            messages.warning(request,"Invalid Input Data")
        return redirect("address")
    
def update_cart_data(user):
    cart = Cart.objects.filter(user=user)
    amount = cart.aggregate(total=Sum(F('quantity') * F('product__discounted_price')))['total'] or 0
    amount = float(amount)
    totalamount = amount + 40 if amount > 0 else 0
    return amount, totalamount

def add_to_cart(request):
    if request.method != 'GET':
        return HttpResponseBadRequest("Invalid request method")
    
    product_id = request.GET.get('prod_id')
    if not product_id:
        return HttpResponseBadRequest("No product ID provided")

    product = get_object_or_404(Product, id=product_id)
    
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity = F('quantity') + 1
        cart_item.save()

    return redirect("showcart")

def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount, totalamount = update_cart_data(user)
    return render(request, 'app/addtocart.html', {'cart': cart, 'amount': amount, 'totalamount': totalamount})

class checkout(View):
    def get(self,request):
        user=request.user
        add=Customer.objects.filter(user=user)
        cart_items=Cart.objects.filter(user=user)
        famount=0;
        for p in cart_items:
            value=p.quantity*p.product.discounted_price
            famount+=value
        totalamount=famount+40
        return render(request,'app/checkout.html',locals())

def plus_cart(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    prod_id = request.GET.get('prod_id')
    if not prod_id:
        return JsonResponse({'error': 'No product ID provided'}, status=400)

    cart_item = Cart.objects.filter(user=request.user, product__id=prod_id).first()
    if not cart_item:
        return JsonResponse({'error': 'Product not in cart'}, status=400)

    cart_item.quantity = F('quantity') + 1
    cart_item.save()
    cart_item.refresh_from_db()

    amount, totalamount = update_cart_data(request.user)
    
    data = {
        'quantity': int(cart_item.quantity),
        'amount': float(amount),
        'totalamount': float(totalamount)
    }
    return JsonResponse(data)

def minus_cart(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    prod_id = request.GET.get('prod_id')
    if not prod_id:
        return JsonResponse({'error': 'No product ID provided'}, status=400)

    cart_item = Cart.objects.filter(user=request.user, product__id=prod_id).first()
    if not cart_item:
        return JsonResponse({'error': 'Product not in cart'}, status=400)

    if cart_item.quantity > 1:
        cart_item.quantity = F('quantity') - 1
        cart_item.save()
        cart_item.refresh_from_db()
    else:
        cart_item.delete()
        cart_item = None

    amount, totalamount = update_cart_data(request.user)
    
    data = {
        'quantity': int(cart_item.quantity) if cart_item else 0,
        'amount': float(amount),
        'totalamount': float(totalamount)
    }
    return JsonResponse(data)

def remove_cart(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    prod_id = request.GET.get('prod_id')
    if not prod_id:
        return JsonResponse({'error': 'No product ID provided'}, status=400)

    Cart.objects.filter(user=request.user, product__id=prod_id).delete()

    amount, totalamount = update_cart_data(request.user)
    
    data = {
        'amount': float(amount),
        'totalamount': float(totalamount)
    }
    return JsonResponse(data)