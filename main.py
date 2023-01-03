import base64
import datetime
import http.client

from flask import Flask, jsonify, render_template, request, redirect, session
import pymongo
from bson.json_util import ObjectId
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
    return jsonify(user)

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
# admin için vehicle ekleme


@app.route('/vehicleadd', methods=['POST'])
def vehicleAdd():
    data = request.get_json()
    id = data['_id']
    title = data['title']
    vehiclesTable.insert_one({'_id': id, 'title': title})
    return 'OK'


@app.route('/vehicledelete', methods=['POST'])
def vehicleDelete():
    data = request.get_json()
    id = data['_id']
    vehiclesTable.delete_one({'_id': id})
    return 'OK'


if __name__ == '__main__':
    app.run()
