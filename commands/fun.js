// Fun Commands for WHIZ-MD-V2
// (e.g., joke, meme, anime, fact, advice, quote, proq, horo, gender)

/*
Example structure:
const jokeCommand = {
    name: 'joke',
    category: 'Fun',
    description: 'Get a random joke.',
    usage: '!joke',
    async execute(sock, msg, args, config, addLog, formatAndSendMessage, externalApis) {
        // const joke = await externalApis.fetchJoke();
        // await formatAndSendMessage(sock, msg.key.remoteJid, joke, { quotedMsg: msg });
    }
};

module.exports = [
    jokeCommand,
    // ... other fun commands
];
*/
const axios = require('axios');

const factCommand = {
    name: 'fact',
    category: 'Fun',
    description: 'Get a random interesting fact.',
    usage: '<prefix>fact',
    cooldown: 10, // Optional: 10 seconds cooldown
    async execute(commandContext) {
        const { sock, msg, config, addLog, formatAndSendMessage } = commandContext;
        const sender = msg.key.remoteJid;
        addLog(`[CMD_FACT] Fact command executed by ${sender}`);

        try {
            // Using Useless Facts API (keyless)
            const response = await axios.get('https://uselessfacts.jsph.pl/api/v2/facts/random?language=en');

            if (response.data && response.data.text) {
                const factText = `🧠 *Did you know?*\n\n${response.data.text}\n\nSource: ${response.data.source_url || 'uselessfacts.jsph.pl'}`;
                await formatAndSendMessage(sock, sender, factText, { quotedMsg: msg, addLog: addLog });
            } else {
                throw new Error('Invalid API response structure from Useless Facts API.');
            }
        } catch (error) {
            addLog(`[CMD_FACT_ERROR] Failed to fetch fact: ${error.message}`, 'ERROR');
            console.error("Fact API Error:", error.response ? error.response.data : error.message);
            let errorMessage = "Sorry, I couldn't fetch a fact right now. Please try again later.";
            if (error.message.includes('ENOTFOUND') || error.message.includes('EAI_AGAIN')) {
                errorMessage = "Sorry, I'm having trouble reaching the fact service. Please check my internet connection or try again later.";
            }
            await formatAndSendMessage(sock, sender, errorMessage, { quotedMsg: msg, addLog: addLog });
        }
    }
};

const animeQuoteCommand = {
    name: 'animequote',
    aliases: ['aq', 'anime'], // 'anime' is already in config.commandsList, ensure no conflict or intended override
    category: 'Fun',
    description: 'Get a random anime quote.',
    usage: '<prefix>animequote',
    cooldown: 5,
    async execute(commandContext) {
        const { sock, msg, addLog, formatAndSendMessage } = commandContext;
        const sender = msg.key.remoteJid;
        addLog(`[CMD_ANIMEQUOTE] Anime Quote command executed by ${sender}`);

        try {
            // Using animechan.xyz API (keyless)
            const response = await axios.get('https://animechan.xyz/api/random');
            // Alternative: https://animechan.vercel.app/api/random (if .xyz is down)

            if (response.data && response.data.quote) {
                const quote = response.data;
                const message = `🎬 *Anime:* ${quote.anime}\n👤 *Character:* ${quote.character}\n\n"${quote.quote}"`;
                await formatAndSendMessage(sock, sender, message, { quotedMsg: msg, addLog: addLog });
            } else {
                throw new Error('Invalid API response structure from AnimeChan API.');
            }
        } catch (error) {
            addLog(`[CMD_ANIMEQUOTE_ERROR] Failed to fetch anime quote: ${error.message}`, 'ERROR');
            console.error("AnimeQuote API Error:", error.response ? error.response.data : error.message);
            let errorMessage = "Sorry, I couldn't fetch an anime quote right now. Please try again later.";
             if (error.message.includes('ENOTFOUND') || error.message.includes('EAI_AGAIN')) {
                errorMessage = "Sorry, I'm having trouble reaching the anime quote service. Please check my internet connection or try again later.";
            }
            await formatAndSendMessage(sock, sender, errorMessage, { quotedMsg: msg, addLog: addLog });
        }
    }
};


module.exports = [
    factCommand,
    animeQuoteCommand,
    // ... other fun commands
];
