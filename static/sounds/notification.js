// This file generates a notification sound using the Web Audio API
// It can be used when the browser doesn't support audio files

function playNotificationSound() {
  try {
    // Create audio context
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    const audioCtx = new AudioContext();
    
    // Create oscillator
    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();
    
    // Connect nodes
    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);
    
    // Set parameters
    oscillator.type = 'sine';
    oscillator.frequency.setValueAtTime(880, audioCtx.currentTime); // A5
    oscillator.frequency.setValueAtTime(1320, audioCtx.currentTime + 0.1); // E6
    oscillator.frequency.setValueAtTime(1760, audioCtx.currentTime + 0.2); // A6
    
    // Start and stop
    gainNode.gain.setValueAtTime(0.5, audioCtx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.5);
    
    oscillator.start();
    oscillator.stop(audioCtx.currentTime + 0.5);
    
    return true;
  } catch (e) {
    console.error("Error playing notification sound:", e);
    return false;
  }
}

// Export the function
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { playNotificationSound };
} 