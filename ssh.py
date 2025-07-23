import paramiko
import os
from dotenv import load_dotenv
from time import sleep

load_dotenv()

ssh_path = "./quasar-geoserver-3.pem"
ip = os.getenv('IP')
# port = os.getenv('PORT')
user = os.getenv('USER')
# password = os.getenv('PASSWORD')



def start_session():
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
    """Subindo shapefile para o GS remoto
    
    :param workspace: Nome do workspace para subir a camada
    :param path_file: Caminho de onde está o zip
    :param
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
        print("Erro:\n", error)
    else:
        print("Upload concluído com sucesso!")
        print(output)

    

def server_operation(file_name_in_s3, remote_folder):
    """Baixar arquivo do S3 e subir para o geoserver
    
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
    
    