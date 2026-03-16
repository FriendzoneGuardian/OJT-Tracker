const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let flaskProcess;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        backgroundColor: '#09090b', // zinc-950 matching the UI
        title: 'OJT-Tracker v1.6.1',
        icon: path.join(__dirname, 'static/favicon.ico'),
        show: false, // Don't show until ready-to-show to prevent white flicker
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
        }
    });

    // v1.6.1: Load local loading screen first
    mainWindow.loadFile(path.join(__dirname, 'templates/loading.html'));

    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
    });

    // v1.3.2/v1.6.1: Robust Reload Logic
    mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL) => {
        // Only retry if we're trying to reach the Flask server
        if (validatedURL.includes('127.0.0.1:8080')) {
            console.log('Backend not ready. Retrying in 1s...');
            setTimeout(() => {
                if (mainWindow) mainWindow.loadURL('http://127.0.0.1:8080');
            }, 1000);
        }
    });

    mainWindow.on('closed', function () {
        mainWindow = null;
    });
}

function startFlask() {
    // Reveal window immediately with loading screen
    createWindow();

    // In production, we'll spawn the bundled EXE. In development, we use python.
    const pythonPath = process.env.NODE_ENV === 'production' ? path.join(__dirname, 'dist/app.exe') : 'python';
    const scriptPath = process.env.NODE_ENV === 'production' ? '' : path.join(__dirname, 'app.py');

    const args = scriptPath ? [scriptPath] : [];
    
    flaskProcess = spawn(pythonPath, args, {
        cwd: __dirname,
        env: { ...process.env, FLASK_ENV: 'production' }
    });

    flaskProcess.stdout.on('data', (data) => {
        const output = data.toString();
        console.log(`Flask: ${output}`);

        // v1.6.1 Handshake Detection
        if (output.includes('Engine Ready') || output.includes('Running on http://127.0.0.1:8080')) {
            console.log('Handshake Confirmed. Navigating to Dashboard...');
            setTimeout(() => {
               if (mainWindow) mainWindow.loadURL('http://127.0.0.1:8080');
            }, 500); // Small buffer for network stabilization
        }
    });

    flaskProcess.stderr.on('data', (data) => {
        console.error(`Flask Error: ${data}`);
    });
}

app.on('ready', startFlask);

app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') {
        if (flaskProcess) flaskProcess.kill();
        app.quit();
    }
});

app.on('activate', function () {
    if (mainWindow === null) {
        createWindow();
    }
});

app.on('quit', () => {
    if (flaskProcess) flaskProcess.kill();
});
