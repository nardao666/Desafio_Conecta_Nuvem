from __future__ import print_function
import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from flask import Flask, render_template
import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt

# Endereço das request da API
SCOPES = ['https://www.googleapis.com/auth/contacts.other.readonly','https://www.googleapis.com/auth/contacts.readonly']

#################################################################################
# Estamos utilizando dois escopes pois pela documentação do google              #
#  - Contacts.readonly, obtem informações dos contatos do Google, como          #
#     a agenda do celular para quem utiliza o serviço deles para tal função     #
#  - Contacts.other.readonly, obtem informações dos contatos do Google,         #
#    pelo email, que já foram enviados                                          #   
#################################################################################


creds = None
# Caminho dos arquivos que serão lidos ou salvos
path_dir = '//home/nardao/Documentos/ConectaNuvem/'

########################################################################
###      https://www.googleapis.com/auth/contacts.other.readonly     ###
########################################################################
# Verifica se tem o arquivo de token com os dados
#   da autenticação do e-mail do google
if os.path.exists( path_dir + 'token.pickle' ):
    with open( path_dir + 'token.pickle', 'rb') as token:
        creds = pickle.load(token)
# Verificação das credenciais e quais informações podem fazer o request
#   na API
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            path_dir + 'credentials.json', SCOPES[0])
        creds = flow.run_local_server(port=0)
# Salva as informações das credenciais
    with open( path_dir + 'token.pickle', 'wb') as token:
        pickle.dump(creds, token)

########################################################################
###        https://www.googleapis.com/auth/contacts.readonly         ###
########################################################################

credsc = None
# Verifica se tem o arquivo de token com os dados
#   da autenticação do e-mail do google
if os.path.exists( path_dir + 'tokenc.pickle'):
    with open( path_dir + 'tokenc.pickle', 'rb') as tokenc:
        credsc = pickle.load(tokenc)
# Verificação das credenciais e quais informações podem fazer o request
#   na API
if not credsc or not credsc.valid:
    if credsc and credsc.expired and credsc.refresh_token:
        credsc.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            path_dir+ 'credentials1.json', SCOPES[1])
        credsc = flow.run_local_server(port=0)
# Salva as informações das credenciais
    with open( path_dir + 'tokenc.pickle', 'wb') as token:
        pickle.dump(credsc, token)


service = build('people', 'v1', credentials=creds)
service_c = build('people', 'v1', credentials=credsc)
email = []


#Obtendo os email pelas request conforme os scopes
results = service.otherContacts().list(
    readMask = 'emailAddresses'
).execute()
connections = results.get('otherContacts',[])

for person in connections:
    names = person.get('emailAddresses', [])
    if names:
        email.append( names[0].get('value') )


results = service_c.people().connections().list(
        resourceName='people/me',
        personFields='emailAddresses').execute()
connections = results.get('connections', [])

for person in connections:
    names = person.get('emailAddresses', [])
    if names:
        email.append(names[0].get('value'))
        

########################################################################
###                     TRATAMENTO DOS EMAILS                        ###
########################################################################

#Criando as colunas do dataframe e o dataframe
col = ['Email', 'Dominio']
df = pd.DataFrame(columns =col)

#Separa o email e o domino
#Adicionando os dados no dataframe
for i in email:
    a = i.split('@')[1] 
    aux=[i,a]  
    df.loc[len(df)]=aux

#Pega os dado unicos da coluna Dominio em uma lista
# ordena a lista
# faz a contagem de cada dominio no dataframe
# transforma uma lista de lista em uma lista
labels = df['Dominio'].unique()
labels.sort()
test = df.groupby('Dominio').count()
sum_dom = np.hstack( test.values.tolist() )

###################################################################
###                    Criando o Grafico                        ###
###################################################################

#Criação do grafico em formato de pizza
plt.figure(figsize=(15,10),dpi=200)
plt.pie(sum_dom,labels=labels, startangle=90, 
        rotatelabels= 45,labeldistance=0.8, autopct = '%1.1f%%')
plt.axis('equal')
plt.savefig(path_dir + 'grafico_sum_contact.jpg',dpi= 300, bbox_inches = 'tight')

###################################################################
###                   Utilizando o Flask                        ###
###################################################################

#Utilização do Flask para a criação da pagina dinamica
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', my_dominio = labels, my_email=email)


if __name__ == "__main__":
    app.debug = True
    app.run()