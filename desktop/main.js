// SmartEye Price Manager — Windows app (Electron). Loads the same files as smarteye.am/calc.
const { app, BrowserWindow, shell, ipcMain } = require('electron');
const fs = require('fs');
const { execFile, spawn } = require('child_process');
const path = require('path');

function createWindow() {
  const win = new BrowserWindow({
    width: 560, height: 920, minWidth: 380, minHeight: 600,
    backgroundColor: '#dfe6ef',
    title: 'SmartEye Price Manager',
    icon: path.join(__dirname, 'icon.png'),
    autoHideMenuBar: true,
    webPreferences: { contextIsolation: true, sandbox: true, nodeIntegration: false, preload: path.join(__dirname, 'preload.js') }
  });
  win.loadFile(path.join(__dirname, 'www', 'index.html'));
  // PDF downloads: save straight to the Downloads folder and show the file, so it can be dragged into Telegram / Viber / WhatsApp
  win.webContents.session.on('will-download', (e, item) => {
    const file = path.join(app.getPath('downloads'), item.getFilename());
    item.setSavePath(file);
    item.once('done', (ev, state) => { if (state === 'completed') shell.showItemInFolder(file); });
  });
  // Instagram / Telegram / Viber / WhatsApp / any web link → default browser or app
  win.webContents.setWindowOpenHandler(({ url }) => { shell.openExternal(url).catch(() => {}); return { action: 'deny' }; });
  win.webContents.on('will-navigate', (e, url) => {
    if (!url.startsWith('file:')) { e.preventDefault(); shell.openExternal(url); }
  });
}

// ---- send a PDF to Telegram / Viber / WhatsApp ----
function regCommand(key) {
  return new Promise(res => execFile('reg', ['query', key, '/ve'], { windowsHide: true }, (err, out) => {
    if (err) return res(null);
    const m = String(out).match(/REG_SZ\s+(.+)/); if (!m) return res(null);
    const exe = (m[1].match(/^"([^"]+)"/) || m[1].match(/^(\S+\.exe)/i) || [])[1];
    res(exe && fs.existsSync(exe) ? exe : null);
  }));
}
async function telegramExe() {
  const c = [
    path.join(process.env.APPDATA || '', 'Telegram Desktop', 'Telegram.exe'),
    path.join(process.env.LOCALAPPDATA || '', 'Programs', 'Telegram Desktop', 'Telegram.exe'),
    path.join(process.env.ProgramFiles || 'C:\\Program Files', 'Telegram Desktop', 'Telegram.exe')
  ].find(p => p && fs.existsSync(p));
  return c || await regCommand('HKCU\\Software\\Classes\\tg\\shell\\open\\command') || await regCommand('HKCR\\tg\\shell\\open\\command');
}
const APP_LINKS = { telegram: 'tg://', viber: 'viber://chats', whatsapp: 'whatsapp://' };
ipcMain.handle('send-file', async (e, { app: target, name, bytes }) => {
  const safe = String(name || 'SmartEye.pdf').replace(/[\\/:*?"<>|]+/g, '_');
  const file = path.join(app.getPath('downloads'), safe);
  fs.writeFileSync(file, Buffer.from(bytes));
  if (target === 'telegram') {
    const exe = await telegramExe();
    if (exe) {
      // Telegram Desktop opens «choose a chat» with the file already attached
      spawn(exe, ['-sendpath', file], { detached: true, stdio: 'ignore', windowsHide: false }).unref();
      return { ok: true, direct: true, file };
    }
  }
  shell.showItemInFolder(file);
  if (APP_LINKS[target]) shell.openExternal(APP_LINKS[target]).catch(() => {});
  return { ok: true, direct: false, file };
});

// Print: the PDF carries an auto-print flag, so the system PDF viewer (Edge/Acrobat) opens straight into the print dialog.
ipcMain.handle('print-file', async (e, { name, bytes }) => {
  const safe = String(name || 'SmartEye.pdf').replace(/[\\/:*?"<>|]+/g, '_');
  const dir = path.join(app.getPath('temp'), 'smarteye-print');
  fs.mkdirSync(dir, { recursive: true });
  const file = path.join(dir, safe);
  fs.writeFileSync(file, Buffer.from(bytes));
  const err = await shell.openPath(file);
  return { ok: !err, err, file };
});

const single = app.requestSingleInstanceLock();
if (!single) app.quit();
else {
  app.on('second-instance', () => { const w = BrowserWindow.getAllWindows()[0]; if (w) { if (w.isMinimized()) w.restore(); w.focus(); } });
  app.whenReady().then(createWindow);
  app.on('window-all-closed', () => app.quit());
}
