// Ретро-звуки для интерфейса
let audioContext;
let isInitialized = false;

// Объект для хранения звуков
const sounds = {
    menuSelect: null,
    menuMove: null,
    buttonClick: null,
    success: null,
    error: null
};

// Инициализация аудио контекста
function initAudio() {
    if (!isInitialized) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        
        // Создаем звуки
        sounds = {
            menuSelect: createSound(440, 0.1, 0.3),
            menuMove: createSound(880, 0.05, 0.2),
            buttonClick: createSound(220, 0.15, 0.4),
            success: createSound(880, 0.2, 0.3),
            error: createSound(110, 0.2, 0.3)
        };
        
        isInitialized = true;
    }
}

// Функция для создания звука
function createSound(frequency, duration, volume = 0.5) {
    return function() {
        if (!isInitialized) {
            initAudio();
        }

        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.type = 'sine';
        oscillator.frequency.value = frequency;
        gainNode.gain.value = volume;
        
        // Добавляем плавное затухание
        gainNode.gain.setTargetAtTime(0, audioContext.currentTime, duration * 0.5);
        
        oscillator.start();
        oscillator.stop(audioContext.currentTime + duration);
    };
}

// Функция для воспроизведения звука
function playSound(soundName) {
    // Отключено
}

// Функция для инициализации звуков
function initializeSounds() {
    // Отключено
}

// Функция для добавления звуков к элементам
function addSoundToElement(element, soundName) {
    // Отключено
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    // Отключено
}); 