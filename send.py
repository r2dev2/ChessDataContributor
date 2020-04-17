import smtplib
from email.message import EmailMessage

import passw

def send(emsg: str, txt: str = None) -> None:
    USERNAME = passw.USERNAME
    # PASSWORD = os.environ("CONTRIBPASS")
    PASSWORD = passw.PASSWORD
    TO_EMAIL = passw.TO_EMAIL
    msg = EmailMessage()
    msg["From"] = USERNAME
    msg["Subject"] = "Chess data"
    msg["To"] = TO_EMAIL
    msg.set_content(emsg)
    if not txt is None:
        msg.add_attachment(open(txt, 'r').read(), filename=txt)

    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.ehlo()
    s.starttls()
    s.login(USERNAME, PASSWORD)
    s.send_message(msg)

def sendNotification(username: str, filename: str) -> None:
    send(f"{username} is starting {filename}.")

def sendFile(username: str, filename: str) -> None:
    send(f"{username} has finished {filename}.", filename)

def main():
    send("Test mail")
    # sendFile("r2dev2", "dest/Berliner.txt")

if __name__ == "__main__":
    main()
