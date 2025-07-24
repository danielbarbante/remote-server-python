from ssh import (list_files_in_s3, download_a_file_from_s3,
                 view_folder_contents, convert_a_file_to_zip,
                 exclude_a_file, list_workspaces_in_geoserver,
                 upload_any_file_to_geoserver, geoserver_get_layers_and_query)

def mega_operation():
    """Faz um monte de coisa
    
    """
    option = 99
    
    while option != 0:
        option = int(input("Escolha uma opção:\n"
                        "1. Listar arquivos no bucket quasar-sensoriamento\n"
                        "2. Baixar um arquivo do bucket quasar-sensoriamento para uma pasta já criada\n"
                        "3. Subir um arquivo para o bucket quasar-sensoriamento\n"
                        "4. Listar arquivos de uma pasta no servidor\n"
                        "5. Subir arquivo de uma pasta para o Geoserver\n"
                        "6. Listar workspaces\n"
                        "7. Subir camadas de um workspace para o banco\n"
                        "0. Exit\n"
                            ))
        if option == 1:
            list_files_in_s3()
        elif option == 2:
            download_a_file_from_s3(
                str(input("Digite o nome do arquivo no biucket quasar-sensoriamento: ")),
                str(input("Digite o caminho da pasta onde o arquivo será salvo: "))
            )
        elif option == 3:
            print("):")
        elif option == 4:
            view_folder_contents(
                str(input("nome e caminho da pasta: "))
            )
        elif option == 5:
            file = str(input("Caminho e nome do arquivo: "))
            workspace = str(input("Nome do workspace: "))
            upload_any_file_to_geoserver(workspace, file)
        elif option == 6:
            list_workspaces_in_geoserver()
        elif option == 7:
            workspace = str(input("Nome do workspace: "))
            db_info = "./info_db.json"
            schema = "playground"
            geoserver_get_layers_and_query(workspace,db_info, schema)
            
                
        
            
            
            
mega_operation()