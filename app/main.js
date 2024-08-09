const { app, ipcMain } = require('electron');
const axios = require('axios');
const readline = require('readline');
const fs = require('fs');

// Using https for CLIENT calls to API (use ur ngrok link)
const NGROK_URL = 'https://4783-46-141-86-75.ngrok-free.app';

function startCli() {
  // Configura l'interfaccia per l'input/output del terminale
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  // Funzione per validare l'email
  function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  // Funzione per chiedere il comando all'utente
  function askCommand() {
    rl.question('Inserisci un comando (es. "encrypt", "decrypt", "send", "exit"): ', (answer) => {

      // Gestione del comando "encrypt"
      if (answer === 'encrypt') {
        rl.question('Inserisci il messaggio da cifrare: ', async (message) => {
          rl.question('Inserisci l\'email del destinatario: ', async (recipientEmail) => {
            if (!validateEmail(recipientEmail)) {
              console.error('Errore: Indirizzo email non valido.');
              return askCommand(); // Chiede il prossimo comando
            }
            try {
              // Chiamata API per cifrare il messaggio
              const response = await axios.post(`${NGROK_URL}/encrypt`, { message, recipientEmail });
              console.log(`Messaggio cifrato: ${response.data.encryptedMessage}`);
              askCommand(); // Chiede il prossimo comando
            } catch (error) {
              console.error('Errore durante la cifratura:', error);
              askCommand(); // Chiede il prossimo comando
            }
          });
        });

      // Gestione del comando "decrypt"
      } else if (answer === 'decrypt') {
        rl.question('Inserisci il percorso del file contenente il messaggio cifrato (assoluto): ', async (filePath) => {
          if (!fs.existsSync(filePath)) {
            console.error('Errore: Il percorso del file non è valido.');
            return askCommand(); // Chiede il prossimo comando
          }
          rl.question('Inserisci la passphrase: ', async (passphrase) => {
            try {
              // Legge il messaggio cifrato dal file
              const encryptedMessage = fs.readFileSync(filePath, 'utf-8');
              // Chiamata API per decifrare il messaggio
              const response = await axios.post(`${NGROK_URL}/decrypt`, { encryptedMessage, passphrase });
              console.log(`Messaggio decifrato: ${response.data.decryptedMessage}`);
              askCommand(); // Chiede il prossimo comando
            } catch (error) {
              console.error('Errore durante la decifratura:', error);
              askCommand(); // Chiede il prossimo comando
            }
          });
        });

      // Gestione del comando "send"
      } else if (answer === 'send') {
        rl.question('Inserisci l\'email del destinatario: ', async (toEmail) => {
          if (!validateEmail(toEmail)) {
            console.error('Errore: Indirizzo email non valido.');
            return askCommand(); // Chiede il prossimo comando
          }
          rl.question('Inserisci l\'oggetto dell\'email: ', async (subject) => {
            if (!subject) {
              console.error('Errore: L\'oggetto non può essere vuoto.');
              return askCommand(); // Chiede il prossimo comando
            }
            rl.question('Inserisci il corpo dell\'email: ', async (message) => {
              if (!message) {
                console.error('Errore: Il corpo del messaggio non può essere vuoto.');
                return askCommand(); // Chiede il prossimo comando
              }
              rl.question('Vuoi cifrare l\'email? (yes/no): ', async (encryptAnswer) => {
                const encrypt = encryptAnswer.toLowerCase() === 'yes';
                rl.question('Vuoi firmare l\'email? (yes/no): ', async (signAnswer) => {
                  const sign = signAnswer.toLowerCase() === 'yes';
                  try {
                    // Chiamata API per inviare l'email con le opzioni di cifratura e firma
                    const response = await axios.post(`${NGROK_URL}/send`, { 
                      to_email: toEmail, 
                      subject, 
                      message, 
                      encrypt, 
                      sign 
                    });
                    console.log(`Risposta del server: ${response.data.message}`);
                    askCommand(); // Chiede il prossimo comando
                  } catch (error) {
                    console.error('Errore durante l\'invio dell\'email:', error);
                    askCommand(); // Chiede il prossimo comando
                  }
                });
              });
            });
          });
        });

      // Gestione del comando "exit"
      } else if (answer === 'exit') {
        rl.close(); // Chiude l'interfaccia di input/output
        app.quit(); // Chiude l'applicazione Electron
      } else {
        console.log('Comando non riconosciuto.');
        askCommand(); // Chiede il prossimo comando
      }
    });
  }

  askCommand(); // Avvia il ciclo delle domande
}

// Eventi del ciclo di vita dell'app Electron
app.whenReady().then(() => {
  console.log("App avviata da terminale!");
  startCli(); // Avvia l'interfaccia a riga di comando
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit(); // Chiude l'app su piattaforme diverse da macOS
});

app.on('activate', () => {
  // Ricrea una finestra nell'app quando l'icona dock è cliccata su macOS
});
