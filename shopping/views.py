import os
import jdatetime
import random
import uuid
from flask import redirect, url_for, render_template, flash, request, session
from flask_login import login_required, current_user
from app import db, app
from . import shopping
from auth.models import User
from .models import Product, Category, Cart, Order
from .forms import ProductForm, CategoryForm, UserInfoForm
from werkzeug.utils import secure_filename
from utils import save_image, allow_extension
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc






@shopping.route('', methods=['POST', 'GET'])
def index():
    page = request.args.get('page', default=1, type=int)
    products = Product.query.order_by(desc(Product.date)).paginate(page=page, per_page=10)
    orders = Order.query.filter_by(user_id=current_user.id, bought=0).all()
    order_product = [order.product_id for order in orders]
    # ============ set global variable, but dont work in app.py =======
    # orders = Order.query.filter_by(user_id=current_user.id).all()
    app.jinja_env.globals['orders'] = orders
    # ==================================================================
    return render_template('shopping/index.html', products=products, order_product=order_product) 


@shopping.route('create-category', methods=['POST', 'GET'])
def category_create():
    form = CategoryForm()
    categories = Category.query.order_by(desc(Category.date)).all()
    if request.method == "POST":
        if form.validate_on_submit():
            cat = Category()
            cat.title = request.form.get('title')
            try:
                db.session.add(cat)
                db.session.commit()
                flash('your data is saved successfully', 'success')
            except IntegrityError as er:
                db.session.rollback()
                flash(f'error {er} is happened, please try again', 'warning')
            finally:
                return redirect(url_for('shopping.category_create', form=form))
        
        flash('form is not valid', 'warning')

    return render_template('shopping/category-create.html', form=form, categories=categories)


@shopping.route('edit-category/<int:cat_id>', methods=['POST', 'GET'])
def category_edit(cat_id):
    categories = Category.query.all()
    category = Category.query.get(cat_id)
    form = CategoryForm()
    if request.method == 'POST':
        title = request.form.get('title')
        category.title = title
        try:
            db.session.add(category)
            db.session.commit()
        except IntegrityError as ie:
            db.session.rollback()
            flash(f'error {ie} is happened', 'warning')
        except Exception as e:
            flash(f'error {e} is happened, please try again !!', 'warning')
        finally:
            return redirect(url_for('shopping.category_edit', categories=categories, title=category.title, cat_id=category.id, form=form))

    return render_template('shopping/category-edit.html', categories=categories, title=category.title, cat_id=category.id, form=form)

@shopping.route('/new-product', methods=['POST', 'GET'])
def product_new():
    print(jdatetime.date.today())
    form = ProductForm()
    if request.method == 'POST': 
        if form.validate_on_submit():
            old_product = Product.query.filter_by(name=request.form.get('name')).first()
            if old_product or request.form.get('name') == '':
                flash('this Name for product is registered previously, please select another name', 'warning')
                return redirect(url_for('shopping.product_new', form=form))
            product = Product()
            product.name = request.form.get('name')
            product.price = request.form.get('price')
            product.category_id = request.form.get('category')
            product.number = request.form.get('number')
            product.rating = request.form.get('rating')
            image = request.files.get('image')
            today = str(jdatetime.date.today())
            if save_image(image, 'shopping', 'shopping.product_new', form):
                product.image = f"uploads/shopping/{today}/{image.filename}"

            try:
                db.session.add(product)
                db.session.commit()
                flash(f'product {product.name} is registered successfully', 'success')
            except IntegrityError as er:
                db.session.rollback()
                flash(f'error {er} is happened', 'warning')
                raise er
            except Exception as e:
                    # Raise all other exceptions. 
                    flash(f'error {e} is happened', 'warning')
                    raise e
            finally:
                return redirect(url_for('shopping.product_new', form=form))

        flash('form is not validate', 'warning')

    return render_template('shopping/product-new.html', form=form)


@shopping.route('/products-list', methods=['POST', 'GET'])
def products_list():
    page = request.args.get('page', default=1, type=int)
    products = Product.query.order_by(desc(Product.date)).paginate(page=page, per_page=4)

    return render_template('shopping/products-list.html', products=products) 


@shopping.route('/product-detail/<int:product_id>', methods=['POST', 'GET'])
def product_detail(product_id):
    print('==================================================================================')
    print('request url is ---> ', request.url)
    print('request url is ---> ', request.base_url, request.host_url, request.root_url)
    # print('request json', request.json)
    print('request blueprint ---> ', request.blueprint)
    print('request cookies ---> ', request.cookies)
    print('request date ---> ', request.date)
    print('request headers ---> ', request.headers)
    print('request user_agent ---> ', request.user_agent)
    print('request args ---> ', request.args)
    print('request values ---> ', request.values)
    print('request scheme ---> ', request.scheme)
    print('request remote_addr ---> ', request.remote_addr)
    print('request path ---> ', request.path)
    # print('request module', request.module)
    print('request headers ---> ', request.headers)
    print('request full_path ---> ', request.full_path)
    print('request endpoint ---> ', request.endpoint)
    print('request access_route ---> ', request.access_route)
    print('request environ ---> ', request.environ)
    print('request environ(REMOTE_ADDR) ---> ', request.environ['REMOTE_ADDR'])
    print('==================================================================================')
    product = Product.query.get(product_id)
    orders = Order.query.filter_by(user_id=current_user.id).all()
    order_product = [order.product_id for order in orders]
    

    return render_template('shopping/product-detail.html', product=product, order_product=order_product)


@shopping.route('edit-product/<int:product_id>', methods=['POST', 'GET'])
def product_edit(product_id):
    form = ProductForm()
    product = Product.query.filter_by(id=product_id).first()
    form.category.default = product.category_id
    form.process()
    if request.method == 'POST':
        form = ProductForm()
        if form.validate_on_submit():
            product.name = request.form.get('name')
            product.price = request.form.get('price')
            product.number = request.form.get('number')
            product.rating = request.form.get('rating')
            product.category_id = request.form.get('category')
            # ===========================_Image_Upload_=================================
            image = request.files.get('image')
            today = str(jdatetime.date.today())
            if image.filename is None:
                flash('you not select an image properly', 'warning')
            if image:
                file_secure = secure_filename(image.filename)
                if not allow_extension(file_secure):
                    flash('the extension of image is not allowed, please try again', 'warning')
                    return redirect(url_for('shopping.product_edit', product_id=product.id, form=form))
                folder = os.path.join(app.config['UPLOAD_DIR'], 'shopping', str(today))
                try:
                    os.makedirs(folder)
                except:
                    pass
                finally:
                    image.save(os.path.join(folder, file_secure))
                    product.image = f"uploads/shopping/{today}/{image.filename}"
            # =============================_End_Of_Image_Upload_===========================
            try:
                db.session.commit()
                flash(f'your product {product.name} is editted successfully', 'success')
            except IntegrityError as er:
                db.session.rollback()
                flash(f'error {er} is happened', 'warning')
            except Exception as e:
                flash(f'error {e} is happened, please try again', 'warning')
            finally:
                return redirect(url_for('shopping.product_edit', product_id=product.id, form=form))
        else:
            flash('your form is not validate, please try again', 'warning')

    return render_template('shopping/product-edit.html', product=product, form=form)


@shopping.route('product/buy/<int:product_id>', methods=['POST', 'GET'])
def product_buy(product_id):
    print(request.endpoint)
    product = Product.query.get(product_id)
    if request.method == 'POST':
        order = Order()
        order.user_id = current_user.id 
        order.product_id = product.id
        order.number = int(request.form.get('number')) if request.form.get('number') != '' else 1
        if order.number > 5 :
            flash('you dont select product more than 5, please decreese your number of product', 'warning')
            if request.args.get('page') == 'product_detail':
                return redirect(url_for('shopping.product_detail', product_id=product.id))
            return redirect(url_for('shopping.index'))
        if order.number > product.number:
            flash(f'this product has {product.number} number, please try again and choose less than selected', 'warning')
            if request.args.get('page') == 'product_detail':
                return redirect(url_for('shopping.product_detail', product_id=product.id))
            return redirect(url_for('shopping.index'))
        try:
            db.session.add(order)
            db.session.commit()
            flash(f'you select {order.number} of product {product.name} and it is added to shopping cart', 'success')
        except Exception as er:
            db.session.rollback()
            flash(f'error {er} is happened, please try again', 'warning')
        finally:
            if request.args.get('page') == 'product_detail':
                return redirect(url_for('shopping.product_detail', product_id=product.id))
            return redirect(url_for('shopping.index'))
        
    Order.query.filter_by(user_id=current_user.id, product_id=product_id).delete()
    db.session.commit()
    flash(f'your product {product.name} is removed from shoppin cart', 'info')
    if request.args.get('page') == 'product_detail':
        return redirect(url_for('shopping.product_detail', product_id=product.id))
    return redirect(url_for('shopping.index'))
    

@shopping.route('cart/details/', methods=['POST', 'GET'])
def cart_details():
    orders = Order.query.filter_by(user_id=current_user.id, bought=0).all()
    sum = 0
    for order in orders:
        sum += int(order.number) * int(order.get_price())

    return render_template('shopping/cart.html', orders=orders, sum=sum)


@shopping.route('cart/product/delete/<int:product_id>', methods=['GET'])
def product_delete(product_id):
    Order.query.filter_by(product_id=product_id).delete()
    db.session.commit()
    return redirect(url_for('shopping.cart_details'))


@shopping.route('buy/end', methods=['POST', 'GET'])
def buy_end():
    if current_user.address == '' or current_user.phone_auth == False:
        return redirect(url_for('shopping.user_info'))
    
    orders = Order.query.filter_by(user_id=current_user.id, bought=False).all()

    if len(orders) < 1:
        page = request.args.get('page', default=1, type=int)
        products = Product.query.order_by(desc(Product.date)).paginate(page=page, per_page=10)
        flash('your shopping basket is empty, please select product', 'warning')
        return redirect(url_for('shopping.index', products=products, order_product=[order.product_id for order in orders]))
    
    sum = 0
    for order in orders:
        sum += int(order.number) * int(order.get_price())
        product = Product.query.get(order.product_id)
        product.sold_number += order.number
    sum_end = sum + int(sum * 0.1)

    if request.method == 'POST':
        cart = Cart()
        cart.user_id = current_user.id 
        cart.sum_price = str(sum_end)
        cart.products = [Product.query.get(order.product_id) for order in orders]

        try:
            db.session.add(cart)
            db.session.commit()
            flash('you are accepted factor and you are connecting to bank', 'success')
            return redirect(url_for('shopping.buy_checkout', cart_id=cart.id))
        except IntegrityError as er :
            db.session.rollback()
            flash(f'error {er} is happened, please try agian', 'danger')
            return redirect(url_for('shopping.buy_end'))
        except Exception as e:
            flash(f'error {e} is occured, please try agian !', 'warning')
            return redirect(url_for('shopping.buy_end'))


    return render_template('shopping/buy-end.html', orders=orders, sum=sum, sum_end=sum_end)


@shopping.route('buy-checkout/<int:cart_id>', methods=['POST', 'GET'])
def buy_checkout(cart_id):
    cart = Cart.query.get_or_404(cart_id)
    if cart.transaction:
        orders = Order.query.filter_by(serial=cart.serial).all()
        return render_template('shopping/buy-checkout.html', cart=cart, orders=orders, today=jdatetime.datetime.now())

    orders = Order.query.filter_by(user_id=current_user.id, bought=False).all()
    cart.transaction = True
    try:
        db.session.add(cart)
        db.session.commit()
        for order in orders:
            order.bought = True
            order.serial = cart.serial
            product = Product.query.get(order.product_id)
            product.number -= order.number
            db.session.add(product)
            db.session.add(order)
            db.session.commit()
        flash('your products is ready to sent', 'success')
        return render_template('shopping/buy-checkout.html', cart=cart, orders=orders, today=jdatetime.datetime.now())
    except IntegrityError as er:
        db.session.rollback()
        flash(f'error {er} is happened', 'danger')
        # return redirect(url_for('shopping.buy_end'))
        return render_template('shopping/buy-checkout.html')
    except Exception as e:
        flash(f'error {e} is happened !!', 'warning')
        return render_template('shopping/buy-checkout.html')
        # return redirect(url_for('shopping.buy_end'))
    

@shopping.route('cart-list/<int:user_id>', methods=['POST', 'GET'])
def cart_list(user_id):
    page = request.args.get('page', default=1, type=int)
    carts = Cart.query.filter_by(user_id=user_id).order_by(desc(Cart.created_at)).paginate(page=page, per_page=8)

    return render_template('shopping/cart-list.html', carts=carts)


@shopping.route('user-info', methods=['POST', 'GET'])
def user_info():
    form = UserInfoForm()
    if request.method == 'POST':
        if current_user.phone_auth:
            return redirect(url_for('shopping.buy_end'))
        if form.validate_on_submit():
            phone = request.form.get('phone')
            province = request.form.get('province')
            city = request.form.get('city')
            street = request.form.get('street')
            post_code = request.form.get('post_code')
            current_user.address = f'{province}**-**{city}**-**{street}**-**{post_code}'
            old_user = User.query.filter_by(phone=phone).one()
            if old_user.id != current_user.id and old_user.phone_auth == True and old_user.phone == phone:
                flash('this mobile number is set for another user, please enter your phone number', 'warning')
                return redirect(url_for('shopping.user_info', form=form))
            if current_user.phone != '' or current_user.phone_auth == False:
                current_user.phone = phone
            try:
                db.session.add(current_user)
                db.session.commit()
                flash('your information is update', 'success')
                code = random.randint(10000,99999)
                print(code)
                session['user_uuid'] = str(code)
                return redirect(url_for('shopping.user_phone_auth'))
            except IntegrityError as er:
                flash(f'error {er} is happend, please try again', 'warning')
                return redirect(url_for('shopping.user_info', form=form))
            except Exception as e:
                flash(f'error {e} is happend. please try again', 'warning')
                return redirect(url_for('shopping.user_info', form=form))
                

    return render_template('shopping/user-info.html', form=form)


@shopping.route('user-info/phone-auth/', methods=['POST', 'GET'])
def user_phone_auth():
    if request.method == 'POST':
        code = request.form.get('code')
        if str(code) == str(session['user_uuid']):
            current_user.phone_auth = True
            db.session.commit()
            session.pop('user_uuid')
            flash('your phone number is validate', 'success')
            return redirect(url_for('shopping.buy_end'))
        else:
            flash('code is wrong, please try agian', 'warning')
            form = UserInfoForm()
            return redirect(url_for('user_info', form=form))
    
    return render_template('shopping/user-phone-auth.html')


@shopping.route('best-seller-list', methods=['POST', 'GET'])
def best_seller_list():
    page = request.args.get('page', default=1, type=int)
    # products = Product.query.order_by(desc(Product.date)).paginate(page=page, per_page=4)
    best_sell = Product.query.order_by(desc(Product.sold_number)).paginate(page=page, per_page=8)

    return render_template('shopping/best-seller-list.html', products=best_sell)
    

@shopping.route('transactions', methods=['POST', 'GET'])
def transactions():
    carts = Cart.query.all()
    sum = 0
    sum_user = 0
    for cart in carts:
        sum += int(cart.sum_price)
        if cart.user_id == current_user.id:
            sum_user += int(cart.sum_price)

    best_sell = Product.query.order_by(desc(Product.sold_number)).first()

    best_sell_user_product_id = Order.query.filter_by(user_id=current_user.id).order_by(desc(Order.number)).first().product_id
    best_sell_user = Product.query.get(best_sell_user_product_id)
    

    return render_template('shopping/transactions.html', sum=sum, sum_user=sum_user, best_product=best_sell.name, best_sell_user=best_sell_user.name)

