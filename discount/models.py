from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Case, When, IntegerField
from decimal import Decimal


class CustomerManager(models.Manager):
    
    '''
    queryset contains field max_discount, we can use it for getting discount,
    when creating order and showing discount in list, make sorting and filtering
    '''
        
    def objects_discount(self):
        objects_raw = self.raw('''
                WITH current_discount_customer AS (
                SELECT id
                FROM discount_customerdiscount
                where valid_from<=datetime('now') and valid_to>=datetime('now')
                )
                select c.id as id, c.name as name,
                IFNULL(cd.discount,0) as max_discount
                from discount_customer as c
                left join (
                    select customer_id, max(discount) as discount from discount_customerdiscount
                    where id in current_discount_customer group by customer_id
                    ) as cd on c.id = cd.customer_id;
                ''')
         
        max_discount_when = [When(id=row.id, then=row.max_discount) for row in objects_raw]
        
        queryset = super(CustomerManager, self).get_queryset()
        
        queryset = queryset.annotate(
            max_discount=Case(
                *max_discount_when,
                default=0,
                output_field=IntegerField()
            )
        )
        
        return queryset
        

class Customer(models.Model):
    name = models.CharField(max_length=255)
    
    objects = CustomerManager()
    
    def __str__(self):
        return self.name

   
class CustomerDiscount(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, db_index=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(validators=[MinValueValidator(0),
                                               MaxValueValidator(100)])
    
    def __str__(self):
        return '{} discount from {} to {}'.format(
            self.customer.__str__(), self.valid_from, self.valid_to)
    

class Category(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name


class ProductManager(models.Manager):
    
    '''
    queryset contains fields product_discount, brand_discount, category_discount, max_discount, discount_price we can use them for getting discounts,
    when creating order and showing discounts in list, make sorting and filtering
    '''
        
    def objects_discount(self):
        objects_raw = self.raw('''
                WITH current_discount AS (
                SELECT id
                FROM discount_discount
                where valid_from<=datetime('now') and valid_to>=datetime('now')
                )
                select dp.id as id,
                IFNULL(dpi.discount,0) as product_discount, 
                IFNULL(dbi.discount,0) as brand_discount, 
                IFNULL(dci.discount,0) as category_discount,
                max(IFNULL(dpi.discount,0), IFNULL(dbi.discount,0), IFNULL(dci.discount,0)) as max_discount,
                IFNULL(dp.price,0)-(IFNULL(dp.price,0)*max(IFNULL(dpi.discount,0), IFNULL(dbi.discount,0), IFNULL(dci.discount,0))/100) as discount_price
                from discount_product as dp
                left join (
                    select product_id, max(discount) as discount from discount_productdiscountitem
                    where head_id in current_discount group by product_id
                    ) as dpi on dp.id = dpi.product_id
                left join (
                    select brand_id, max(discount) as discount from discount_branddiscountitem
                    where head_id in current_discount group by brand_id
                    ) as dbi on dp.brand_id = dbi.brand_id
                left join (
                    select category_id, max(discount) as discount from discount_categorydiscountitem
                    where head_id in current_discount group by category_id
                    ) as dci on dp.category_id = dci.category_id;
                ''')
        
        product_discount_when=[]
        brand_discount_when=[]
        category_discount_when=[]
        max_discount_when=[]
        discount_price_when=[]
        
        for row in objects_raw:
            product_discount_when.append(When(id=row.id, then=row.product_discount))
            brand_discount_when.append(When(id=row.id, then=row.brand_discount))
            category_discount_when.append(When(id=row.id, then=row.category_discount))
            max_discount_when.append(When(id=row.id, then=row.max_discount))
            discount_price_when.append(When(id=row.id, then=row.discount_price))
        
        queryset = super(ProductManager, self).get_queryset()
        
        queryset = queryset.annotate(
            product_discount=Case(
                *product_discount_when,
                default=0,
                output_field=IntegerField()
            ),
            brand_discount=Case(
                *brand_discount_when,
                default=0,
                output_field=IntegerField()
            ),
            category_discount=Case(
                *category_discount_when,
                default=0,
                output_field=IntegerField()
            ),
            max_discount=Case(
                *max_discount_when,
                default=0,
                output_field=IntegerField()
            ),
            discount_price=Case(
                *discount_price_when,
                default=0,
                output_field=IntegerField()
            )
        )
        
        return queryset
    

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, db_index=True)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, db_index=True)
    
    objects = ProductManager()
    
    def __str__(self):
        return self.name
  
  
class Discount(models.Model):
    
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    
    def __str__(self):
        return 'discount from {} to {}'.format(self.valid_from, self.valid_to)


class ProductDiscountItem(models.Model):
    head = models.ForeignKey(Discount, related_name='productdiscount',
                                on_delete=models.CASCADE, db_index=True)
    product = models.ForeignKey(Product, related_name='product_items',
                                on_delete=models.PROTECT, db_index=True)
    discount = models.IntegerField(validators=[MinValueValidator(0),
                                               MaxValueValidator(100)])

    def __str__(self):
        return '{}'.format(self.product.__str__())
    
    
class BrandDiscountItem(models.Model):
    head = models.ForeignKey(Discount, related_name='branddiscount',
                                on_delete=models.CASCADE, db_index=True)
    brand = models.ForeignKey(Brand, related_name='brand_items',
                                on_delete=models.PROTECT, db_index=True)
    discount = models.IntegerField(validators=[MinValueValidator(0),
                                               MaxValueValidator(100)])

    def __str__(self):
        return '{}'.format(self.brand.__str__())
    
    
class CategoryDiscountItem(models.Model):
    head = models.ForeignKey(Discount, related_name='categorydiscount',
                                on_delete=models.CASCADE, db_index=True)
    category = models.ForeignKey(Category, related_name='category_items',
                                on_delete=models.PROTECT, db_index=True)
    discount = models.IntegerField(validators=[MinValueValidator(0),
                                               MaxValueValidator(100)])

    def __str__(self):
        return '{}'.format(self.category.__str__())


class Order(models.Model):
    
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    
    discount = models.IntegerField(default=0,
                                   validators=[MinValueValidator(0),
                                               MaxValueValidator(100)])

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return 'Order {}'.format(self.id)

    def total_cost(self):
        total_cost = sum(item.get_cost() for item in self.items.all())
        return total_cost - total_cost * (self.discount / Decimal('100'))
    
    def save(self, force_insert=False, force_update=False, using=None, 
        update_fields=None):
        
        cust = Customer.objects.objects_discount().filter(id=self.customer.id)
        if cust:
            self.discount = cust[0].max_discount
        
        return models.Model.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    discount = models.IntegerField(default=0,
                                   validators=[MinValueValidator(0),
                                               MaxValueValidator(100)])

    def __str__(self):
        return '{}'.format(self.id)

    def get_cost(self):
        total_cost =  self.price * self.quantity 
        return total_cost - total_cost * (self.discount / Decimal('100'))
    
    def save(self, force_insert=False, force_update=False, using=None, 
        update_fields=None):
        
        prod = Product.objects.objects_discount().filter(id=self.product.id)
        if prod:
            self.discount = prod[0].max_discount
            self.price = prod[0].price
        
        return models.Model.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)  
