import streamlit as st
from cryptography.fernet import Fernet
import os
import time

def write_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    with open('key.key', "rb") as file:
        key = file.read()
    return key

def verify_master_pwd(master_pwd):
    with open("master_pwd.txt", 'rb') as f:
        stored_pwd = f.read()
    return stored_pwd == master_pwd.encode()

def update_master_pwd(new_master_pwd):
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
            st.experimental_rerun()

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

# Initialize the session state
if 'unlocked' not in st.session_state:
    st.session_state.unlocked = False
if 'attempts' not in st.session_state:
    st.session_state.attempts = 10

initialize()

key = load_key()
fernet = Fernet(key)

if not st.session_state.unlocked:
    master_pwd = st.text_input('Enter your master password:', type="password")
    if st.button("Unlock"):
        if verify_master_pwd(master_pwd):
            st.success("Access granted")
            st.session_state.unlocked = True
        else:
            st.session_state.attempts -= 1
            st.error(f"Access denied. Incorrect master password. {st.session_state.attempts} attempts left.")
else:
    option = st.selectbox('Choose an option:', ('View Passwords', 'Add Password'))
    
    if option == 'View Passwords':
        view(fernet)
    elif option == 'Add Password':
        add(fernet)

