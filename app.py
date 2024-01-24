from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def hello():
    return 'Hello, World!'
@app.route('/api/getIDLibretasAdeudadas/<phpsessid>', methods=['GET'])
def getIDLibretasAdeudadas(phpsessid):
    url = "https://campus.ort.edu.ar/dashboard/"
    headers = {
        "Cookie": "_ga=GA1.1.1013411711.1703598408; PHPSESSID=" + phpsessid + "; notified=0; _ga_Z4YD9X4VXX=GS1.1.1706046015.10.1.1706046028.0.0.0",
    }
    IDs = []
    response = requests.get(url, headers=headers,verify=False)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        elementos = soup.find_all('div', {'data-idlibreta': lambda x: x is not None and x != '[]'})
        for elemento in elementos:
            data_idlibreta_valor = elemento['data-idlibreta']
            IDs.append(data_idlibreta_valor)
            
    else:
        print(f"No se pudo acceder a la página. Código de estado: {response.status_code}")
    return IDs

@app.route('/api/getAdeudadosByID/<ID>/<phpsessid>', methods=['GET'])
def getAdeudadosByID(id,phpsessid):
    url = "https://campus.ort.edu.ar/dashboardajax/"
    headers = {
        "Cookie": "_ga=GA1.1.1013411711.1703598408; PHPSESSID=" + phpsessid + "; notified=0; _ga_Z4YD9X4VXX=GS1.1.1706046015.10.1.1706046497.0.0.0",
    }

    data = {
        "method": "listaPendientes",
        "idlibreta": "[" + id + "]",
        "idAlumno": "undefined"
    }
    pendientesInfo = []

    response = requests.post(url, headers=headers, data=data,verify=False)
    if response.status_code == 200:
        data = response.json()
        for pendiente in data["Pendientes"]:
            
            pendientesInfo.append({
                "fechaFin": pendiente["FechaFin"],
                "name": pendiente["NombreContenido"],
            })

    else:
        print(f"Error en la solicitud. Código de estado: {response.status_code}")
    return pendientesInfo

@app.route('/api/getAllAdeudados/<phpsessid>', methods=['GET'])
def getAllAdeudados(phpsessid):
    IDs = getIDLibretasAdeudadas(phpsessid)
    data = []
    for id in IDs:
        info = getAdeudadosByID(id,phpsessid)
        if(info != []):
            data.append(info)
    return data
    
@app.route('/api/getPHPSESSID/<user>/<password>', methods=['GET'])
def getPHPSESSID(user,password):
    url = "https://campus.ort.edu.ar/ajaxactions/LogearUsuario?u=" + user + "&c=" + password + "&saveForm=false&r="
    response = requests.post(url,verify=False)
    if response.status_code == 200:
        return response.cookies.get_dict()['PHPSESSID']

if __name__ == '__main__':
    app.run(debug=True)
