let mediaRecorder = null;
let recordedChunks = [];

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "START_RECORDING") {
    startRecording();
  } else if (request.action === "STOP_RECORDING") {
    stopRecording();
  }
});

async function startRecording() {
  try {
    // Request both video and audio, but we'll only save the audio
    const stream = await navigator.mediaDevices.getDisplayMedia({
      video: true,  // We need this to be true to get system audio
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        sampleRate: 44100
      }
    });
    
    // Extract audio track from the stream
    const audioStream = new MediaStream(stream.getAudioTracks());
    
    // Create audio-only recorder
    mediaRecorder = new MediaRecorder(audioStream, {
      mimeType: 'audio/webm'
    });
    
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        recordedChunks.push(event.data);
      }
    };
    
    mediaRecorder.onstop = () => {
      const blob = new Blob(recordedChunks, { type: 'audio/webm' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = 'meet-audio.webm';
      document.body.appendChild(a);
      a.click();
      URL.revokeObjectURL(url);
      recordedChunks = [];
    };
    
    // Start recording
    mediaRecorder.start(10);
    
    // Add recording indicator
    const indicator = document.createElement('div');
    indicator.id = 'audio-record-indicator';
    indicator.style.cssText = 'position: fixed; top: 10px; right: 10px; background: red; padding: 5px; color: white; border-radius: 5px; z-index: 9999;';
    indicator.textContent = '🎤 Recording Audio';
    document.body.appendChild(indicator);
    
  } catch (error) {
    console.error("Error starting audio recording:", error);
    alert("Please make sure to select a tab and enable 'Share audio' in the popup!");
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
    mediaRecorder.stream.getTracks().forEach(track => track.stop());
    
    const indicator = document.getElementById('audio-record-indicator');
    if (indicator) {
      indicator.remove();
    }
  }
}