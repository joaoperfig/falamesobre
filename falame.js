function main(topic) {
  sendarquivo(topic);
  //sendgpt(topic);
}


function sendarquivo(query){
  console.log("Sending "+query+" to arquivo (usando cors bypass)");

  const requestOptions = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest' // Add this header to work with the CORS proxy
    },
    body: JSON.stringify({
      q: query,
      maxItems :5
    })
  };

  fetch('https://cors-anywhere.herokuapp.com/http://arquivo.pt/textsearch', requestOptions)
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.log('Error:', error));
}

function sendgpt(message){
  console.log("Sending "+message+" to chatgpt");
  const oak = "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";

  const requestOptions = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${oak}`
    },
    body: JSON.stringify({
      model: "gpt-3.5-turbo",
      messages: [{"role": "user", "content": message}]
    })
  };

  fetch('https://api.openai.com/v1/chat/completions', requestOptions)
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.log('Error:', error));
}
