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
        title: 'OJT-Tracker v1.3.0',
        icon: path.join(__dirname, 'static/favicon.ico'), // Ensure we have/point to an icon
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
        }
    });

    // Load the Flask app - Using 127.0.0.1 to avoid localhost resolution delays
    mainWindow.loadURL('http://127.0.0.1:8080');

    // v1.3.2 Hotfix: Retry loading if the connection fails (Flask still booting)
    mainWindow.webContents.on('did-fail-load', () => {
        console.log('Connection failed. Retrying in 1s...');
        setTimeout(() => {
            if (mainWindow) mainWindow.loadURL('http://127.0.0.1:8080');
        }, 1000);
    });

    mainWindow.on('closed', function () {
        mainWindow = null;
    });
}

function startFlask() {
    // In production, we'll spawn the bundled EXE. In development, we use python.
    const pythonPath = process.env.NODE_ENV === 'production' ? path.join(__dirname, 'dist/app.exe') : 'python';
    const scriptPath = process.env.NODE_ENV === 'production' ? '' : path.join(__dirname, 'app.py');

    const args = scriptPath ? [scriptPath] : [];
    
    flaskProcess = spawn(pythonPath, args, {
        cwd: __dirname,
        env: { ...process.env, FLASK_ENV: 'production' }
    });

    flaskProcess.stdout.on('data', (data) => {
        console.log(`Flask: ${data}`);
        // If we see the server is up, or after a short delay, create the window
        if (data.toString().includes('Running on http://127.0.0.1:8080') && !mainWindow) {
            createWindow();
        }
    });

    flaskProcess.stderr.on('data', (data) => {
        console.error(`Flask Error: ${data}`);
    });

    // Backup: Create window after 2 seconds regardless
    setTimeout(() => {
        if (!mainWindow) createWindow();
    }, 2000);
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
