from pyAesCrypt import encryptFile, decryptFile
import os

while True:
    try:
        decryptFile('OSINT.db.enc','OSINT.db',input('Enter the password to decrpyt the db >> ') ,1024 * 64)
        os.remove('OSINT.db.enc')  
        print("FILE DECRYPTED!")
        break
    except ValueError:
        print('Wrong password!')