const fileElem = document.getElementById("fileElem");
const dropArea = document.getElementById("drop-area");
const uploadBtn = document.getElementById("uploadBtn");
const loadingEl = document.getElementById("loading");
const resultEl = document.getElementById("result");
const extractedTextEl = document.getElementById("extractedText");
const errorEl = document.getElementById("error");
const downloadLink = document.getElementById("downloadLink");

let selectedFile = null;

function showError(msg) {
  errorEl.textContent = msg;
  errorEl.classList.remove("hidden");
}
function clearError() {
  errorEl.textContent = "";
  errorEl.classList.add("hidden");
}

// drag & drop
["dragenter", "dragover"].forEach(evt => {
  dropArea.addEventListener(evt, e => {
    e.preventDefault();
    dropArea.classList.add("dragover");
  });
});
["dragleave", "drop"].forEach(evt => {
  dropArea.addEventListener(evt, e => {
    e.preventDefault();
    dropArea.classList.remove("dragover");
  });
});
dropArea.addEventListener("drop", e => {
  const files = e.dataTransfer.files;
  if (files && files.length) fileSelected(files[0]);
});

// file chooser
fileElem.addEventListener("change", e => {
  if (e.target.files && e.target.files.length) fileSelected(e.target.files[0]);
});

function fileSelected(file) {
  selectedFile = file;
  clearError();
  uploadBtn.disabled = false;
  uploadBtn.textContent = `Ready: ${file.name}`;
}

uploadBtn.addEventListener("click", async () => {
  if (!selectedFile) { showError("Please choose a file first."); return; }

  uploadBtn.disabled = true;
  loadingEl.classList.remove("hidden");
  resultEl.classList.add("hidden");
  clearError();

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const resp = await fetch("/extract-text", { method: "POST", body: formData });
    const data = await resp.json();
    if (!data.success) {
      showError(data.error || "Extraction failed");
    } else {
      extractedTextEl.textContent = data.text || "[No text found]";
      resultEl.classList.remove("hidden");
      const blob = new Blob([data.text], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      downloadLink.href = url;
      downloadLink.download = "extracted.txt";
      downloadLink.classList.remove("hidden");
    }
  } catch (err) {
    showError("Error: " + err.message);
  } finally {
    loadingEl.classList.add("hidden");
    uploadBtn.disabled = false;
    uploadBtn.textContent = "Upload & Extract";
  }
});
