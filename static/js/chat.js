/* ═══════════════════════════════════════════
   AgroGuide AI — Chat Assistant JS
═══════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', function () {
  const chatBox  = document.getElementById('chatBox');
  const chatInput= document.getElementById('chatInput');
  const chatForm = document.getElementById('chatForm');
  const CHAT_URL = window.CHAT_URL;

  if (!chatForm) return;

  chatForm.addEventListener('submit', async function (e) {
    e.preventDefault();
    const msg = chatInput.value.trim();
    if (!msg) return;
    appendMsg('user', msg);
    chatInput.value = '';
    const typing = appendTyping();
    try {
      const r = await fetch(CHAT_URL, {
        method:'POST',
        headers:{'Content-Type':'application/json','X-CSRFToken': getCsrf()},
        body: JSON.stringify({message: msg}),
      });
      const data = await r.json();
      typing.remove();
      appendMsg('assistant', data.reply || 'Sorry, I could not process that.');
    } catch(err) {
      typing.remove();
      appendMsg('assistant', 'Connection error. Please try again.');
    }
    chatBox.scrollTop = chatBox.scrollHeight;
  });

  // Quick question buttons
  document.querySelectorAll('.chat-quick-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      chatInput.value = btn.dataset.q;
      chatInput.focus();
    });
  });

  function appendMsg(role, text) {
    const isUser = role === 'user';
    const div = document.createElement('div');
    div.className = `chat-msg ${role}`;
    div.innerHTML = `
      ${isUser ? '' : `<div class="chat-avatar ai-avatar">🌾</div>`}
      <div class="chat-bubble">${text.replace(/\n/g,'<br>')}</div>
      ${isUser ? `<div class="chat-avatar user-avatar">👨‍🌾</div>` : ''}
    `;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
    return div;
  }

  function appendTyping() {
    const div = document.createElement('div');
    div.className = 'chat-msg assistant';
    div.innerHTML = `
      <div class="chat-avatar ai-avatar">🌾</div>
      <div class="chat-bubble" style="color:#888;font-style:italic">Thinking…</div>`;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
    return div;
  }

  function getCsrf() {
    const m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? m[1] : '';
  }
});
