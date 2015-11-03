from django.contrib import messages
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext, loader
from .forms import ZipcodeForm, ProductSearchForm, StoreSearchForm, ProductAddForm, StoreAddForm
from .models import Store, Item, Inventory
from .utils import ElocalUtils

def homePage(request):
    if request.method == 'GET':
        form = ZipcodeForm()
    else:
        form = ZipcodeForm(request.POST)
        if form.is_valid():
            zip_code = form.cleaned_data['zip_code']
            coordinates = ElocalUtils.getCoorFromZipcode(zip_code)
            if ElocalUtils.isValidZipcode(zip_code) and len(coordinates) != 0:
                request.session['zip_code'] = zip_code
                request.session['coordinates'] = coordinates
                request.session['radius'] = 20
                request.session['cart'] = []
                request.session['stores'] = ElocalUtils.geolocateStores(request.session['coordinates'], 20)
                request.session['products'] = ElocalUtils.geolocateProducts(request.session['coordinates'], 20)
                searchForm = StoreSearchForm()
                addProductForm = ProductAddForm(request.session['coordinates'], request.session['radius'])
                addStoreForm = StoreAddForm()
                return HttpResponseRedirect('/stores')
            else:
                form.add_error('zip_code', 'Must be a valid zipcode.')
    return render(request, 'eLocal_app/homePage.html', {'form': form})

def productSearchPage(request):
    if request.method == 'GET':
        if 'zip_code' not in request.session:
            return HttpResponseRedirect('/')
        zip_code = request.session['zip_code']
        searchForm = ProductSearchForm()
        addProductForm = ProductAddForm(request.session['coordinates'], request.session['radius'])
        addStoreForm = StoreAddForm()
        products = request.session['products']
        return render(request, 'eLocal_app/productSearchPage.html', {'searchForm': searchForm, 'addProductForm': addProductForm, 'addStoreForm': addStoreForm, 'products': products, 'zip_code': zip_code})

def storeSearchPage(request):
    if request.method == 'GET':
        if 'zip_code' not in request.session:
            return HttpResponseRedirect('/')
        zip_code = request.session['zip_code']
        searchForm = StoreSearchForm()
        addProductForm = ProductAddForm(request.session['coordinates'], request.session['radius'])
        addStoreForm = StoreAddForm()
        stores = request.session['stores']
        return render(request, 'eLocal_app/storeSearchPage.html', {'searchForm': searchForm, 'addProductForm': addProductForm, 'addStoreForm': addStoreForm, 'stores': stores, 'zip_code': zip_code})

def shoppingPage(request):
    if request.method == 'GET':
        if 'zip_code' not in request.session:
            return HttpResponseRedirect('/')
        zip_code = request.session['zip_code']
        addProductForm = ProductAddForm(request.session['coordinates'], request.session['radius'])
        addStoreForm = StoreAddForm()
        results = request.session['cart']
        return render(request, 'eLocal_app/shoppingPage.html', {'addProductForm': addProductForm, 'addStoreForm': addStoreForm, 'products': results, 'zip_code': zip_code})

def addStore(request):
    if request.method == 'POST':
        form = StoreAddForm(request.POST)
        if form.is_valid():
            store_name = form.cleaned_data['store_name']
            address = form.cleaned_data['street_number'] + ' ' + form.cleaned_data['street_address']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zip_code = form.cleaned_data['zip_code']
            country = form.cleaned_data['country']
            has_card = form.cleaned_data['has_card']
            if not Store.hasDuplicate(store_name, address, city, state, zip_code, country, has_card):
                coordinates = ElocalUtils.getCoorFromAddress(address, city, state, zip_code, country)
                store = Store.create(store_name, address, city, state, zip_code, country, has_card, coordinates[0], coordinates[1])
                if ElocalUtils.checkDistance(request.session['coordinates'], [(store.latitude, store.longitude)], request.session['radius']):
                    store_list = request.session['stores']
                    store_list.append(ElocalUtils.parseStore(store))
                    request.session['stores'] = store_list
        return HttpResponseRedirect('/stores')

def addProduct(request):
    if request.method == 'POST':
        zip_code = request.session['zip_code']
        form = ProductAddForm(request.session['coordinates'], request.session['radius'], request.POST)
        if form.is_valid():
            product_name = form.cleaned_data['product_name']
            description = form.cleaned_data['description']
            price = float(form.cleaned_data['price'])
            store_id = form.cleaned_data['store_name']
            if not Inventory.hasDuplicateItem(product_name, store_id):
                product_list = request.session['products']
                item = ElocalUtils.getProductFromZipcode(product_name, product_list)
                if item is None:
                    item = Item.create(product_name, description)
                    item.addToStore(store_id, price)
                    product_list.append(ElocalUtils.parseProduct(item))
                else:
                    item.addToStore(store_id, price)
                    product_list = ElocalUtils.parseProductAddStore(product_list, item, store_id, price)
                request.session['products'] = product_list
        return HttpResponseRedirect('/products')

def searchProduct(request):
    if request.method == 'GET':
        if 'zip_code' not in request.session:
            return HttpResponseRedirect('/')
        zip_code = request.session['zip_code']
        searchForm = ProductSearchForm(request.GET)
        addProductForm = ProductAddForm(request.session['coordinates'], request.session['radius'])
        addStoreForm = StoreAddForm()
        products = request.session['products']
        if searchForm.is_valid():
            name = searchForm.cleaned_data['name']
            products = ElocalUtils.searchProduct(name, products)
            if len(products) == 0:
                messages.error(request, 'No matching products.')
        else:
            messages.error(request, 'Must input a product.')
        return render(request, 'eLocal_app/productSearchPage.html', {'searchForm': searchForm, 'addProductForm': addProductForm, 'addStoreForm': addStoreForm, 'products': products, 'zip_code': zip_code})

def searchStore(request):
    if request.method == 'GET':
        if 'zip_code' not in request.session:
            return HttpResponseRedirect('/')
        zip_code = request.session['zip_code']
        searchForm = StoreSearchForm(request.GET)
        addProductForm = ProductAddForm(request.session['coordinates'], request.session['radius'])
        addStoreForm = StoreAddForm()
        stores = request.session['stores']
        if searchForm.is_valid():
            name = searchForm.cleaned_data['name']
            stores = ElocalUtils.searchStore(name, stores)
            if len(stores) == 0:
                messages.error(request, 'No matching stores.')
        else:
            messages.error(request, 'Must input a store.')
        return render(request, 'eLocal_app/storeSearchPage.html', {'searchForm': searchForm, 'addProductForm': addProductForm, 'addStoreForm': addStoreForm, 'stores': stores, 'zip_code': zip_code})

def addCart(request, product_id, store_id):
    if 'cart' in request.session:
        hashCode = ElocalUtils.getHash(product_id, store_id)
        cart = request.session['cart']
        updated_cart = ElocalUtils.addCart(hashCode, cart)
        if updated_cart is not None:
            cart = updated_cart
        else:
            product = Item.objects.get(id=product_id)
            store = Store.objects.get(id=store_id)
            cart_item = ElocalUtils.getInfoFromProductStore(product, store)
            cart.append(cart_item)
        request.session['cart'] = cart
    return HttpResponseRedirect('/cart')

def removeCart(request, product_id, store_id):
    if 'cart' in request.session:
        hashCode = ElocalUtils.getHash(product_id, store_id)
        cart = request.session['cart']
        updated_cart = ElocalUtils.removeCart(hashCode, cart)
        request.session['cart'] = updated_cart
    return HttpResponseRedirect('/cart')

