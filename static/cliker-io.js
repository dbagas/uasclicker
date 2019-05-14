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
        var tabel = []
        for (var response in data) {
            tabel.push(data[response])
            document.querySelector('#' + response).innerHTML = data[response]
        }
        console.log(tabel);
        var ctx = document.getElementById('myChart').getContext('2d');
          var myChart = new Chart(ctx, {
              type: 'bar',
              data: {
                  labels: ['a', 'b', 'c', 'd', 'e'],
                  datasets: [{
                      label: '# of Votes',
                      data: tabel,
                      backgroundColor: [
                          'rgba(255, 99, 132, 0.2)',
                          'rgba(54, 162, 235, 0.2)',
                          'rgba(255, 206, 86, 0.2)',
                          'rgba(75, 192, 192, 0.2)',
                          'rgba(153, 102, 255, 0.2)',
                          'rgba(255, 159, 64, 0.2)'
                      ],
                      borderColor: [
                          'rgba(255, 99, 132, 1)',
                          'rgba(54, 162, 235, 1)',
                          'rgba(255, 206, 86, 1)',
                          'rgba(75, 192, 192, 1)',
                          'rgba(153, 102, 255, 1)',
                          'rgba(255, 159, 64, 1)'
                      ],
                      borderWidth: 1
                  }]
              },
              options: {
                  scales: {
                      yAxes: [{
                          ticks: {
                              beginAtZero: true
                          }
                      }]
                  }
              }
          });
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
