from django.shortcuts import render, redirect
from .models import Registered
from .forms import RegisterForm 
from django.http import HttpResponseRedirect, FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch 
from reportlab.lib.pagesizes import letter



def home(request):
	if request.method == "POST":
		lastname = request.POST['lastname']
		firstname = request.POST['firstname']
		records = Registered.objects.filter(s_name__iexact=lastname)
		success = False
		firstname_m = ''
		firstname_f = ''
		s_name = ''
		s_id = ''
		if records:
			for record in records:
				if firstname == record.f_name_m or firstname == record.f_name_f:
					firstname_m = record.f_name_m
					firstname_f = record.f_name_f
					s_name = record.s_name
					s_id = record.id
					success = True

				else:
					pass

		return render(request, 'home.html', {'lastname': lastname, 'records': records, 'firstname': firstname, 
			'success': success, 'f_name_m': firstname_m, 'f_name_f': firstname_f, 's_name': s_name, 'id': s_id})

	else:
		return render(request, 'home.html', {})
	

def registered(request):
	lastname = ''	
	if request.method == "POST":
		lastname = request.POST['searched']
		registered_list = Registered.objects.filter(s_name__contains=lastname)
		return render(request, 'viewregistered.html', {'registered_list': registered_list, 'search': lastname})
	else:
		registered_list = Registered.objects.all()
		return render(request, 'viewregistered.html', {'registered_list': registered_list, 'search': lastname})

def register(request):
	submitted = False
	if request.method == 'POST':
		form = RegisterForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect('/register?submitted=True')

	else:
		form = RegisterForm
		if 'submitted' in request.GET:
			submitted = True
		return render(request, 'register.html', {'form': form, 'submitted': submitted})

def show_registee(request, registered_id):
	registered = Registered.objects.get(pk=registered_id)
	registered.present = 'Yes'
	registered.save()
	img = f"{registered.id}.png"
	if request.method == 'POST':
		return redirect('view-registered')
	return render(request, 'show_registee.html', {'registered': registered, 'img': img})

def search_record(request):
	if request.method == "POST":
		lastname = request.POST['lastname']
		firstname = request.POST['firstname']
		records = Registered.objects.filter(s_name__iexact=lastname)
		success = False
		firstname_m = ''
		firstname_f = ''
		s_name = ''
		s_id = ''
		if records:
			for record in records:
				if firstname == record.f_name_m or firstname == record.f_name_f:
					firstname_m = record.f_name_m
					firstname_f = record.f_name_f
					s_name = record.s_name
					s_id = record.id
					success = True
				else:
					pass

		return render(request, 'search_record.html', {'lastname': lastname, 'records': records, 'firstname': firstname, 
			'success': success, 'f_name_m': firstname_m, 'f_name_f': firstname_f, 's_name': s_name, 'id': s_id})

	else:
		return render(request, 'search_record.html', {})

def update_registee(request, registered_id):
	registered = Registered.objects.get(pk=registered_id)
	registered_list = Registered.objects.all()
	form = RegisterForm(request.POST or None, instance=registered)
	if form.is_valid():
		form.save()
		return redirect('view-registered')
	return render(request, 'update_registee.html', {'registered': registered, 'form': form})

def delete_registee(request, registered_id):
	registered = Registered.objects.get(pk=registered_id)
	registered.delete()
	return redirect('view-registered')

def pdf_registee(request, registered_id):
	import qrcode
	from PIL import Image
	image = 'img/back.png'
	registered = Registered.objects.get(pk=registered_id)
	buf = io.BytesIO()
	c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
	c.drawImage(image, 0,-5, width=None,height=None, mask=None)

	# Link for website
	input_data = f"http://127.0.0.1:8000/show_registee/{registered.id}"
	#Creating an instance of qrcode
	qr = qrcode.QRCode(
	        version=1,
	        box_size=10,
	        border=5)
	qr.add_data(input_data)
	qr.make(fit=True)
	img = qr.make_image(fill='black', back_color='white')
	img.save(f'{registered.id}.png')

	imag = f'{registered.id}.png'
	c.drawImage(imag, 185,140, width=30,height=30, mask=None)
	c.drawImage(imag, 185,320, width=30,height=30, mask=None)

	registered_list = Registered.objects.all()
	lines = []
 	
	c.setFont("Times-Bold", 12)
	c.drawString(73, 120,  (f'{registered.s_name}').lower())
	c.drawString(73, 135, (f'{registered.f_name_m}').upper())

	c.setFillColorRGB(255, 0, 0)
	c.drawString(220, 160, f'{registered.id}')

	c.setFillColorRGB(0, 0, 0)
	c.drawString(73, 300,  (f'{registered.s_name}').lower())
	c.drawString(73, 315, (f'{registered.f_name_f}').upper())

	c.setFillColorRGB(255, 0, 0)
	c.drawString(220, 340, f'{registered.id}')

	c.showPage()
	c.save()
	buf.seek(0)

	return FileResponse(buf, as_attachment=True, filename=f'{registered.s_name}.pdf')
