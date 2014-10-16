//Dont change it
requirejs(['ext_editor_1', 'jquery_190', 'raphael_210', 'snap.svg_030'],
    function (ext, $, Raphael, Snap) {

        var cur_slide = {};

        ext.set_start_game(function (this_e) {
        });

        ext.set_process_in(function (this_e, data) {
            cur_slide = {};
            cur_slide["in"] = data[0];
            this_e.addAnimationSlide(cur_slide);
        });

        ext.set_process_out(function (this_e, data) {
            cur_slide["out"] = data[0];
        });

        ext.set_process_ext(function (this_e, data) {
            cur_slide.ext = data;
        });

        ext.set_process_err(function (this_e, data) {
            cur_slide['error'] = data[0];
            this_e.addAnimationSlide(cur_slide);
            cur_slide = {};
        });

        ext.set_animate_success_slide(function (this_e, options) {
            var $h = $(this_e.setHtmlSlide('<div class="animation-success"><div></div></div>'));
            this_e.setAnimationHeight(115);
        });

        ext.set_animate_slide(function (this_e, data, options) {
            var $content = $(this_e.setHtmlSlide(ext.get_template('animation'))).find('.animation-content');
            if (!data) {
                console.log("data is undefined");
                return false;
            }

            //YOUR FUNCTION NAME
            var fname = 'find_path';

            var checkioInput = data.in || [
                "XXXX",
                "XPEX",
                "XXXX"
            ];
            var checkioInputStr = fname + '(' + JSON.stringify(checkioInput).replace("[", "(").replace("]", ")") + ')';

            var failError = function (dError) {
                $content.find('.call').html(checkioInputStr);
                $content.find('.output').html(dError.replace(/\n/g, ","));

                $content.find('.output').addClass('error');
                $content.find('.call').addClass('error');
                $content.find('.answer').remove();
                $content.find('.explanation').remove();
                this_e.setAnimationHeight($content.height() + 60);
            };

            if (data.error) {
                failError(data.error);
                return false;
            }

            if (data.ext && data.ext.inspector_fail) {
                failError(data.ext.inspector_result_addon);
                return false;
            }

            $content.find('.call').html(checkioInputStr);
            $content.find('.output').html('Working...');

            var svg = new SVG($content.find(".explanation")[0]);


            if (data.ext) {
                var userResult = data.out;
                var result = data.ext["result"];
                var result_addon = data.ext["result_addon"];
                var maze = data.ext["maze"];
                var player = data.ext["old_player"];

                svg.drawMaze(maze, checkioInput[0], player);

                svg.moving(userResult);

                //if you need additional info from tests (if exists)
                var explanation = data.ext["explanation"];
                $content.find('.output').html('&nbsp;Your result:&nbsp;' + JSON.stringify(userResult));
                if (!result) {
                    $content.find('.answer').html(result_addon);
                    $content.find('.answer').addClass('error');
                    $content.find('.output').addClass('error');
                    $content.find('.call').addClass('error');
                }
                else {
                    $content.find('.answer').remove();
                }
            }
            else {
                $content.find('.answer').remove();
            }


            //Your code here about test explanation animation
            //$content.find(".explanation").html("Something text for example");
            //
            //
            //
            //
            //


            this_e.setAnimationHeight($content.height() + 60);

        });

        //This is for Tryit (but not necessary)
//        var $tryit;
//        ext.set_console_process_ret(function (this_e, ret) {
//            $tryit.find(".checkio-result").html("Result<br>" + ret);
//        });
//
//        ext.set_generate_animation_panel(function (this_e) {
//            $tryit = $(this_e.setHtmlTryIt(ext.get_template('tryit'))).find('.tryit-content');
//            $tryit.find('.bn-check').click(function (e) {
//                e.preventDefault();
//                this_e.sendToConsoleCheckiO("something");
//            });
//        });

        function SVG(dom) {

            var colorOrange4 = "#F0801A";
            var colorOrange3 = "#FA8F00";
            var colorOrange2 = "#FAA600";
            var colorOrange1 = "#FABA00";

            var colorBlue4 = "#294270";
            var colorBlue3 = "#006CA9";
            var colorBlue2 = "#65A1CF";
            var colorBlue1 = "#8FC7ED";

            var colorGrey4 = "#737370";
            var colorGrey3 = "#9D9E9E";
            var colorGrey2 = "#C5C6C6";
            var colorGrey1 = "#EBEDED";

            var colorWhite = "#FFFFFF";

            var paper;

            var player;

            var exit;

            var grid;

            var pad = 10;

            var cell = 30;

            var aCell = {"stroke": colorBlue4, "stroke-width": 2, "fill": colorGrey1};
            var aFullExit = {"stroke": colorBlue4, "fill": colorBlue4, "font-family": "Roboto, Arial, sans", "font-size": cell};
            var aEmptyExit = {"stroke": colorBlue2, "fill": colorBlue2, "font-family": "Roboto, Arial, sans", "font-size": cell};
            var aPlayer = {"stroke": colorBlue4, "fill": colorOrange4, "stroke-width": 2};

            var DIRS = {"N": [-1, 0], "S": [1, 0], "W": [0, -1], "E": [0, 1]};

            this.drawMaze = function (maze, visible, playerCoor) {
                paper = Raphael(dom, pad * 2 + cell * maze[0].length, pad * 2 + cell * maze.length);
                grid = paper.set();
                for (var i = 0; i < maze.length; i++) {
                    var temp = paper.set();
                    for (var j = 0; j < maze[0].length; j++) {
                        var symb = maze[i][j];
                        var r = paper.rect(pad + cell * j, pad + cell * i, cell, cell).attr(aCell);
                        r.mark = symb;
                        temp.push(r);

                        if (symb == "X") {
                            r.attr("fill", colorGrey3);
                        }
                        if (symb == "E") {
                            exit = paper.text(pad + cell * (j + 0.5), pad + cell * (i + 0.5), "E").attr(aFullExit);
                        }
                    }
                    grid.push(temp);
                }

                for (i = playerCoor[0] - visible["N"] - 1; i <= playerCoor[0] + visible["S"] + 1; i++) {
                    if (maze[i][playerCoor[1]] == "X") {
                        grid[i][playerCoor[1]].attr("fill", colorBlue4);
                    }
                    else {
                        grid[i][playerCoor[1]].attr("fill", colorBlue1);
                    }
                }
                for (j = playerCoor[1] - visible["W"] - 1; j <= playerCoor[1] + visible["E"] + 1; j++) {
                    if (maze[playerCoor[0]][j] == "X") {
                        grid[playerCoor[0]][j].attr("fill", colorBlue4);
                    }
                    else {
                        grid[playerCoor[0]][j].attr("fill", colorBlue1);
                    }
                }



                player = paper.circle(
                    pad + cell * (playerCoor[1] + 0.5), pad + cell * (playerCoor[0] + 0.5), cell / 3
                ).attr(aPlayer);
                player.row = playerCoor[0];
                player.col = playerCoor[1];
            };


            this.moving = function (data) {
                var actions = data[0];
                if (typeof(actions) !== "string") {
                    return false;
                }
                var i = 0;
                var stepTime = 200;
                var delay = 100;
                (function move() {
                    var act = actions[i];
                    if (grid[player.row][player.col].mark !== ".") {
                        return false;
                    }
                    if ("NSWE".indexOf(act) === -1) {
                        return false
                    }
                    player.row = player.row + DIRS[act][0];
                    player.col = player.col + DIRS[act][1];
                    i++;
                    setTimeout(function () {
                        player.animate({"transform": "...T" + (DIRS[act][1] * cell) + "," + (DIRS[act][0] * cell)},
                            stepTime, callback = move);
                    }, delay);
                })();
            }

        }

        //Your Additional functions or objects inside scope
        //
        //
        //


    }
);
