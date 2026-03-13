import KeatsOrb from './orb.js';
import { startAudioPlayerWorklet } from "./audio-player.js";
import { startAudioRecorderWorklet } from "./audio-recorder.js";

// Initialize the Orb (with delay for visual entrance)
const orb = new KeatsOrb('canvas-container');
const canvas = document.querySelector('#canvas-container canvas');
if (canvas) canvas.style.opacity = '0';

setTimeout(() => {
    if (canvas) {
        canvas.style.transition = 'opacity 3s ease';
        canvas.style.opacity = '1';
    }
}, 4000); 

// State Management
const userId = "demo-user";
const sessionId = "demo-session-" + Math.random().toString(36).substring(7);
let websocket = null;
let is_audio = false;
let fadeTimeout = null;
let keatsSpeakingTimeout = null;

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
    if (fadeTimeout) clearTimeout(fadeTimeout);
    fadeTimeout = setTimeout(() => {
        messageOverlay.style.opacity = 0;
    }, duration);
}

function connectWebsocket() {
    // If already connecting or open, don't double connect
    if (websocket && (websocket.readyState === WebSocket.OPEN || websocket.readyState === WebSocket.CONNECTING)) {
        return;
    }

    const ws_url = getWebSocketUrl();
    websocket = new WebSocket(ws_url);

    websocket.onopen = () => {
        console.log("WebSocket connected.");
        updateStatus("ready", 'SILENCE');
    };

    websocket.onmessage = (event) => {
        let adkEvent;
        try {
            adkEvent = JSON.parse(event.data);
        } catch (e) {
            console.error("Failed to parse WebSocket message:", e);
            return;
        }
        
        if (adkEvent.type === 'reconnecting') {
            updateStatus("reconnecting...", 'SILENCE');
            return;
        }

        // Handle Audio Output
        if (adkEvent.content && adkEvent.content.parts) {
            for (const part of adkEvent.content.parts) {
                if (part.inlineData && part.inlineData.mimeType.startsWith("audio/pcm") && audioPlayerNode) {
                    const audioData = base64ToArray(part.inlineData.data);
                    audioPlayerNode.port.postMessage(audioData);
                    
                    // State Detection: KEATS_SPEAKING
                    orb.setState('KEATS_SPEAKING', 0.5);
                    if (keatsSpeakingTimeout) clearTimeout(keatsSpeakingTimeout);
                    keatsSpeakingTimeout = setTimeout(() => {
                        orb.setState('SILENCE');
                    }, 5000); // 5s fallback safety
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
            if (keatsSpeakingTimeout) clearTimeout(keatsSpeakingTimeout);
            updateStatus("listening", 'SILENCE');
        }

        if (adkEvent.interrupted) {
            console.warn("[AUDIO] Gemini interrupted - clearing buffers");
            if (audioPlayerNode) {
                audioPlayerNode.port.postMessage({ command: "endOfAudio" });
            }
            if (keatsSpeakingTimeout) clearTimeout(keatsSpeakingTimeout);
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

// Reconnect on visibility change (mobile screen wake)
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        if (!websocket || websocket.readyState === WebSocket.CLOSED) {
            console.log("Visibility regained, reconnecting...");
            connectWebsocket();
        }
    }
});

// Decode Base64 data to Array
function base64ToArray(base64) {
    let standardBase64 = base64.replace(/-/g, '+').replace(/_/g, '/');
    while (standardBase64.length % 4) standardBase64 += '=';
    const binaryString = window.atob(standardBase64);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) bytes[i] = binaryString.charCodeAt(i);
    return bytes.buffer;
}

// Audio recorder handler
function audioRecorderHandler(pcmData) {
    if (websocket && websocket.readyState === WebSocket.OPEN && is_audio) {
        // Send audio as binary WebSocket frame (more efficient than base64 JSON)
        websocket.send(pcmData);
        
        // Pulse orb for user speaking based on activity
        const samples = new Int16Array(pcmData);
        let sum = 0;
        for (let i = 0; i < samples.length; i++) {
            sum += Math.abs(samples[i]);
        }
        const avg = sum / samples.length;
        if (avg > 100) { // Very low threshold for visual pulse
            orb.setState('USER_SPEAKING', Math.min(avg / 1000, 1.0));
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
