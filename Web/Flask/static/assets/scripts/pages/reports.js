const client = mqtt.connect('wss://broker.emqx.io:8084/mqtt');

client.on('connect', function () {
    console.log('Connected to broker');
    client.subscribe('flask/test');
});

client.on('message', function (topic, message) {
    const msg = message.toString();
    const div = document.getElementById("messages");
    div.innerHTML += `<p><b>${topic}</b>: ${msg}</p>`;
});