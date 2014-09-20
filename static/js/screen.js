
var CellState = {
    EMPTY: 0,
    WHITE: 1,
    BLACK: 2,
    POSSIBLE_MOVE: 3
};

var BOARD_HOR = 8;
var BOARD_VER = 8;

var DEFAULT_POSITION = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 3, 0, 0, 0, 0],
    [0, 0, 3, 1, 2, 0, 0, 0],
    [0, 0, 0, 2, 1, 3, 0, 0],
    [0, 0, 0, 0, 3, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0]
];

var Board = function (options) {
    var canvas = options.canvas;

    var renderCell = function (state, t, l, w, h) {
        if (state == CellState.WHITE) {
            var color = 'white';
        } else if (state == CellState.BLACK) {
            var color = 'black';
        } else if (state == CellState.POSSIBLE_MOVE) {
            canvas.add(new fabric.Rect({
                top: t,
                left: l,
                width: w,
                height: h,
                fill: 'rgba(0, 200, 0, 0.5)',
                stroke: 'black',
                strokeWidth: 1,
                selectable: false
            }));
            return;
        } else {
            return;
        }
        var padding = 5;
        canvas.add(new fabric.Circle({
            radius: w / 2 - padding,
            left: l + padding,
            top: t + padding,
            fill: color,
            selectable: false
        }));
    };

    var renderPosition = function (position) {
        var w = options.width / BOARD_HOR;
        var h = options.height / BOARD_VER;
        for (var i=0; i < position.length; i++) {
            var line = position[i];
            for (var n=0; n < line.length; n++) {
                var t = options.top + i * h;
                var l = options.left + n * w;
                renderCell(line[n], t, l, w, h);
            }
        }
    };

    var renderBackground = function () {
        canvas.add(new fabric.Rect({
            top: options.top,
            left: options.left,
            width: options.width,
            height: options.height,
            fill: 'green',
            stroke: 'black',
            strokeWidth: 2,
            selectable: false
        }));
        var w = options.width / BOARD_HOR;
        var h = options.height / BOARD_VER;
        for (var i=1; i <= BOARD_HOR; i++) {
            var line = new fabric.Line([options.left + i * w, options.left, options.left + i * w, options.left + options.height], {
                stroke: 'black'
            });
            canvas.add(line);
        }
        for (var i=1; i <= BOARD_VER; i++) {
            var line = new fabric.Line([options.top, options.top + i * h, options.top + options.width, options.top + i * h], {
                stroke: 'black'
            });
            canvas.add(line);
        }
    };

    this.render = function (position) {
        renderBackground();
        renderPosition(position);
    };
};

var Screen = function (options) {
    this.render = function (position) {
        if (!this.canvas) {
            this.canvas = new fabric.Canvas(options.canvasId, {
                backgroundColor: 'blue',
                interactive: false,
                selection: false
            });
        }

        if (!this.board) {
            this.board = new Board({
                canvas: this.canvas,
                top: 50,
                left: 50,
                width: 300, //this.canvas.getWidth(),
                height: 300 //this.canvas.getHeight()
            });
        }

        this.canvas.clear();
        this.board.render(position || DEFAULT_POSITION);
    }

};
