import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
import gnupg
import psycopg2
from psycopg2 import sql
from typing import Optional

# Configurazione di GPG
gpg_home = os.getenv('GNUPGHOME', '/Users/stek/.gnupg')
gpg = gnupg.GPG(gnupghome=gpg_home)

# Carica le variabili d'ambiente
load_dotenv()


def send_email(to_email, subject, message, encrypt=False, sign=False):
    """Invia un'email, con opzioni per cifrare e/o firmare il messaggio."""
    # Crittografia, se richiesta
    if encrypt:
        public_key = get_recipient_key(to_email)
        if not public_key:
            raise ValueError("Public key not found for recipient")
        message = encrypt_message(message, public_key)

    # Firma, se richiesta
    if sign:
        message = sign_message(message)

    # Configurazione email
    from_email = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASSWORD')
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Avvia TLS
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print('Email sent successfully')
    except Exception as e:
        print(f'Failed to send email: {e}')


def sign_message(message):
    """Firma un messaggio con la chiave privata del mittente.
            (usa la tua chiave privata)
    """
    signed_data = gpg.sign(
        message, keyid='BDFCF22CDC3FD0F9DAB3B1ED1A3E214268D8FA16'
    )
    if not signed_data:
        raise ValueError(f"Signing failed: {signed_data.status}")
    return str(signed_data)


def verify_signature(signed_message):
    """Verifica la firma di un messaggio firmato."""
    verified = gpg.verify(signed_message)
    return verified.valid


def encrypt_message(message, recipient_public_key):
    """Cifra un messaggio usando la chiave pubblica del destinatario."""
    import_result = gpg.import_keys(recipient_public_key)
    encrypted_data = gpg.encrypt(message, import_result.fingerprints[0])
    if not encrypted_data.ok:
        raise ValueError(f"Encryption failed: {encrypted_data.status}")
    return str(encrypted_data)


def decrypt_message(encrypted_message, passphrase):
    """Decifra un messaggio cifrato usando una passphrase."""
    decrypted_data = gpg.decrypt(encrypted_message, passphrase=passphrase)
    if not decrypted_data.ok:
        print(f"Decryption failed: {decrypted_data.status}")
        return None
    decrypted_message = str(decrypted_data)
    if verify_signature(decrypted_message):
        print("The message is authentic.")
    else:
        print("The message could not be verified.")
    return decrypted_message


def get_recipient_key(email: str) -> Optional[str]:
    """Recupera la chiave pubblica del destinatario dal database.
            (Utilizza il tuo db)
    """
    conn_params = {
        'dbname': 'db_Crittografia',
        'user': 'stek',
        'password': 'stek765',
        'host': 'localhost',
        'port': '5440'
    }
    try:
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        cursor.execute(sql.SQL(
            "SELECT public_key FROM recipient_keys WHERE email = %s"), (email,)
        )
        result = cursor.fetchone()
        return result[0] if result else None
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
