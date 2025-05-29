const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      enableRemoteModule: false,
      nodeIntegration: false
    }
  });

  mainWindow.loadFile('templates/index.html');

  mainWindow.on('closed', function () {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});

ipcMain.handle('send-to-backend', async (event, data) => {
  console.log('IPC Received in main.js:', data); // Log incoming IPC data
  try {
    // Varsayılan metod POST, ama data.method varsa onu kullan
    const method = data.method || 'POST';
    // GET istekleri için body gönderilmez
    const fetchOptions = {
      method: method,
      headers: {
        'Content-Type': 'application/json'
      }
    };
    
    // Sadece GET dışı metodlarda body ekle
    if (method !== 'GET') {
      fetchOptions.body = JSON.stringify(data.body);
    }

    const response = await fetch(data.url, fetchOptions);
    console.log('Fetch Response Status:', response.status); // Log HTTP status
    const result = await response.json();
    console.log('Fetch Response Data:', result); // Log response data
    
    if (response.ok) {
      return result;
    } else {
      throw new Error(result.detail || 'Backend hatası');
    }
  } catch (error) {
    console.error('Fetch Error:', error.message); // Log fetch errors
    throw error;
  }
});