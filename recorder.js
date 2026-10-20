let mediaRecorder;
let audioChunks = [];

function startRecording() {
  navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
      mediaRecorder = new MediaRecorder(stream);
      audioChunks = [];

      mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
        const audioUrl = URL.createObjectURL(audioBlob);

        document.getElementById("audioPlayback").src = audioUrl;

        const file = new File([audioBlob], "voice.webm", { type: "audio/webm" });
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);

        document.getElementById("voiceFile").files = dataTransfer.files;
      };

      mediaRecorder.start();
      alert("Recording started... Speak now!");
    })
    .catch(err => {
      alert("Microphone access denied!");
      console.log(err);
    });
}

function stopRecording() {
  if (mediaRecorder) {
    mediaRecorder.stop();
    alert("Recording stopped!");
  }
}
