import streamlit as st
from cryptography.fernet import Fernet
import os
import time

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'attempts' not in st.session_state:
    st.session_state.attempts = 10
if 'lockout_time' not in st.session_state:
    st.session_state.lockout_time = None

def write_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    st.write("Loading key...")  # Debugging line
    file = open('key.key', "rb")
    key = file.read()
    file.close()
    st.write(f"Loaded key: {key}")  # Debugging line
    return key

def verify_master_pwd(master_pwd):
    st.write("Verifying master password...")  # Debugging line
    with open("master_pwd.txt", 'rb') as f:
        stored_pwd = f.read()
    st.write(f"Stored password: {stored_pwd}, Input password: {master_pwd.encode()}")  # Debugging line
    return stored_pwd == master_pwd.encode()

def update_master_pwd(new_master_pwd):
    st.write(f"Updating master password to: {new_master_pwd}")  # Debugging line
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

def lockout_timer(duration):
    st.warning(f"Too many failed attempts. Please wait {duration // 60} minutes before trying again.")
    st.session_state.lockout_time = time.time() + duration

def view(fernet):
    st.write("Viewing stored passwords...")  # Debugging line
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

if st.session_state.lockout_time and time.time() < st.session_state.lockout_time:
    st.warning("Account is locked. Please wait a while before trying again.")
elif st.session_state.authenticated:
    option = st.selectbox('Choose an option:', ('View Passwords', 'Add Password', 'Change Master Password'))
    
    if option == 'View Passwords':
        view(fernet)
    elif option == 'Add Password':
        add(fernet)
    elif option == 'Change Master Password':
        current_pwd = st.text_input("Enter current master password:", type="password")
        if st.button("Verify"):
            if verify_master_pwd(current_pwd):
                new_master_pwd = st.text_input("Enter new master password:", type="password")
                if st.button("Change Password"):
                    update_master_pwd(new_master_pwd)
                    st.success("Master password updated successfully!")
            else:
                st.error("Incorrect master password.")
else:
    master_pwd = st.text_input('Enter your master password:', type="password")
    
    if st.button("Unlock"):
        if verify_master_pwd(master_pwd):
            st.session_state.authenticated = True
            st.success("Access granted")
        else:
            st.session_state.attempts -= 1
            st.error(f"Access denied. Incorrect master password. {st.session_state.attempts} attempts left.")
            if st.session_state.attempts <= 0:
                lockout_timer(1800)  # Lockout for 30 minutes
