import base64
import datetime
import http.client

from flask import Flask,jsonify,render_template,request,redirect,session
import pymongo
import json


app = Flask(__name__)

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["SanalGaleri"]
vehiclesTable = mydb["vehicles"]
usersTable = mydb["users"]
otomobilBrandsTable = mydb["otomobilBrands"]
motorcycleBrandsTable = mydb["motorcycleBrands"]
suvBrandsTable = mydb["suvBrands"]
carDetailTable = mydb["carDetails"]
vehicleListTable = mydb["vehicleList"]
favoritesTable = mydb["favorites"]


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    userName = data["userName"]
    password = data["password"]
    userCheck = usersTable.find_one({'userName': userName})

    if (userCheck['password'] == password):
        return jsonify(userCheck)
    else:
        return '404'
"""
def get_sequence(seq_name):
    return mydb.counters.find_and_modify(query={"_id": seq_name}, update={"$inc": {"seq": 1}}, upsert=True)["seq"]
"""


@app.route('/script')
def script():
    # TODO: burası sonradan veri doldurmak için script yazılacak
    return 0


@app.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    count = list(usersTable.find())
    user = {
        "_id": len(count) + 1,
        "role": "user",
        "userName": data["userName"],
        "password": data["password"]
    }
    usersTable.insert_one(user)
    return {"resultCode":"Ok"}


# ana sayfa doldurma
@app.route('/vehicles')
def vehicles():
    vehicleData = {"res": list(vehiclesTable.find({}))}
    return vehicleData


@app.route('/brands')
def brands():
    brandData = {"res": list(otomobilBrandsTable.find({}))}
    return brandData


@app.route('/motorcyclebrands')
def motorcycleBrands():
    motorcyleBrandData = {"res": list(motorcycleBrandsTable.find({}))}
    return motorcyleBrandData


@app.route('/suvbrands')
def suvBrands():
    suvBrandData = {"res": list(suvBrandsTable.find({}))}
    return suvBrandData


@app.route('/cardetails', methods=['POST'])
def carDetails():
    data = request.get_json()

    id = data['_id']
    carDetailsData = {"res": list(carDetailTable.find({'_id': id}))}

    return jsonify(carDetailsData)


@app.route('/profile', methods=['POST'])
def userDetail():
    data = request.get_json()
    id = data['_id']
    user = {"res": list(usersTable.find({'_id': id}))}
    return user

@app.route('/vehiclelist', methods=['POST'])
def vehicleList():
    req = request.get_json()

    vehicleListData = {"res": list(vehicleListTable.find({"brand": req["brand"], "type": req["type"]}))}

    return vehicleListData

@app.route('/ownvehiclelist', methods=['POST'])
def ownvehicleList():
    req = request.get_json()
    print("req ney",req)
    ownvehicleListData = {"res": list(vehicleListTable.find({"created_by": req["created_by"]}))}

    return ownvehicleListData


# TODO: Burda kişin favorilerinin içindekileri alıp gelmesi gerekiyor

"""
@app.route('/favorites',methods=['POST'])
def favoritesList():
    req = request.get_json()
    fav = list(favoritesTable.find({"user_id":req['user_id']},{"ad_id":1,"_id":0}))
    print("fav ne",list(fav))

    for id in fav:
        favData = {"res":list(carDetailTable.find({"_id": id["ad_id"]}))}
    print("list", favData)
    return jsonify(favData)
"""


@app.route('/favoritesList',methods=['POST'])
def favoritesList():
    req = request.get_json()
    fav = list(favoritesTable.find({"user_id": req['user_id']}, {"ad_id": 1, "_id": 0}))
    print("fav",fav)
    favData= []
    for id in fav:
        data = vehicleListTable.find_one({"ad_id": id["ad_id"]})
        favData.append(data)
        print("data", data)
    print("favdata", {"res":favData})
    return {"res": favData}
# admin için vehicle ekleme


@app.route('/vehicleadd', methods=['POST'])
def vehicleAdd():
    data = request.get_json()

    if data["category"] == "Otomobil":
        data["category"] = "car"
    elif data["category"] == "SUV":
        data["category"] = "suv"
    elif data["category"] == "Motorsiklet":
        data["category"] = "motorcycle"


    countofList = vehicleListTable.count_documents({})

    countofDetail = carDetailTable.count_documents({})

    data["_id"] = countofList + 1

    data["ad_id"] = countofDetail + 1

    #vehicleListTable.insert_one(data)
    print("listeye eklenecek olan",data)

    data["_id"] = countofDetail + 1

    del data["ad_id"]
    #carDetailTable.insert_one(data)
    print("detail eklenecek olan ",data)

    """
     id = data['_id']
    title = data['title']
    vehiclesTable.insert_one({'_id': id, 'title': title})
    """

    return {"resultCode": "Ok"}

@app.route('/file', methods=['POST'])
def file():
    print("sern nesin be abi:")
    return {"resultCode": "Ok"}

@app.route('/vehicledelete', methods=['POST'])
def vehicleDelete():
    data = request.get_json()
    id = data['_id']
    vehiclesTable.delete_one({'_id': id})
    return {"resultCode": "Ok"}


if __name__ == '__main__':
    app.run()