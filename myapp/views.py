
from django.shortcuts import render,redirect
from .models import Contact,User,Book,Cart,Wishlist,Transaction
from django.conf import settings
from django.core.mail import send_mail
import random
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt

def initiate_payment(request):
    if request.method == "GET":
        return render(request, 'myapp/pay.html')
    try:
        amount = int(request.POST['amount'])
    except:
        return render(request, 'myapp/pay.html', context={'error': 'Wrong Accound Details or amount'})
    user=User.objects.get(email=request.session['email'])
    transaction = Transaction.objects.create(made_by=user, amount=amount)
    transaction.save()
    merchant_key = settings.PAYTM_SECRET_KEY

    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str(user.email)),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://127.0.0.1:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    checksum = generate_checksum(paytm_params, merchant_key)

    transaction.checksum = checksum
    transaction.save()

    paytm_params['CHECKSUMHASH'] = checksum
    print('SENT: ', checksum)
    return render(request, 'myapp/redirect.html', context=paytm_params)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
        return render(request, 'myapp/callback.html', context=received_data)

def index(request):
	try:
		if  request.session['email']:
			user=User.objects.get(email=request.session['email'])
			print(user)
			if user.usertype=="user":
				return render(request,'myapp/index.html')
			elif user.usertype=="seller":
				return render(request,'myapp/seller_index.html')
	except:
		return render(request,'myapp/login.html')
def python(request):
	books=Book.objects.filter(book_category='python')
	return render(request,'myapp/python.html',{'books':books})
def java(request):
	books=Book.objects.filter(book_category='java')
	return render(request,'myapp/java.html',{'books':books})
def php(request):
	books=Book.objects.filter(book_category='php')
	return render(request,'myapp/php.html',{'books':books})
def login(request):
	if request.method=="POST":
		email=request.POST['email']
		password=request.POST['password']
		try:
			user=User.objects.get(email=email,password=password)
			if user.status=="active" and user.usertype=="user":
				mycart=Cart.objects.filter(user=user)
				request.session['cartcount']=len(mycart)
				request.session['fname']=user.first_name
				request.session['email']=user.email
				request.session['user_image']=user.user_image.url
				
				return render(request,'myapp/index.html')
			elif user.status=="active" and user.usertype=="seller":
				request.session['fname']=user.first_name
				request.session['email']=user.email
				request.session['user_image']=user.user_image.url
				return render(request,'myapp/seller_index.html')
			else:
				msg="you still not verify your account"
				return render(request,'myapp/enter_email.html',{'msg':msg})
		except:
			msg="Email and password does not exist."
			return render(request,'myapp/login.html',{'msg':msg})
	else:
		return render(request,'myapp/login.html')
def signup(request):
	if request.method=="POST":
		user=User()
		user.usertype=request.POST['usertype']
		user.fname=request.POST['fname']
		user.lname=request.POST['lname']
		user.email=request.POST['email']
		user.mobile=request.POST['mobile']
		user.password=request.POST['password']
		user.cpassword=request.POST['cpassword']
		user.user_image=request.FILES['user_image']
		a=User.objects.filter(email=user.email)

		if a:
			msg="Email alrady exist"
			return render(request,'myapp/login.html',{'msg':msg})
		
		elif user.password==user.cpassword:
			User.objects.create(first_name=user.fname,last_name=user.lname,email=user.email,password=user.password,cpassword=user.cpassword,mobile=user.mobile,usertype=user.usertype,user_image=user.user_image)
			rec=[user.email,]
			subject="OTP for Registration"
			otp=random.randint(1000,9999)
			message="your OTP for Registration is "+str(otp)
			email_from=settings.EMAIL_HOST_USER
			send_mail(subject,message,email_from,rec)
			return render(request,'myapp/verify_otp.html',{'otp':otp,'email':user.email})
		else:
			msg="Password and Confirm Password Doen't Match"
			return render(request,'myapp/signup.html',{'msg':msg,'user':user})
			
	else:
		return render(request,'myapp/signup.html')

def contact(request):
	if request.method=="POST":
		name=request.POST['name']
		email=request.POST['email']
		mobile=request.POST['mobile']
		remarks=request.POST['remarks']
		Contact.objects.create(name=name,email=email,mobile=mobile,remarks=remarks)
		# msg="contact saved successfully"
		# contacts=Contact.objects.all().order_by("-id")
		# return render(request,'myapp/contact.html',{'msg':msg, 'contacts':contacts})
		return redirect("contact")
	else:
		contacts=Contact.objects.all().order_by("-id")
		return render(request,'myapp/contact.html',{'contacts':contacts,})

def verify_otp(request):
	otp=request.POST['otp']
	email=request.POST['email']
	u_otp=request.POST['u_otp']

	if 	otp==u_otp:
		user=User.objects.get(email=email)
		if user.status=="active":
			return render(request,"myapp/new_password.html",{'email':email})
		else:
			user.status="active"
			user.save()
			msg="Your account now Active"
			return render(request,"myapp/login.html",{'msg':msg})
	else:
		msg="entered OTP is incorrect Please re-enter your correct OTP"
		return render(request,"myapp/verify_otp.html",{'otp':otp,'email':email,'msg':msg})


	
def logout(request):
	try:
		del request.session['fname']
		del request.session['email']
		return render(request,'myapp/login.html')
	except:
		pass
											
def enter_email(request):
	return render(request,'myapp/enter_email.html')

def forgot_password(request):
	email=request.POST['email']
	password=request.POST['password']
	cpassword=request.POST['cpassword']
	if password==cpassword:
		try:
			user=User.objects.get(email=email)
			user.password=password
			user.cpassword=cpassword
			user.save()
			msg="Password Updated Succeed"
			return render(request,'myapp/login.html',{'msg':msg})
		except:
			pass
	else:	
			msg="Password and Confirm Password not matched"
			return render(request,'myapp/new_password.html',{'msg':msg,'email':email})

def send_otp(request):
	email=request.POST['email']
	try:
		user=User.objects.get(email=email)
		if user:
			rec=[email,]
			subject="OTP for validation"
			otp=random.randint(1000,9999)
			message="your OTP for Registration is "+str(otp)
			email_from=settings.EMAIL_HOST_USER
			try:
				send_mail(subject,message,email_from,rec)
				return render(request,'myapp/verify_otp.html',{'otp':otp,'email':email})
			except:
				msg="Network issue."
				return render(request,'myapp/login.html',{'msg':msg})
	except:
		msg="email does not exist."
		return render(request,'myapp/login.html',{'msg':msg})

def change_password(request):
	if request.method=="POST":	
		user=User.objects.get(email=request.session['email'])
		old_password=request.POST['old_password']
		new_password=request.POST['new_password']
		new_cpassword=request.POST['new_cpassword']
		if user.password!=old_password:
			msg="old Password is doesn't match"
			return render(request,'myapp/change_password.html',{'msg':msg})
		elif new_password!=new_cpassword:
			msg="New Password & Confirm Password Doesn't Match"
			return render(request,'myapp/change_password.html',{'msg':msg})
		else:
			user.password=new_password
			user.cpassword=new_cpassword
			user.save()
			try:
				del request.session['fname']
				del request.session['email']
				msg="Password changed successfully.Please login again"
				return render(request,'myapp/login.html',{'msg':msg})
			except:
				pass
	return render(request,'myapp/change_password.html')

def add_book(request):
	if request.method=="POST":
		bc=request.POST['book_category']
		bn=request.POST['book_name']
		bp=request.POST['book_price']
		ba=request.POST['book_author']
		bd=request.POST['book_desc']
		bi=request.FILES['book_image']
		bse=request.session['email']
		Book.objects.create(book_category=bc,book_name=bn,book_price=bp,book_author=ba,book_desc=bd,book_image=bi,book_seller_email=bse),
		msg="Book Added successfully"
		return render(request,'myapp/add_book.html',{'msg':msg})
	else:
		return render(request,'myapp/add_book.html')

def seller_index(request):
	return render(request,'myapp/seller_index.html')

def view_book(request):
	books=Book.objects.filter(book_status="active",book_seller_email=request.session["email"])
	return render(request,'myapp/view_book.html',{'books':books})

def book_detail(request,pk):
	books=Book.objects.get(pk=pk)
	return render(request,'myapp/book_detail.html',{'books':books})

def delete_book(request,pk):
 	books=Book.objects.get(pk=pk)
 	books.book_status="inactive"
 	books.save()
 	books=Book.objects.filter(book_status="active",book_seller_email=request.session["email"])
 	msg="Book Inactivated successfully."
 	return render(request,'myapp/view_book.html',{'msg':msg,'books':books})

def inactive_book(request):
	books=Book.objects.filter(book_status="inactive")
	return render(request,'myapp/inactive_book.html',{'books':books})

def active_book(request,pk):
	books=Book.objects.get(pk=pk)
	books.book_status="active"
	books.save()
	books=Book.objects.filter(book_status="inactive")
	msg="book Activated successfully"
	return render(request,'myapp/view_book.html',{'msg':msg,'books':books})

def search_book(request):
	search=request.POST["search"]
	try:
		user=User.objects.get(email=request.session['email'])
		if user.usertype=='seller':
			books=Book.objects.filter(book_status="active",book_category__contains=search,book_seller_email=request.session["email"])
			return render(request,'myapp/more_details.html',{'books':books})
		else:
			books=Book.objects.filter(book_status="active",book_category__contains=search)
			return render(request,'myapp/view_book.html',{'books':books})
	except Exception as e:
		print(e)


def profile(request):
	if request.method=="POST":
		first_name=request.POST['fname']
		last_name=request.POST['lname']
		mobile=request.POST['mobile']
		email=request.POST['email']
		user=User.objects.get(email=email)
		try:
			if request.FILES['user_image']:
				user_image=request.FILES['user_image']
		except:
			user_image=user.user_image
		user.user_image=user_image
		user.first_name=first_name
		user.last_name=last_name
		user.mobile=mobile
		user.save()
		request.session['fname']=user.first_name
		request.session['email']=user.email
		request.session['user_image']=user.user_image.url
		msg="Profile Updated successfully"
		return render(request,'myapp/profile.html',{'msg':msg,'user':user})
	else:
		user=User.objects.get(email=request.session['email'])
		try:
			if user.usertype=='user':
				data="user"
				return render(request,'myapp/profile.html',{'user':user,'data':data})
			else:
				return render(request,'myapp/profile.html',{'user':user})
		except:
			return render(request,'myapp/profile.html')
		
def user_book_details(request,pk):
	books=Book.objects.get(pk=pk)
	return render(request,'myapp/user_book_details.html',{'books':books})

def add_to_cart(request,pk):
	book=Book.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Cart.objects.create(book=book,user=user)
	mycart=Cart.objects.filter(user=user)
	request.session['cartcount']=len(mycart)

	w=Wishlist.objects.filter(pk=pk)
	w.delete()
	return render(request,'myapp/my_cart.html',{'mycart':mycart})

def my_cart(request):
	total_price=0
	user=User.objects.get(email=request.session['email'])
	mycart=Cart.objects.filter(user=user)
	request.session['cartcount']=len(mycart)
	for i in mycart:
		total_price=total_price+int(i.book.book_price)
		# a=i.book.book_price
		# print("price is",a)
	return render(request,'myapp/my_cart.html',{'mycart':mycart,'total_price':total_price})

def remove_cart(request,pk):
	mycart=Cart.objects.filter(pk=pk)
	mycart.delete()
	user=User.objects.get(email=request.session['email'])
	mycart=Cart.objects.filter(user=user)
	request.session['cartcount']=len(mycart)
	msg="Book's Removed from Cart successfully"
	return render(request,'myapp/my_cart.html',{'mycart':mycart,'msg':msg})

def move_to_wishlist(request,pk):
	cart=Cart.objects.get(pk=pk)
	book=Wishlist.objects.filter(book=cart.book,user=cart.user)
	if book:
		user=User.objects.get(email=request.session['email'])
		wish_list=Wishlist.objects.filter(user=user)
		msg="book is alrady available in wishlist"
		return render(request,'myapp/wish_list.html',{'wish_list':wish_list,'msg':msg})
	else:
		Wishlist.objects.create(book=cart.book,user=cart.user)
		cart.delete()
		user=User.objects.get(email=request.session['email'])
		wish_list=Wishlist.objects.filter(user=user)
		return render(request,'myapp/wish_list.html',{'wish_list':wish_list})


def wishlist(request):
	user=User.objects.get(email=request.session['email'])
	wish_list=Wishlist.objects.filter(user=user)
	return render(request,'myapp/wish_list.html',{'wish_list':wish_list})

def remove_wishlist(request,pk):
	wishlist=Wishlist.objects.filter(pk=pk)
	wishlist.delete()
	msg="Wised Book Deleted"
	return render(request,'myapp/wish_list.html',{'msg':msg,'wishlist':wishlist})

def move_to_cart(request,pk):
	wishlist=Wishlist.objects.get(pk=pk)
	cart=Cart.objects.filter(book=wishlist.book,user=wishlist.user)
	if cart:
		user=User.objects.get(email=request.session['email'])
		cart=Cart.objects.filter(user=user)
		msg="book is alrady available in Cart"
		return render(request,'myapp/my_cart.html',{'cart':cart,'msg':msg})
	else:
		Cart.objects.create(book=wishlist.book,user=wishlist.user)
		wishlist.delete()
		user=User.objects.get(email=request.session['email'])
		mycart=Cart.objects.filter(user=user)
		return render(request,'myapp/my_cart.html',{'mycart':mycart,'user':user})

def add_to_wishlist(request,pk):
	book=Book.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Wishlist.objects.create(book=book,user=user)
	wish_list=Wishlist.objects.filter(user=user)
	return render(request,'myapp/wish_list.html',{'wish_list':wish_list})







