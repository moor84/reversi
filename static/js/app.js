
var App = function (options) {
    this.gameId = undefined;
    this.playerId = undefined;
    this.position = undefined;
    this.myTurn = false;

    this.run = function () {
        console.log("Run...");
        this.connect();
        this.updateScreen();
    };

    this.connect = function () {
        var app = this;
        this.ws = new ReconnectingWebSocket("ws://" + options.host + ":" + options.port + '/ws');

        this.ws.onmessage = function (evt) {
            // console.log('message received: ' + evt.data);
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
        var payload = JSON.stringify({
            event: event,
            data: data,
            game_id: this.gameId
        });
        // console.log('sending message: ' + payload);
        this.ws.send(payload);
    };

    this.updateScreen = function () {
        var app = this;
        if (!this.screen) {
            this.screen = new Screen({
                canvasId: options.canvasId,
                onClick: function (x, y) {

                },
                onBoardClicked: function (cellA, cellB) {
                    // console.log('Board clicked - ' + cellA + ':' + cellB);
                    app.on_board_clicked(cellA, cellB);
                },
            });
        }
        this.screen.render({
            position: this.position
        });
    };

    this.startNewGame = function () {
        this.gameId = undefined;
        this.position = undefined;
        console.log('Starting new game...');
        this.send('start_new_game', {});
        this.updateScreen();
    };

    this.joinGame = function () {
        this.gameId = undefined;
        this.position = undefined;
        console.log('Joining a game...');
        this.send('join_game', {});
        this.updateScreen();
    };

    this.setMyTurn = function () {
        this.myTurn = true;
        console.log("Your turn");
    };

    this.setOpponentsTurn = function () {
        this.myTurn = false;
        console.log("Opponent's turn...");
    };

    this.on_connected = function () {

    };

    this.on_game_started = function(data) {
        this.gameId = data.game_id
        this.playerId = data.player.id
        console.log('Game started: ' + data.game_id);
        console.log('Your player id: ' + data.player.id + '(' + data.player.ip + ')');
        console.log('Waiting for the second player connected...');
    };

    this.on_joined_game = function(data) {
        this.gameId = data.game_id
        this.playerId = data.player.id
        console.log('Joined game: ' + data.game_id);
        console.log('Your opponent (black): (' + data.host_ip + ')');
        console.log('You play white tiles');
        document.title = 'Reversi: White';
    };

    this.on_player_joined_game = function (data) {
        console.log('Player joined the game');
        console.log('Your opponent (white): (' + data.player.ip + ')');
        console.log('You play black tiles');
        document.title = 'Reversi: Black';
    };

    this.on_board_clicked = function (cellX, cellY) {
        if (!this.gameId || !this.position) {
            return;
        }
        if (!this.playerId || !this.myTurn) {
            return;
        }
        if (this.position[cellX][cellY] == CellState.POSSIBLE_MOVE) {
            this.send('move', {'x': cellX, 'y': cellY, 'player_id': this.playerId});
        } else {
            console.log('Invalid move');
        }
    };

    this.on_position_changed = function (data) {
        this.position = data.position;
        console.log('Your score: ' + data.my_score + '. Opponent\'s score: ' + data.opponents_score);
        if (data.my_turn) {
            this.setMyTurn();
        } else {
            this.setOpponentsTurn();
        }
        this.updateScreen();
    };

    this.on_game_over = function (data) {
        this.position = data.position;
        this.gameId = undefined;
        this.playerId = undefined;
        console.log('Your score: ' + data.my_score + '. Opponent\'s score: ' + data.opponents_score);
        if (data.i_won) {
            console.log("Congrats! You're the winner! :)");
        } else if (data.opponent_won) {
            console.log("Sorry, you've lost the game :(");
        } else {
            console.log('The game was a tie!');
        }
        this.updateScreen();
    };
}
