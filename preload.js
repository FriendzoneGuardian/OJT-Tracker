const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('__electron_ipc', {
    send: (channel, data) => ipcRenderer.send(channel, data)
});
