// General Commands for WHIZ-MD-V2
const { create, all } = require('mathjs');
const { formatUptime } = require('../utils/commandUtils.js'); // Assuming formatUptime is here

const math = create(all);

const pingCommand = {
    name: 'ping',
    aliases: ['p', 'alive'], // Added 'alive' as an alias
    category: 'General',
    description: 'Checks bot responsiveness and shows uptime.',
    usage: '<prefix>ping', // Example usage, prefix will be handled by index.js
    ownerOnly: false,
    adminOnly: false,
    groupOnly: false,
    async execute(commandContext) {
        const { sock, msg, config, addLog, formatAndSendMessage, startTime } = commandContext;

        addLog(`[CMD_PING] Ping command executed by ${commandContext.msg.key.remoteJid}`);
        const uptime = formatUptime(commandContext.startTime);
        const replyText = `Pong! 🏓\n*${commandContext.config.botName}* is responsive.\nUptime: ${uptime}`;

        await commandContext.formatAndSendMessage(commandContext.sock, commandContext.msg.key.remoteJid, replyText, { quotedMsg: commandContext.msg, addLog: commandContext.addLog });
    }
};

const menuCommand = {
    name: 'menu',
    aliases: ['help', 'commands'],
    category: 'General',
    description: 'Displays the bot command menu with categories.',
    usage: '<prefix>menu',
    async execute(commandContext) {
        const { sock, msg, config, addLog, startTime } = commandContext; // formatAndSendMessage not used directly for menu
        const sender = msg.key.remoteJid;

        addLog(`[CMD_MENU] Menu command executed by ${sender}`);

        const uptime = formatUptime(startTime); // formatUptime is already imported
        const lineRepeatCount = config.menu?.lineRepeatCount || 35; // Allow config override, default 35

        const topBorder = `╭─⊷ ${config.botName} v${config.botVersion} ⊶─╮`;
        const bottomLine = `╰─⊷ Have fun using ${config.botName}! ⊶─╯`;
        const mainSectionSeparator = `├${'─'.repeat(lineRepeatCount)}┤`;
        const categorySeparator = (title) => `├─⊷ ${title.toUpperCase()} ⊶─┤`;

        let menuText = `${topBorder}\n`;
        // Use msg.pushName for user, fallback to JID part if pushName is not available
        const userNameForMenu = msg.pushName || sender.split('@')[0];
        menuText += `│ User    : ${userNameForMenu}\n`;
        menuText += `│ Owner   : ${config.ownerName}\n`;
        menuText += `│ Prefix  : (Multiple - e.g., ${config.prefixes.join(', ')})\n`; // Updated Prefix display
        menuText += `│ Uptime  : ${uptime}\n`;
        menuText += `│ Repo    : ${config.repoUrl}\n`;
        menuText += `│ Group   : ${config.whatsappGroupUrl}\n`; // Plain group link in menu body

        const commandsByCategory = {};
        if (Array.isArray(config.commandsList)) {
            config.commandsList.forEach(cmdDef => {
                if (!commandsByCategory[cmdDef.category]) {
                    commandsByCategory[cmdDef.category] = [];
                }
                commandsByCategory[cmdDef.category].push(cmdDef);
            });
        }

        menuText += `${mainSectionSeparator}\n`;
        menuText += `│ *Available Commands:*\n`;

        const categoryOrder = ['General', 'Media', 'Utility', 'Search', 'Download', 'Fun', 'Group Admin', 'Owner Only', 'AI & API Tools'];

        for (const category of categoryOrder) {
            if (commandsByCategory[category] && commandsByCategory[category].length > 0) {
                menuText += `${categorySeparator(category)}\n`;
                commandsByCategory[category].forEach(cmdDef => {
                    const argsDisplay = cmdDef.args ? ` ${cmdDef.args}` : '';
                    menuText += `│ ${cmdDef.cmd}${argsDisplay} - ${cmdDef.desc}\n`; // Removed prefix from display
                });
            }
        }

        // If you want to list Automatic Features separately in the menu structure
        menuText += `${categorySeparator('Automatic Features')}\n`;
        menuText += `│ 🔥 Auto React to Statuses (with '🔥')\n`;
        // menuText += `│ 👁️ _Auto View Statuses (Under Review)_\n`; // Removed as it's problematic and not implemented

        menuText += `${mainSectionSeparator.replace('├', '╰').replace('┤', '╯')}\n`; // Creates a bottom border like ╰───╯
        menuText += bottomLine;

        try {
            await sock.sendMessage(sender, { text: menuText.trim() });
            addLog(`[CMD_MENU] Sent enhanced menu to ${sender}`);
        } catch (error) {
            addLog(`[CMD_MENU] Error sending menu to ${sender}: ${error.message}`, 'ERROR');
            // Fallback or simpler message if complex one fails (though unlikely for text)
            await sock.sendMessage(sender, {text: "Sorry, couldn't display the full menu. Try again later."});
        }
    }
};

// Add other general commands here later, like menu, contact, source, jid, uptime (as a standalone command)

const contactCommand = {
    name: 'contact',
    category: 'General',
    description: 'Get owner & group information.',
    usage: '<prefix>contact',
    async execute(commandContext) {
        const { sock, msg, config, addLog, formatAndSendMessage, getBotFooter } = commandContext; // Added getBotFooter
        const sender = msg.key.remoteJid;

        addLog(`[CMD_CONTACT] Contact command executed by ${sender}`);

        const ownerActualJidNumber = process.env[config.ownerJidEnvKey] ?
                                     process.env[config.ownerJidEnvKey].split('@')[0] :
                                     config.ownerContact.replace(/\D/g, ''); // Fallback to config.ownerContact

        if (!ownerActualJidNumber) {
            addLog(`[CMD_CONTACT] Owner JID or contact number not configured.`, 'ERROR');
            return formatAndSendMessage(sock, sender, "Owner contact information is not configured.", { quotedMsg: msg, addLog: addLog });
        }

        const vCard =
`BEGIN:VCARD
VERSION:3.0
FN:${config.ownerName}
TEL;type=CELL;type=VOICE;waid=${ownerActualJidNumber}:${config.ownerName} Contact
END:VCARD`; // Using ownerName in TEL for better display

        try {
            await sock.sendMessage(sender, {
                contacts: {
                    displayName: `${config.ownerName} (Owner WHIZ-MD)`,
                    contacts: [{ vcard: vCard }]
                }
            });
            addLog(`[CMD_CONTACT] Sent contact card for ${config.ownerName} to ${sender}`);

            const contactFollowUp = `For community support or further questions, you can also join our WhatsApp group:\n${config.whatsappGroupUrl}` + getBotFooter();
            // Send follow-up as a separate text message using formatAndSendMessage for consistency in footer, but without logo for this part.
            // Or, more simply, just send text + footer.
            // Let's use formatAndSendMessage with an option to suppress logo for simple text replies.
            // For now, direct send:
            await sock.sendMessage(sender, { text: contactFollowUp });
            addLog(`[CMD_CONTACT] Sent contact follow-up message to ${sender}`);

        } catch (error) {
            addLog(`[CMD_CONTACT] Error sending contact info to ${sender}: ${error.message}`, 'ERROR');
            await formatAndSendMessage(sock, sender, "Sorry, an error occurred while fetching contact information.", { quotedMsg: msg, addLog: addLog });
        }
    }
};


const sourceCommand = {
    name: 'source',
    aliases: ['repo', 'github'],
    category: 'General',
    description: 'Get the link to the bot\'s source code repository.',
    usage: '<prefix>source',
    async execute(commandContext) {
        const { sock, msg, config, addLog, formatAndSendMessage } = commandContext;
        const sender = msg.key.remoteJid;

        addLog(`[CMD_SOURCE] Source command executed by ${sender}`);

        const sourceMessageText = `You can find my source code, star the repo, and contribute at:\n${config.repoUrl}`;

        await formatAndSendMessage(sock, sender, sourceMessageText, { quotedMsg: msg, addLog: addLog });
    }
};

const jidCommand = {
    name: 'jid',
    category: 'General',
    description: 'Get JID of current chat and/or quoted user.',
    usage: '<prefix>jid (optional: reply to a message)',
    async execute(commandContext) {
        const { sock, msg, config, addLog, formatAndSendMessage } = commandContext;
        const sender = msg.key.remoteJid;

        addLog(`[CMD_JID] JID command executed by ${sender} in chat ${sender}`);

        let replyText = `💬 *Chat JID:*\n\`${sender}\``;

        const contextInfo = msg.message?.extendedTextMessage?.contextInfo;
        const isReply = !!contextInfo?.stanzaId; // More reliable check for a reply

        if (isReply && contextInfo?.participant) {
            // If replying in a group, contextInfo.participant is the original sender of the quoted message.
            replyText += `\n👤 *Quoted User JID:*\n\`${contextInfo.participant}\``;
        } else if (isReply && sender.endsWith('@s.whatsapp.net') && contextInfo?.stanzaId) {
            // If it's a reply in a DM, the "quoted user" is simply the other person in the chat (the sender of the !jid command).
            // This isn't particularly useful to display as it's already known.
            // However, if the user replies to their *own* message in a DM, participant would be their JID.
            // If they reply to the BOT's message in a DM, participant is the bot's JID.
            // For simplicity, we primarily focus on `contextInfo.participant` which is most useful in groups.
            // No specific "quoted user" line for DMs unless participant is present.
        }

        await formatAndSendMessage(sock, sender, replyText, { quotedMsg: msg, addLog: addLog });
    }
};

const uptimeCommand = {
    name: 'uptime',
    category: 'General',
    description: 'Show how long the bot has been running.',
    usage: '<prefix>uptime',
    async execute(commandContext) {
        const { sock, msg, config, addLog, formatAndSendMessage, startTime } = commandContext;
        const sender = msg.key.remoteJid;

        addLog(`[CMD_UPTIME] Uptime command executed by ${sender}`);

        const currentUptime = formatUptime(startTime);
        const replyText = `📈 *${config.botName} Uptime:*\n${currentUptime}`;

        await formatAndSendMessage(sock, sender, replyText, { quotedMsg: msg, addLog: addLog });
    }
};

module.exports = [
    pingCommand,
    menuCommand,
    contactCommand,
    sourceCommand,
    jidCommand,
    uptimeCommand,
    // ...
];

const calcCommand = {
    name: 'calc',
    aliases: ['calculate', 'math'],
    category: 'General', // Or 'Utility'
    description: 'Calculate a mathematical expression.',
    usage: '<prefix>calc <expression>',
    async execute(commandContext) {
        const { sock, msg, argsString, addLog, formatAndSendMessage } = commandContext;
        const sender = msg.key.remoteJid;

        if (!argsString) {
            await formatAndSendMessage(sock, sender, "Please provide a mathematical expression to calculate.\nExample: `<prefix>calc 2+2*10/sqrt(16)`", { quotedMsg: msg });
            return;
        }

        addLog(`[CMD_CALC] Calc command executed by ${sender} with expression: "${argsString}"`);

        try {
            // Basic sanitization: limit expression length to prevent abuse
            if (argsString.length > 100) {
                await formatAndSendMessage(sock, sender, "Expression is too long. Please keep it under 100 characters.", { quotedMsg: msg });
                return;
            }

            // Further sanitization could be added here if needed (e.g., disallowing certain functions)
            // For now, relying on mathjs's parser and evaluation scope.

            const result = math.evaluate(argsString);

            // Check if result is a function (e.g. if user types "sqrt"), which we don't want to output directly
            if (typeof result === 'function') {
                 await formatAndSendMessage(sock, sender, `❓ Please provide a full expression to calculate. You entered a function name.`, { quotedMsg: msg });
                 return;
            }

            let resultString = result.toString();
            if (resultString.length > 4000) { // WhatsApp message length limit
                resultString = "Result is too long to display.";
            }

            await formatAndSendMessage(sock, sender, `🧮 *Result:*\n\`\`\`${argsString} = ${resultString}\`\`\``, { quotedMsg: msg });

        } catch (error) {
            addLog(`[CMD_CALC_ERROR] Error evaluating expression "${argsString}" for ${sender}: ${error.message}`, 'ERROR');
            await formatAndSendMessage(sock, sender, `Sorry, I couldn't calculate that. Please ensure it's a valid mathematical expression.\nError: \`${error.message}\``, { quotedMsg: msg });
        }
    }
};


// Add the new command to the module.exports array
// Make sure to add it to the existing array, not replace it.
// Reading the file again to correctly append is tricky in this env.
// Assuming the previous module.exports was:
// module.exports = [pingCommand, menuCommand, contactCommand, sourceCommand, jidCommand, uptimeCommand];

module.exports = [
    pingCommand,
    menuCommand,
    contactCommand,
    sourceCommand,
    jidCommand,
    uptimeCommand,
    calcCommand, // Added calcCommand
];
