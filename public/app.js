const clearChatBtn = document.getElementById('clearChat');
const messagesEl = document.getElementById('messages');
const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');

let history = [];

clearChatBtn.addEventListener('click', () => {
  history = [];
  messagesEl.innerHTML = '';
});

function addMessage(text, role) {
  const div = document.createElement('div');
  div.className = `msg ${role}`;
  div.textContent = text;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return div;
}

async function sendMessage(text) {
  const pending = addMessage('…', 'model pending');
  sendBtn.disabled = true;

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, history }),
    });

    const data = await res.json();

    if (!res.ok) {
      pending.remove();
      addMessage(data.error || `Request failed (${res.status})`, 'error');
      return;
    }

    pending.remove();
    addMessage(data.reply, 'model');
    history = data.history;
  } catch (err) {
    pending.remove();
    addMessage(`Network error: ${err.message}`, 'error');
  } finally {
    sendBtn.disabled = false;
  }
}

chatForm.addEventListener('submit', (e) => {
  e.preventDefault();
  const text = userInput.value.trim();
  if (!text) return;
  addMessage(text, 'user');
  userInput.value = '';
  sendMessage(text);
});

userInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    chatForm.requestSubmit();
  }
});
