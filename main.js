const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let flaskProcess;

// v1.10: Dev Superpowers - Hot Reloading
const isDev = process.argv.includes('--dev');
if (isDev) {
    try {
        require('electron-reloader')(module);
    } catch (_) {}
}


function createWindow() {
    mainWindow = new BrowserWindow({
        width: isDev ? 1800 : 1400, // v1.10: Expand for DevTools
        height: 900,
        backgroundColor: '#09090b', // zinc-950 matching the UI
        title: `OJT-Tracker v1.9.4 ${isDev ? '[DEV MODE]' : ''}`,

        icon: path.join(__dirname, 'static/favicon.ico'),
        show: false, // Don't show until ready-to-show to prevent white flicker
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        }
    });

    // v1.6.1: Load local loading screen first
    mainWindow.loadFile(path.join(__dirname, 'templates/loading.html'));

    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        if (isDev) {
            mainWindow.webContents.openDevTools();
        }
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

    // v1.10: Production Hardening
    if (!isDev) {
        mainWindow.setMenuBarVisibility(false);
    }
}


function startFlask() {
    // Reveal window immediately with loading screen
    createWindow();

    // v1.6.6: Clean Slate Boot - Kill any lingering python processes before starting
    const { execSync } = require('child_process');
    try {
        if (process.platform === 'win32') {
            execSync('taskkill /F /IM python.exe /T', { stdio: 'ignore' });
        }
    } catch (e) {
        // Ignore errors (e.g. no process to kill)
    }

    // v1.6.8: Cold Start Protocol - Automatic venv detection
    let pythonPath = 'python'; // Default fallback
    
    if (process.env.NODE_ENV === 'production') {
        pythonPath = path.join(__dirname, 'dist/app.exe');
    } else {
        const venvPath = process.platform === 'win32' 
            ? path.join(__dirname, 'venv/Scripts/python.exe')
            : path.join(__dirname, 'venv/bin/python');
            
        const fs = require('fs');
        if (fs.existsSync(venvPath)) {
            console.log(`[BOOT] Cold Start: venv detected at ${venvPath}`);
            pythonPath = venvPath;
        } else {
            console.warn('[BOOT] Warning: No venv detected. Falling back to system python.');
        }
    }

    // v1.10.1 Fix: Only omit app.py if we are running the compiled dist/app.exe
    const scriptPath = (pythonPath.endsWith('app.exe')) ? '' : path.join(__dirname, 'app.py');

    const args = scriptPath ? [scriptPath] : [];
    if (isDev && scriptPath) {
        args.push('--debug'); // v1.10: Pass debug flag to Flask
    }
    
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

// v1.9.1 Auto-Update Restart Handler
ipcMain.on('restart-app', () => {
    if (flaskProcess) flaskProcess.kill();
    app.relaunch();
    app.exit(0);
});
