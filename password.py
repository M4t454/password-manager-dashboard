
from cryptography.fernet import Fernet
import time
import os 

'''def write_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key) '''

def load_key():
    file = open('key.key', "rb")
    key = file.read()
    file.close()
    return key

def verify_master_pwd(master_pwd):
    with open("master_pwd.txt", 'rb') as f:
        stored_pwd = f.read()
    return stored_pwd == master_pwd.encode()

def update_master_pwd(new_master_pwd):
    with open('master_pwd.txt', "wb") as f:
        f.write(new_master_pwd.encode())

def initialize():
    if not os.path.exists('master_pwd.txt'):
        new_master_pwd = input("No master password found. Please set a new master password: ")
        update_master_pwd(new_master_pwd)
        print('Master password set successfully.')

    else:
        with open('master_pwd.txt', 'rb') as f:
            f.read()
        setup_option = input("Type 'setup' to set up a new master password, 'change' to change it, or 'enter' to use the existing one: ").lower()
        if setup_option == 'setup':
            new_master_pwd = input('Set your master password: ')
            update_master_pwd(new_master_pwd)
            print('Master password set succesfully.')
        elif setup_option == 'change':
            current_pwd = input("Enter current master password: ")
            if verify_master_pwd(current_pwd):

                new_master_pwd = input("Enter new master password: ")
                update_master_pwd(new_master_pwd)
                print("Master password updated successfully.")

            else:
                print("Incorrect master password")
        else:
            print('You can now enter your master password.')
            
    

def lockout_timer(duration):
    print(f"Too many failed attempts. Please wait {duration // 60} minutes before trying again.")
    time.sleep(duration)


initialize()
master_pwd = input('What is the master password? ')

attempts = 10
lockout_duration = 1800

while not verify_master_pwd(master_pwd):
    attempts -= 1 
    if attempts == 0:
        lockout_timer(lockout_duration)
        attempts = 10 
    master_pwd = input (f'Incorrect master password. You have {attempts} left. Try again:')


key = load_key()
fer = Fernet(key)


def view():
    with open('password.txt', 'r') as f:
        for lines in f.readlines():
            data = lines.rstrip()
            user, passw = data.split("|")
            print("User:", user, ' | Password:', fer.decrypt(passw.encode()).decode())

def add():
    name = input('Account name: ')
    pwd = input('Password: ')

    with open('password.txt', 'a') as f:
        f.write(name + '|' + fer.encrypt(pwd.encode()).decode() + '\n')
                 
while True:
    mode = input('Would you like to add or view a password (view, add)? q to quit ').lower()
    if mode == 'q':
        break
         
    if mode == 'view':
        view()
         
    elif mode == 'add':
        add()

    else:
        print('Invalid mode.')
        continue