from django.contrib import admin
from .models import*


class CategoryShow(admin.ModelAdmin):
	list_display = ['name', 'slug']
	prepopulated_fields = {'slug': ('name',)}

	class Meta:
		model = Category
admin.site.register(Category, CategoryShow)
	


class CouponShow(admin.ModelAdmin):
	list_display = ['uid', 'coupon_code', 'is_expired', 'discount_price', 'minimum_amount']
	class Meta:
		model = Coupon		
admin.site.register(Coupon, CouponShow)




class AddWriter(admin.ModelAdmin):
	list_display = ['name', 'slug']
	prepopulated_fields = {'slug': ('name',)}

admin.site.register(Writer, AddWriter)




class BookImageAdmin(admin.StackedInline):
    model = BookImage

class AddBook(admin.ModelAdmin):
	list_display = ['name', 'price', 'stock', 'status', 'created_at', 'updated_at']
	list_filter = ['status', 'created_at', 'updated_at']
	list_editable = ['price', 'stock', 'status']
	prepopulated_fields = {'slug': ('name',)}
	inlines = [BookImageAdmin]

admin.site.register(Book, AddBook)
admin.site.register(BookImage)



class ReviewShow(admin.ModelAdmin):
	list_display = ['customer', 'book', 'review_star', 'review_text']
	list_filter = ['customer']

admin.site.register(Review, ReviewShow)