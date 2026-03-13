import KeatsOrb from './orb.js';
import { startAudioPlayerWorklet } from "./audio-player.js";
import { startAudioRecorderWorklet } from "./audio-recorder.js";

// Initialize the Orb
const orb = new KeatsOrb('canvas-container');

// State Management
const userId = "demo-user";
const sessionId = "demo-session-" + Math.random().toString(36).substring(7);
let websocket = null;
let is_audio = false;

// DOM Elements
const statusText = document.getElementById("statusText");
const messageOverlay = document.getElementById("message-overlay");
const startAudioButton = document.getElementById("startAudioButton");
const cameraButton = document.getElementById("cameraButton");

// Audio State
let audioPlayerNode;
let audioPlayerContext;
let audioRecorderNode;
let audioRecorderContext;
let micStream;

function getWebSocketUrl() {
    const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${wsProtocol}//${window.location.host}/ws/${userId}/${sessionId}`;
}

function updateStatus(text, state = 'SILENCE') {
    statusText.textContent = text;
    orb.setState(state);
}

function displayMessage(text, duration = 5000) {
    messageOverlay.textContent = text;
    messageOverlay.style.opacity = 1;
    
    // Fade out after duration
    if (this.fadeTimeout) clearTimeout(this.fadeTimeout);
    this.fadeTimeout = setTimeout(() => {
        messageOverlay.style.opacity = 0;
    }, duration);
}

function connectWebsocket() {
    const ws_url = getWebSocketUrl();
    websocket = new WebSocket(ws_url);

    websocket.onopen = () => {
        console.log("WebSocket connected.");
        updateStatus("ready", 'SILENCE');
    };

    websocket.onmessage = (event) => {
        const adkEvent = JSON.parse(event.data);
        
        if (adkEvent.type === 'reconnecting') {
            updateStatus("reconnecting...", 'SILENCE');
            return;
        }

        // Handle Audio Output
        if (adkEvent.content && adkEvent.content.parts) {
            for (const part of adkEvent.content.parts) {
                if (part.inlineData && part.inlineData.mimeType.startsWith("audio/pcm") && audioPlayerNode) {
                    audioPlayerNode.port.postMessage(base64ToArray(part.inlineData.data));
                    orb.setState('KEATS_SPEAKING', 0.5); // Baseline intensity
                }
            }
        }

        // Handle Transcriptions for visual feedback
        if (adkEvent.inputTranscription) {
            orb.setState('USER_SPEAKING', 0.8);
            if (adkEvent.inputTranscription.text) {
                statusText.textContent = "you: " + adkEvent.inputTranscription.text.toLowerCase();
            }
        }

        if (adkEvent.outputTranscription) {
            orb.setState('KEATS_SPEAKING', 1.0);
            if (adkEvent.outputTranscription.text) {
                displayMessage(adkEvent.outputTranscription.text);
            }
        }

        if (adkEvent.turnComplete) {
            updateStatus("listening", 'SILENCE');
        }

        if (adkEvent.interrupted) {
            if (audioPlayerNode) {
                audioPlayerNode.port.postMessage({ command: "endOfAudio" });
            }
            updateStatus("listening", 'SILENCE');
        }
    };

    websocket.onclose = () => {
        updateStatus("reconnecting...", 'SILENCE');
        setTimeout(connectWebsocket, 2000);
    };

    websocket.onerror = (e) => {
        console.error("WebSocket error:", e);
        updateStatus("connection error", 'SILENCE');
    };
}

// Audio Utils
function base64ToArray(base64) {
    let standardBase64 = base64.replace(/-/g, '+').replace(/_/g, '/');
    while (standardBase64.length % 4) standardBase64 += '=';
    const binaryString = window.atob(standardBase64);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) bytes[i] = binaryString.charCodeAt(i);
    return bytes.buffer;
}

function audioRecorderHandler(pcmData) {
    if (websocket && websocket.readyState === WebSocket.OPEN && is_audio) {
        // Simple mic gating: calculate average amplitude
        const samples = new Int16Array(pcmData);
        let sum = 0;
        for (let i = 0; i < samples.length; i++) {
            sum += Math.abs(samples[i]);
        }
        const avg = sum / samples.length;
        
        // Only send if average amplitude is above noise floor (approx 150)
        // This helps prevent session timeouts due to continuous silence streaming
        if (avg > 150) {
            websocket.send(pcmData);
        }
    }
}

function startAudio() {
    startAudioPlayerWorklet().then(([node, ctx]) => {
        audioPlayerNode = node;
        audioPlayerContext = ctx;
    });
    startAudioRecorderWorklet(audioRecorderHandler).then(([node, ctx, stream]) => {
        audioRecorderNode = node;
        audioRecorderContext = ctx;
        micStream = stream;
    });
}

// Event Listeners
startAudioButton.addEventListener("click", () => {
    startAudioButton.classList.add('hidden');
    startAudio();
    is_audio = true;
    updateStatus("listening", 'SILENCE');
});

// Initial Connection
connectWebsocket();
