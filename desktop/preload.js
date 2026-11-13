// Small bridge for the page: save a PDF and hand it straight to Telegram (or show it for drag & drop).
const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('smarteyeDesktop', {
  sendFile: (app, name, bytes) => ipcRenderer.invoke('send-file', { app, name, bytes }),
  printFile: (name, bytes) => ipcRenderer.invoke('print-file', { name, bytes })
});
