from checkio.signals import ON_CONNECT
from checkio import api
from checkio.referees.multicall import CheckiORefereeMulti
from checkio.referees import cover_codes
from checkio.referees import checkers
from checkio.signals import PROCESS_ENDED
from checkio import api
from checkio.api import DEFAULT_FUNCTION

from checkio.runner_types import SIMPLE


REQ = 'req'
REFEREE = 'referee'

from tests import TESTS

DIRS = {"N": (-1, 0), "S": (1, 0), "W": (0, -1), "E": (0, 1)}

WALL = "X"
EXIT = "E"
EMPTY = "."
MAX_STEP = 250


def get_visible(maze, player):
    result = {}
    for direction, (dr, dc) in DIRS.items():
        cr, cc = player
        distance = -1
        while maze[cr][cc] != WALL:
            cr += dr
            cc += dc
            distance += 1
        result[direction] = distance
    return result


def initial(data):
    scanner = get_visible(data["maze"], data["player"])
    return {"input": [scanner, 0], "player": data["player"], "old_player": data["player"],
            "maze": data["maze"], "step": 0}


def process(data, user_result):
    maze = data["maze"]
    player = data["player"]
    data["old_player"] = player
    step = data["step"]
    if not isinstance(user_result, (list, tuple)) or len(user_result) != 2:
        data.update({
            "result": False,
            "result_addon": "The function should return an action string and a number."
        })
        return data
    actions, memory = user_result
    if not isinstance(actions, str) or any(ch not in DIRS.keys() for ch in actions):
        data.update({
            "result": False,
            "result_addon": "The actions string should return a string with directions."
        })
        return data
    if not isinstance(memory, int) or memory < 0 or memory >= 2 ** 100:
        data.update({
            "result": False,
            "result_addon": "The memory number should be an integer from 0 to 2**100."
        })
        return data


    for act in actions:
        if step >= MAX_STEP:
            data.update({
                "result": False,
                "result_addon": "You are tired and your scanner is off. Bye bye."
            })
            return data
        r, c = player[0] + DIRS[act][0], player[1] + DIRS[act][1]
        if maze[r][c] == WALL:
            data.update({
                "result": False,
                "result_addon": "BAM! You in the wall at {}, {}.".format(r, c)
            })
            return data
        elif maze[r][c] == EXIT:
            data.update({
                "result": True,
                "result_addon": "GRATZ!",
                "is_win": True
            })
            return data
        else:
            player = r, c
            step += 1

    scanner = get_visible(maze, player)
    data.update({
        "result": True,
        "result_addon": "Next iteration",
        "player": player,
        "input": [scanner, memory],
        "step": step
    })
    return data


def is_win(data):
    return data.get("is_win", False)




class CheckiORefereeMultiReset(CheckiORefereeMulti):
    def __init__(self, *args, **kwargs):
        self.next_step = False
        super().__init__(*args, **kwargs)

    def test_current_step(self, dummy=None):
        self.current_step += 1
        api.execute_function(input_data=self.referee_data["input"],
                             callback=self.check_current_test,
                             errback=self.fail_cur_step,
                             func=self.function_name)


    def check_current_test(self, data):
        user_result = data['result']

        self.referee_data = self.process_referee(self.referee_data, user_result)

        referee_result = self.referee_data.get("result", False)

        is_win_result = False

        if referee_result:
            is_win_result = self.is_win_referee(self.referee_data)

        self.referee_data.update({"is_win": is_win_result})

        api.request_write_ext(self.referee_data)

        if not referee_result:
            return api.fail(self.current_step, self.get_current_test_fullname())

        if not is_win_result:
            self.next_step = True
            api.kill_runner('req')
        else:
            if self.next_env():
                self.restart_env()
            else:
                api.success()

    def process_req_ended(self, data):
        if self.restarting_env:
            print("RESTART!!!!")
            self.next_step = False
            self.restarting_env = False
            self.start_env()
        elif self.next_step:
            self.next_step = False
            self.start_env_middle()
        else:
            api.fail(self.current_step, self.get_current_test_fullname())

    def start_env_middle(self):
        api.start_runner(code=self.code,
                         runner=self.runner,
                         prefix=REQ,
                         controller_type=SIMPLE,
                         callback=self.test_current_step,
                         errback=self.fail_cur_step,
                         add_close_builtins=self.add_close_builtins,
                         add_allowed_modules=self.add_allowed_modules,
                         remove_allowed_modules=self.remove_allowed_modules,
                         write_execute_data=True,
                         cover_code=self.cover_code.get(self.runner))


api.add_listener(
    ON_CONNECT,
    CheckiORefereeMultiReset(
        tests=TESTS,
        cover_code={
            'python-27': cover_codes.unwrap_args,  # or None
            'python-3': cover_codes.unwrap_args
        },
        initial_referee=initial,
        process_referee=process,
        is_win_referee=is_win,
        function_name="find_path"
    ).on_ready)

