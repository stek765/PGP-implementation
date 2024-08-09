# PGP-implementation
Applicazione del protocollo PGP (Preatty Good Privacy) per inviare mail in modo da rispettare: CONFIDENZIALITÀ, INTEGRITÀ E AUTENTICITÀ.
- - - - - - - - -  - - - -

# Secure PGP Email Application
This application enables secure email operations using PGP encryption and signatures, facilitated through a local server exposed securely to the internet via Ngrok.


## Overview
The application provides an interface for users to perform the following PGP operations:
- **Encrypt Messages**: Secure your messages by encrypting them with the recipient's public key.
- **Decrypt Messages**: Access the original content of encrypted messages using your private key and passphrase.
- **Sign Messages**: Authenticate your messages with a digital signature using your private key.
- **Send Secure Emails**: Combine encryption and signing to send emails that are both confidential and authenticated.


## Architecture
The architecture is designed to ensure secure and reliable communication:

1. **Client (App)**: The user interacts with the application, which sends HTTPS requests to the server for various PGP operations.
2. **Ngrok**: Creates a secure tunnel that exposes the local server to the internet via a public HTTPS URL, ensuring that all data in transit is encrypted.
3. **Local Server**: Handles the core PGP operations:
   - **Encryption**: Encrypts messages using the recipient's public key.
   - **Decryption**: Decrypts messages using the recipient's private key.
   - **Email Sending**: Sends the encrypted and/or signed messages via a configured SMTP server.
4. **SMTP Server**: Delivers the secure emails to the intended recipient, ensuring the email is transmitted securely.



## Security Features
- **HTTPS Communication**: All API calls between the client and server are secured using HTTPS, protecting data in transit.
- **PGP Encryption**: Ensures the confidentiality of the message content.
- **PGP Signing**: Validates the authenticity and integrity of the messages.


## Getting Started
To get started with this application, follow the steps below:

1. **Set Up Ngrok**: Install and configure Ngrok to expose your local server.
2. **Install Dependencies**: Use `npm install` to set up the client environment.
3. **Configure Environment Variables**: Set up the required environment variables such as email credentials and PGP key paths.
4. **Run the Application**: Start the local server and interact with it through the client interface.
