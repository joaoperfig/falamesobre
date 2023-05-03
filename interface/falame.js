async function main(topic) {
  // Remove search box
  const container = document.getElementById("container");
  container.innerHTML = '<img src="loading.gif" width="30" alt="loading"> &nbsp; &nbsp; A criar agente...';
  // send to api
  await sendapi(topic);
  // create agent chat
  console.log("Got summary, changing to chat");
  window.location.href = "chat.html?topic="+topic;
  console.log("Changed to chat");

}

var api = "http://127.0.0.1:8000/";
//var api = "http://188.37.68.45:22123/";

async function sendapi(query) {
  console.log("Sending " + query + " to api");

  const requestOptions = {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  };

  try {
    const response = await fetch(api + "resumo/" + query, requestOptions);
    const data = await response.json();
    console.log(data);
    console.log("Fetch ended");
  } catch (error) {
    console.log('Error:', error);
  }
}
