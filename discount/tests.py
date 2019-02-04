from django.test import TestCase

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Customer(models.Model):
    name = models.CharField(max_length=255)
    discount = models.DecimalField(decimal_places=2, max_digits=10)
 
   
class CustomerDiscount(models.Model):
    customer = models.ForeignKey(Customer)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(validators=[MinValueValidator(0),
                                               MaxValueValidator(100)])

class Category(models.Model):
    name = models.CharField(max_length=255)
    discount = models.DecimalField(decimal_places=2, max_digits=10)


class Brand(models.Model):
    name = models.CharField(max_length=255)
    discount = models.DecimalField(decimal_places=2, max_digits=10)


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    category = models.ForeignKey(Category)
    brand = models.ForeignKey(Brand)
    discount = models.DecimalField(decimal_places=2, max_digits=10)

    def get_discounts(self):
        all_fields = self._meta.get_fields()
        discounts = []
        for field in all_fields:
            if field.get_internal_type() == 'ForeignKey':
                field_ref = getattr(self, field.name)
                if hasattr(field_ref, 'discount'):
                    discounts.append(field_ref.discount)

        return discounts

    def get_max_discount(self):
        return max(self.get_discounts())
  
  
class Discount(models.Model):
    
    limit = models.Q(app_label = 'discount', model = 'Category') |\
        models.Q(app_label = 'discount', model = 'Brand') |\
        models.Q(app_label = 'discount', model = 'Product')
    content_type = models.ForeignKey(ContentType, limit_choices_to = limit)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(validators=[MinValueValidator(0),
                                               MaxValueValidator(100)])
    
    #attendees = Attendee.objects.filter(content_type__model = 'Profile1')


def get_search_results(self, request, queryset, search_term):
    """Override to Include searching `product__name` which is a
     GenericForeignKey Field of all product types.
     Returns a tuple containing a queryset to implement the search,
     and a boolean indicating if the results may contain duplicates.
    """
    products = [v for k, v in pro_models.PRODUCT_DICT.iteritems()]
    generic_queryset = queryset

    product_list = list()
    for bit in search_term.split():
        for product in products:
            product_queryset = product.objects.filter(
                Q(name__icontains=bit))
            product_list += list(product_queryset)

        generic_query = [Q(**{
            'content_type': ContentType.objects.get_for_model(product),
            'object_id': product.id
        }) for product in product_list]

        if generic_query:
            generic_queryset = generic_queryset.filter(
                reduce(operator.or_, generic_query))
        else:
            generic_queryset = generic_queryset.none()

    default_queryset, use_distinct = \
        super(OrderAdmin, self).get_search_results(
            request,
            queryset,
            search_term
        )
    return default_queryset | generic_queryset, use_distinct

    # GREATEST (rank_1, rank_2, rank_3) AS largest_rank
    # max(,,,)


    #attendees = Attendee.objects.filter(content_type__model = 'Profile1')
    
    #activites = Activity.objects.filter(
        #models.Q(actor__in=user_list) |
        #models.Qposts__tags__in=tag_list) |
        #models.Q(photos__tags__in=tag_list)
        
    #from django.contrib.contenttypes.models import ContentType

    #issue = Issue.objects.get(scan=scan_obj)
    #tickets = Ticket.objects.filter(issue_id=issue.id, 
        #issue_ct=ContentType.objects.get_for_model(issue)
      
    #WITH current_discount AS (
        #SELECT id
        #FROM discount_discount
        #where valid_from<=datetime('now') and valid_to>=datetime('now')
    #)
           
    #select dp.id, dp.name, IFNULL(dp.price,0), IFNULL(dpi.discount,0), 
    #max(IFNULL(dpi.discount,0), IFNULL(dbi.discount,0), IFNULL(dci.discount,0)) as ddd  
    #from discount_product as dp
    #left join discount_productdiscountitem as dpi on dp.id = dpi.product_id
    #left join discount_branddiscountitem as dbi on dp.id = dbi.brand_id
    #left join discount_categorydiscountitem as dci on dp.id = dci.category_id
    #where dpi.head_id in current_discount or 1
    #or dbi.head_id in current_discount
    #or dci.head_id in current_discount;
    
    #select dp.id, dp.name, IFNULL(dp.price,0), IFNULL(dpi.discount,0), 
    #max(IFNULL(dpi.discount,0), IFNULL(dbi.discount,0), IFNULL(dci.discount,0)) as ddd  
    #from discount_product as dp
    #left join discount_productdiscountitem as dpi on dp.id = dpi.product_id
    #left join discount_branddiscountitem as dbi on dp.brand_id = dbi.brand_id
    #left join discount_categorydiscountitem as dci on dp.category_id = dci.category_id
    #where dpi.head_id in current_discount or 1
    #or dbi.head_id in current_discount
    #or dci.head_id in current_discount;

    #CREATE VIEW current_discount 
    #AS 
    #SELECT id
    #FROM discount_discount
    #where valid_from<=datetime('now') and valid_to>=datetime('now');
    
    
    #select dp.id, dp.name, IFNULL(dp.price,0) as price,
    #max(IFNULL(dpi.discount,0), IFNULL(dbi.discount,0), IFNULL(dci.discount,0)) as discount,
    #IFNULL(dp.price,0)-(IFNULL(dp.price,0)*max(IFNULL(dpi.discount,0), IFNULL(dbi.discount,0), IFNULL(dci.discount,0))/100) as discount_price
    #from discount_product as dp
    #left join (
        #select product_id, max(discount) as discount from discount_productdiscountitem
        #where head_id in current_discount group by product_id
        #) as dpi on dp.id = dpi.product_id
    #left join (
        #select brand_id, max(discount) as discount from discount_branddiscountitem
        #where head_id in current_discount group by brand_id
        #) as dbi on dp.brand_id = dbi.brand_id
    #left join (
        #select category_id, max(discount) as discount from discount_categorydiscountitem
        #where head_id in current_discount group by category_id
        #) as dci on dp.category_id = dci.category_id;
        
    #iterator(chunk_size=2000)
    #for p in Person.objects.raw('SELECT * FROM myapp_person'):
        #print(p)

