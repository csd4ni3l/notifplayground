import arcade, arcade.gui, time, random, os, json

from plyer import notification

from utils.constants import ROWS, COLS

class Game(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()

        self.pypresence_client = pypresence_client
        self.pypresence_client.update(state="Playing Pong inside notifications!")

        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))
        self.info_label = self.anchor.add(arcade.gui.UILabel("Use arrow keys or WASD to move\nYou can see the game inside notifications.", font_size=24, multiline=True))

        self.running = True
        self.last_update_time = time.perf_counter()

        self.ball_position = arcade.math.Vec2(int(COLS / 2), int(ROWS / 4))
        
        self.ball_direction = arcade.math.Vec2(*random.choice([(-1, 1), (1, 1), (-1, 1), (-1, -1)]))

        self.paddle_a_position = arcade.math.Vec2(0, int(ROWS / 4))
        self.paddle_a_direction = 0

        self.paddle_b_position = arcade.math.Vec2(COLS - 1, int(ROWS / 4))
        self.paddle_b_direction = 0

        self.score_a = 0
        self.score_b = 0

        if not os.path.exists("data.json"):
            self.data = {}
        else:
            with open("data.json", "r") as file:
                self.data = json.load(file)

        if not "pong" in self.data:
            self.data["pong"] = {"high_score": 0}

        self.high_score = self.data["pong"]["high_score"]

    def on_update(self, delta_time):
        if self.running and time.perf_counter() - self.last_update_time >= 0.4:
            self.last_update_time = time.perf_counter()

            self.ball_position += self.ball_direction

            if self.paddle_b_position.y < self.ball_position.y:
                self.paddle_b_direction = 1
            elif self.paddle_b_position.y > self.ball_position.y:
                self.paddle_b_direction = -1
            else:
                self.paddle_b_direction = 0
            
            self.paddle_a_position = arcade.math.Vec2(self.paddle_a_position.x, self.paddle_a_position.y + self.paddle_a_direction)
            self.paddle_b_position = arcade.math.Vec2(self.paddle_b_position.x, self.paddle_b_position.y + self.paddle_b_direction)
            self.paddle_a_direction, self.paddle_b_direction = 0, 0

            if self.ball_position.distance(self.paddle_a_position) <= 1:
                self.ball_direction = self.ball_direction.reflect(arcade.math.Vec2(1, 0))
                self.ball_position += self.ball_direction * 2 # needed so it doesnt get stuck in an infinite loop

            elif self.ball_position.distance(self.paddle_b_position) <= 1:
                self.ball_direction = self.ball_direction.reflect(arcade.math.Vec2(-1, 0))
                self.ball_position += self.ball_direction * 2 # needed so it doesnt get stuck in an infinite loop

            else:
                if self.ball_position.x <= 0:
                    if self.ball_position.y <= 0 or self.ball_position.y >= int(ROWS / 2):
                        self.ball_position = arcade.math.Vec2(0, self.ball_position.y)
                        self.ball_direction = self.ball_direction.reflect(arcade.math.Vec2(1, 0))
                    else:
                        self.score_b += 1
                        self.ball_position = arcade.math.Vec2(int(COLS / 2), int(ROWS / 4))
                        self.ball_direction = arcade.math.Vec2(*random.choice([(-1, 1), (1, 1), (-1, 1), (-1, -1)]))

                elif self.ball_position.x >= COLS:
                    if self.ball_position.y <= 0 or self.ball_position.y >= int(ROWS / 2):
                        self.ball_position = arcade.math.Vec2(COLS, self.ball_position.y)
                        self.ball_direction = self.ball_direction.reflect(arcade.math.Vec2(-1, 0))
                    else:
                        self.score_a += 1
                        self.ball_position = arcade.math.Vec2(int(COLS / 2), int(ROWS / 4))
                        self.ball_direction = arcade.math.Vec2(*random.choice([(-1, 1), (1, 1), (-1, 1), (-1, -1)]))
      
                if self.ball_position.y <= 0:
                    self.ball_position = arcade.math.Vec2(self.ball_position.x, 0)
                    self.ball_direction = self.ball_direction.reflect(arcade.math.Vec2(0, 1))
                elif self.ball_position.y >= int(ROWS / 2):
                    self.ball_position = arcade.math.Vec2(self.ball_position.x, int(ROWS / 2))
                    self.ball_direction = self.ball_direction.reflect(arcade.math.Vec2(0, -1))

            text = ""
            
            for y in range(int(ROWS / 2)):
                for x in range(COLS):
                    if (x, y) == self.paddle_a_position or (x, y) == self.paddle_b_position:
                        text += "|"
                    elif self.ball_position == (x, y):
                        text += "O"
                    else:
                        text += "_"

                text += "\n"

            if self.score_a > self.high_score:
                self.high_score = self.score_a

            notification.notify(
                title=f"Pong (A: {self.score_a}, B: {self.score_b}, High Score: {self.high_score})",
                message=text
            )

    def on_show_view(self):
        super().on_show_view()

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.data["pong"]["high_score"] = self.high_score
            with open("data.json", "w") as file:
                file.write(json.dumps(self.data, indent=4))

            from menus.main import Main
            self.window.show_view(Main(self.pypresence_client))
        elif symbol == arcade.key.R and not self.running:            
            self.paddle_a_direction = 0
            self.paddle_a_position = arcade.math.Vec2(0, int(ROWS / 4))

            self.paddle_b_direction = 0
            self.paddle_b_position = arcade.math.Vec2(COLS - 1, int(ROWS / 4))

            self.ball_position = arcade.math.Vec2(int(COLS / 2), int(ROWS / 4))
            self.ball_direction = arcade.math.Vec2(*random.choice([(-1, 1), (1, 1), (-1, 1), (-1, -1)]))

            self.running = True

        elif symbol == arcade.key.UP or symbol == arcade.key.W:
            self.paddle_a_direction = -1
        elif symbol == arcade.key.DOWN or symbol == arcade.key.S:
            self.paddle_a_direction = 1