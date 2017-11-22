import pymongo
import datetime
from bson import ObjectId,json_util
import json

def getProdByFuelTypeInMongo(year,month,day):
    client = pymongo.MongoClient()
    db=client.Energy1
    collection=db.prodByFuelType
    fd=datetime.datetime(year,month,day)
    stfd=datetime.datetime.strftime(fd,"%Y%m%d")
    return json.loads(json_util.dumps(collection.find_one({"flowdate":stfd})))

