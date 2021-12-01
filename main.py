from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo
from bson import ObjectId
from flask_cors import CORS
from flask import Flask, render_template, url_for, request, session, redirect,g,flash
from flask_pymongo import PyMongo



app = Flask(__name__)
CORS(app)

app.config['MONGO_DBNAME'] = 'loginauthen'
app.config['MONGO_URI'] = 'mongodb+srv://realbuy:pass123word@cluster0.la93s.mongodb.net/loginauthen?retryWrites=true&w=majority'
#db connection
mongo = PyMongo(app)

@app.route('/')
def home():
    #
    #     g.user=session['user']
    #     #return 'You are logged in as ' + session['username']
    session['user']=None
    return render_template('Home.html')

@app.route('/login', methods=['POST','GET'])
def login():
    return render_template('signin1.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    return render_template('Signup.html')

@app.route("/user_add", methods = ['POST'])
def user_add():
    msg=" "
    name = request.form.get("one")
    email = request.form.get("three")
    contact = request.form.get("two")
    password = request.form.get("four")
    question =request.form.get("five")
    account = mongo.db.account
    existing_user = account.find_one({'email': email})
    if existing_user is None:
        account.insert_one({'name': name, 'email' : email, 'contact' : contact, 'password': password, 'temp' : [],'question':question})
        error="you are successfuly logged in"
        # return  redirect(url_for('home'))
        message=flash('Profile creation is Successfull ,Please Signin to continue.')
        return render_template('signin1.html',message=message)
    else:
        error="User already exist please create account using new email id"
    return render_template('Home.html',error=error)

@app.route("/login_validation", methods = ['POST','GET'])
def login_validation():

        Username = request.form.get('username')
        Password = request.form.get('password')
        users = mongo.db.account
        if Username=='admin@gmail.com' and Password=='admin':
            return render_template('admin.html')

        login_user = users.find_one({'email': request.form['username']})
        if request.method=='POST':
            session.pop('user',None)
            if login_user:
                if Password == login_user['password']:
                    u=users.find_one(login_user)
                    session['user']=request.form['username']
                    session['name']=u['name']
                    session['contact']=u['contact']
                    session['password']=u['password']
                    return redirect(url_for('protected'))
        messages=flash('invalid Email-Id or Password ,Please enter valid Email and Password.')
        return render_template('signin1.html',messages=messages)

@app.route("/adminhome", methods = ['POST','GET'])
def admin_page():
    return render_template('admin.html')


@app.route('/protected',methods=['GET','POST'])
def protected():
    if g.user:
        #flash('You were successfully logged in')
        return render_template('aftersignin.html',user=session['user'],name=session['name'])
    return redirect(url_for('login'))

@app.before_request
def before_request():
    g.user=None
    if 'user' in session:
        g.user = session['user']

@app.route('/dropsession')
def dropsession():
    session.pop('user',None)
    return render_template('Home.html')

@app.route("/display",methods=['GET'])
def display():
    if g.user:
        account = mongo.db.account
        UserData = account.find_one({'email': session['user']})
        return render_template('manageaccount.html', user=UserData['email'], name=UserData['name'],
                               contact=UserData['contact'], password=UserData['password'],question=UserData['question'])

@app.route("/update",methods=['GET','POST'])
def update():
    print(request.args,session['user'])
    name = request.args.get("one")
    Username = request.args.get("three")
    contact = request.args.get("two")
    password = request.args.get("four")
    question=request.args.get("five")

    user_details=dict()
    if name:
        user_details['name']=name
    if contact:
        user_details['contact']=contact
    if password:
        user_details['password']=password
    if question:
        user_details['question']=question

    print(user_details)
    account = mongo.db.account
    print(session['user'])
    account.update_one({'email': session['user']}, {"$set": user_details})
    messages=flash("update successful")
    return redirect(url_for('display'))
    #return render_template('Home.html',user=session['user'])
    #return login_validation()
    #return render_template('aftersignin.html',user=session['user'])
    #return render_template('aftersigin.html',name=user_details['name'],contact=user_details['contact'],
                       #  password=user_details['password'],user=user_details['user'])



    # if existing_user is None:
    #     account.insert({'name': name, 'email': email, 'contact': contact, 'password': password})
    #     return render_template('Home.html')
    # return "User already exist"

# @app.route("/search",methods=['POST','GET'])
# def search():
#     products = mongo.db.products
#
#     product = request.args.get("text")
#     print(request.args)
#     productdetails=products.find_one({'productname':product})
#     print(productdetails)
#     return productdetails
# #@app.route("/addproducts",methods=['POST','GET'])
# #def addproducts():

@app.route('/forgotpassword1',methods=['GET','POST'])
def forgotpassword1():
    username = request.form.get("username")
    question = request.form.get("five")
    newpassword = request.form.get("four")
    users = mongo.db.account
    print(username,question,newpassword)
    login_user = users.find_one({'email': request.form['username']})
    print(login_user)
    if login_user['question']==question:
        user_details = dict()

        if newpassword:
            user_details['password'] = newpassword
            users.update_one({'email': username}, {"$set": user_details})

        return render_template("Home.html",)

@app.route("/<prices>/<prices1>", methods=['POST', 'GET'])
def index1(prices, prices1):
    print(prices,prices1)
    #print(session['user'])
    #if session['user']:
    if request.method == 'POST':
        searchString = request.form['content'].replace(" ","")  # obtaining the search string entered in the form
        print(searchString)
        try:
            dbConn = pymongo.MongoClient('mongodb+srv://realbuy:pass123word@cluster0.la93s.mongodb.net/products?retryWrites=true&w=majority')
            db = dbConn['products']  # connecting to the database called pricecrawlerDB
            db=mongo.db
            # searching the collection with the name same as the keyword
            products=db.products.find_one({'Product':searchString})
            if products:  # if there is a collection with searched keyword and it has records in it
                prices = db.products.find({'Product':searchString})
                print(prices)
                print(session['user'])
                if session['user'] is not None:
                    print('this')
                    return render_template('results2.html',prices=prices,user=session['user'])
                    #print('this')# show the results to user
                else:
                    print('that')
                    #flash("to add to cart please sign in ")
                    return render_template('results2.html',prices=prices)
            else:
                flipkart_url = "https://www.flipkart.com/search?q=" + searchString  # preparing the URL to search the product on flipkart
                paytm_url = "https://paytmmall.com/shop/search?q=" + searchString
                print(paytm_url)
                uClient = uReq(flipkart_url)  # requesting the webpage from the internet
                uClient2 = uReq(paytm_url)  #
                paytmPage = uClient2.read()

                flipkartPage = uClient.read()  # reading the webpage
                uClient.close()  # closing the connection to the web server
                uClient2.close()
                flipkart_html = bs(flipkartPage, "html.parser")  # parsing the webpage as HTML
                paytm_html = bs(paytmPage, "html.parser")  #
                bigboxes = flipkart_html.findAll("div", {
                    "class": "_13oc-S"})  # searching for appropriate tag to redirect to the product link
                bigboxes1 = paytm_html.findAll("div", {"class": "_3WhJ"})

                #                priceboxes = bigboxes.div.div.a.div.div.div.find_all('div', {'class': "_30jeq3 _1_WHN1"})
                table = db['products']  # creating a collection with the same name as search string. Tables and Collections are analogous.
                prices = []
                prices1 = []

                pricebox = bigboxes[0]
                pricebox1 = bigboxes1[0]

                #            for pricebox in bigboxes:
                try:
                    #                        pricebox.select('div', {'class' : "_30jeq3 _1_WHN1"})
                    ProductSpec = pricebox.div.a.find_all('div', {'class': "_4rR01T"})[0].text
                    ProductSpec1 = pricebox1.a.find_all('div', {'class': "_2PhD"})[0].text

                #                   ProductSpec1 =

                except:
                    ProductSpec = 'Product Not Available'
                    ProductSpec1 = 'Product Not Available'

                try:
                    ProductPrice = pricebox.div.a.find_all('div', {'class': "_30jeq3 _1_WHN1"})[0].text
                    ProductPrice1 = pricebox1.a.find_all('div', {'class': "_1kMS"})[0].text

                except:
                    ProductPrice = 'We will add this product category soon'
                    ProductPrice1 = 'We will add this product category soon'

                #                    try:
                #                        DiscountPerc = pricebox.div.find_all('div', {'class': "_3Ay6Sb"}).text

                #                    except:
                #                        DiscountPerc = 'No Discount'

                #                    mydict = {"Product": searchString, "AfterDiscount": AfterDiscount, "BeforeDiscount": BeforeDiscount, "PercentOff": DiscountPerc} # saving that detail to a dictionary
                mydict = {"Product": searchString, "ProductSpec": ProductSpec, "ProductPrice": ProductPrice, "Seller" : 'Flipkart' }
                mydict1 = {"Product": searchString, "ProductSpec": ProductSpec1, "ProductPrice": ProductPrice1, "Seller" : 'Paytm Mall'}

                x = table.insert_one(mydict)  # insertig the dictionary containing the rview comments to the collection
                x = table.insert_one(mydict1)

                prices.append(mydict)
                prices1.append(mydict1)
                products = list(table.find())
                print(products)
                return render_template('result1.html', prices=prices, prices1=prices1, products=products)
        except:
            return 'Sorry This Product is Not available. We will get this product very soon'
    else:
        return render_template('Home.html')

@app.route("/addtocart", methods=['POST', 'GET'])
def addtocart():

    account = mongo.db.account
    print(session['user'])
    name = request.args.get("id")
    print(name)
    temp = dict()

    if id:
        temp['id'] = name
    # temp = []
    # temp.append(ids)

    print(account.update_one({'email': session['user']}, {"$push": {'temp': name}}))

    # account.update_one({'email': session['user']}, {"$set": {'temp': ids}})

    #return name
    return render_template("aftersignin.html",user=session['user'])
    #return redirect(url_for('index1'),)

@app.route("/viewcart", methods=['POST', 'GET'])
def viewcart():
    account = mongo.db.account
    cart=mongo.db.products
    login_user = account.find_one({'email': session['user']})
    d = []

    list1=login_user['temp']
    print(len(list1))
    print(list1)
    if len(list1)!=0:
        objectid=[]

        x=dict()
        for i in list1:

            #objectid.append(ObjectId(i))
            x= cart.find_one({"_id": ObjectId(i)})
            #d.append(list(x)[0])
            print(x)
            if x:
                d.append(x)
    if not d :
        messages="cart empty please add items"
        return render_template("emptycart.html")
    print(d)
    return render_template("viewcart.html",lt=d)
@app.route("/usersdisplay",methods=['POST','GET'])
def usersdisplay():
    usersinfo = mongo.db.account
    userdata=usersinfo.find()
    print(userdata)
    y=dict()
    d=[]
    for row in userdata:
        print(row)
        d.append(row)

    print(d)
    return render_template('usertable.html',userdata=d)

@app.route("/feedbackdisplay",methods=['POST','GET'])
def feedbackdisplay():
    feedbackdata = mongo.db.feedbacks
    userfeedback=feedbackdata.find()
    print(userfeedback)
    y=dict()
    d=[]
    for row in userfeedback:
        print(row)
        d.append(row)


    return render_template('feedbacks.html',userdata=d)


@app.route('/feedback',methods=['GET','POST'])
def feedback():
    return render_template('feedback.html')

@app.route('/save',methods=['GET','POST'])
def save():
    feedback=request.form.get("description")

    print(feedback)
    print(session['user'])
    custfeedback = mongo.db.feedbacks
    custfeedback.insert(
        {'email': session['user'], 'feedback': feedback })
    messages=flash("Thanks for your message Real buy is working on it")
    return render_template("feedback.html")

@app.route('/updatecustomerdetails',methods=['GET','POST'])
def updatecustomerdetails():
    return render_template('updatecustomerdetails.html')

@app.route('/updatecustomerdetails1',methods=['GET','POST'])
def updatecustomerdetails1():
    email= request.form.get("three")
    name= request.form.get("one")
    contact=request.form.get("two")
    account=mongo.db.account
    print(email)
    user_details = dict()
    if name:
        user_details['name'] = name
    if contact:
        user_details['contact'] = contact


    print(user_details)

    #print(session['user'])
    account.update_one({'email': email}, {"$set": user_details})
    return "update successful"

@app.route('/forgotpassword',methods=['GET','POST'])
def forgotpassword():
    return render_template("resetpage.html")

@app.route('/deletecart',methods=['GET','POST'])
def deletecart():
    account = mongo.db.account
    print(session['user'])
    name = request.args.get("id")
    print(name)
    temp = dict()
    if id:
        temp['id'] = name
    # temp = []
    # temp.append(ids)
    print(account.update_one({'email': session['user']}, {"$pull": {'temp': name}}))
    # account.update_one({'email': session['user']}, {"$set": {'temp': ids}})
    messages=flash('Item Deleted from Cart Successfully')
   # return render_template('viewcart.html',user=session['user'],messages=messages)
    return redirect(url_for('viewcart'))

app.secret_key = 'mysecret'

if __name__ == '__main__':

    app.run(debug=True)