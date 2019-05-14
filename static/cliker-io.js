document.addEventListener('DOMContentLoaded', () => {
    // Support TLS-specific URLs, when appropriate.
    if (window.location.protocol == "https:") {
        var ws_scheme = "wss://";
    } else {
        var ws_scheme = "ws://"
    };
    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // When connected, configure buttons
    socket.on('connect', () => {

        // Each button should emit a "submit response" event
        document.querySelectorAll('button').forEach(button => {
            button.onclick = () => {
                // When button clicked emit a dataset
                const selection = button.dataset.response;
                console.log(selection);
                socket.emit('submit response', {'selection': selection});
            };
        });
        document.querySelectorAll('input').forEach(input => {
            input.onclick = () => {
                // When button clicked emit a dataset
                const response = input.dataset.input;
                console.log(response);
                socket.emit(response);
            };
        });
        //socket.emit('timer');
    });

    // When a new response is announced, add to the unordered list
    socket.on('response totals', data => {
        console.log(data);
        for (var response in data) {
            document.querySelector('#' + response).innerHTML = data[response]
        }
    });
    socket.on('response number', data => {
        console.log(data);
        document.querySelector('#number').innerHTML = data;
    });
    socket.on('time', data => {
        console.log(data.time);
        //document.querySelector('#counter').html(data.time);
    });
});
