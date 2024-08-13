from django.db import models
from django.contrib.auth.models import User
from base.models import BaseModel
# from accounts.models import Profile
from django.utils.text import slugify

# Create your models here.
class Category(BaseModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    icon = models.FileField(upload_to = "category/")
    image = models.ImageField(upload_to = "categories")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Writer(BaseModel):
	name = models.CharField(max_length = 100)
	slug = models.SlugField(max_length=150, unique=True ,db_index=True)
	bio = models.TextField()
	pic = models.FileField(upload_to = "writer/")

	def __str__(self):
		return self.name
      
	  
class Book(BaseModel):
	writer = models.ForeignKey(Writer, on_delete = models.CASCADE)
	category = models.ForeignKey(Category, on_delete = models.CASCADE)
	name = models.CharField(max_length = 100)
	slug = models.SlugField(unique=True, max_length=100, db_index=True)
	price = models.IntegerField()
	stock = models.IntegerField()
	coverpage = models.FileField(upload_to = "coverpage/")
	totalreview = models.IntegerField(default=0)
	totalrating = models.FloatField(default=0.0)
	status = models.IntegerField(default=0)
	description = models.TextField()

	def __str__(self):
		return self.name

	def get_average_rating(self):
		review_obj = Review.objects.filter(book = self.uid)
		count = 0
		total_rating = 0
		for review in review_obj:
			total_rating += review.review_star
			count+=1
		if count == 0:
			return 0
		else:
			return round(total_rating/count, 2)



class BookImage(BaseModel):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="book_images")
    image = models.ImageField(upload_to = "bookpage/")


class Coupon(BaseModel):
	coupon_code = models.CharField(max_length = 10)
	is_expired = models.BooleanField(default=False)
	discount_price = models.IntegerField(default=100)
	minimum_amount = models.IntegerField(default=500)

class Review(BaseModel):
	customer = models.ForeignKey(User, on_delete = models.CASCADE)
	book = models.ForeignKey(Book, on_delete = models.CASCADE)
	review_star = models.IntegerField(default=0)
	review_text = models.TextField(default="", max_length=100)

	def get_profileimage(self):
		from accounts.models import Profile
		return Profile.objects.get(user = self.customer).profile_image

	def get_review_count(self):
		reviews = Review.objects.filter(book = self.book)
		print()
		return reviews.count()
