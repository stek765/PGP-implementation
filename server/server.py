import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
import re
import email_handler


# Configurazione dell'app Flask
app = Flask(__name__)

# Chiave segreta per CSRF protection (# Genera una chiave segreta di 24 byte)
app.config['SECRET_KEY'] = os.urandom(24)

csrf = CSRFProtect(app)  # Protezione contro CSRF
CORS(app)  # Abilita CORS per tutte le rotte


# Route per la pagina principale
@app.route('/')
def index():
    return render_template('index.html')


# Route per inviare email
@app.route('/send', methods=['POST'])
@csrf.exempt  # Esclude questa route dalla protezione CSRF
def send_email():
    data = request.get_json()               # Ottiene i dati della richiesta
    to_email = data.get('to_email')         # Email del destinatario
    subject = data.get('subject')           # Oggetto dell'email
    message = data.get('message')           # Corpo del messaggio
    encrypt = data.get('encrypt', False)    # Se cifrare il messaggio?
    sign = data.get('sign', False)          # Se firmare il messaggio?

    # Validazione dell'input
    if not re.match(r"[^@]+@[^@]+\.[^@]+", to_email):
        return jsonify({'error': 'Invalid email address'}), 400
    if not subject or not message:
        return jsonify({'error': 'Subject and message are required'}), 400

    # Tentativo di invio email
    try:
        email_handler.send_email(to_email, subject, message, encrypt, sign)
        return jsonify({'message': 'Email sent successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to send email: {str(e)}'}), 500


# Route per cifrare un messaggio
@app.route('/encrypt', methods=['POST'])
@csrf.exempt  # Esclude questa route dalla protezione CSRF
def encrypt():
    data = request.json  # Ottiene i dati della richiesta JSON
    message = data.get('message')  # Messaggio da cifrare
    recipient_email = data.get('recipientEmail')  # Email del destinatario

    # Validazione dell'input
    if not message or not recipient_email:
        return jsonify({'error': 'Message and recipient email required'}), 400

    # Tentativo di cifratura
    try:
        recipient_key = email_handler.get_recipient_key(recipient_email)
        if not recipient_key:
            return jsonify({'error': 'Recipient key not found'}), 404

        encrypted_message = email_handler.encrypt_message(
            message, recipient_key
        )
        return jsonify({'encryptedMessage': encrypted_message}), 200
    except Exception as e:
        return jsonify({'error': f'Encryption failed: {str(e)}'}), 500


# Route per decifrare un messaggio
@app.route('/decrypt', methods=['POST'])
@csrf.exempt  # Esclude questa route dalla protezione CSRF
def decrypt():
    data = request.json  # Ottiene i dati della richiesta JSON
    encrypted_message = data.get('encryptedMessage')  # Messaggio cifrato
    passphrase = data.get('passphrase')  # Passphrase per la decifratura

    # Validazione dell'input
    if not encrypted_message or not passphrase:
        return jsonify({'error': 'Encrypted msg and psphrs required'}), 400

    # Tentativo di decifratura
    try:
        decrypted_message = email_handler.decrypt_message(
            encrypted_message, passphrase
        )
        if decrypted_message:
            return jsonify({'decryptedMessage': decrypted_message}), 200
        else:
            return jsonify({'error': 'decrpt failed or signatr invalid'}), 500
    except Exception as e:
        return jsonify({'error': f'Decryption failed: {str(e)}'}), 500


# Avvio del server Flask
if __name__ == '__main__':
    app.run(port=3900)
