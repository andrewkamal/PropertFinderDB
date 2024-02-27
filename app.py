from flask import Flask, render_template, request, flash
import mysql.connector
import MySQLdb

app = Flask(__name__)
app.secret_key = "D(G+KbPeShVmYq3"

mydb = MySQLdb.connect(host = "db4free.net",
                    port = 3306,
                    user="propertyandrew", 
                    passwd = "************",
                    database = "propertyandrew"
                    )
print("Connected to:", mydb.get_server_info())
#print all the tables in the database
# cur = mydb.cursor()
# val = "Pro-Homes"
# resultValue = cur.execute("SELECT AVG(RatingNum) as AggregatedRating FROM agentuser a inner join brokercompany b on a.AgentBroker = b.BName WHERE b.BName LIKE %s", (val,))
# inquiryDetails = cur.fetchall()
# print(inquiryDetails[0][0])

cursor = mydb.cursor()
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
print(tables)
#Home route
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('home.html')

#Register route
@app.route('/register', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        # Fetch form data
        userInfo = request.form
        email = userInfo['email']
        name = userInfo['name']
        gender = userInfo['gender']
        birthdate = userInfo['birthdate']
        try:
            cur = mydb.cursor()
            cur.execute("INSERT INTO users(Email, Username, Gender, birthdate) VALUES(%s, %s, %s, %s)",(email, name, gender, birthdate))
            mydb.commit()
            cur.close()
            return render_template('userAdded.html', status = "Welcome Aboard!") 
        except MySQLdb.OperationalError as errcode:    
            return render_template('failGen.html', status = "Connection Error! Please try again")
        except MySQLdb.IntegrityError as errcode:
                # User registered already
                errormsg = errcode.args[1]
                if "Duplicate entry" in errormsg:
                    return render_template('failed.html')
    return render_template('register.html')

#add Review route
@app.route('/addReview', methods=['GET', 'POST'])
def Review():
    if request.method == 'POST':
        # Fetch form data
        reviewInfo = request.form
        AgentPhone = reviewInfo['AgentPhone']
        AgentFName = reviewInfo['AgentFName']
        AgentBroker = reviewInfo['AgentBroker']
        UserEmail = reviewInfo['UserEmail']
        RatingNum = reviewInfo['RatingNum']
        RatingText = reviewInfo['RatingText']
        try:
            cur = mydb.cursor()
            cur.execute("INSERT INTO agentuser(AgentPhone, AgentFName, AgentBroker, UserEmail, RatingNum, RatingText) VALUES(%s, %s, %s, %s, %s, %s)",(AgentPhone, AgentFName, AgentBroker, UserEmail, RatingNum, RatingText))
            mydb.commit()
            cur.close()
            return render_template('reviewAdded.html', status = "Review Submitted!")
        except MySQLdb.OperationalError as errcode:    
            exceptionMsg = errcode.args[1]
            return render_template('failGen.html', status = "Lost connection to mysql server during result retreival, please try again")
        except MySQLdb.IntegrityError as errcode:
                errormsg = errcode.args[1]
                if "Duplicate entry" in errormsg:
                    return render_template('failed.html')
                
                if "foreign key" in errormsg: 
                    if "AgentPhone" in errormsg:
                        return render_template('failGen.html', status = "Phone number does not exist in database")
                    elif "UserEmail" in errormsg:
                        return render_template('failGen.html', status = "Email does not exist in database")
                    elif "AgentFName" in errormsg:
                        return render_template('failGen.html', status = "First name does not exist in database")
                else:
                    return render_template('failGen.html', status = "Failed, error happened")
    return render_template('addReview.html')

#add View Agent Review route
@app.route('/viewReview')
def selectAgent():
    return render_template('selectAgent.html')

@app.route('/viewReview', methods=['GET', 'POST'])
def selectedAgents():
    if request.method == 'POST':
        # Fetch form data
        agentInfo = request.form
        AgentPhone = agentInfo['AgentPhone']
        AgentFName = agentInfo['AgentFName']
        AgentBroker = agentInfo['AgentBroker']
        try:
            cur = mydb.cursor()
            resultValue = cur.execute("SELECT AgentPhone, AgentFName, AgentBroker, UserEmail, RatingNum, RatingText FROM agentuser WHERE AgentPhone LIKE %s and AgentFName LIKE %s and AgentBroker LIKE %s", [AgentPhone, AgentFName, AgentBroker] )
            if resultValue > 0:
                inquiryDetails = cur.fetchall()
                return render_template('selectedAgentRev.html',inquiryDetails=inquiryDetails)
            else:
                return render_template('failGen.html', status = "There are no reviews for this Agent")
        except MySQLdb.OperationalError as errcode:    
            exceptionMsg = errcode.args[1]
            return render_template('failGen.html', status = "Connection Error! Please try again")
    return render_template('selectedAgentRev.html',inquiryDetails=inquiryDetails)

#add View Brokerage Rating route
@app.route('/brokerageRate')
def selectBokerage():
    return render_template('selectBrokerage.html')

@app.route('/brokerageRate', methods=['GET', 'POST'])
def selectedBrokerage():
    if request.method == 'POST':
        # Fetch form data
        agentInfo = request.form
        BName = agentInfo['BName']
        try:
            cur = mydb.cursor()
            resultValue = cur.execute("SELECT AVG(RatingNum) as AggregatedRating FROM agentuser a inner join brokercompany b on a.AgentBroker = b.BName WHERE b.BName LIKE %s", [BName] )
            
            if resultValue > 0:
                inquiryDetails = cur.fetchall()
                return render_template('selectedBrokerageRat.html',inquiryDetails=inquiryDetails)
            else:
                return render_template('failGen.html', status = "There are no ratings for this Brokerage")
        except MySQLdb.OperationalError as errcode:    
            exceptionMsg = errcode.args[1]
            return render_template('failGen.html', status = "Connection Error! Please try again")
    return render_template('selectedBrokerageRat.html',inquiryDetails=inquiryDetails)

#add View Development Info route
@app.route('/devLocation')
def selectDevelopment():
    return render_template('selectDevelopment.html')

@app.route('/devLocation', methods=['GET', 'POST'])
def selectedDevelopment():
    if request.method == 'POST':
        # Fetch form data
        propertyInfo = request.form
        DevelopmentName = propertyInfo['DevelopmentName']
        try:
            cur = mydb.cursor()
            resultValue = cur.execute("SELECT DevelopmentName, City, CityArea, Street, Type, count(Type) as PerType, avg(Price/AreaSqm) as PricePerSqm  FROM property WHERE DevelopmentName LIKE %s group by 1,2,3,4,5", [DevelopmentName] )
            if resultValue > 0:
                inquiryDetails = cur.fetchall()
                return render_template('selectedDevelopment.html',inquiryDetails=inquiryDetails)
            else:
                return render_template('failGen.html', status = "There are no information for this Development")
        except MySQLdb.OperationalError as errcode:    
            exceptionMsg = errcode.args[1]
            return render_template('failGen.html', status = "Connection Error! Please try again")
    return render_template('selectedDevelopment.html',inquiryDetails=inquiryDetails)             


#add View Property By City route
@app.route('/propCity')
def selectPropCity():
    return render_template('selectPropCity.html')

@app.route('/propCity', methods=['GET', 'POST'])
def selectedPropCity():
    if request.method == 'POST':
        # Fetch form data
        propertyInfo = request.form
        City = propertyInfo['City']
        try:
            cur = mydb.cursor()
            resultValue = cur.execute("SELECT City, count(ID) as PropertiesPerType ,Type, avg(Price/AreaSqm) as PricePerSqm FROM property WHERE city = %s group by 1,3;", [City] )
            if resultValue > 0:
                inquiryDetails = cur.fetchall()
                return render_template('selectedPropCity.html',inquiryDetails=inquiryDetails)
            else:
                return render_template('failGen.html', status = "There are no Properties with the specified city")
        except MySQLdb.OperationalError as errcode:    
            exceptionMsg = errcode.args[1]
            return render_template('failGen.html', status = "Connection Error! Please try again")
    return render_template('selectPropCity.html',inquiryDetails=inquiryDetails)  

#add View Property By City, Price & Amenities route
@app.route('/propPriceAmenities')
def selectPropPriceAmenities():
    return render_template('selectPropCityAmen.html')

@app.route('/propPriceAmenities', methods=['GET', 'POST'])
def selectedPropPriceAmenities():
    if request.method == 'POST':
        # Fetch form data
        propertyInfo = request.form
        City = propertyInfo['City']
        Less = propertyInfo['less']
        Greater = propertyInfo['greater']
        #assign amenites with all the amenities selected
        Amenities = []
        Amenities = request.form.getlist('Amenities')
        #convert list to tuple
        Amenities = tuple(Amenities)
        Length = len(Amenities)
        print(Amenities)
        print(Length)
        try:
            cur = mydb.cursor()
            resultValue = cur.execute("select p.ID, price, city, cityArea, AreaSqm, Type, NumOfBaths, NumOfBeds, hasMaidRoom, ListDate, AgentPhoneNum, group_concat(amenities) from propertyamenities a inner join property p on a.ID = p.ID where p.ID in (select p.ID from propertyamenities a inner join property p on a.ID = p.ID where city = %s and price >= %s and price <= %s and Amenities in %s group by a.ID having count(distinct Amenities)=%s) group by 1,2;", [City,Less,Greater,Amenities,Length] )
            if resultValue > 0:
                inquiryDetails = cur.fetchall()
                return render_template('selectedPropCityAmen.html',inquiryDetails=inquiryDetails)
            else:
                return render_template('failGen.html', status = "There are no Properties with the specified criteria")
        except MySQLdb.OperationalError as errcode:    
            exceptionMsg = errcode.args[1]
            return render_template('failGen.html', status = "Connection Error! Please try again")
    return render_template('selectedPropCityAmen.html',inquiryDetails=inquiryDetails)

#Top 10 Areas route
@app.route('/topTen', methods=['GET', 'POST'])
def topTenAreas():
        try:
            cur = mydb.cursor()
            resultValue = cur.execute("SELECT cityArea, count(Type) as Inventory, avg(Price/AreaSqm) as PricePerSqm from property where cityArea is not null group by 1 order by Inventory desc limit 10;")
            if resultValue > 0:
                inquiryDetails = cur.fetchall()
                return render_template('top10Areas.html',inquiryDetails=inquiryDetails)
            else:
                return render_template('failGen.html', status = "There are no Properties with the specified city")
        except MySQLdb.OperationalError as errcode:    
            exceptionMsg = errcode.args[1]
            return render_template('failGen.html', status = "Connection Error! Please try again")

#Top 5 Brokerage route
@app.route('/topFive', methods=['GET', 'POST'])
def topFiveBrokers():
        try:
            cur = mydb.cursor()
            resultValue = cur.execute("SELECT BName, Listings, avg(Price/AreaSqm), count(Distinct a.PhoneNum) as agents, (Listings/count(Distinct a.PhoneNum)) from brokercompany b inner join agent a on a.BrokerName = b.BName inner join property p on p.AgentBrokerName = a.BrokerName group by 1,2 order by listings desc limit 5;")
            if resultValue > 0:
                inquiryDetails = cur.fetchall()
                return render_template('top5Brokerages.html',inquiryDetails=inquiryDetails)
            else:
                return render_template('failGen.html', status = "There are no Properties with the specified city")
        except MySQLdb.OperationalError as errcode:    
            exceptionMsg = errcode.args[1]
            return render_template('failGen.html', status = "Connection Error! Please try again")
  
#add View Property By City, Price & Amenities route
@app.route('/propAgent')
def selectAgentsProp():
    return render_template('selectAgentProp.html')

@app.route('/propAgent', methods=['GET', 'POST'])
def selectedAgentsProp():
    if request.method == 'POST':
        # Fetch form data
        propertyInfo = request.form
        FName = propertyInfo['FName']
        LName = propertyInfo['LName']
        PhoneNum = propertyInfo['PhoneNum']
        try:
            cur = mydb.cursor()
            resultValue = cur.execute("select p.ID, price, city, cityArea, AreaSqm, Type, NumOfBaths, NumOfBeds, hasMaidRoom, ListDate, AgentPhoneNum, FName, LName from property p inner join agent a on a.PhoneNum = p.AgentPhoneNum and a.FName = AgentFName where (FName = %s and LName = %s) or  AgentPhoneNum = %s;", [FName,LName,PhoneNum] )
            if resultValue > 0:
                inquiryDetails = cur.fetchall()
                return render_template('selectedAgentProp.html',inquiryDetails=inquiryDetails)
            else:
                return render_template('failGen.html', status = "There are no Properties with the specified criteria")
        except MySQLdb.OperationalError as errcode:    
            exceptionMsg = errcode.args[1]
            return render_template('failGen.html', status = "Connection Error! Please try again")
    return render_template('selectedAgentProp.html',inquiryDetails=inquiryDetails)
