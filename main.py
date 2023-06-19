import base64
import datetime
import http.client
import os
import csv

#imports for machine learning
from sklearn.tree import DecisionTreeClassifier


from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

#imports for webapi
from flask import Flask,jsonify,render_template,request,redirect,session
import pymongo
import json

from werkzeug.utils import secure_filename


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
logsTable = mydb["logs"]
imagelogsTable = mydb["image_logs"]


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
    countofDetail = carDetailTable.count_documents({})

    # fotoğrafları ilana ekleme

    logs_images = list(imagelogsTable.find({"ad_id": countofDetail+1}))

    array = []
    for filename in logs_images:
       array.append('http://10.0.2.2:5000/static/ad/'+filename["file_name"])

    print(array)


    return array


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

@app.route('/newadid',methods=['GET'])
def newadid():
    last_id = list(carDetailTable.find({}))
    last_id_count = len(last_id)
    last_id_count = last_id_count + 1
    return str(last_id_count)

@app.route('/suvbrands')
def suvBrands():
    suvBrandData = {"res": list(suvBrandsTable.find({}))}
    return suvBrandData


@app.route('/cardetails', methods=['POST'])
def carDetails():
    data = request.get_json()

    id = data['_id']
    logsCount=logsTable.count_documents({})
    logsTable.insert_one({"_id": logsCount+1, "ad_id": data['_id'], "user_id": data["user_id"]})
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
@app.route('/addtofavorites',methods = ['POST'])
def addtofav():
    req = request.get_json()
    favcount = favoritesTable.count_documents({})
    req['_id'] = favcount + 1
    favoritesTable.insert_one(req)
    return "favorilere ekleme başarılı"

@app.route('/favoritesList',methods=['POST'])
def favoritesList():
    req = request.get_json()
    fav = list(favoritesTable.find({"user_id": req['user_id']}, {"ad_id": 1, "_id": 0}))

    favData= []
    for id in fav:
        data = vehicleListTable.find_one({"ad_id": id["ad_id"]})
        favData.append(data)

    return {"res": favData}





ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/file-upload', methods=['POST'])
def upload_file():

    file = request.files['file']
    file.save(os.path.join('/Users/dogukan/Desktop/Backend/static/ad', file.filename))
    last_id = carDetailTable.count_documents({})+1
    imagelogsTable.insert_one({"ad_id":last_id,"file_name":file.filename})
    return ""


# admin için vehicle ekleme


@app.route('/vehicleadd', methods=['POST'])
def vehicleAdd():
    data = request.get_json()

    if data["category"] == "Otomobil":
        data["type"] = "car"
    elif data["category"] == "SUV":
        data["type"] = "suv"
    elif data["category"] == "Motorsiklet":
        data["type"] = "motorcycle"


    countofList = vehicleListTable.count_documents({})

    countofDetail = carDetailTable.count_documents({})

    data["_id"] = countofList + 1

    data["ad_id"] = countofDetail + 1

    #fotoğrafları ilana ekleme

    logs_images = list(imagelogsTable.find({"ad_id": countofDetail + 1}))

    array = []
    for filename in logs_images:
        array.append('http://10.0.2.2:5000/static/ad/' + filename["file_name"])

    data["images"] = array
    data["image"] = array[0]

    vehicleListTable.insert_one(data)

    data["_id"] = countofDetail + 1

    del data["ad_id"]
    carDetailTable.insert_one(data)


    """
     id = data['_id']
    title = data['title']
    vehiclesTable.insert_one({'_id': id, 'title': title})
    """

    return {"resultCode": "Ok"}


@app.route('/vehicledelete', methods=['POST'])
def vehicleDelete():
    data = request.get_json()
    id = data['_id']
    vehiclesTable.delete_one({'_id': id})
    return {"resultCode": "Ok"}

@app.route('/machine-learning',methods=['POST'])
def learn():
    df = pd.read_csv('veri.csv')

    # Veri setini ön işleme
    df = df[['id','modelYear', 'brand', 'price', 'km', 'color']]
    label_encoder = LabelEncoder()
    df['brand'] = label_encoder.fit_transform(df['brand'])
    df['color'] = label_encoder.fit_transform(df['color'])
    scaler = MinMaxScaler()
    df[['price', 'km']] = scaler.fit_transform(df[['price', 'km']])

    # Kullanıcının tıkladığı araçları yükleme
    clicked_cars = pd.read_csv('logs.csv')
    clicked_cars = clicked_cars[['id','modelYear', 'brand', 'price', 'km', 'color']]
    clicked_cars['brand'] = label_encoder.fit_transform(clicked_cars['brand'])
    clicked_cars['color'] = label_encoder.fit_transform(clicked_cars['color'])
    clicked_cars[['price', 'km']] = scaler.transform(clicked_cars[['price', 'km']])

    # Kullanıcının tıkladığı araçların özelliklerini birleştirme
    user_features = clicked_cars.mean().values.reshape(1, -1)

    # Benzerlik matrisini hesaplama
    similarity_matrix = cosine_similarity(df, user_features)

    # Benzerlik skorlarını sıralama
    similarity_scores = pd.Series(similarity_matrix.flatten(), index=df.index)
    sorted_similarity_scores = similarity_scores.sort_values(ascending=False)

    # Kullanıcıya önerilecek araçları seçme
    recommended_cars = df.loc[sorted_similarity_scores.index]
    recommended_cars = recommended_cars[~recommended_cars.index.isin(clicked_cars.index)]


    recommended_cars_ids = []
    rci = recommended_cars["id"].values.tolist()

    for ids in rci:
        recommended_cars_ids.append(ids)


    recomended_cars = list(vehicleListTable.find({"_id": {"$in": recommended_cars_ids}}))


    return {"res":recomended_cars}

@app.route('/learning-csv', methods=['POST'])
def write_csv():
    req = request.get_json()

    logs = list(logsTable.find({"user_id":req['user_id']},{"ad_id":1,"_id":0}))

    ids_of_logs=[]
    for l in logs:
        ids_of_logs.append(l['ad_id'])

    cars = list(carDetailTable.find({"_id": {"$in": ids_of_logs}}))
    data = []
    header = ['id','modelYear', 'brand', 'price', 'km', 'color']
    cars_count = len(cars)
    for i in range(cars_count):
        id= cars[i]["_id"]
        modelYear = cars[i]["modelYear"]
        brand = cars[i]["brand"]
        price = cars[i]["price"]
        km = cars[i]["km"]
        color = cars[i]["color"]
        t = [id,modelYear, brand, price, km, color]
        print(t)
        data.append(t)


    with open('/Users/dogukan/Desktop/Backend/logs.csv', 'w', encoding='UTF-8', newline='') as file:
        writer = csv.writer(file)
        #başlık
        writer.writerow(header)
        #satırlar
        writer.writerows(data)

    return "ok"


@app.route('/all-cars-csv')
def write_all_cars_csv():

    cars = list(carDetailTable.find({}))
    print("cars",cars)
    data = []

    header = ['id','modelYear', 'brand', 'price', 'km', 'color']

    cars_count = len(cars)
    for i in range(cars_count):
        id = cars[i]["_id"]
        modelYear = cars[i]["modelYear"]
        brand = cars[i]["brand"]
        price = cars[i]["price"]
        km = cars[i]["km"]
        color = cars[i]["color"]
        t = [id,modelYear, brand, price, km, color]
        print(t)

        data.append(t)

    print("data",data)

    with open('/Users/dogukan/Desktop/Backend/veri.csv', 'w', encoding='UTF-8', newline='') as file:

        writer = csv.writer(file)
        #başlık
        writer.writerow(header)
        #satırlar
        writer.writerows(data)

    return "ok"



if __name__ == '__main__':
    app.run()