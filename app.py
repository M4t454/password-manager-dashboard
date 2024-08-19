import streamlit as st
from cryptography.fernet import Fernet
import os
import time 

# Initialize the attempts variable globally
attempts = 10

def write_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    file = open('key.key', "rb")
    key = file.read()
    file.close()
    return key

def verify_master_pwd(master_pwd):
    st.write("Verifying master password...")  # Debugging line
    with open("master_pwd.txt", 'rb') as f:
        stored_pwd = f.read()
    if stored_pwd == master_pwd.encode():
        return True
    else:
        global attempts
        attempts -= 1
        st.write(f"Access denied. Incorrect master password. {attempts} attempts left.")
        return False

def update_master_pwd(new_master_pwd):
    st.write(f"Updating master password...")  # Debugging line
    with open('master_pwd.txt', "wb") as f:
        f.write(new_master_pwd.encode())

def initialize():
    if not os.path.exists('key.key'):
        write_key()
    if not os.path.exists('master_pwd.txt'):
        new_master_pwd = st.text_input("No master password found. Please set a new master password:", type="password")
        if st.button("Set Password"):
            update_master_pwd(new_master_pwd)
            st.success('Master password set successfully.')

def view(fernet):
    if os.path.exists('password.txt'):
        with open('password.txt', 'r') as f:
            for lines in f.readlines():
                data = lines.rstrip()
                user, passw = data.split("|")
                st.write(f"User: {user} | Password: {fernet.decrypt(passw.encode()).decode()}")

def add(fernet):
    name = st.text_input('Account name:')
    pwd = st.text_input('Password:', type="password")
    if st.button("Save Password"):
        with open('password.txt', 'a') as f:
            f.write(name + '|' + fernet.encrypt(pwd.encode()).decode() + '\n')
        st.success('Password saved successfully!')

# Streamlit App
st.title("Password Manager")

initialize()

key = load_key()
fernet = Fernet(key)

master_pwd = st.text_input('Enter your master password:', type="password")

if st.button("Unlock"):
    if verify_master_pwd(master_pwd):
        st.success("Access granted")
        option = st.selectbox('Choose an option:', ('View Passwords', 'Add Password'))
        
        if option == 'View Passwords':
            view(fernet)
        elif option == 'Add Password':
            add(fernet)
    else:
        if attempts <= 0:
            st.error("Too many failed attempts. Please wait before trying again.")
        else:
            st.error(f"Access denied. Incorrect master password. {attempts} attempts left.")
