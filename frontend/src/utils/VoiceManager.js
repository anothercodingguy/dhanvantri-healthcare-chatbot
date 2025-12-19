/**
 * VoiceManager handles text-to-speech using the Web Speech API.
 * It prioritizes high-quality ("Google", "Microsoft") voices.
 */
class VoiceManager {
    constructor() {
        this.synth = window.speechSynthesis;
        this.voices = [];

        // Load voices immediately
        this.loadVoices();

        // Handle async voice loading (Chrome needs this)
        if (speechSynthesis.onvoiceschanged !== undefined) {
            speechSynthesis.onvoiceschanged = this.loadVoices.bind(this);
        }

        this.languageMap = {
            'en': ['Google US English', 'Microsoft Zira', 'Google UK English Female'],
            'hi': ['Google Hindi', 'Microsoft Hemant', 'Lekha'],
            'bn': ['Google Bangla', 'Microsoft Tanishaa'],
            'kn': ['Google Kannada', 'Microsoft Gagan'],
            'bho': ['Google Hindi', 'Microsoft Madhur'] // Fallback
        };
    }

    loadVoices() {
        this.voices = this.synth.getVoices();
        console.log(`Loaded ${this.voices.length} voices.`);
    }

    getBestVoice(langCode) {
        if (this.voices.length === 0) {
            this.loadVoices(); // Try again
        }

        // Normalize code (e.g. 'en' -> 'en')
        const simpleLang = langCode.split('-')[0];

        // 1. Try preferred voices list
        const preferredNames = this.languageMap[simpleLang] || [];
        for (const name of preferredNames) {
            const found = this.voices.find(v => v.name.includes(name));
            if (found) return found;
        }

        // 2. Try matching language code exactly
        const exactMatch = this.voices.find(v => v.lang.startsWith(langCode));
        if (exactMatch) return exactMatch;

        // 3. Try matching simple language code
        const simpleMatch = this.voices.find(v => v.lang.startsWith(simpleLang));
        if (simpleMatch) return simpleMatch;

        // 4. Fallback to English/First
        return this.voices[0];
    }

    speak(text, langCode = 'en') {
        return new Promise((resolve, reject) => {
            if (!this.synth) {
                reject('Speech Synthesis not supported');
                return;
            }

            // Cancel current speech
            this.cancel();

            const utterance = new SpeechSynthesisUtterance(text);
            const voice = this.getBestVoice(langCode);

            if (voice) {
                utterance.voice = voice;
                utterance.lang = voice.lang; // Ensure lang matches voice
                console.log(`Speaking with voice: ${voice.name} (${voice.lang})`);
            } else {
                console.warn(`No voice found for ${langCode}, using default.`);
                utterance.lang = langCode;
            }

            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;

            utterance.onend = () => {
                resolve();
            };

            utterance.onerror = (e) => {
                console.error('Speech error:', e);
                reject(e);
            };

            this.synth.speak(utterance);
        });
    }

    cancel() {
        if (this.synth) {
            this.synth.cancel();
        }
    }
}

export const voiceManager = new VoiceManager();
