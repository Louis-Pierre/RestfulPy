import datetime as dt
import json
import jsonpickle
import pymongo

import numpy as np
import requests


from productionObjects.production import production
from restfulPy.api.ProductionData.RTE_API.production.fuelTypes import fuelTypesList
from restfulPy.api.ProductionData.RTE_API.constant import *


# pyCharmPath=os.path.realpath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
# os.sys.path.append(pyCharmPath+"/fundamentalObjects")


def getProdByFuelType(year,month,day="",asJson=True):

    convertFormat=lambda x:str(x) if x>=10 else "0"+str(x)
    styear=str(year)
    stmonth=convertFormat(int(month))
    if day!="":
        stday = convertFormat(int(day))
    ##URL##
    url=urlAPI+"dataset=cdc_prod_par_filiere"
    url = url +"&rows="+str(maxRows)+"&sort=-date_heure"
    #Type de filtre
    url = url + "&facet=date_heure&facet=qualite"
    #Value for filter
    url = url + "&refine.qualite=Interm%C3%A9diaire"
    url = url + "&refine.date_heure=" + str(year)+"/"+str(month)
    if day !="":
        url = url +"/"+str(day)

    print(url)
    res=requests.get(url)

    dres=json.loads(res.content.decode("utf-8"))

    #Parsing
    dInitClass={}
    if "records" in dres.keys():
        for record in dres["records"]:
            if "fields" in record.keys():
                data=record["fields"]
                flowdate=dt.datetime.strptime(data['date_heure'][:16],"%Y-%m-%dT%H:%M")
                for fuelType in fuelTypesList():
                    key="prod_"+fuelType
                    if key in data.keys():
                        fd=flowdate.date()
                        if fd in dInitClass.keys():
                            if fuelType in dInitClass[fd].keys():
                                dInitClass[fd][fuelType]=np.vstack(
                                    (dInitClass[fd][fuelType],np.array([flowdate,float(data[key])])))
                            else:
                                dInitClass[fd][fuelType]=np.empty([0, 2])
                                dInitClass[fd][fuelType] = np.vstack(
                                    (dInitClass[fd][fuelType], np.array([flowdate, float(data[key])])))
                        else:
                            dInitClass[fd]={fuelType:np.array([flowdate, float(data[key])])}


    ## Make sure it is ordered
    for fd,dic in dInitClass.items():
        for ft,data in dic.items():
            indexOrder=data[:,0].argsort()
            #We only keep values (no more datetime) but make sure it s chronologically ordered
            dInitClass[fd][ft]=data[indexOrder,1]


    dFinal={}
    dFinalToEncode = {}
    for fd,dic2 in dInitClass.items():
        for fueltype,data2 in dic2.items():
            prod=production(fd,data2,fueltype,"FR")
            if dt.datetime.strftime(fd,"%Y%m%d") in dFinal.keys():
                dFinal[dt.datetime.strftime(fd,"%Y%m%d")][fueltype]=prod
                dFinalToEncode[dt.datetime.strftime(fd, "%Y%m%d")][fueltype] = prod._toDic()
            else:
                dFinal[dt.datetime.strftime(fd,"%Y%m%d")]={fueltype:prod}
                dFinalToEncode[dt.datetime.strftime(fd, "%Y%m%d")] = {fueltype: prod._toDic()}

    if asJson:
        return jsonpickle.dumps(dFinalToEncode,unpicklable=False)
    else:
        return dFinal


def saveProdByFuelType(year,month,day):
    try:
        jsondata=getProdByFuelType(year,month,day,True)
        print("Prod data successfuly loaded from RTE API")
    except:
        print("ERROR in loading Prod data from RTE API")
        return False

    try:
        dic=json.loads(jsondata)
        client = pymongo.MongoClient()
        db=client.Energy1
        collection=db.prodByFuelType
        fd=dt.datetime(year,month,day)
        stfd=dt.datetime.strftime(fd,"%Y%m%d")
        data=dic[stfd]
        data.update({"flowdate":stfd})
        collection.insert_one(data)
        print("Prod data uploaded in Energy1")
        return True
    except:
        print("ERROR in uploading prod data loaded in Energy1")
        return False



#query on objectid
#db.prodByFuelType.find({_id:ObjectId("59dbe19619a9b82a24e402d6")})


# RTE API 2 // connexion with OAuth2
def getProdByFuelTypeAPI2():
    url="https://digital.iservices.rte-france.com/open_api/actual_generation/v1/actual_generations_per_unit"
    #Authentification
    #Cette partie est l'envoi au serveur d'authentification qui doit renvoyer un token
    # Ce qui suit basic dans Authorization est l encodage en base 64 de id_client:id_secret
    #ie c4fe4cb3-fb00-45bd-9f7b-92667f66bb21:c4bdf301-602a-4edd-8c0d-1730bf956ac7
    #Ces id sont ceux fournis dans mon app de l api LP
    #Attention ils peuvent changer. utiliser un site en ligne pour faire la conversion en base 64
    # le== a la fin fait partie de la co,nversion en base 64
    url="https://digital.iservices.rte-france.com/token/oauth"
    headers = {"Authorization": "Basic YzRmZTRjYjMtZmIwMC00NWJkLTlmN2ItOTI2NjdmNjZiYjIxOmM0YmRmMzAxLTYwMmEtNGVkZC04YzBkLTE3MzBiZjk1NmFjNw==",
               "Content-Type": "application/x-www-form-urlencoded"}
    a=requests.post(url,headers=headers)
    print(a)
    dicToken=json.loads(a.content.decode("utf-8"))

    #Utilisation du token pour requeter la donnee
    url2 = "https://digital.iservices.rte-france.com/open_api/actual_generation/v1/actual_generations_per_production_type"
    headers2 = {"Authorization": dicToken['token_type'] + " " +dicToken['access_token'],
    "Content-Type" : "application/soap+xml;charset=UTF-8;"}
    b=requests.get(url2,headers=headers2)
    print(b)

    return json.loads(b.content.decode("utf-8"))


if __name__ == '__main__':
    #a=getProdByFuelType(2017,5,3,False)
    for i in range(16, 25):
        saveProdByFuelType(2017, 5, i)
