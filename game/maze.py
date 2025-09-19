import arcade, arcade.gui, time, random
from plyer import notification
from utils.constants import ROWS, COLS

class Game(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()
        self.pypresence_client = pypresence_client
        self.pypresence_client.update(state="Solving a maze inside notifications!")

        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))
        self.info_label = self.anchor.add(arcade.gui.UILabel("Use arrow keys or WASD to move.\nMaze is shown in notifications.", font_size=24, multiline=True))

        self.running = True
        self.time_start = time.perf_counter()

        self.current_position = arcade.math.Vec2(1, 1)
        self.direction = arcade.math.Vec2()
        
    def on_show_view(self):
        self.maze, start_x, start_y = self.generate_maze(int(COLS / 2), int(ROWS / 2))
        self.current_position = arcade.math.Vec2(start_x, start_y)
        self.update()

    def update(self):
        if not self.running:
            return

        next_pos = self.current_position + self.direction
        nx, ny = int(next_pos.x), int(next_pos.y)

        if 0 <= ny < len(self.maze) and 0 <= nx < len(self.maze[0]):
            if self.maze[ny][nx] != "#":
                self.current_position = next_pos
                if self.maze[ny][nx] == "E":
                    self.running = False
                    elapsed = int(time.perf_counter() - self.time_start)

                    self.info_label.text = f"Maze completed in {elapsed}s! Press r to restart."

                    notification.notify(
                        title="Maze Completed!",
                        message=f"You reached the end in {elapsed}s!")
                    return

        display_rows = []
        for y, row in enumerate(self.maze):
            line = ""
            for x, ch in enumerate(row):
                if (x, y) == (int(self.current_position.x), int(self.current_position.y)):
                    line += "P"
                else:
                    line += ch
            display_rows.append(line)

        self.direction = arcade.math.Vec2()
        notification.notify(
            title=f"Maze | {int(time.perf_counter() - self.time_start)}s",
            message='\n'.join(display_rows),
            timeout=15
        )

    def on_key_press(self, symbol, modifiers):
        if symbol in (arcade.key.UP, arcade.key.W):
            self.direction = arcade.math.Vec2(0, -1)
            self.update()
        elif symbol in (arcade.key.DOWN, arcade.key.S):
            self.direction = arcade.math.Vec2(0, 1)
            self.update()
        elif symbol in (arcade.key.LEFT, arcade.key.A):
            self.direction = arcade.math.Vec2(-1, 0)
            self.update()
        elif symbol in (arcade.key.RIGHT, arcade.key.D):
            self.direction = arcade.math.Vec2(1, 0)
            self.update()
        elif symbol == arcade.key.R and not self.running:
            self.running = True
            self.time_start = time.perf_counter()

            self.info_label.text = "Use arrow keys or WASD to move.\nMaze is shown in notifications."
            
            self.maze, start_x, start_y = self.generate_maze(int(COLS / 3), int(ROWS / 3))
            self.current_position = arcade.math.Vec2(start_x, start_y)
            self.update()

        elif symbol == arcade.key.ESCAPE:
            from menus.main import Main
            self.window.show_view(Main(self.pypresence_client))

    def generate_maze(self, width, height):
        maze = [['#' for _ in range(width)] for _ in range(height)]

        def is_valid(x, y):
            return 1 <= x < width - 1 and 1 <= y < height - 1

        def get_neighbors(x, y):
            neighbors = []
            
            for dx, dy in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
                nx, ny = x + dx, y + dy

                if is_valid(nx, ny) and maze[ny][nx] == '#':
                    neighbors.append((nx, ny))

            return neighbors

        def carve(x, y):
            maze[y][x] = '_'

            neighbors = get_neighbors(x, y)
            random.shuffle(neighbors)

            for nx, ny in neighbors:
                if maze[ny][nx] == '#':
                    maze[y + (ny - y) // 2][x + (nx - x) // 2] = '_'
                    carve(nx, ny)

        start_x = 1 if width % 2 == 1 else 2
        start_y = 1 if height % 2 == 1 else 2
        
        carve(start_x, start_y)

        maze[start_y][0] = '_'

        for y in range(height - 2, 0, -1):
            if maze[y][width - 2] == '_':
                maze[y][width - 1] = '_'
                break

        maze[height - 2][width - 1] = 'E'

        return maze, start_x, start_y