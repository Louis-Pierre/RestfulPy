import requests
import json
import numpy as np
import datetime as dt
import os

#pyCharmPath=os.path.realpath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
#os.sys.path.append(pyCharmPath+"/fundamentalObjects")

from productionObjects.production import production

from RTE_API.constant import *
from RTE_API.production.fuelTypes import fuelTypesList


def getProdByFuelType(year,month,day=""):
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
    for fd,dic in dInitClass.items():
        for fueltype,data in dic.items():
            prod=production(fd,data,fueltype,"FR")
            if fd in dFinal.keys():
                dFinal[fd][fueltype]=prod
            else:
                dFinal[fd]={fueltype:prod}

    return dFinal


if __name__ == '__main__':
    #getProdByFuelType(2017,"05")
    print("done")