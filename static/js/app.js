
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
            console.log("message received: " + evt.data);
            app.updateScreen();
        };

        this.ws.onclose = function (evt) {
            console.log("Connection close");
        };

        this.ws.onopen = function(evt) {
            console.log('Connected');
        };
    };

    this.updateScreen = function () {
        if (!this.screen) {
            this.screen = new Screen({
                canvasId: options.canvasId
            });
        }
        this.screen.render(this.position);
    };
}
