const { app, BrowserWindow, Menu, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let apiProcess;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true
        },
        icon: path.join(__dirname, 'icon.png'),
        title: 'LaDashy - Homelab Documentation'
    });

    // Start the API server
    apiProcess = spawn('python', [path.join(__dirname, '../backend/api.py')]);
    
    apiProcess.stdout.on('data', (data) => {
        console.log(`API: ${data}`);
    });

    // Wait a moment for the server to start
    setTimeout(() => {
        mainWindow.loadURL('http://localhost:5000');
    }, 2000);

    mainWindow.on('closed', () => {
        mainWindow = null;
        if (apiProcess) {
            apiProcess.kill();
        }
    });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (mainWindow === null) {
        createWindow();
    }
});
