const msgerForm = get(".msger-inputarea");
const msgerInput = get(".msger-input");
const msgerChat = get(".msger-chat");

const urlParams = new URLSearchParams(window.location.search);
const topic = urlParams.get('topic');

var api = "http://127.0.0.1:8000/"
//var api = "https://falamesobre-1-b8293400.deta.app/docs"

console.log("Topic: "+topic);

const msgText = document.querySelector(".msg-text");

// Replace the text "xyz" with "gatos"
msgText.innerHTML = msgText.innerHTML.replace("xyz", topic);

const CONVERSATION = [
  "Fala-me sobre "+topic,
  "Claro! O que gostarias de saber?"
];

// Icons made by Freepik from www.flaticon.com
const BOT_NAME = "Agente";
const PERSON_NAME = "Utilizador";

msgerForm.addEventListener("submit", async event => {
  event.preventDefault();

  const msgText = msgerInput.value;
  if (!msgText) return;

  appendMessage(PERSON_NAME, "right", msgText);
  msgerInput.value = "";

  CONVERSATION.push(msgText);

  await botResponse();
});

function appendMessage(name, side, text) {
  //   Simple solution for small apps
  const msgHTML = `
    <div class="msg ${side}-msg">

      <div class="msg-bubble">
        <div class="msg-info">
          <div class="msg-info-name">${name}</div>
        </div>

        <div class="msg-text">${text}</div>
      </div>
    </div>
  `;

  msgerChat.insertAdjacentHTML("beforeend", msgHTML);
  msgerChat.scrollTop += 500;
}

async function botResponse() {
  console.log("Sending chat to api");

  const requestOptions = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      "parts": CONVERSATION
    })
  };

  try {
    const response = await fetch(api + "chat/", requestOptions);
    const data = await response.json();
    console.log(data);
    console.log("Fetch ended");
    appendMessage(BOT_NAME, "left", data.response);
  } catch (error) {
    console.log('Error:', error);
  }
}

// Utils
function get(selector, root = document) {
  return root.querySelector(selector);
}
