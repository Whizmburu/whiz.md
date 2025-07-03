require('dotenv').config();
const {
  default: makeWASocket,
  DisconnectReason,
  fetchLatestBaileysVersion,
  useMultiFileAuthState,
  downloadMediaMessage,
  getContentType
} = require('@whiskeysockets/baileys');
const qrcodeTerminal = require('qrcode-terminal');
const qrcodeLib = require('qrcode'); // Added for web QR
const express = require('express');
const fs = require('fs');
const path = require('path');
// Note: YouTube, mathjs etc. will be required in specific command files, not globally here.

// --- Local Modules ---
const config = require('./config.js');
const { addLog, getBotLogsForWebUI, MAX_LOG_ENTRIES: MAX_WEB_LOG_ENTRIES } = require('./utils/logger.js');
const { formatAndSendMessage, getBotFooter, formatHiddenLink } = require('./utils/messageFormatter.js');
const { formatUptime } = require('./utils/commandUtils.js');

const startTime = new Date();
const app = express();

const DATA_DIR = process.env.RENDER_DISK_MOUNT_PATH || process.env.DATA_DIR || '.';
if (DATA_DIR !== '.' && !fs.existsSync(DATA_DIR)) {
    try {
        fs.mkdirSync(DATA_DIR, { recursive: true });
        console.log(`[INIT] Created persistent data directory: ${DATA_DIR}`);
    } catch (e) {
        console.error(`[INIT_ERROR] Failed to create data directory ${DATA_DIR}: ${e.message}. Exiting.`);
        process.exit(1);
    }
}
addLog(`${config.botName} v${config.botVersion} (Baileys) starting up...`);
addLog(`Data directory set to: ${path.resolve(DATA_DIR)}`, 'DEBUG');


const BAILEYS_AUTH_PATH = path.join(DATA_DIR, 'baileys_auth_info');
if (!fs.existsSync(BAILEYS_AUTH_PATH)) {
    fs.mkdirSync(BAILEYS_AUTH_PATH, { recursive: true });
    addLog(`Created Baileys auth directory: ${BAILEYS_AUTH_PATH}`, 'DEBUG');
}

let sock = null;
let currentQR = null; // Variable to store the current QR code string
const commandsMap = new Map();

// --- Command Loader ---
async function loadCommands() {
    addLog('[COMMAND_LOADER] Loading commands...');
    commandsMap.clear();
    // Re-enable all command categories
    const commandCategories = ['general', 'media', 'group', 'owner', 'fun', 'search', 'download', 'api_driven'];

    addLog('[COMMAND_LOADER] Loading all command categories.', 'INFO');

    for (const category of commandCategories) {
        const filePath = path.join(__dirname, 'commands', `${category}.js`);
        try {
            if (fs.existsSync(filePath)) {
                delete require.cache[require.resolve(filePath)];
                const commandModules = require(filePath);

                if (Array.isArray(commandModules)) {
                    commandModules.forEach(cmdObj => {
                        if (cmdObj && cmdObj.name && typeof cmdObj.execute === 'function') {
                            commandsMap.set(cmdObj.name.toLowerCase(), cmdObj);
                            addLog(`[COMMAND_LOADER] Loaded command: ${cmdObj.name} from ${category}.js`, 'DEBUG');
                            if (cmdObj.aliases && Array.isArray(cmdObj.aliases)) {
                                cmdObj.aliases.forEach(alias => {
                                    commandsMap.set(alias.toLowerCase(), cmdObj);
                                    addLog(`[COMMAND_LOADER] Loaded alias: ${alias} for ${cmdObj.name}`, 'DEBUG');
                                });
                            }
                        } else {
                            addLog(`[COMMAND_LOADER] Invalid command object structure in ${category}.js`, 'WARNING');
                        }
                    });
                } else {
                     addLog(`[COMMAND_LOADER] ${category}.js did not export an array of commands.`, 'WARNING');
                }
            } else {
                addLog(`[COMMAND_LOADER] Command file not found: ${category}.js`, 'DEBUG');
            }
        } catch (error) {
            addLog(`[COMMAND_LOADER] Error loading commands from ${category}.js: ${error.message}`, 'ERROR');
            console.error(error);
        }
    }
    addLog(`[COMMAND_LOADER] Total commands loaded: ${commandsMap.size}`);
}


// --- Main WhatsApp Connection Logic ---
async function connectToWhatsApp() {
  addLog('[BAILEYS_CONNECT] Attempting to connect to WhatsApp...');
  await loadCommands();

  const { state, saveCreds } = await useMultiFileAuthState(BAILEYS_AUTH_PATH);
  const { version, isLatest } = await fetchLatestBaileysVersion();
  addLog(`[BAILEYS_CONNECT] Using Baileys version: ${version.join('.')}, isLatest: ${isLatest}`);

  sock = makeWASocket({
    version,
    printQRInTerminal: false,
    auth: state,
    browser: [config.botName, 'Chrome', '120.0'],
  });

// --- Helper function to generate command list string ---
function generateCommandListString(loadedCommandsMap, configRef, startTimeRef) {
    const uptime = formatUptime(startTimeRef);
    const lineRepeatCount = 35; // Consistent with menu command

    const topBorder = `╭─⊷ ${configRef.botName} v${configRef.botVersion} ⊶─╮`;
    const bottomLine = `╰─⊷ Type ${configRef.prefixes[0]}menu for descriptions & more! ⊶─╯`; // Updated bottom line
    const mainSectionSeparator = `├${'─'.repeat(lineRepeatCount)}┤`;
    const categorySeparator = (title) => `├─⊷ ${title.toUpperCase()} ⊶─┤`;

    let listText = `${topBorder}\n`;
    listText += `│ Owner   : ${configRef.ownerName}\n`;
    listText += `│ Prefix  : (Multiple - e.g., ${configRef.prefixes.join(', ')})\n`; // Updated Prefix display
    listText += `│ Uptime  : ${uptime}\n`;
    // listText += `│ Repo    : ${configRef.repoUrl}\n`; // Already in the default startup, could be redundant
    // listText += `│ Group   : ${formatHiddenLink(configRef.whatsappGroupUrl)}\n`; // Also in footer

    const commandsByCategory = {};
    const processedCmdNames = new Set(); // To avoid listing aliases as main commands

    loadedCommandsMap.forEach(cmdObj => {
        if (cmdObj && cmdObj.name && cmdObj.category && !processedCmdNames.has(cmdObj.name.toLowerCase())) {
            if (!commandsByCategory[cmdObj.category]) {
                commandsByCategory[cmdObj.category] = [];
            }
            commandsByCategory[cmdObj.category].push(cmdObj);
            processedCmdNames.add(cmdObj.name.toLowerCase());
        }
    });

    listText += `${mainSectionSeparator}\n`;
    listText += `│ *Quick Overview of Commands:*\n`;

    const categoryOrder = ['General', 'Media', 'Utility', 'Search', 'Download', 'Fun', 'Group Admin', 'Owner Only', 'AI & API Tools'];

    for (const category of categoryOrder) {
        if (commandsByCategory[category] && commandsByCategory[category].length > 0) {
            listText += `${categorySeparator(category)}\n`;
            commandsByCategory[category].forEach(cmdDef => {
                const argsDisplay = cmdDef.usage && cmdDef.usage.includes('<') ? ` ${cmdDef.usage.substring(cmdDef.usage.indexOf('<'))}` : (cmdDef.args ? ` ${cmdDef.args}` : '');
                listText += `│ » ${cmdDef.name}${argsDisplay}\n`; // Use '»' and no prefix
            });
        }
    }
    listText += `${mainSectionSeparator.replace('├', '╰').replace('┤', '╯')}\n`;
    listText += bottomLine;
    return listText;
}
// --- End Helper ---

sock.ev.on('connection.update', async (update) => {
    const { connection, lastDisconnect, qr } = update;
    if (qr) {
        currentQR = qr;
        const qrPageUrl = process.env.RENDER_EXTERNAL_URL ? `${process.env.RENDER_EXTERNAL_URL}/qr-code` : `http://localhost:${WEB_SERVER_PORT}/qr-code`;
        addLog(`[BAILEYS_CONNECT] QR code received. Scan it by visiting: ${qrPageUrl}`);
        addLog('[BAILEYS_CONNECT] Fallback QR code will be printed in the terminal shortly.', 'DEBUG');
        qrcodeTerminal.generate(qr, { small: true }, (qrString) => {
            console.log("\n" + qrString + "\n"); // Keep terminal QR as fallback
            addLog('[BAILEYS_CONNECT] Terminal QR code printed.', 'DEBUG');
        });
    } else {
        // If there's no new QR, and connection is not open, clear any old QR
        if (connection !== 'open') {
            currentQR = null;
        }
    }

    if (connection === 'close') {
        currentQR = null; // QR is no longer valid
        const statusCode = lastDisconnect?.error?.output?.statusCode;
        const reason = DisconnectReason[statusCode] || 'Unknown';
        addLog(`[BAILEYS_CONNECT] Connection closed. Status: ${statusCode} (${reason})`, 'WARNING');
        if (statusCode === DisconnectReason.loggedOut || statusCode === DisconnectReason.badSession) {
            addLog('Authentication error. Clearing auth info and attempting to reconnect for new QR.', 'ERROR');
            try { if (fs.existsSync(BAILEYS_AUTH_PATH)) { fs.readdirSync(BAILEYS_AUTH_PATH).forEach(f => fs.unlinkSync(path.join(BAILEYS_AUTH_PATH, f))); addLog('Old auth files deleted.', 'INFO');}} catch (err) { addLog(`Error deleting auth files: ${err.message}`, 'ERROR');}
            connectToWhatsApp();
        } else if (statusCode !== DisconnectReason.connectionReplaced) {
            addLog('Unexpected disconnect or connection issue. Attempting to reconnect...', 'WARNING');
            connectToWhatsApp();
        }
    }
    else if (connection === 'open') {
      currentQR = null; // Successfully connected, QR no longer needed
      addLog(`[BAILEYS_CONNECT] WhatsApp connection opened successfully. ${config.botName} is now online! 🎉`);
      const botJid = sock.user?.id;
      if (botJid) {
        const userName = sock.user?.name || sock.user?.notify || botJid.split('@')[0].split(':')[0]; // Clean up JID if no name

        // Initial connection message - TEMPORARILY SIMPLIFIED
        // const initialConnectMessage = `👋 Hello ${userName}!\n*${config.botName} v${config.botVersion}* is now online and ready.\n\n🔗 My Repo: ${config.repoUrl}`;
        // await formatAndSendMessage(sock, botJid, initialConnectMessage, { withLogo: true, addLog: addLog });

        // Generate and send command list as a follow-up message - TEMPORARILY SIMPLIFIED
        // if (commandsMap.size > 0) {
        //     const commandListMessage = generateCommandListString(commandsMap, config, startTime);
        //     await formatAndSendMessage(sock, botJid, commandListMessage, { withLogo: false, addLog: addLog });
        // } else {
        //     await formatAndSendMessage(sock, botJid, "No commands currently loaded. Please check configuration.", { withLogo: false, addLog: addLog });
        // }
        // addLog("[BAILEYS_CONNECT] Startup notifications sent to self.");

        // Simplified startup message for stability testing - REVERTING TO FULL STARTUP MESSAGES
        // const simpleStartupMsg = `✅ ${config.botName} connected! Ready for basic commands (e.g., !ping).`;
        // try {
        //     await sock.sendMessage(botJid, { text: simpleStartupMsg });
        //     addLog(`[BAILEYS_CONNECT] Sent simplified startup message to self: ${simpleStartupMsg}`, 'INFO');
        // } catch (e) {
        //     addLog(`[BAILEYS_CONNECT] Error sending simplified startup message: ${e.message}`, 'ERROR');
        // }
        // console.log("Bot connected successfully and attempted to send test message to self for stability check.");

        // Re-enable full startup messages:
        // Initial connection message
        const initialConnectMessage = `👋 Hello ${userName}!\n*${config.botName} v${config.botVersion}* is now online and ready.\n\n🔗 My Repo: ${config.repoUrl}`;
        await formatAndSendMessage(sock, botJid, initialConnectMessage, { withLogo: true, addLog: addLog });

        // Generate and send command list as a follow-up message
        if (commandsMap.size > 0) { // Check if commandsMap is populated (it should be, even if only 'general')
            const commandListMessage = generateCommandListString(commandsMap, config, startTime);
            await formatAndSendMessage(sock, botJid, commandListMessage, { withLogo: false, addLog: addLog });
        } else {
            // This case should ideally not be hit if 'general' commands load
            await formatAndSendMessage(sock, botJid, "Bot connected. No commands seem to be loaded, please check configuration.", { withLogo: false, addLog: addLog });
        }
        addLog("[BAILEYS_CONNECT] Full startup notifications sent to self.");

      } else { addLog("[BAILEYS_CONNECT] Could not determine bot JID for startup message.", 'WARNING');}
    }
  });

  sock.ev.on('creds.update', saveCreds);

  sock.ev.on('messages.upsert', async ({ messages }) => {
    const msg = messages[0];
    if (!msg.message || msg.key.fromMe) return;

    const sender = msg.key.remoteJid; // JID of the user or group sending the message
    const originalMsgText = (msg.message?.conversation || msg.message?.extendedTextMessage?.text || msg.message?.imageMessage?.caption || msg.message?.videoMessage?.caption || '').trim();

    let detectedPrefix = null;
    let commandName = null;
    let argsString = '';
    let argsArray = [];

    for (const p of config.prefixes) {
        if (originalMsgText.toLowerCase().startsWith(p)) {
            detectedPrefix = p;
            const commandAndArgs = originalMsgText.substring(detectedPrefix.length).trim();
            const firstSpaceIndex = commandAndArgs.indexOf(' ');
            if (firstSpaceIndex === -1) {
                commandName = commandAndArgs.toLowerCase();
                argsString = ''; argsArray = [];
            } else {
                commandName = commandAndArgs.substring(0, firstSpaceIndex).toLowerCase();
                argsString = commandAndArgs.substring(firstSpaceIndex + 1).trim();
                argsArray = argsString.split(/\s+/);
            }
            addLog(`[MSG_HANDLER] Command: '${commandName}', Prefix: '${detectedPrefix}', Args: "${argsString}" from ${sender}`, 'DEBUG');
            break;
        }
    }

    if (detectedPrefix && commandName) {
        const commandHandler = commandsMap.get(commandName);
        if (commandHandler) {
            try {
                // --- Permission Checks ---
                const ownerJidFromEnv = process.env[config.ownerJidEnvKey];
                // msg.key.participant is the JID of the user who sent the command in a group.
                // sender is the group JID itself if it's a group message.
                // For DMs, msg.key.participant is undefined, and sender is the user's JID.
                const commandSenderJid = msg.key.participant || sender;

                if (commandHandler.ownerOnly === true) {
                    if (!ownerJidFromEnv || !commandSenderJid.startsWith(ownerJidFromEnv.split('@')[0])) {
                        addLog(`[AUTH_FAIL] Non-owner ${commandSenderJid} attempted owner command '${commandName}'.`, 'WARNING');
                        return; // Silently ignore for non-owners
                    }
                }

                const isGroup = sender.endsWith('@g.us');
                if (commandHandler.groupOnly === true && !isGroup) {
                     addLog(`[AUTH_FAIL] Command '${commandName}' used outside a group by ${commandSenderJid}.`, 'WARNING');
                     return formatAndSendMessage(sock, sender, "This command can only be used in groups.", { quotedMsg: msg, addLog: addLog });
                }

                if (commandHandler.adminOnly === true && isGroup) {
                    const groupMeta = await sock.groupMetadata(sender).catch(() => null);
                    const admins = groupMeta?.participants.filter(p => p.admin !== null && p.admin !== undefined).map(p => p.id) || [];

                    if (commandHandler.botMustBeAdmin === true || ['promote', 'demote', 'kick', 'rename', 'chat', 'grouplink_admin_only'].includes(commandHandler.name) ) { // Example check
                        const botIsAdmin = admins.includes(sock.user?.id);
                        if (!botIsAdmin) {
                             addLog(`[AUTH_FAIL] Bot is not admin in group ${sender} for admin command '${commandName}'.`, 'WARNING');
                             return formatAndSendMessage(sock, sender, "I need to be an admin in this group to perform that action.", { quotedMsg: msg, addLog: addLog });
                        }
                    }
                    // Optionally, check if user sending command is admin
                    // const senderIsAdmin = admins.includes(commandSenderJid);
                    // if (!senderIsAdmin) {
                    //    addLog(`[AUTH_FAIL] Non-admin user ${commandSenderJid} tried admin command '${commandName}'.`, 'WARNING');
                    //    return formatAndSendMessage(sock, sender, "Only group admins can use this command.", { quotedMsg: msg, addLog: addLog });
                    // }
                }

                const commandContext = {
                    sock, msg, originalMsgText, argsString, argsArray, config, addLog,
                    formatAndSendMessage, downloadMediaMessage, getContentType, startTime, commandsMap,
                    isGroup, commandSenderJid // Pass these for convenience in command files
                };
                await commandHandler.execute(commandContext);

            } catch (error) {
                addLog(`[CMD_ERROR] Error executing command '${commandName}' for ${sender}: ${error.message}`, 'ERROR');
                console.error(`Full error for ${commandName}:`, error);
                await formatAndSendMessage(sock, sender, `Oops! An error occurred while running \`${commandName}\`. Please try again.`, { quotedMsg: msg, addLog: addLog });
            }
        } else {
            addLog(`[MSG_HANDLER] Unknown command '${commandName}' with prefix '${detectedPrefix}' from ${sender}`, 'DEBUG');
        }
    } else {
        // Non-command message handling (e.g., Auto-Like Status)
        if (msg.key.remoteJid === 'status@broadcast' && msg.key.participant) {
            addLog(`[STATUS] New status detected from contact: ${msg.key.participant} (Msg ID: ${msg.key.id})`);
            try {
                await sock.sendMessage(msg.key.remoteJid, { react: { text: '🔥', key: msg.key }});
                addLog(`[STATUS] Reacted with '🔥' to status from ${msg.key.participant}`);
            } catch (statusErr) {
                addLog(`[STATUS] Failed to react to status from ${msg.key.participant}: ${statusErr.message}`, 'ERROR');
            }
        }
    }
  });
  return sock;
}

// --- Express Web Server for Bot Logs ---
const WEB_SERVER_PORT = process.env.PORT || process.env.BOT_WEB_PORT || 3001;
app.set('views', path.join(__dirname, 'bot_views'));
app.set('view engine', 'ejs');
app.use('/bot-static', express.static(path.join(__dirname, 'bot_public')));

app.get('/', (req, res) => {
    addLog(`[BOT_WEB] Root path '/' accessed.`);
    res.render('index', {
        title: `${config.botName} - Home`,
        botName: config.botName,
        botVersion: config.botVersion,
        ownerName: config.ownerName
    });
});

app.get('/bot-log', (req, res) => {
    addLog(`[BOT_WEB] /bot-log page accessed.`);
    res.render('log', {
        title: `${config.botName} Bot Live Logs`,
        MAX_LOG_ENTRIES: MAX_WEB_LOG_ENTRIES
    });
});

app.get('/qr-code', async (req, res) => {
    addLog(`[BOT_WEB] /qr-code page accessed.`);
    if (currentQR) {
        try {
            const qrDataUrl = await qrcodeLib.toDataURL(currentQR, { errorCorrectionLevel: 'H' });
            res.send(`
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Scan QR Code - ${config.botName}</title>
                    <style>
                        body { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 90vh; background-color: #f0f0f0; font-family: Arial, sans-serif; }
                        img { max-width: 80%; max-height: 80vh; border: 1px solid #ccc; padding: 10px; background-color: white; }
                        p { margin-top: 20px; font-size: 1.2em; }
                        .instructions { margin-bottom:20px; text-align:center; }
                    </style>
                </head>
                <body>
                    <div class="instructions">
                        <h2>Scan QR Code to Connect ${config.botName}</h2>
                        <p>Open WhatsApp on your phone, go to Linked Devices and scan the QR code below.</p>
                        <p>This page will not auto-refresh. If connection fails or times out, you might need to restart the bot to get a new QR code.</p>
                    </div>
                    <img src="${qrDataUrl}" alt="WhatsApp QR Code">
                    <p>Status: ${sock && sock.ev && sock.ws.readyState === 1 ? 'Attempting to connect...' : (currentQR ? 'Waiting for scan...' : 'QR Code Expired or Not Available')} </p>
                </body>
                </html>
            `);
        } catch (err) {
            addLog(`[BOT_WEB_QR_ERROR] Failed to generate QR code image: ${err.message}`, 'ERROR');
            res.status(500).send('Error generating QR code. Please check logs.');
        }
    } else {
        res.status(404).send(`
            <!DOCTYPE html><html lang="en"><head><title>QR Not Found</title></head>
            <body style="font-family: Arial, sans-serif; text-align: center; padding-top: 50px;">
            <h1>QR Code Not Available</h1>
            <p>No QR code is currently available for scanning. This might be because:</p>
            <ul>
                <li>The bot is already connected.</li>
                <li>The bot is still starting up.</li>
                <li>The previous QR code has expired.</li>
            </ul>
            <p>Please check the bot's console logs for more information or try restarting the bot if you were expecting a QR code.</p>
            </body></html>
        `);
    }
});

app.get('/bot-api/logs', (req, res) => { res.json(getBotLogsForWebUI()); });
app.listen(WEB_SERVER_PORT, () => {
    const baseUrl = process.env.RENDER_EXTERNAL_URL || `http://localhost:${WEB_SERVER_PORT}`;
    addLog(`[BOT_WEB] ${config.botName} v${config.botVersion} status page active on ${baseUrl}/`);
    addLog(`[BOT_WEB] ${config.botName} v${config.botVersion} log server listening on ${baseUrl}/bot-log`);
    addLog(`[BOT_WEB] If QR code is needed, it will be available at ${baseUrl}/qr-code`);
});
// --- End Express Web Server ---

// --- Graceful Shutdown ---
const shutdown = async (signal) => {
    addLog(`🛑 ${signal} received. Closing ${config.botName} connection and exiting...`);
    if (sock) {
        try { await sock.logout(`Shutdown triggered by ${signal} for ${config.botName}`); addLog("Socket logged out."); }
        catch (e) { addLog(`Error during ${signal} logout: ${e.message}`, 'ERROR'); }
    }
    process.exit(0);
};
process.on('SIGINT', () => shutdown('SIGINT'));
process.on('SIGTERM', () => shutdown('SIGTERM'));
// --- End Graceful Shutdown ---

// --- Start Bot ---
connectToWhatsApp().catch(err => {
    addLog(`[FATAL_ERROR] Initial connection to WhatsApp failed for ${config.botName}: ${err.message}`, 'ERROR');
    console.error(err);
    process.exit(1);
});
addLog(`Core logic for ${config.botName} setup complete. Attempting initial WhatsApp connection...`);
