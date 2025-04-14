import datetime
from bson import ObjectId
from flask import Flask, request,Response, render_template, session, redirect
import pymongo
my_collections = pymongo.MongoClient("mongodb://localhost:27017/")
my_db = my_collections['BusTicket']
providers_col = my_db['serviceProvider']
bustypes_col = my_db['bustypes']
bus_col = my_db['bus']
reservations_col = my_db['reservations']
payments_col = my_db['payments']
customer_col = my_db['customer']

app = Flask(__name__)
app.secret_key = "BusTicket"

@app.route("/")
def index():
    return render_template("userLogin.html")


@app.route("/adminLogin")
def adminLogin():
    return render_template("adminLogin.html")


@app.route("/adminLogin1", methods=['post'])
def adminLogin1():
    username = request.form.get('username')
    password = request.form.get('password')
    print(username,password)
    if username == 'admin' and password == 'admin':
        session['role'] = 'Admin'
        return redirect("/adminHome")
    else:
        return render_template("adminLogin.html", message="Invalid Login Details")


@app.route("/adminHome")
def adminHome():
    return render_template("adminHome.html")


@app.route("/userLogin")
def userLogin():
    print(datetime.datetime.now()+datetime.timedelta(minutes=15))
    return render_template("/userLogin.html")


@app.route("/userLogin1", methods=['post'])
def userLogin1():
    email = request.form.get('email')
    password = request.form.get('password')
    print(email,password)
    query = {"email": email, "password": password}
    count = customer_col.count_documents(query)
    if count > 0:
        user = customer_col.find_one(query)
        session['user_id'] = str(user['_id'])
        session['role'] = 'User'
        return redirect("/userHome")
    else:
        return render_template("userLogin.html", message="Invalid Login Details",color="red")


@app.route("/userHome")
def userHome():
    user_id = session['user_id']
    query = {"_id": ObjectId(user_id)}
    user=customer_col.find_one(query)
    return render_template("userHome.html",user=user )


@app.route("/userRegister")
def userRegister():
    return render_template("/userRegister.html")


@app.route("/userRegister1", methods=['post'])
def userRegister1():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    conf_password = request.form.get('conf_password')
    address = request.form.get('address')
    query = {"$or": [{"email": email}, {"phone": phone}]}
    count = customer_col.count_documents(query)
    if count > 0:
        return render_template("userRegister.html", message="Duplicate Details!!!.....", color="red")
    if conf_password != password:
        return render_template("userRegister.html", message="Password Not Matched!!!.....", color="red")
    query = {"name": name, "email": email, "phone": phone, "password": password,  "address": address}
    result = customer_col.insert_one(query)
    return render_template("userLogin.html", message="User Registered successfully", color="green")

7
@app.route("/addProviders")
def addProviders():
    return render_template("addProviders.html")


@app.route("/addProviders1", methods=['post'])
def addProviders1():
    Providers_name = request.form.get('Providers_name')
    phone_number = request.form.get('phone_number')
    address = request.form.get('address')
    # country = request.form.get('country')
    query = {"name": Providers_name,"Phone Number":phone_number,"Address":address}
    providers_col.insert_one(query)
    return render_template("msg.html", message="Providers Added Successfully", color="bg-success text-white")


@app.route("/viewProviders")
def viewProviders():
    providerslist = providers_col.find()
    return render_template("viewProviders.html",providerslist=providerslist)

@app.route("/Buses")
def Buses():
    l=[]
    for i in bus_col.find():
        l.append(i['destination'])
        l.append(i['source'])
    l=list(set(l))
    print(l)
    return render_template("busSearch.html",region=l)

@app.route("/busSearch", methods=['post'])
def busSearch():
    date = request.form.get('date')
    source = request.form.get('source')
    destination = request.form.get('destination')
    query={"destination":destination,"source":source}
    data=bus_col.find(query)
    buses=[]
    j=1
    for i in data:
        dd=str(i['departure_date'])[:10]
        print(dd)
        if dd==date and int(i["max_seats"])>0:
            i["Id"]=j
            buses.append(i)
            j+=1
    return render_template("buslist.html",buses=buses)

@app.route("/addBuses")
def addBuses():
    providers_id = request.args.get('providers_id')
    return render_template("addBus.html", providers_id=providers_id)


@app.route("/addBuses1", methods=['post'])
def addBuses1():
    driver = request.form.get('driver')
    provider_id = request.form.get('providers_id')
    max_seats=request.form.get('no_of_ticket')
    price_per_ticket = request.form.get('price_per_ticket')
    destination=request.form.get('destination')
    source=request.form.get('source')
    departure_date=request.form.get('departure_date')
    arrival_date=request.form.get('arrival_date')
    departure_date = departure_date.replace('T', ' ')
    arrival_date = arrival_date.replace('T', ' ')
    departure_date=datetime.datetime.strptime(departure_date,"%Y-%m-%d %H:%M")
    arrival_date=datetime.datetime.strptime(arrival_date,"%Y-%m-%d %H:%M")
    query = {"provider_id": ObjectId(provider_id),"DriverName":driver, "price_per_ticket": price_per_ticket,"max_seats":max_seats,"departure_date":departure_date,"arrival_date":arrival_date,"source":source,"destination":destination}
    bus_col.insert_one(query)
    return render_template("msg.html", message="Bus Added Successfully", color="bg-success text-white")


@app.route("/viewBuses")
def viewBuses():
    providers_id = request.args.get('providers_id')
    query = {"provider_id": ObjectId(providers_id)}
    Buses = bus_col.find(query)
    count=bus_col.count_documents(query)
    print(Buses)
    print(count)
    print(session['role'])
    if count==0:
        return render_template("viewBus.html", count=count)
    elif session['role'] == 'User':
        return render_template("viewBus.html", Buses=Buses, get_bus_id=get_bus_id)
    else:
        return render_template("viewtickets.html", Buses=Buses, get_bus_id=get_bus_id)

    

def get_bus_id(bus_id):
    query = {'_id': bus_id}
    providers = providers_col.find_one(query)
    return providers

def get_buses(bus_id):
    query = {'_id': ObjectId(bus_id)}
    print("ijnbvfghjkjhgf")
    buses = bus_col.find_one(query)
    print(buses)
    return buses

@app.route("/BusBooking")
def slotBooking():
    bus_id = request.args.get('bus_id')
    buslist=[]
    buses = bus_col.find()
    j=1
    for i in buses:
        i["Id"]=j
        buslist.append(j)
        j+=1
    print(buslist)
    return render_template("buslist.html", bus_id=bus_id, buses=buslist, int=int)


@app.route("/BusBooking1", methods=['post'])
def BusBooking1():
    bus_id = request.form.get('bus_id')
    # n =int(request.form.get("ticket"))
    print(bus_id)
    bus=bus_col.find_one({'_id':ObjectId(bus_id)})
    # buslist = []
    # # for i in bus:
    # bus["arrival_date"] = bus["arrival_date"].replace("T"," ")
    # bus["departure_date"] = bus["departure_date"].replace("T"," ")
    # print(bus)
    # bus["arrival_date"] = datetime.datetime.strptime(str(bus["arrival_date"])+":00", '%Y-%m-%d %H:%M:%S')
    # bus["departure_date"] = datetime.datetime.strptime(str(bus["departure_date"])+":00", '%Y-%m-%d %H:%M:%S')
        # buslist.append(i)
    return render_template("ticketdetails.html",bus=bus, bus_id=bus_id)

@app.route("/BusBooking2", methods=['post'])
def BusBooking2():
    n=request.form.get("n")
    bus_id=request.form.get("bus_id")
    userid=session['user_id'] 
    name=request.form.get("name")
    phone_number=request.form.get("phno")
    email=request.form.get("email")
    passengers=request.form.get("passengers")
    avlseats=request.form.get("avlseats")
    age=request.form.get("age")
    gender=request.form.get("gender")
    if int(avlseats)<int(passengers):
        bus_id = request.form.get('bus_id')
        # n =int(request.form.get("ticket"))
        print(bus_id)
        bus=bus_col.find_one({'_id':ObjectId(bus_id)})
        return render_template("ticketdetails.html",bus=bus, bus_id=bus_id,message="Passengers Greater than available seats")
    passenger=[]
    cost=int(eval(str(bus_col.find_one({"_id":ObjectId(bus_id)})))['price_per_ticket'])
    price=cost*int(passengers)
    print(price)
    print(passenger)
    query={"bus_id":bus_id,"user_id":userid,"name":name,"email":email,"phone_number":phone_number,"total_price":price,"passengers":passengers,"DOB":age,"gender":gender,"status":"Booked"}
    id=reservations_col.insert_one(query).inserted_id
    payments_col.insert_one({"reservation_id":id,"status":"booked","total_price":price})
    aval_seats=int(bus_col.find_one({"_id":ObjectId(bus_id)})['max_seats'])-int(passengers)
    bus_col.update_one({"_id":ObjectId(bus_id)},{"$set":{"max_seats":aval_seats}})
    return render_template("nextPayAmount.html",price=price)


@app.route("/paymentdone", methods=['post'])
def paymentdone():
    return render_template("msg.html", message="Booked Successfully", color="bg-success text-white")

@app.route("/viewBookings")
def viewBookings():
    print("------------------------------------")
    passengers=reservations_col.find({"user_id":session['user_id']})
    print(session['user_id'])
    psng=[]
    for i in passengers:
        if i['user_id']==session['user_id']:
            psng.append(i)
    print(psng)
    return render_template("viewBookings.html",psng=psng,get_buses=get_buses)


@app.route("/cancel")
def cancel():
    id = request.args.get("id")
    reserv = reservations_col.find_one({"_id":ObjectId(id)})
    bus = bus_col.find_one({"_id":ObjectId(reserv["bus_id"])})
    seats = bus["max_seats"]+int(reserv["passengers"])
    reservations_col.update_one({"_id":ObjectId(id)},{"$set":{"status":"Cancelled and Money Redunded"}})
    bus_col.update_one({"_id":ObjectId(reserv["bus_id"])},{"$set":{"max_seats":seats}})
    passengers=reservations_col.find({"user_id":session['user_id']})
    print(session['user_id'])
    psng=[]
    for i in passengers:
        if i['user_id']==session['user_id']:
            psng.append(i)
    print(psng)
    return render_template("viewBookings.html",psng=psng,get_buses=get_buses)


@app.route("/logout")
def logout():
    session.clear()
    return render_template("index.html")


if __name__=="__main__":
    app.run(debug=True,port=5030)
