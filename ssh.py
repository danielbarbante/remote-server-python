import paramiko as pm
import os
from dotenv import load_dotenv

client = pm.SSHClient()
client.set_missing_host_key_policy(pm.AutoAddPolicy())