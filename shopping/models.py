import uuid
from jdatetime import datetime
from app import db
from sqlalchemy import Column, ForeignKey, Text, Integer, String, Boolean, DateTime, event, Table, DECIMAL
from auth.models import User
from flask_login import current_user



carts_products = Table('carts_products', db.metadata,
    Column('cart_id', Integer, ForeignKey('shopping_cart.id', ondelete='cascade')),
    Column('product_id', Integer, ForeignKey('shopping_products.id', ondelete='cascade'))
)


class Cart(db.Model):
    __tablename__  = 'shopping_cart'
    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), ForeignKey('users.id'))
    products = db.relationship('Product', secondary=carts_products, back_populates='carts')
    sum_price = Column(String(150), default='0')
    created_at = Column(DateTime(), default=datetime.now())
    updated_at = Column(DateTime(), default=datetime.now())
    serial = Column(String(100))
    transaction = Column(Boolean(), default=False)

    def __init__(self):
        self.serial = str(uuid.uuid5(uuid.NAMESPACE_DNS, f'{current_user.name + str(datetime.now())}'))
        
    def __repr__(self) -> str:
        return self.products
    
    def user(self):
        return User.query.get(self.user_id).name
    
    def get_products(self):
        return [product.name for product in self.products ]


        
    



class Product(db.Model):
    __tablename__ = 'shopping_products'
    id = Column(Integer(), primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    price = Column(Integer(), default=0)
    category_id = Column(Integer(), ForeignKey('shopping_categories.id', ondelete='cascade'))
    number = Column(Integer(), default=0)
    image = Column(String(100), default='img/product.jpg')
    date = Column(DateTime(), default=datetime.now())
    rating = Column(db.DECIMAL(8, 2), default=1.0)
    carts = db.relationship('Cart', secondary=carts_products, back_populates='products')
    sold_number = Column(Integer(), default=0)
    
    def __repr__(self) -> str:
        return self.name
    
    def is_available(self):
        return True if len(self.number) > 0 else False 
    
    def getCategory(self, category_id):
        return Category.query.get(category_id).title
    



class Category(db.Model):
    __tablename__ = 'shopping_categories'
    id = Column(Integer(), primary_key=True)    
    title = Column(String(100), nullable=False, unique=True)
    date = Column(DateTime(), default=datetime.now())
    products = db.relationship('Product', backref='category')

    def __repr__(self) -> str:
        return self.title
        



class Order(db.Model):
    __tablename__ = 'shopping_orders'
    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), ForeignKey('users.id'))
    product_id = Column(Integer(), ForeignKey('shopping_products.id'))
    number = Column(Integer(), default=1)
    bought = Column(Boolean(), default=False)
    date = Column(DateTime(), default=datetime.now())
    serial = Column(String(120))

    def __repr__(self) -> str:
        return super().__repr__()
    
    def get_price(self):
        return Product.query.get(self.product_id).price
    
    def get_product_name(self):
        return Product.query.get(self.product_id).name
    
    def get_category_name(self, category_id):
        category_id =  Product.query.get(self.product_id).category_id
        return Category.query.get_or_404(category_id).title
    
    def get_product_image(self):
        return Product.query.get(self.product_id).image
    

    




