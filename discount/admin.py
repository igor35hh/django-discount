from django.contrib import admin
from discount.models import (
    Customer, CustomerDiscount, Discount, ProductDiscountItem,
    Category, Brand, Product, BrandDiscountItem, CategoryDiscountItem,
    Order, OrderItem)

class OrderProductItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderProductItemInline]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    
    list_display = ['name', 'max_discount']
    
    def get_queryset(self, request):
        
        queryset = Customer.objects.objects_discount()
        
        return queryset
    
    def max_discount(self, obj):
        return obj.max_discount
    
    max_discount.admin_order_field = 'max_discount'

@admin.register(CustomerDiscount)
class CustomerDiscountAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    pass


class ProductAdminPriceDiscountFilter(admin.SimpleListFilter):
    title = 'discount_price'
    parameter_name = 'discount_price'

    def lookups(self, request, model_admin):
        return (
            ('from_1000_to_100000', 'From 1000 to 10000'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        print(value)
        if value == 'from_1000_to_100000':
            return queryset.filter(discount_price__range=(1000,10000))

        return queryset


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'id','name','category','brand','price', 'product_discount',
        'brand_discount', 'category_discount', 'max_discount',
        'discount_price'
        ]
    list_editable = ['price']
    list_filter = [ProductAdminPriceDiscountFilter]
    
    def get_queryset(self, request):
        
        queryset = Product.objects.objects_discount()
        
        return queryset
    
    def product_discount(self, obj):
        return obj.product_discount
    
    def brand_discount(self, obj):
        return obj.brand_discount
    
    def category_discount(self, obj):
        return obj.category_discount
    
    def max_discount(self, obj):
        return obj.max_discount
        
        
    def discount_price(self, obj):
        return obj.discount_price
    
    discount_price.admin_order_field = 'discount_price'
    

class CategoryDiscountItemInline(admin.TabularInline):
    model = CategoryDiscountItem
    raw_id_fields = ['category']


class BrandDiscountItemInline(admin.TabularInline):
    model = BrandDiscountItem
    raw_id_fields = ['brand']


class ProductDiscountItemInline(admin.TabularInline):
    model = ProductDiscountItem
    raw_id_fields = ['product']


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    inlines = [ProductDiscountItemInline, BrandDiscountItemInline, CategoryDiscountItemInline]
    