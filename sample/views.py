from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse,FileResponse
from . forms import userdataForm,UserLoginForm,DemoDateForm
from .models import User,UserLogin,DemoDate,Buses,Flights,Tours,VisitingData,TravelsData,SeasonsData,TouristPlaces,Distances,AdventureSports,BookedTicket
from django.db.models import Q
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.core.exceptions import ValidationError
import json
import re
import numpy as np
# from python_tsp.exact import solve_tsp_dynamic_programming

SEAT_FIELD_MAP = {
	1: 'one', 2: 'two', 3: 'three', 4: 'four',
	5: 'five', 6: 'six', 7: 'seven', 8: 'eight',
	9: 'nine', 10: 'ten', 11: 'elven', 12: 'twelve',
	13: 'thirtn', 14: 'fouthn', 15: 'fivethn', 16: 'sixthn',
}

BOOKED_SEAT_COLOR = "#1FACD4"

def parse_amount(value):
	amount = re.sub(r'[^0-9]', '', str(value))
	return int(amount) if amount else 0

def is_bus_seat_booked(bus, seat_id):
	field_name = SEAT_FIELD_MAP.get(seat_id)
	return bool(field_name and getattr(bus, field_name, '') == BOOKED_SEAT_COLOR)

def mark_bus_seat_booked(travels, seat_id):
	field_name = SEAT_FIELD_MAP.get(seat_id)
	if field_name:
		Buses.objects.filter(travels=travels).update(**{field_name: BOOKED_SEAT_COLOR})

def validate_email_format(email):
    """Validate email format using regex"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, str(email))

def authenticate_user(email, password):
    """
    Authenticate user with email and password
    Returns user object if valid, None otherwise
    """
    try:
        user = User.objects.get(email__iexact=email)
        # Check if password matches (supports both hashed and plain text for backward compatibility)
        if hasattr(user, 'password'):
            # Try checking with check_password first (for hashed passwords)
            try:
                if check_password(password, user.password):
                    return user
            except:
                pass
            # Fallback to plain text comparison (for backward compatibility)
            if user.password == password:
                return user
        return None
    except User.DoesNotExist:
        return None
    except User.MultipleObjectsReturned:
        # If multiple users found, try to authenticate with first matching
        users = User.objects.filter(email__iexact=email)
        for user in users:
            try:
                if check_password(password, user.password):
                    return user
            except:
                pass
            if user.password == password:
                return user
        return None

def project(request):
	return render(request,"home.html")

def home(request):
	if 'email' not in request.session:
		return HttpResponse("<h1 align='center'>Session Expired</h1>")
	else:
		email=request.session['email']
	return render(request,'userhome_updated.html',{'email':email})
 
def viewusers(request):
	users=User.objects.all()
	return render(request,'display.html',{'users':users})

def loginpage(request):
	form = UserLoginForm()
	error_message = None
	
	if request.method == 'POST':
		form = UserLoginForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data.get('email')
			password = form.cleaned_data.get('password')
			
			# Validate email format
			if not validate_email_format(email):
				error_message = "Please enter a valid email address"
				return render(request, "login.html", {'form': form, 'error': error_message})
			
			# Validate password is not empty
			if not password:
				error_message = "Please enter your password"
				return render(request, "login.html", {'form': form, 'error': error_message})
			
			# Try to authenticate user
			user = authenticate_user(email, password)
			
			if user:
				# Create session with user info
				request.session['email'] = user.email
				request.session['user_id'] = user.userid
				request.session['firstname'] = user.firstname
				
				if 'email' not in request.session:
					return HttpResponse("Session Expired")
				else:
					return render(request, 'userhome.html', {'email': user.email})
			else:
				# Check if email exists to provide more specific error
				email_exists = User.objects.filter(email__iexact=email).exists()
				if email_exists:
					error_message = "Invalid password. Please try again."
				else:
					error_message = "No account found with this email. Please sign up first."
				return render(request, "login.html", {'form': form, 'error': error_message})
		else:
			# Form is invalid, show errors
			error_message = "Please enter valid email and password"
			form = UserLoginForm()
	
	return render(request, 'login.html', {'form': form, 'error': error_message})
def viewseats(request,travels):
	if 'email' not in request.session:
		return HttpResponse("<h1 align='center'>Session Expired</h1>")
	else:
		bus=Buses.objects.filter(Q(travels__iexact=travels))
		if bus:
			return render(request,'viewseats.html',{'bus':bus})
		else:
			return HttpResponse("not found")
		#return render(request,'viewseats.html',{'bus':bus})

def profile(request):
	if 'email' not in request.session:
		return HttpResponse("<h1 align='center'>Session Expired</h1>")
	else:
		email=request.session['email']
		user=User.objects.filter(Q(email__iexact=email))
		# Get user's booked tickets
		booked_tickets = BookedTicket.objects.filter(Q(user_email__iexact=email)).order_by('-booked_at')
		return render(request,'profile.html',{'user':user, 'booked_tickets': booked_tickets})

def busfilter(request):
	if request.method=="POST":
		dep=request.POST["dep"]
		arr=request.POST["arr"]
		d=request.POST["d"]
		buses=Buses.objects.filter(Q(departure_palce__iexact=dep) & Q(arrival_place__iexact=arr) & Q(date__iexact=d)) 
		return render(request,'busfilter.html',{'buses':buses})
		
def flightfilter(request):
	if request.method=="POST":
		dep=request.POST["dep"]
		arr=request.POST["arr"]
		d=request.POST["d"]
		flights=Flights.objects.filter(Q(departure_palce__iexact=dep) & Q(arrival_place__iexact=arr) & Q(date__iexact=d)) 
		return render(request,'bookflightpage.html',{'flights':flights})


def dashboard(request):
	if 'email' not in request.session:
		return HttpResponse("<h1 align='center'>Session Expired</h1>")
	else:
		labels=[]
		data=[]

		queryset=VisitingData.objects.order_by('-population')[:9]
		for place in queryset:
			labels.append(place.place)
			data.append(place.population)
		if not labels:
			labels = ['Delhi', 'Mumbai', 'Hyderabad', 'Goa', 'Kerala']
			data = [45, 38, 31, 29, 24]

		# Get booking statistics
		email=request.session['email']
		total_bus_bookings = BookedTicket.objects.filter(user_email__iexact=email, ticket_type='Bus').count()
		total_flight_bookings = BookedTicket.objects.filter(user_email__iexact=email, ticket_type='Flight').count()
		total_adventure_bookings = BookedTicket.objects.filter(user_email__iexact=email, ticket_type='Adventure').count()
		total_bookings = total_bus_bookings + total_flight_bookings + total_adventure_bookings
		recent_bookings = BookedTicket.objects.filter(user_email__iexact=email).order_by('-booked_at')[:6]
		
		# Booking chart data
		booking_labels = ['Bus', 'Flight', 'Adventure']
		booking_data = [total_bus_bookings, total_flight_bookings, total_adventure_bookings]

		return render(request,'dashboard.html',{
			'labels':labels, 
			'data':data,
			'total_bookings': total_bookings,
			'total_bus_bookings': total_bus_bookings,
			'total_flight_bookings': total_flight_bookings,
			'total_adventure_bookings': total_adventure_bookings,
			'recent_bookings': recent_bookings,
			'booking_labels': booking_labels,
			'booking_data': booking_data,
			'chart_labels': json.dumps(labels),
			'chart_data': json.dumps(data),
			'booking_chart_labels': json.dumps(booking_labels),
			'booking_chart_data': json.dumps(booking_data),
		})

def seasonsdashboard(request):
	if 'email' not in request.session:
		return HttpResponse("<h1 align='center'>Session Expired</h1>")
	else:
		season_styles = {
			'Spring': {'icon': '🌸', 'tip': 'Hill stations, gardens, and easy sightseeing.', 'color': '#22c55e'},
			'Summer': {'icon': '☀️', 'tip': 'Beach breaks, hill escapes, and early morning tours.', 'color': '#f97316'},
			'Monsoon': {'icon': '🌧️', 'tip': 'Waterfalls, green valleys, and scenic drives.', 'color': '#06b6d4'},
			'Autumn': {'icon': '🍂', 'tip': 'Festival trips, heritage walks, and calm weather.', 'color': '#eab308'},
			'Winter': {'icon': '❄️', 'tip': 'Snow trips, desert stays, and city sightseeing.', 'color': '#60a5fa'},
		}
		fallback_seasons = [
			('Spring', 25),
			('Summer', 30),
			('Monsoon', 22),
			('Autumn', 35),
			('Winter', 40),
		]
		season_rows = list(SeasonsData.objects.order_by('-population').values_list('season', 'population')[:6])
		if not season_rows:
			season_rows = fallback_seasons

		labels = [season for season, population in season_rows]
		data = [population for season, population in season_rows]
		max_population = max(data) if data else 1
		total_population = sum(data)
		peak_season = labels[0] if labels else 'Winter'
		season_cards = []

		for season, population in season_rows:
			style = season_styles.get(season, {
				'icon': '✈️',
				'tip': 'A strong season for flexible travel plans.',
				'color': '#a855f7',
			})
			season_cards.append({
				'name': season,
				'population': population,
				'progress': round((population / max_population) * 100),
				'icon': style['icon'],
				'tip': style['tip'],
				'color': style['color'],
			})

	return render(request,'seasonsdashbord_fixed_updated.html',{
		'labels': labels,
		'data': data,
		'season_cards': season_cards,
		'total_population': total_population,
		'peak_season': peak_season,
		'chart_labels': json.dumps(labels),
		'chart_data': json.dumps(data),
	})

def paymentpage(request,travels,id):
		if 'email' not in request.session:
			return HttpResponse("<h1 align='center'>Session Expired</h1>")
		bus_obj = Buses.objects.filter(Q(travels__iexact=travels)).first()
		if not bus_obj:
			return HttpResponse("Bus not found")
		if is_bus_seat_booked(bus_obj, id):
			return HttpResponse("This seat is already booked. Please choose another seat.")
		email=request.session['email']
		request.session['travel']=travels
		request.session['seat_id']=id
		buses=Buses.objects.filter(Q(travels__iexact=travels))
		return render(request,'buspaymentpage.html',{'buses':buses,'email':email,'id':id})

def forgotpassword(request):
	return render(request,'forgotpassword.html')
def confirmpayment(request):
	travels=request.session.get('travel')
	if not travels:
		return redirect('bookbuspage')
	buses=Buses.objects.filter(Q(travels__iexact=travels))
	return render(request,'buscardpayment.html',{'v':buses,'travel':travels,})

def resetpassword(request):
	if request.method=="POST":
		email=request.POST["email"]
		opwd=request.POST["opwd"]
		npwd=request.POST["npwd"]
		
		# Hash the new password
		hashed_password = make_password(npwd)
		
		# Try to find user and verify old password
		try:
			user = User.objects.get(email__iexact=email)
			
			# Check if old password matches (supports both hashed and plain text)
			if check_password(opwd, user.password) or user.password == opwd:
				User.objects.filter(email__iexact=email).update(password=hashed_password)
				msg = "Password Updated Successfully! Please login with your new password."
				return render(request, 'forgotpassword.html', {'msg': msg})
			else:
				return render(request, 'forgotpassword.html', {'msg': 'Current password is incorrect.'})
		except User.DoesNotExist:
			return render(request, 'forgotpassword.html', {'msg': 'No account found with this email.'})
	else: 
		return HttpResponse("Not Successful")

"""def sam(request):
	if 'email' not in request.session:
		return HttpResponse("<h1 align='center'>Session Expired</h1>")
	else:
		m=request.session['email']
		del request.session['email']
		return HttpResponse("deleted")"""

"""def sam(request):
	distance_matrix = np.array([
    [0,  5, 4, 10],
    [5,  0, 8,  5],
    [4,  8, 0,  3],
    [10, 5, 3,  0]])
	permutation, distance = solve_tsp_dynamic_programming(distance_matrix)
	return HttpResponse(distance)"""
def sam(request):
	#env = Buses.objects.filter(travels="Morning Star Travels").values_list('fare', flat=True)[0]
	#env=int(env)+2;
	#matrix=[[1,env],[2,env]]
	if request.method != "POST":
		places=TouristPlaces.objects.all()
		return render(request,'createtour.html',{'places':places})

	d=request.POST.get("num", "").strip()
	bu=request.POST.get("budget", "").strip()
	if d!="" and d.isdigit():
		days=int(d)
	elif d!="":
		return HttpResponse("Please enter a valid number of days")
	if bu!="" and bu.isdigit():
		budget=int(bu)
	elif bu!="":
		return HttpResponse("Please enter a valid budget")
	dcount=0
	bcount=0
	places=TouristPlaces.objects.all()
	a=[]
	b=[]
	c=[]
	for i in places:
		name=i.place
		time=i.time
		cost=i.cost
		if bu!="":
			r=cost/time
		else:
			r=time/cost
		#print(name,cost)
		if name in request.POST:
			b.append([name,time,cost,r])
	
	if not b:
		return HttpResponse("Please select at least one tourist place")

	b.sort(key=lambda b:b[3])
	if d=="" and bu!="":
		print(b)
		rows=len(b)
		print("rows",rows)
		for j in range(rows):
			#print(j)
			if bcount+b[j][2]<=budget:
				print("inside")
				c.append([b[j][0],b[j][1],b[j][2],b[j][3]])
				bcount=bcount+b[j][2]
				print(bcount)
	elif d!="" and bu=="":
		print(b)
		rows=len(b)
		print("rows",rows)
		for j in range(rows):
			#print(j)
			if dcount+b[j][1]<=days:
				c.append([b[j][0],b[j][1],b[j][2],b[j][3]])
				dcount=dcount+b[j][1]
				print(dcount)
	elif d!="" and bu!="":
		print("both not equals case")
		print(b)
		rows=len(b)
		print("rows",rows)
		for j in range(rows):
			#print(j)
			if dcount+b[j][1]<=days and bcount+b[j][2]<=budget:
				c.append([b[j][0],b[j][1],b[j][2],b[j][3]])
				dcount=dcount+b[j][1]
				bcount=bcount+b[j][2]
				print("b",bcount)
				print("d",dcount)
	elif d=="" and bu=="":
		return HttpResponse("You Did not fill any field")

	print(dcount)
	print(bcount)
	request.session['plan']=c
	return render(request,'planpage.html',{'plan':c,'days':dcount,'budget':bcount,})			
	return HttpResponse(b)
		


def logout(request):
	request.session.pop('email', None)
	form = UserLoginForm()
	return render(request,'logout.html')

def signuppage(request):
	form = userdataForm()
	if request.method == 'POST':
		form = userdataForm(request.POST)
		if form.is_valid():
			# Check if email already exists
			email = form.cleaned_data.get('email')
			if User.objects.filter(email__iexact=email).exists():
				return render(request, 'signup.html', {
					'form': form,
					'msg': 'An account with this email already exists. Please login or use a different email.'
				})
			
			# Hash the password before saving
			raw_password = form.cleaned_data.get('password')
			hashed_password = make_password(raw_password)
			
			# Create user instance but don't save yet
			user = form.save(commit=False)
			user.password = hashed_password
			user.save()
			
			return render(request,'signup.html',{
				'msg': 'Account Created Successfully! Please login with your credentials.',
				'form': userdataForm()
			})
		else:
			form = userdataForm() 
	return render(request,'signup.html',{'form': form})

def tourspage(request):
	if 'email' not in request.session:
		return HttpResponse("<h1 align='center'>Session Expired</h1>")
	else:
		tours=Tours.objects.all()
		return render(request,'tourspage.html',{'tours':tours})

def booked(request):
	if 'email' not in request.session:
		return HttpResponse("<h1 align='center'>Session Expired</h1>")
	else:
		# Get the travel details from session
		travels = request.session.get('travel')
		seat_id = request.session.get('seat_id', 1)  # Default to seat 1 if not set
		
		if travels:
			# Get bus details
			buses = Buses.objects.filter(Q(travels__iexact=travels)).first()
			if buses:
				if is_bus_seat_booked(buses, seat_id):
					return HttpResponse("This bus seat was already booked. Please choose another seat.")
				# Map seat number
				seat_map = {1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 
				          7: '7', 8: '8', 9: '9', 10: '10', 11: '11', 12: '12',
				          13: '13', 14: '14', 15: '15', 16: '16'}
				seat_number = seat_map.get(seat_id, '1')
				mark_bus_seat_booked(travels, seat_id)
				if buses.seats_available > 0:
					Buses.objects.filter(Q(travels__iexact=travels)).update(seats_available=buses.seats_available - 1)
				
				# Create the booked ticket
				BookedTicket.objects.create(
					user_email=request.session['email'],
					ticket_type='Bus',
					travels_name=buses.travels,
					departure_place=buses.departure_palce,
					arrival_place=buses.arrival_place,
					departure_time=buses.departure_timeHours + ':' + buses.departure_timeMinutes,
					arrival_time=buses.arrival_timeHours + ':' + buses.arrival_timeMinutes,
					date=buses.date,
					fare=buses.fare,
					seat_number=seat_number
				)
		
		return render(request,'confirmpayment.html')

def tourinformation(request,location):
	if 'email' not in request.session:
		return HttpResponse("<h1 align='center'>Session Expired</h1>")
	else:
		tour=Tours.objects.filter(Q(location__iexact=location))
		return render(request,'tourinformation.html',{'tour':tour})
def tourconfirm(request):
	if 'email' not in request.session:
		return HttpResponse("<h1 align='center'>Session Expired</h1>")
	else:
		return render(request,'tourconfirm.html',)

def bookbuspage(request):
	if 'email' not in request.session:
		return HttpResponse("<h1 align='center'>Session Expired</h1>")
	else:
		buses=Buses.objects.all()
		return render(request,'bookbuspage.html',{'buses':buses})

def bookflightpage(request):
	if 'email' not in request.session:
		return HttpResponse("<h1 align='center'>Session Expired</h1>")
	else:
		flights=Flights.objects.all()
		return render(request,'bookflightpage.html',{'flights':flights})

def hospitalitypage(request):
	if 'email' not in request.session:
		return HttpResponse("<h1 align='center'>Session Expired</h1>")
	else:
		return render(request,'hospitalitypage.html')

def lr(request):
	return render(request,'linear_regression.html')
def demodate(request):
	form=DemoDateForm()
	return render(request,'demodatedisplay.html',{'form':form})
def flightticketdetails(request,flight):
	request.session['flight']=flight
	flight_obj=Flights.objects.filter(Q(flight__iexact=flight)).first()
	if not flight_obj:
		return HttpResponse("Flight not found")
	return render(request,'flightticket.html',{'flight': flight, 'flight_obj': flight_obj})
def flightpaymentpage(request):
	if 'email' not in request.session:
		return HttpResponse("<h1 align='center'>Session Expired</h1>")
	if request.method == "POST":
		f=request.POST.get('flight', '').strip()
		flight_class=request.POST.get('cl', '').strip()
		passengers_text=request.POST.get('nt', '1').strip()
		if not f or not flight_class:
			return HttpResponse("Please complete the flight class details")
		if not passengers_text.isdigit() or int(passengers_text) < 1:
			return HttpResponse("Please enter a valid passenger count")
		request.session['flight'] = f
		request.session['flight_class'] = flight_class
		request.session['flight_passengers'] = int(passengers_text)

	f=request.session.get('flight')
	if not f:
		return redirect('bookflightpage')
	flight_obj=Flights.objects.filter(Q(flight__iexact=f)).first()
	if not flight_obj:
		return HttpResponse("Flight not found")
	flight_class=request.session.get('flight_class', 'Economy')
	passengers=int(request.session.get('flight_passengers', 1))
	base_fare=parse_amount(flight_obj.fare)
	total_fare=base_fare * passengers
	return render(request,'flightpaymentpage.html',{
		'f':f,
		'flight': [flight_obj],
		'flight_obj': flight_obj,
		'flight_class': flight_class,
		'passengers': passengers,
		'total_fare': total_fare,
	})

def flightticketconfirm(request):
	if 'email' not in request.session:
		return HttpResponse("<h1 align='center'>Session Expired</h1>")
	if request.method != "POST":
		return redirect('bookflightpage')
	f=request.POST.get('flight') or request.session.get('flight')
	c=request.POST.get('cl') or request.session.get('flight_class')
	n=request.POST.get('nt') or request.session.get('flight_passengers', 1)
	if not f or not c or not n:
		return HttpResponse("Please complete the flight booking details")
	n=int(n)
	# Get flight details
	flight_obj = Flights.objects.filter(Q(flight__iexact=f)).first()
	if flight_obj:
		total_fare = parse_amount(flight_obj.fare) * n
		# Save the booked ticket
		BookedTicket.objects.create(
			user_email=request.session['email'],
			ticket_type='Flight',
			travels_name=flight_obj.flight,
			departure_place=flight_obj.departure_palce,
			arrival_place=flight_obj.arrival_place,
			departure_time=flight_obj.departure_timeHours + ':' + flight_obj.departure_timeMinutes,
			arrival_time=flight_obj.arrival_timeHours + ':' + flight_obj.arrival_timeMinutes,
			date=flight_obj.date,
			fare=str(total_fare),
			seat_number=f"{c} x{n}"
		)
	
	flight=Flights.objects.filter(Q(flight__iexact=f))
	email=request.session['email']
	return render(request,'flightticketconfirm.html',{
		'email':email,
		'flight': flight,
		'flight_name': f,
		'flight_class': c,
		'passengers': n,
		'total_fare': parse_amount(flight_obj.fare) * n if flight_obj else 0,
	})

def createtour(request):
	places=TouristPlaces.objects.all()
	return render(request,'createtour.html',{'places':places})

def shortpath(request):
	plan=request.session.get('plan')
	if not plan:
		return redirect('createtour')
	print(plan)
	rows=len(plan)
	print(rows)
	if rows < 2:
		return render(request,'shortpath.html',{'newplan':plan})
	d=0
	matrix=[]
	temp=[]
	all_distances_found=True
	for p1 in range(rows):
		#for p3 in range(p1+1):
				#temp.append(0)
		for p2 in range(rows):
			#if p2<p1+1:
				#temp.append(matrix[p1+1][0])
			#else:
			#print(p1,p2)
			if p1==p2:
				temp.append(0)
			else:
				fp=plan[p1][0]
				tp=plan[p2][0]
			#print(p1,p2)
				i = Distances.objects.filter((Q(fromplace__iexact=fp) & Q(toplace__iexact=tp)) |(Q(fromplace__iexact=tp) & Q(toplace__iexact=fp))   ).values('distance').first()
				if i:
					env = i['distance']
				else:
					env = 0
					all_distances_found=False
				temp.append(env)
		#print(temp)
		matrix.append(temp)
		temp=[]
	#d=Distances.objects.filter(fromplace=plan[0][0]).values('distance')[0]
	
	#for p in range(rows):
		#d=Distances.objects.filter(fromplace=plan[p][0]).values('distance')
		#print(d)
	if not all_distances_found:
		return render(request,'shortpath.html',{'newplan':plan})

	distance_matrix = np.array(matrix)
	try:
		permutation, distance = solve_tsp_dynamic_programming(distance_matrix)
	except NameError:
		permutation = range(rows)
	#return HttpResponse(distance)
	print(permutation)
	newplan=[]
	for t1 in range(rows):
		newplan.append(plan[permutation[t1]])
	return render(request,'shortpath.html',{'newplan':newplan})

def adventurepage(request):
	if 'email' not in request.session:
		return HttpResponse("<h1 align='center'>Session Expired</h1>")
	else:
		# Check if adventure sports data exists, if not add some sample data
		if not AdventureSports.objects.exists():
			adventure_activities = [
				AdventureSports(activity_name="River Rafting", location="Rishikesh", state="Uttarakhand", 
					description="Experience the thrill of white water rafting in the Ganges. Multiple rapids suitable for beginners to experts.", 
					price_range="₹1500-₹5000", difficulty="Moderate", best_season="September-June"),
				AdventureSports(activity_name="Bungee Jumping", location="Rishikesh", state="Uttarakhand", 
					description="India's highest bungee jump from a 83m platform. Free-fall experience like never before!", 
					price_range="₹3000-₹4500", difficulty="Expert", best_season="October-March"),
				AdventureSports(activity_name="Scuba Diving", location="Andaman Islands", state="Andaman & Nicobar", 
					description="Explore vibrant coral reefs and marine life in the crystal clear waters of Havelock Island.", 
					price_range="₹3500-₹8000", difficulty="Easy", best_season="October-April"),
				AdventureSports(activity_name="Snorkeling", location="Goa", state="Goa", 
					description="Discover underwater world with colorful fish and coral reefs along Goa's beautiful beaches.", 
					price_range="₹1500-₹3000", difficulty="Easy", best_season="October-May"),
				AdventureSports(activity_name="Paragliding", location="Bir Billing", state="Himachal Pradesh", 
					description="Soar like a bird with spectacular views of the Himalayas. India's paragliding capital!", 
					price_range="₹2000-₹4500", difficulty="Moderate", best_season="March-June, October-November"),
				AdventureSports(activity_name="Trekking to Everest Base Camp", location="Sikkim", state="Sikkim", 
					description="Challenging trek to the base of world's highest peak. A lifetime adventure experience.", 
					price_range="₹25000-₹50000", difficulty="Expert", best_season="March-May, September-December"),
				AdventureSports(activity_name="Kayaking", location="Daman", state="Daman & Diu", 
					description="Paddle through mangrove forests and scenic backwaters. Perfect for nature lovers.", 
					price_range="₹800-₹2000", difficulty="Easy", best_season="October-March"),
				AdventureSports(activity_name="Rock Climbing", location="Madhubani", state="Madhya Pradesh", 
					description="Natural rock formations for climbing enthusiasts. Various difficulty levels available.", 
					price_range="₹1000-₹2500", difficulty="Moderate", best_season="October-March"),
AdventureSports(activity_name="Zip Lining", location="Neemrana", state="Rajasthan", 
					description="Asia's longest zip line over 1km. Speed through the air with stunning Aravali views!",
					price_range="₹700-₹1500", difficulty="Easy", best_season="September-April"),
				AdventureSports(activity_name="Wildlife Safari", location="Jim Corbett", state="Uttarakhand", 
					description="Jeep safari to spot tigers, elephants and rare wildlife in India's oldest national park.", 
					price_range="₹2000-₹10000", difficulty="Easy", best_season="November-June"),
				AdventureSports(activity_name="Mountain Cycling", location="Spiti Valley", state="Himachal Pradesh", 
					description="High altitude cycling through treacherous mountain passes and villages.", 
					price_range="₹5000-₹15000", difficulty="Expert", best_season="June-September"),
				AdventureSports(activity_name="Camping", location="Leh-Ladakh", state="Jammu & Kashmir", 
					description="Night camping under stars in the Himalayas. Unforgettable experience!", 
					price_range="₹1500-₹5000", difficulty="Easy", best_season="May-September"),
				AdventureSports(activity_name="Skiing", location="Gulmarg", state="Jammu & Kashmir", 
					description="World-class skiing slopes in the snow capital of India. Premium powder snow!", 
					price_range="₹3000-₹15000", difficulty="Moderate", best_season="December-March"),
				AdventureSports(activity_name="Hot Air Ballooning", location="Jaipur", state="Rajasthan", 
					description="Float over Jaipur's beautiful forts and palaces in a hot air balloon.", 
					price_range="₹7500-₹12000", difficulty="Easy", best_season="October-March"),
				AdventureSports(activity_name="Water Rappelling", location="Kodaikanal", state="Tamil Nadu", 
					description="Abseiling down waterfalls. Refreshing adventure in the Western Ghats!", 
					price_range="₹1000-₹2000", difficulty="Moderate", best_season="June-December"),
				AdventureSports(activity_name=" Cliff Jumping", location="Lonavala", state="Maharashtra", 
					description="Leap off cliffs into natural water pools. exciting water adventure!", 
					price_range="₹800-₹1500", difficulty="Moderate", best_season="June-October"),
				AdventureSports(activity_name="Surfing", location="Kovalam", state="Kerala", 
					description="Catch your first wave in India's surf paradise. Lessons available for beginners.", 
					price_range="₹1500-₹4000", difficulty="Easy", best_season="October-March"),
				AdventureSports(activity_name="Ice Skating", location="Shimla", state="Himachal Pradesh", 
					description="唯一的自然溜冰场。冬季在印度体验溜冰乐趣!", 
					price_range="₹300-₹800", difficulty="Easy", best_season="December-February"),
			]
			for activity in adventure_activities:
				activity.save()
		
		adventures = AdventureSports.objects.all()
		return render(request, 'adventurespage.html', {'adventures': adventures})

def book_adventure(request, adventure_id):
	if 'email' not in request.session:
		return HttpResponse("<h1 align='center'>Session Expired</h1>")
	if request.method != "POST":
		return redirect('adventures')

	adventure = AdventureSports.objects.filter(id=adventure_id).first()
	if not adventure:
		return HttpResponse("Adventure package not found")

	BookedTicket.objects.create(
		user_email=request.session['email'],
		ticket_type='Adventure',
		travels_name=adventure.activity_name.strip(),
		departure_place=adventure.location,
		arrival_place=adventure.state,
		departure_time='Package',
		arrival_time='Booked',
		date='Flexible',
		fare=adventure.price_range,
		seat_number=adventure.difficulty
	)
	messages.success(request, f"{adventure.activity_name.strip()} package booked successfully.")
	return redirect('profile')
