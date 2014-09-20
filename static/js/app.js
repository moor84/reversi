
var App = function (options) {
    this.position = undefined;

    this.run = function () {
        console.log("Run...");
        this.connect();
        this.updateScreen();
    };

    this.connect = function () {
        var app = this;
        this.ws = new WebSocket("ws://" + options.host + ":" + options.port + '/ws');

        this.ws.onmessage = function (evt) {
            console.log('message received: ' + evt.data);
            var message = JSON.parse(evt.data);
            app['on_' + message.event](message.data);
        };

        this.ws.onclose = function (evt) {
            console.log("Connection close");
        };

        this.ws.onopen = function(evt) {
            console.log('Connected');
            app.on_connected();
        };
    };

    this.send = function (event, data) {
        var payload = JSON.stringify({event: event, data: data});
        console.log('sending message: ' + payload);
        this.ws.send(payload);
    };

    this.updateScreen = function () {
        var app = this
        if (!this.screen) {
            this.screen = new Screen({
                canvasId: options.canvasId,
                onClick: function (x, y) {

                },
                onBoardClicked: function (cellA, cellB) {
                    console.log('Board clicked - ' + cellA + ':' + cellB);
                    app.on_board_clicked(cellA, cellB);
                },
            });
        }
        this.screen.render({
            position: this.position
        });
    };

    this.on_connected = function () {
        this.send('game_started', {});
    };

    this.on_board_clicked = function (cellA, cellB) {
        this.send('move', {'a': cellA, 'b': cellB});
    };

    this.on_position_changed = function (data) {
        this.position = data.position;
        this.updateScreen();
    };
}
