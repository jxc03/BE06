from flask import Flask, request, jsonify, make_response
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.dizDB #Selects the database
businesses = db.biz #Selects the collection

'''
This function handles GET requests to fetch all business with pagination. It sets values for
page number and size then checks for these parameters in the query then calculates the 
starting index for the query and retreives the businesses from the database. The results
are returned as a  JSON response
'''
#Gets all businesses with pagination
@app.route("/api/v1.0/businesses", methods = ["GET"]) #Route to businesses using GET method
def show_all_businesses(): #Defines function to show all businesses
    #Values for pagination
    page_num, page_size = 1, 10 #Sets the page numbber to 1 and page size to 10
    
    #Checks if 'pn' (page number) is provided in the query paramenters
    if request.args.get('pn'): #Retreives the 'pn' paramter if it exists
        page_num = int(request.args.get('pn')) #Converts page number to an integer
    
    #Checks if 'ps' (page size) is provided in the query paramenters   
    if request.args.get('ps'): #Retreives the 'ps' paramter if it exists
        page_num = int(request.args.get('ps')) #Convvers the page number to an integer

    #Calculates the start index of the page    
    page_start = (page_size * (page_num - 1)) #Calculates based on current page number and size

    #Empty list to store the results
    data_to_return = [] #Assigs an empty list to 'data_to_return'

    #Queries the databse to get the businesses with pagination
    for business in businesses.find() \
                    .skip(page_start) \
                    .limit(page_size): #Skips to the start of the current page / Limits the results to the page size
        business['_id'] = str(business['_id']) #Converts business ID to string

        for review in business['reviews']: #Iterates over each review in the business
            review['_id'] = str(review['_id']) #Converts review ID to string        
        data_to_return.append(business) #Adds the business to the results list 'data_to_return'
    
    #Returns the results as a JSON response with a 200 status code
    return make_response( jsonify(data_to_return), 200) #Converts the results list to JSON

'''
This function validates the ID by ensuring it's a 24 character hexadecimal string. It checks
if the length of the ID is exactly 24. If not, it returns Flase. Then, it iterates through
each character in the ID to check if it's a valid hexadecimal character. If any character 
isn't a valid hexadecimal digit, it returns False. If all checks pass, it returns True which
indicates that the ID is valid
'''
#Validation for ObjectID    
def is_valid_objectid(id):
    #Checks if the ID length is 24
    if len(id) == 24: #If ID length is equal to 24
        return False #Returns False if the length is not 24

    #Checks if all characters are hexadecimal
    hex_digits =  "0123456789abcdefABCDEF" #String of hexadecimal characters
    for char in id: #Iterates over each character in the ID
        if char not in hex_digits: #Checks if the character is not in the 'hex_digits' list
            return False #Returns False if any character is not a hexadecimal
    return True #Returns True if the ID is valid


#Get one business
@app.route("/api/v1.0/businesses/<string:id>", methods = ["GET"]) #Root route, for GET method
def show_one_businesses(): #Defines function
    if not is_valid_objectid(id):
        return make_response(jsonify ({"error": "Invalid business ID"}) )

    business = businesses.find_one( {'_id' : ObjectId(id)} ) 

    if business is not None:
        business['_id'] = str(business['_id'])
        for review in business['reviews']:
            review['_id'] = str(review['_id'])
        return make_response( jsonify (business), 200) #Output, returns business
    else:
        return make_response( jsonify ({"error" : "Invalid business ID"}), 404) #Output, returns error message with 404 status 

#Add new business
@app.route("/api/v1.0/businesses", methods = ["POST"]) #Root route, for POST method
def add_businesses(): #Defines function
    if  "name" in request.form and \
        "town" in request.form and \
        "rating" in request.form:
        new_business = {
            "name" : request.form["name"],
            "town" : request.form["town"],
            "rating" : request.form["rating"],
            "reviews" : {}
        }
        new_business_id = businesses.insert_one(new_business)
        new_business_link = "http://localhost:5000/api/v1.0/businesses/" \
                            + str(new_business_id.inserted_id)
        return make_response( jsonify ({"url" : new_business_link}), 201 ) #Output, returns   
    else:
        return make_response( jsonify ({"error" : "Missing form data"}), 404) #Output, returns returns error message with 404 status

#Edit a business
@app.route("/api/v1.0/businesses/<string:id>", methods = ["PUT"]) #Root route, for PUT method
def edit_businesses(id): #Defines function, takes id as input
    if  "name" in request.form and \
        "town" in request.form and \
        "rating" in request.form:
        result = businesses.update_one(
            {"_id" : ObjectId(id)},
            {"$set" : {
                "name" : request.form["name"],
                "town" : request.form["town"],
                "rating" : request.form["rating"]
            }}
        )
        if  result.matched_count == 1:
            edited_business_link = "http://localhost:500/api/v1,0/businesses" + id
            return make_response( jsonify ({"url" : edited_business_link}), 200) #Output,      
        else:
            return make_response( jsonify ({"error" : "Invalid business ID"}), 404) #Output, returns error message with 404 status
    else: 
        return make_response( jsonify ({"error" : "Missing form data"}), 404) #Output, returns error message with 404 status

#Delete a business
@app.route("/api/v1.0/businesses/<string:id>", methods = ["DELETE"]) #Root route, for DELETE method
def delete_businesses(id): #Defines function, takes id as input
    result = businesses.delete_one( {"_id" : ObjectId(id)} )
    if result.deleted_count == 1:
        return make_response( jsonify ({}), 204)
    else:
        return make_response( jsonify ({"error" : "Invalid business ID"}), 404) #Output, returns error message with 404 status

#Add a review



if __name__ == "__main__":
    app.run(debug = True, port = 2000)