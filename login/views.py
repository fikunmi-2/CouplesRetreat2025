from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def admin_login(request):
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect('view-registered')
		else:
			messages.success(request, ("Login error, Try again..."))
			return redirect('admin_login')

	else:
		return render(request, 'admin_login.html', {})

def admin_logout(request):
	logout(request)
	messages.success(request, ("You were logged out"))
	return redirect('home')