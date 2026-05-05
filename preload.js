const { contextBridge, ipcRenderer } = require('electron');
const fs = require('fs');
const path = require('path');

contextBridge.exposeInMainWorld('__electron_ipc', {
    send: (channel, data) => ipcRenderer.send(channel, data),
    getLoadingQuotes: () => {
        try {
            const csvPath = path.join(__dirname, 'data', 'loading_quotes.csv');
            if (!fs.existsSync(csvPath)) return [];
            
            const content = fs.readFileSync(csvPath, 'utf8');
            const lines = content.split('\n').slice(1); // Skip header
            
            return lines.filter(line => line.trim() !== '').map(line => {
                // Handle simple CSV (quote,topic) - assuming no commas in quotes for now or simple split
                // Better: find the last comma
                const lastComma = line.lastIndexOf(',');
                if (lastComma === -1) return line.replace(/"/g, '');
                return line.substring(0, lastComma).replace(/"/g, '');
            });
        } catch (e) {
            console.error('Failed to read quotes:', e);
            return [];
        }
    }
});
