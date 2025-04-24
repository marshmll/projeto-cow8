const client = mqtt.connect("wss://broker.emqx.io:8084/mqtt");

client.on("connect", () => {
    console.log("Connected to broker");
    client.subscribe("cow8/measurement");
});

client.on("message", (topic, message) => {
    const msg = message.toString();
    const div = document.getElementById("messages");
    div.innerHTML += `<p><b>${topic}</b>: ${msg}</p>`;
});
