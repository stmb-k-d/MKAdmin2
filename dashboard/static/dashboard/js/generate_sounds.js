// Функция для создания WAV-файла
function createWavFile(frequency, duration, volume = 0.5) {
    const sampleRate = 44100;
    const numSamples = Math.floor(duration * sampleRate);
    const buffer = new ArrayBuffer(44 + numSamples * 2);
    const view = new DataView(buffer);
    
    // WAV header
    writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + numSamples * 2, true);
    writeString(view, 8, 'WAVE');
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, 1, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true);
    writeString(view, 36, 'data');
    view.setUint32(40, numSamples * 2, true);
    
    // Generate audio data
    for (let i = 0; i < numSamples; i++) {
        const value = Math.sin(2 * Math.PI * frequency * i / sampleRate) * volume;
        view.setInt16(44 + i * 2, value * 32767, true);
    }
    
    return buffer;
}

// Helper function to write strings to DataView
function writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
    }
}

// Generate sounds
const sounds = {
    menuSelect: createWavFile(440, 0.1, 0.3),  // A4 note, 100ms
    menuMove: createWavFile(880, 0.05, 0.2),   // A5 note, 50ms
    buttonClick: createWavFile(220, 0.15, 0.4), // A3 note, 150ms
    success: createWavFile(880, 0.2, 0.3),      // A5 note, 200ms
    error: createWavFile(110, 0.2, 0.3)         // A2 note, 200ms
};

// Save sounds to files
Object.entries(sounds).forEach(([name, buffer]) => {
    const blob = new Blob([buffer], { type: 'audio/wav' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${name}.wav`;
    a.click();
    URL.revokeObjectURL(url);
}); 