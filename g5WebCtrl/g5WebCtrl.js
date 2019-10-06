var WebSocket   	= require("ws");
const Max = require('max-api');

// LOCAL
// wsServer = "ws://localhost:3000";
// HEROKU
wsServer = "wss://g5interspecies.herokuapp.com/wss";

Max.post('WebSocket to '+wsServer);

Max.addHandler("function", (msg) => {
	console.log("Received function : "+msg);
	const ws = new WebSocket(wsServer);
	ws.on('open', function open() {
		ws.send(JSON.stringify(
			{
				charset : 'utf8mb4', 
				command: msg
			}));
		ws.close();
	});
});

Max.addHandler("setChart", (i) => {
	console.log("Received /setChart "+i);
	const ws = new WebSocket(wsServer);
	ws.on('open', function open() {
		ws.send(JSON.stringify(
			{
				charset : 'utf8mb4', 
				command: "setChart",
				chart: i
			}));
		ws.close();
	});
});

Max.addHandler("setSocketAddress", (msg) => {
	console.log("Received /setSocketAddress "+msg);
	wsServer = msg;
	Max.post('WebSocket to '+wsServer);
});

Max.addHandler("keepAlive", (msg) => {
	const ws = new WebSocket(wsServer);
	ws.on('open', function open() {
		ws.send(JSON.stringify(
			{
				charset : 'utf8mb4', 
				command: "keepAlive"
			}));
		ws.close();
	});
});

Max.addHandler("setReferendum", (msg) => {
	console.log("Received /setReferendum "+msg);
	const ws = new WebSocket(wsServer);
	ws.on('open', function open() {
		ws.send(JSON.stringify(
			{
				charset : 'utf8mb4', 
				command: "setReferendum",
				referendum: msg
			}));
		ws.close();
	});
});

Max.addHandler("setLang", (msg) => {
	console.log("Received /setLang "+msg);
	const ws = new WebSocket(wsServer);
	ws.on('open', function open() {
		ws.send(JSON.stringify(
			{
				charset : 'utf8mb4', 
				command: "setLang",
				lang: msg
			}));
		ws.close();
	});
});