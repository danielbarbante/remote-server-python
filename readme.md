# Projeto: Automação Remota para Geoserver e AWS S3

Este projeto permite gerenciar arquivos e camadas geoespaciais em um servidor remoto, integrando operações com o Geoserver e o bucket S3 `quasar-sensoriamento`. As operações são realizadas via SSH e comandos REST, facilitando o fluxo de trabalho para uploads, downloads, listagens e integração com banco de dados.

## Antes de iniciar

```
python -m venv venv
```
```
venv\Scripts\Activate
```
```
pip install -r requirements.txt
```

## Funcionalidades

O sistema oferece um menu interativo com as seguintes opções:

1. **Listar arquivos no bucket S3**  
   Exibe todos os arquivos presentes no bucket `quasar-sensoriamento`.

2. **Baixar arquivo do bucket S3 para uma pasta**  
   Permite baixar um arquivo do S3 para uma pasta já existente no servidor remoto.

3. **Subir arquivo para o bucket S3**  
   (Em desenvolvimento) Permite enviar arquivos do servidor para o bucket S3.

4. **Listar arquivos de uma pasta no servidor**  
   Mostra todos os arquivos de uma pasta específica no servidor remoto.

5. **Subir arquivo de uma pasta para o Geoserver**  
   Faz upload de arquivos (GeoJSON, TIFF, ZIP, etc.) para um workspace do Geoserver.

6. **Listar workspaces no Geoserver**  
   Exibe todos os workspaces cadastrados no Geoserver.

7. **Listar layers de um workspace**  
   Mostra todas as camadas (layers) de um workspace específico do Geoserver.

8. **Subir camadas de um workspace para o banco**  
   Insere informações das layers do workspace em uma tabela do banco de dados.

0. **Sair**  
   Encerra o programa.

## Como Usar

1. **Pré-requisitos**
   - Python 3.x
   - Acesso SSH ao servidor remoto
   - Geoserver rodando no servidor
   - Bucket S3 configurado
   - Banco de dados PostgreSQL configurado (para opção 8)

2. **Instalação**
   - Clone este repositório.
   - Instale as dependências necessárias (veja `requirements.txt` se disponível).
   - Configure as credenciais de acesso SSH e banco de dados.

3. **Execução**
   - Crie o ambiente virtual:
     ```
     python -m venv venv
     venv\Scripts\Activate
     ```
   - Execute o arquivo principal:
     ```
     python super_automation.py
     ```
   - Siga as instruções do menu para realizar as operações desejadas.

## Estrutura dos Arquivos

- `super_automation.py`: Menu principal e integração das funções.
- `ssh.py`: Funções para operações via SSH, manipulação de arquivos, integração com Geoserver e S3.
- `info_db.json`: Arquivo de configuração do banco de dados (utilizado na opção 8).

## Observações

- Algumas funções podem exigir permissões administrativas no servidor remoto.
- Para integração com o banco de dados, ajuste o arquivo `info_db.json` conforme sua configuração.
- O projeto pode ser expandido para suportar outros formatos de arquivo e operações.

## Contribuição

Sinta-se à vontade para abrir issues ou pull requests para melhorias, correções ou novas funcionalidades.

## Licença

Este projeto é distribuído sob a licença MIT. Consulte o arquivo LICENSE

