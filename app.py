from flask import Flask, request, jsonify, make_response
from pymongo import MongoClient
from bson import ObjectID

app = Flask(__name__)

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.dizDB
businesses = db.biz

#Get all businesses
@app.route("/api/v1.0/businesses", methods = ["GET"])
def show_all_businesses():
    page_num, page_size = 1, 10
    if request.args.get('pn'):
        page_num = int(request.args.get('pn'))
    if request.args.get('ps'):
        page_num = int(request.args.get('ps'))
    page_start = (page_size * (page_num - 1))


    data_to_return = []
    for business in businesses.find() \
                    .skip(page_start) \
                    .limit(page_size):
        business['_id'] = str(business['_id'])
        for review in business['reviews']:
            review['_id'] = str(review['_id'])
        data_to_return.append(business)
    
    return make_response( jsonify(data_to_return), 200)

#Get one business
@app.route("/api/v1.0/businesses/<string:id>", methods = ["GET"]) #Root route, for GET method
def show_all_businesses(): #Defines function
    business = businesses.find_one( {'_id' : ObjectID(id)} ) 
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
            {"_id" : ObjectID(id)},
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
    result = businesses.delete_one( {"_id" : ObjectID(id)} )
    if result.deleted_count == 1:
        return make_response( jsonify ({}), 204)
    else:
        return make_response( jsonify ({"error" : "Invalid business ID"}), 404) #Output, returns error message with 404 status

#Add a review



if __name__ == "__main__":
    app.run(debug = True)