
var CellState = {
    EMPTY: 0,
    WHITE: 1,
    BLACK: 2,
    POSSIBLE_MOVE: 3
};

var BOARD_HOR = 8;
var BOARD_VER = 8;

var Board = function (options) {
    var canvas = options.canvas;

    this.top = options.top;
    this.left = options.left;
    this.width = options.width;
    this.height = options.height;

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
        if (position) {
            renderPosition(position);
        }
    };

    this.getCellFromCoords = function (x, y) {
        var localX = x - this.left;
        var localY = y - this.top;
        var cellWidth = options.width / BOARD_HOR;
        var cellHeight = options.height / BOARD_VER;
        return [Math.floor(localY / cellHeight), Math.floor(localX / cellWidth)];
    };
};

var Screen = function (screen_options) {
    this.render = function (data) {
        var screen = this;
        if (!this.canvas) {
            this.canvas = new fabric.Canvas(screen_options.canvasId, {
                backgroundColor: 'blue',
                interactive: false,
                selection: false
            });
            this.canvas.on('mouse:down', function(options) {
                var point = screen.canvas.getPointer(options.e);
                screen_options.onClick(point.x, point.y);
                if (point.x >= screen.board.left && point.y >= screen.board.top
                    && point.x <= (screen.board.left + screen.board.width)
                    && point.y <= (screen.board.top + screen.board.height)) {
                    var cell = screen.board.getCellFromCoords(point.x, point.y);
                    screen_options.onBoardClicked(cell[0], cell[1]);
                }
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
        this.board.render(data.position);
    }
};
