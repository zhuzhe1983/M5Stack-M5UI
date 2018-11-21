var CLIENT_VER = '181011-Beta';

var DEFAULT_SERVER = 'ws://192.168.31.25:8000';

var ws;		// Websocket

newSession(DEFAULT_SERVER);


// ================================================================
// Create a new websocket server, including all events:
// ws.onopen()
// ws.onmessage()
// ws.onclose()
// ws.onerror()
// ================================================================
function newSession(server) {

	// -- Connect to Web Socket
	ws = new WebSocket(server);

	// -- Set event handlers
	ws.onopen = function() {
		showMsg(`Server opened. Client ver: ${CLIENT_VER}`);
		var now = new Date();

		// -- Send login request
		ws.send(JSON.stringify(['ls', 0]));
	};
		
	ws.onmessage = function(e) {
		// -- e.data contains received string.
		var getMsg = JSON.parse(e.data);
		// console.log(getMsg);

		// -- Server reply "login"
		console.log(getMsg)
		if (getMsg[0] === "ls" || getMsg[0] === "cd") {
			for (var i = 0; i < getMsg[1].length; i++) {
				showMsg(getMsg[1][i]);
			}
		}
		else if (getMsg[0] === "get") {
			editor.setValue(getMsg[1]);
		}
	};

	ws.onclose = function() {
		showMsg("Server closed.");
	};

	ws.onerror = function(e) {
		showMsg("Server error.", "red");
		formStatusSet(false);
	};
}

// ================================================================
// Output something in log region. There are 2 typical situations:
// 1. msg is plain text: text will be shown directly;
// 2. msg is json object: text will be handled first.
// And encrypt mode status can influence the handling process.
// ================================================================
function showMsg(msg, color="#CCCCCC") {
	var log = $('#log');
	var notice = true;
	// -- msg is plain text
	log.prepend(`<font color="${color}">${msg}<br></font>`);

}

$('#btn_enter').click(function () {
	var cmd = $('#s_cmd').val();
	showMsg(`>> ${cmd}`, color="#00FF00")
	ws.send(JSON.stringify(cmd.split(' ')));
});