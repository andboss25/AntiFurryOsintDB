from pyAesCrypt import encryptFile, decryptFile
import os

encryptFile('OSINT.db','OSINT.db.enc',input('Enter a passowrd >> ') ,1024 * 64)
os.remove('OSINT.db')
print("FILE ENCRYPTED!")