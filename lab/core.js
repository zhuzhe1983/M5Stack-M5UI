var CLIENT_VER = '181011-Beta';

var DEFAULT_SERVER = 'ws://192.168.31.25:8000';

var ws;		// Websocket

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
			fileListUpdate(getMsg[1]);
		}
		else if (getMsg[0] === "get") {
			editor.setValue(getMsg[1]);
		}
		else if (getMsg[0] === "post") {
			if (getMsg[1] === 1) {
				alert('File uploaded.');
			} else {
				alert('Upload failed.');
			}
		}
	};

	ws.onclose = function() {
	};

	ws.onerror = function(e) {
		formStatusSet(false);
	};
}

function fileListUpdate(fileList) {
	var log = $('#log');
	$('#log')[0].innerHTML = '';
	log.append(`<a class=\"fileLink\" href=\"javascript:onFileSelected('/')\">/</a><br>`);
	log.append(`<a class=\"fileLink\" href=\"javascript:onFileSelected('..')\">..</a><br>`);
	for (var i = 0; i < fileList.length; i++) {
		log.append(`<a class=\"fileLink\" href=\"javascript:onFileSelected('${fileList[i]}')\">${fileList[i]}</a><br>`);
	}
}

function onFileSelected(fname) {
	var cmd;
	// fname points to a folder
	if (fname.indexOf('.') === -1 || fname === '..') {
		cmd = `cd ${fname}`;
	} else {
		// fname points to a file
		fname_ext = fname.split('.');
		if (['py', 'txt', 'conf', 'csv', 'json'].indexOf(fname_ext[fname_ext.length-1].toLowerCase()) > -1) {
			cmd = `get ${fname}`;
			$('#s_fname').val(fname);
		} else {
			return -1
		}
	}
	ws.send(JSON.stringify(cmd.split(' ')));
}


$('#btn_enter').click(function () {
	DEFAULT_SERVER = 'ws://' + $('#s_host').val();
	newSession(DEFAULT_SERVER);
	// ws.send(JSON.stringify(cmd.split(' ')));
});

$('#btn_exit').click(function () {
	var cmd = 'exit 0';
	ws.send(JSON.stringify(cmd.split(' ')));
});

$('#btn_upload').click(function () {
	var cut = function (dataStr, maxSlice) {
		var sliceNum = parseInt(dataStr.length / maxSlice);
		var slices = [];
		var p = 0;

		for (var i=0; i<sliceNum+1; i++) {
			slices.push(dataStr.substring(p, p+maxSlice));
			p += maxSlice;
		}
		return slices;
	}

	var fname = $('#s_fname').val();
	var text = editor.getValue();

	var text_slice = cut(text, 600);

	for (var i=0; i<text_slice.length; i++) {
		if (i === text_slice.length - 1) {
			var cmd = ['post', fname, -1, text_slice[i]];
		} else {
			var cmd = ['post', fname, 1, text_slice[i]];
		}
		ws.send(JSON.stringify(cmd));
		console.log(cmd);
	}
});