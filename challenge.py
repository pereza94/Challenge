
from __future__ import print_function
import httplib2, os
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from flask import Flask, request,json
from flask import Response







app = Flask(__name__)

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
#SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


@app.route('/obtener-permiso')
def obtenerPermiso():
    credentials = get_credentials() #obtiene credenciales
    http = credentials.authorize(httplib2.Http()) #incializa http
    service = discovery.build('drive', 'v3', http=http) #inicializa servicios de API de google



@app.route('/search-in-doc/<id>')
def main(id):
    credentials = get_credentials() #obtiene credenciales
    http = credentials.authorize(httplib2.Http()) #incializa http
    service = discovery.build('drive', 'v3', http=http) #inicializa servicios de API de google
    

    #obtiene en primer lugar el archivo a traves de su ID, para poder conocer su nombre
    results = service.files().get(fileId=id).execute()
    name = results.get('name', [])

    #obtiene el valor de la palabra buscada    
    word = request.args.get('word', 'no llego parametro')


    #Consulta por el contenido del archivo
    results = service.files().list(q=" name = '"+name+"' and fullText contains '"+word+"'",fields="nextPageToken, files(id, name)").execute()


    if(word != 'no llego parametro'):
        if (len(results['files'])>0): #Verifica que exista al menos un archivo en la lista
            message= {
              'message': 'Palabra encontrada'
            }
            response = app.response_class(response=json.dumps(message),status=200,mimetype='application/json')
            return response
        else:
            message= {
              'message': 'Palabra NO encontrada'
            }
            response = app.response_class(response=json.dumps(message),status=404,mimetype='application/json')
            return response
    else:
        message= {
              'message': 'Falta el parametro Palabra para ejecutar la accion'
            }
        response = app.response_class(response=json.dumps(message),status=404,mimetype='application/json')
        return response
      
  


@app.route('/file/', methods =['POST'])
def file():
    
    credentials = get_credentials() #obtiene credenciales
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)


    #lee parametros
    titulo = request.args.get('titulo', 'no llego titulo')
    descripcion = request.args.get('descripcion', 'no llego descripcion')

    #Genera el metadato del archivo
    file_metadata = {
    'name': titulo,
    'mimeType': 'application/vnd.google-apps.spreadsheet',
    'descripcion':descripcion
    }   
   
    if (titulo != 'no llego titulo' and descripcion != 'no llego descripcion'): #verifica que existan los campos para crear el archivo
        file = service.files().create(body=file_metadata,fields='id').execute()
    else:
        nuevo= {
        'message': 'Parametros invalidos'
        }   
        response = app.response_class(response=json.dumps(nuevo),status=400,mimetype='application/json')
        return response

    if (file.get('id')):
        nuevo= {
            'id': file.get('id'),
            'titulo': titulo,
            'descripcion':descripcion
            }   
        response = app.response_class(response=json.dumps(nuevo),status=200,mimetype='application/json')
        return response
    else:
        if(not file):
            nuevo= {
                     'message': 'Archivo no creado'
                     }
            response = app.response_class(response=json.dumps(nuevo),status=500,mimetype='application/json')
            return response
    



if __name__ == '__main__':
    app.run(debug = True, port = 8000) #Se encarga de ejecutar el Servidor en el puerto 500