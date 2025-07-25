import paramiko
import os
from dotenv import load_dotenv
from time import sleep
import json
import sqlalchemy
import psycopg2

load_dotenv()

ssh_path = "./quasar-geoserver-3.pem"
ip = os.getenv('IP')
# port = os.getenv('PORT')
user = os.getenv('USER')
# password = os.getenv('PASSWORD')



def start_session():
    """Inicia uma sessão SSH com o servidor remoto
    
    :return: Cliente SSH conectado ao servidor remoto
    """
    print(f"Connecting to {ip} as {user}...")

    key = paramiko.RSAKey.from_private_key_file(ssh_path)

    # print(type(key))

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ip, username=user, pkey=key)
    return client

# para descobrir o caminho correto do curl...   
''' 
client=start_session()
stdin, stdout, stderr = client.exec_command("which curl")
sleep(1)
if stderr.read():
    print("Error downloading from S3:", stderr.read().decode())
    client.close()
else:
    print(stdout.read().decode())
    client.close() 
'''


# client.exec_command("ls")

# stdin, stdout, stderr = client.exec_command('ls')
# sleep(1)
# print(stdout.read().decode())
# client.close()

# command = input("Enter command to execute on remote server: ")

# while command != "exit":
#     stdin, stdout, stderr = client.exec_command(command)
#     sleep(1)
#     print(stdout.read().decode())
#     if stderr.read():
#         print("Error:", stderr.read().decode())
#     else:
#         print("Command executed successfully.")
#     command = input("Enter command to execute on remote server (or type 'exit' to quit): ")



#### ------------////////////////////////////---------------#




def view_folder_contents(remote_folder):
    """Visualizar o conteúdo de uma pasta no servidor remoto
    
    :param remote_folder: Pasta no servidor remoto que será visualizada
    
    """
    client = start_session()
    command = f"ls {remote_folder}"
    
    stdin, stdout, stderr = client.exec_command(command)
    sleep(1)
    if stderr.read():
        print("Error:", stderr.read().decode())
        client.close()
    else:
        print(stdout.read().decode())
        client.close()
        

def list_layers_in_geoserver():
    """Listar camadas no Geoserver remoto
    """
    client = start_session()
    command = "/home/ubuntu/anaconda3/bin/curl -s -u admin:geoserver -XGET http://localhost:8080/geoserver/rest/layers.json"
    stdin, stdout, stderr = client.exec_command(command)
    sleep(2)
    error = stderr.read().decode()
    if error:
        print("Erro:\n", error)
        client.close()
    else:
        print("Camadas no GS: ")
        print(stdout.read())
        client.close()
        
def list_workspaces_in_geoserver():
    """Listar workspaces no Geoserver remoto
    """
    client = start_session()
    command = "/home/ubuntu/anaconda3/bin/curl -s -u admin:geoserver -XGET http://localhost:8080/geoserver/rest/workspaces"
    stdin, stdout, stderr = client.exec_command(command)
    sleep(2)
    error = stderr.read().decode()
    if error:
        print("Erro:\n", error)
        client.close()
    else:
        print("Workspaces no GS: ")
        print(stdout.read())
        client.close()
    
def upload_zip_to_geoserver(workspace, path_file, store_name):
    """Subindo shapefiles para o GS remoto
    
    :param workspace: Nome do workspace para subir a camada
    :param path_file: Caminho de onde está o zip
    :param store_name: Nome do datastore onde a camada será criada
    :return: Mensagem de sucesso ou erro
    """
    client = start_session()
    command = (
        f'curl -s -u admin:geoserver -XPUT '
        f'-H "Content-type: application/zip" '
        f'--data-binary "@{path_file}" '
        f'"http://localhost:8080/geoserver/rest/workspaces/{workspace}/datastores/{store_name}/file.shp"'
    )

    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    client.close()

    if error:
        return print("Erro:\n", error)
    else:
        return print("Upload concluído com sucesso!\n", output)  
    
   
def upload_raster_to_geoserver(workspace, path_file, store_name):
    """Subindo arquivos raster para o GS remoto
    
    :param workspace: Nome do workspace para subir a camada
    :param path_file: Caminho de onde está o zip com raster
    :param store_name: Nome do datastore onde a camada será criada
    :return: Mensagem de sucesso ou erro
    """
    client = start_session()
    command = (
        f'curl -s -u admin:geoserver -v -XPUT '
        f'-H "Content-type: application/zip" '
        f'--data-binary "@{path_file}" '
        f'"http://localhost:8080/geoserver/rest/workspaces/{workspace}/coveragestores/{store_name}/file.geotiff"'
    )

    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    client.close()

    if error:
        return print("Erro:\n", error)
    else:
        return print("Upload concluído com sucesso!\n", output)


def upload_geojson_to_geoserver(workspace, path_file, store_name=None):
    """
    Converte GeoJSON em GPKG via SSH e publica no GeoServer via REST API.

    :param workspace: Nome do workspace no GeoServer
    :param path_file: Caminho no servidor do arquivo .geojson (ex: geoserver-automation/map.geojson)
    :param store_name: (Opcional) Nome do datastore. Se None, usa o nome do arquivo
    :return: Mensagem de sucesso ou erro
    """
    client = start_session()

    if not path_file.lower().endswith('.geojson'):
        raise ValueError("O arquivo de entrada deve ser um GeoJSON (*.geojson)")

    filename = os.path.basename(path_file)
    base_name = os.path.splitext(filename)[0]
    if store_name is None:
        store_name = base_name


    gpkg_relative = os.path.join(os.path.dirname(path_file), f"{base_name}.gpkg").replace("\\", "/")

    stdin, stdout, stderr = client.exec_command(f"realpath {gpkg_relative}")
    gpkg_path = stdout.read().decode().strip()
    # gpkg_path = os.path.join(os.path.dirname(path_file), f"{base_name}.gpkg").replace("\\", "/")
    
    
    print(gpkg_path)

    # Converter GeoJSON em GPKG no servidor via SSH
    print(f"Convertendo {path_file} para {gpkg_path} via SSH...")

    convert_cmd = f'ogr2ogr -f GPKG {gpkg_path} {path_file}'
    
    print(convert_cmd)
    
    stdin, stdout, stderr = client.exec_command(convert_cmd)
    err_convert = stderr.read().decode()
    out_convert = stdout.read().decode()
    
    print(out_convert)

    if err_convert:
        print("Erro na conversão do GeoJSON para GPKG:")
        print(err_convert)
        client.close()
        return

    command = (
        f'curl -s -u admin:geoserver -XPUT '
        f'-H "Content-type: application/x-sqlite3" '
        f'--data-binary "@{gpkg_path}" '
        f'"http://localhost:8080/geoserver/rest/workspaces/{workspace}/datastores/{store_name}/file.gpkg"'
    )

    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    client.close()

    if error:
        return print("Erro:\n", error)
    else:
        return print("Upload concluído com sucesso!\n", output)  
    # Criar datastore apontando para o GPKG
    # datastore_payload = {
    #     "dataStore": {
    #         "name": store_name,
    #         "connectionParameters": {
    #             "entry": [
    #                 {"@key": "filetype", "$": "gpkg"},
    #                 {"@key": "url", "$": f"file:{gpkg_path}"}
    #             ]
    #         }
    #     }
    # }
    
    # print(datastore_payload["dataStore"]["connectionParameters"]["entry"])
    # input()

    # create_store_cmd = (
    #     f"curl -s -o /tmp/create_output.txt -w '%{{http_code}}' -u admin:geoserver -XPOST "
    #     f"-H 'Content-type: application/json' "
    #     f"-d '{json.dumps(datastore_payload)}' "
    #     f"http://localhost:8080/geoserver/rest/workspaces/{workspace}/datastores"
    # )

    # stdin, stdout, stderr = client.exec_command(create_store_cmd)
    # out1 = stdout.read().decode()
    # err1 = stderr.read().decode()

    # # Publicar a camada
    # publish_payload = {
    #     "featureType": {
    #         "name": store_name,
    #         "title": store_name,
    #         "srs": "EPSG:4326"
    #     }
    # }

    # publish_cmd = (
    #     f"curl -s -u admin:geoserver -XPOST "
    #     f"-H 'Content-type: application/json' "
    #     f"-d '{json.dumps(publish_payload)}' "
    #     f"http://localhost:8080/geoserver/rest/workspaces/{workspace}/datastores/{store_name}/featuretypes"
    # )

    # stdin, stdout, stderr = client.exec_command(publish_cmd)
    # out2 = stdout.read().decode()
    # err2 = stderr.read().decode()

    # client.close()

    # if err1 or err2:
    #     print("Erro ao criar datastore ou publicar camada:")
    #     if err1:
    #         print("Datastore:", err1)
    #     if err2:
    #         print("Camada:", err2)
    # else:
    #     print("-----------------------------")
    #     print(out1 + out2)


# upload_geojson_to_geoserver("teste", "geoserver-automation/map.geojson")



def convert_a_file_to_zip(file_name, remote_folder):
    """Converte um arquivo para zip no servidor remoto
    
    :param file_name (str): Nome do arquivo a ser convertido
    :param remote_folder (str): Pasta no servidor onde o arquivo está localizado
    """
    client = start_session()
    zip_name = os.path.splitext(file_name)[0]
    print("o file_name é: ", file_name)
    # input()
    command = f"cd {remote_folder} && zip -r {zip_name}.zip {file_name}"
    
    stdin, stdout, stderr = client.exec_command(command)
    sleep(1)
    if stderr.read():
        print("Error converting to zip:", stderr.read().decode())
        client.close()
    else:
        print(stdout.read().decode())
        client.close()
        return zip_name + ".zip"
        
def exclude_a_file(file_name, remote_folder):
    client = start_session()
    command = f"cd {remote_folder} && rm {file_name}"
    stdin, stdout, stderr = client.exec_command(command)
    sleep(1)
    if stderr.read():
        print("Error excluding file:", stderr.read().decode())
        client.close()
    else:
        print(stdout.read().decode())
        client.close()

def download_a_file_from_s3(file_name_in_s3, remote_folder):
    """Baixar arquivo do S3 e salvar numa pasta no servidor remoto
    
    :param file_name_in_s3: Nome do arquivo no bucket quasar-sensoriamento S3 com a extensão
    :param remote_folder: Pasta no sevidor onde esse arquivo será salvo antes de subir para o geoserver
    """
    client = start_session()
    download_command = f"aws s3 cp s3://quasar-sensoriamento/{file_name_in_s3} {remote_folder}"
    
    stdin, stdout, stderr = client.exec_command(download_command)
    sleep(1)
    if stderr.read():
        print("Error downloading from S3:", stderr.read().decode())
        client.close()
    else:
        print(stdout.read().decode())
        client.close()  
    
def consult_a_workspace_in_geoserver(workspace):
    """Consultar se um workspace existe no Geoserver remoto
    
    :param workspace: Nome do workspace a ser consultado
    :return: 200 se existir ou 404 se não existir
    """    
    client = start_session()
    command = f"/home/ubuntu/anaconda3/bin/curl -s -u admin:geoserver -XGET http://localhost:8080/geoserver/rest/workspaces/{workspace}"
    
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    client.close()

    if error:
        return print("Erro:\n", error)
    try:
        data = json.loads(output)
        if "workspace" in data:
            print(f"Workspace '{workspace}' existe.")
            return 200
        else:
            print(f"Resposta JSON recebida, mas sem chave 'workspace':\n{data}")
            return 404
    except json.JSONDecodeError:
        if "No such workspace" in output or output.strip() == "":
            print(f"Workspace '{workspace}' não existe.")
            return 404
        else:
            print(f"Erro desconhecido ):\n{output}")
            return 400
        
        
def create_a_workspace_in_geoserver(workspace):
    """Cria um workspace no geoserver remoto

    Args:
        workspace (str): Nome do workspace a ser criado
        
    Returns:
        201 se criado com sucesso ou 400 se erro 
    """
    client = start_session()
    command = f"/home/ubuntu/anaconda3/bin/curl -s -u admin:geoserver -XPOST -H 'Content-type: application/json' -d '{{\"workspace\": {{\"name\": \"{workspace}\"}}}}' http://localhost:8080/geoserver/rest/workspaces"
    
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    client.close()

    if error:
        return print("Erro:\n", error)
    else:
        return print(f"Workspace '{workspace}' criado com sucesso!\n", output)
          

def upload_any_file_to_geoserver(workspace, path_file, store_name=None):
    _, ext = os.path.splitext(path_file)
    ext = ext.lower()

    if store_name is None:
        filename = os.path.basename(path_file)
        store_name = os.path.splitext(filename)[0]

    if ext == ".shp" or ext == ".zip":
        upload_zip_to_geoserver(workspace, path_file, store_name)
    elif ext in [".tif", ".tiff"]:
        file_name = os.path.basename(path_file)
        remote_folder = os.path.dirname(path_file)
        zip_tif_name = convert_a_file_to_zip(file_name, remote_folder)
        zip_tif_path = os.path.join(remote_folder, zip_tif_name).replace("\\", "/")
        upload_raster_to_geoserver(workspace, zip_tif_path, store_name)
    elif ext == ".geojson":
        upload_geojson_to_geoserver(workspace, path_file, store_name)
        # exclude_a_file(os.path.splitext(file_name)[0]+".zip", remote_folder)
    else:
        print(f"Extensão '{ext}' não suportada para upload.")
    

    
def list_files_in_s3():
    """Listar arquivos em um bucket S3
    
    :param bucket_name: Nome do bucket S3
    :return: Lista de arquivos no bucket
    """
    client = start_session()
    command = f"aws s3 ls s3://quasar-sensoriamento/"
    
    stdin, stdout, stderr = client.exec_command(command)
    sleep(1)
    if stderr.read():
        print("Error listing files in S3:", stderr.read().decode())
        client.close()
    else:
        print(stdout.read().decode())
        client.close()
        
        
def connect_to_db(db_info):
    db_cred = json.load(open(db_info))
    engine = sqlalchemy.create_engine('postgresql://{0}:{1}@{2}:{3}/{4}'.format(db_cred['user'], db_cred['password'], db_cred['host'], db_cred['port'], db_cred['database']))
    return engine

def execute_query(qry, db_info):
    engine = connect_to_db(db_info)
    try:
        with engine.connect() as con:
            rs = con.execute(sqlalchemy.text(qry))
            con.commit()
            con.close()
            return rs
    except Exception as e:
        raise e
    

def get_layers_from_workspace(workspace):
    """
    Faz um GET no Geoserver para listar as layers de um workspace específico.
    Retorna o resultado como dict.
    """
    client = start_session()
    command = f'/home/ubuntu/anaconda3/bin/curl -s -u admin:geoserver -XGET http://localhost:8080/geoserver/rest/workspaces/{workspace}/layers.json'
    stdin, stdout, stderr = client.exec_command(command)
    sleep(2)
    output = stdout.read().decode()
    error = stderr.read().decode()
    client.close()
    if error:
        print("Erro ao buscar layers:", error)
        return None
    try:
        result = json.loads(output)
        return result
    except Exception as e:
        print("Erro ao decodificar JSON:", e)
        return None

def geoserver_get_layers_and_query(workspace, db_info, schema):
    try:
        result = get_layers_from_workspace(workspace)
        if result and result.get('layers') and result['layers'].get('layer'):
            for layer in result['layers']['layer']:
                layer_name = layer.get('name')
                layer_href = layer.get('href')
                geoserver_layer_name = workspace + ":" + layer_name

                qry = f"""
                INSERT INTO {schema}.geoserver_layers
                (layer_name, geoserver_workspace, geoserver_layer_name, geoserver_layer_url)
                VALUES(
                    '{layer_name}', '{workspace}', '{geoserver_layer_name}', '{layer_href}'
                )
                """
                try:
                    execute_query(qry, db_info)
                    print(f"Layer '{geoserver_layer_name}' inserted successfully.")
                except psycopg2.errors.UniqueViolation:
                    print(f"A camada '{geoserver_layer_name}' já existe no banco.")
                except Exception as e:
                    print(f"Erro ao inserir layer '{geoserver_layer_name}': {e}")

            print(f"Was uploaded {len(result['layers']['layer'])} layers to database.")

        else:
            print("No layers found in workspace: " + workspace)
            return
    except Exception as e:
        print("Erro!!! ", e)
        return