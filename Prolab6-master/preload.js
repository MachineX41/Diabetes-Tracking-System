const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  sendToBackend: (data) => ipcRenderer.invoke('send-to-backend', data)
});