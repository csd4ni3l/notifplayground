import arcade, arcade.gui, time, random, os, json

from plyer import notification

from utils.constants import TETRIS_SHAPES

class Game(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()

        self.pypresence_client = pypresence_client
        self.pypresence_client.update(state="Playing Tetris inside notifications!")

        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))
        self.info_label = self.anchor.add(arcade.gui.UILabel("Use arrow keys or WASD to move the blocks\nThe game is shown inside notifications.", font_size=24, multiline=True))

        self.running = True
        self.last_update_time = time.perf_counter()

        if not os.path.exists("data.json"):
            self.data = {}
        else:
            with open("data.json", "r") as file:
                self.data = json.load(file)

        if not "tetris" in self.data:
            self.data["tetris"] = {"high_score": 0}
        
        self.high_score = self.data["tetris"]["high_score"]
        self.score = 0

        self.shape_to_place = random.choice(list(TETRIS_SHAPES.keys()))
        self.next_shape_to_place = random.choice(list(TETRIS_SHAPES.keys()))
        self.shape_data = TETRIS_SHAPES[self.shape_to_place]
        
        self.grid = [[0 for _ in range(10)] for _ in range(20)]
        self.shape_tuple = ()

        self.current_rotation_index = 0
        self.rotated_shapes = {}
        self.shape_widths = {}

        self.tiles_to_destroy = []

    def can_move(self, x, y, shape_name, dx, dy, rotation_index):
        current_positions = [(x + sx, y + sy) for sx, sy in self.rotated_shapes[shape_name][rotation_index]]

        for sx, sy in self.rotated_shapes[shape_name][rotation_index]:
            nx, ny = x + sx + dx, y + sy + dy

            if nx < 0 or nx >= 10 or ny < 0 or ny >= 20:
                return False

            if self.grid[ny][nx] and (nx, ny) not in current_positions:
                return False

        return True

    def cache_rotated_shapes(self):
        for name, shape in TETRIS_SHAPES.items():
            self.rotated_shapes[name] = []
            
            self.rotated_shapes[name].append(shape)
            self.rotated_shapes[name].append([(y, -x) for x, y in shape]) # 90 degrees
            self.rotated_shapes[name].append([(-x, -y) for x, y in shape]) # 180 degrees
            self.rotated_shapes[name].append([(-y, x) for x, y in shape]) # 270 degrees

    def list_get(self, lst, index, default=None):
        return lst[index] if 0 <= index < len(lst) else default

    def create_shape(self, start_x, start_y, shape_name, rotation_index=0):
        for x, y in self.rotated_shapes[shape_name][rotation_index]:
            self.grid[start_y + y][start_x + x] = 1

        return (start_x, start_y, shape_name)

    def move_shape(self, start_x, start_y, shape_name, change_x, change_y):
        if not self.can_move(start_x, start_y, shape_name, change_x, change_y, self.current_rotation_index):
            self.shape_to_place = self.next_shape_to_place
            self.next_shape_to_place = random.choice(list(TETRIS_SHAPES.keys()))
            self.spawn_shape()

            return

        for x, y in self.rotated_shapes[shape_name][self.current_rotation_index]:
            self.grid[start_y + y][start_x + x] = 0

        for x, y in self.rotated_shapes[shape_name][self.current_rotation_index]:            
            self.grid[start_y + change_y + y][start_x + change_x + x] = 1

        self.shape_tuple = (start_x + change_x, start_y + change_y, shape_name)

    def rotate_shape(self, start_x, start_y, shape_name):
        for x, y in self.rotated_shapes[shape_name][self.current_rotation_index]:
            self.grid[start_y + y][start_x + x] = 0

        self.current_rotation_index += 1

        if self.current_rotation_index == 4:
            self.current_rotation_index = 0

        return self.create_shape(start_x, start_y, shape_name, self.current_rotation_index)

    def on_show_view(self):
        super().on_show_view()
        
        self.cache_rotated_shapes()
        self.spawn_shape()
        
    def spawn_shape(self):
        self.shape_tuple = self.create_shape(int(10 / 2), 0, self.shape_to_place)

    def on_update(self, delta_time):
        if self.running and time.perf_counter() - self.last_update_time >= 0.4:
            self.last_update_time = time.perf_counter()

            self.move_shape(*self.shape_tuple, 0, 1)

            if any(all(self.grid[row][col] for row in range(5)) for col in range(10)): # check if any columns are all full
                self.info_label.text = "Game Over.\nPress r to restart"
                self.running = False

                notification.notify(
                    title="Tetris inside notifications",
                    message="Game Over!"
                )

                return
            
            for row in range(20):
                if all(self.grid[row]):
                    self.grid[row] = [0] * 10
                    self.score += 10 * 10

            text = ""

            for y in range(20):
                for x in range(10):
                    if self.grid[y][x]:
                        text += "#"
                    else:
                        text += "_"

                text += "\n"

            if self.score > self.high_score:
                self.high_score = self.score

            notification.notify(
                title=f"Tetris | Score: {self.score} High Score: {self.high_score}",
                message=text
            )

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.data["tetris"]["high_score"] = self.high_score
            with open("data.json", "w") as file:
                file.write(json.dumps(self.data, indent=4))

            from menus.main import Main
            self.window.show_view(Main(self.pypresence_client))
        elif symbol == arcade.key.R and not self.running:
            self.score = 0

            self.shape_to_place = random.choice(list(TETRIS_SHAPES.keys()))
            self.next_shape_to_place = random.choice(list(TETRIS_SHAPES.keys()))
            self.shape_data = TETRIS_SHAPES[self.shape_to_place]
            
            self.grid = [[0 for _ in range(10)] for _ in range(20)]
            self.shape_tuple = ()

            self.current_rotation_index = 0

            self.tiles_to_destroy = []

            self.spawn_shape()

            self.running = True
        elif symbol == arcade.key.SPACE:
            self.shape_tuple = self.rotate_shape(*self.shape_tuple)
        elif symbol == arcade.key.LEFT and self.can_move(*self.shape_tuple, -1, 0, self.current_rotation_index):
            self.move_shape(*self.shape_tuple, -1, 0)
        elif symbol == arcade.key.RIGHT and self.can_move(*self.shape_tuple, 1, 0, self.current_rotation_index):
            self.move_shape(*self.shape_tuple, 1, 0)
        elif symbol == arcade.key.DOWN and self.can_move(*self.shape_tuple, 0, 1, self.current_rotation_index):
            self.move_shape(*self.shape_tuple, 0, 1)