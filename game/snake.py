import arcade, arcade.gui, time, random, os, json

from plyer import notification

class Game(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()

        self.pypresence_client = pypresence_client
        self.pypresence_client.update(state="Playing Snake inside notifications!")

        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))
        self.info_label = self.anchor.add(arcade.gui.UILabel("Use arrow keys or WASD to move.\nYou can see the game inside notifications.", font_size=24, multiline=True), anchor_x="center", anchor_y="center")

        self.direction = "right"
        self.running = True
        self.last_update_time = time.perf_counter()

        with open("settings.json", "r") as file:
            self.settings = json.load(file)

        self.snake = [(int(self.settings.get("notification_cols", 25) / 2), int(self.settings.get("notification_rows", 20) / 2))]
        self.foods = []

        if not os.path.exists("data.json"):
            self.data = {}
        else:
            with open("data.json", "r") as file:
                self.data = json.load(file)

        if not "snake" in self.data:
            self.data["snake"] = {"high_score": 0}

        self.high_score = self.data["snake"]["high_score"]
        self.score = 0

    def spawn_food(self):
        while True:
            x, y = (random.randint(0, self.settings.get("notification_cols", 25)), random.randint(0, self.settings.get("notification_rows", 20)))

            if not (x, y) in self.snake:
                return (x, y)

    def on_update(self, dt):
        if self.running and time.perf_counter() - self.last_update_time >= self.settings.get("notification_timeout", 0.4):
            self.last_update_time = time.perf_counter()

            head_x, head_y = self.snake[0]

            if self.direction == "right":
                new_head = (head_x + 1, head_y)
            elif self.direction == "left":
                new_head = (head_x - 1, head_y)
            elif self.direction == "up":
                new_head = (head_x, head_y - 1)
            elif self.direction == "down":
                new_head = (head_x, head_y + 1)

            if new_head in self.snake or not (0 <= new_head[0] < self.settings.get("notification_cols", 25) and 0 <= new_head[1] < self.settings.get("notification_rows", 20)):
                self.info_label.text = "Game Over.\nPress r to restart"
                self.running = False

                notification.notify(
                    title="Snake inside notifications",
                    message='Game Over!'
                )

                return

            if new_head in self.foods:
                self.score += 1
                
                self.foods.remove(new_head)
                self.snake = [new_head] + self.snake
                self.foods.append(self.spawn_food())
            else:
                self.snake = [new_head] + self.snake[:-1]

            text = ""

            for y in range(self.settings.get("notification_rows", 20)):
                for x in range(self.settings.get("notification_cols", 25)):
                    if (x, y) == self.snake[0]:
                        text += "H"
                    elif (x, y) in self.snake[1:]:
                        text += "o"
                    elif (x, y) in self.foods:
                        text += "*"
                    else:
                        text += "_"

                text += "\n"
            
            if self.score > self.high_score:
                self.high_score = self.score

            notification.notify(
                title=f"Snake | Score: {self.score} High Score: {self.high_score}",
                message=text
            )

    def on_show_view(self):
        super().on_show_view()

        self.foods = [self.spawn_food() for _ in range(3)]

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.LEFT or symbol == arcade.key.A:
            self.direction = "left"
        elif symbol == arcade.key.RIGHT or symbol == arcade.key.D:
            self.direction = "right"
        elif symbol == arcade.key.UP or symbol == arcade.key.W:
            self.direction = "up"
        elif symbol == arcade.key.DOWN or symbol == arcade.key.S:
            self.direction = "down"
        elif symbol == arcade.key.R and not self.running:
            self.info_label.text = "Press keys inside this window to interact with the game.\nYou can see the game inside notifications."
            self.info_label.fit_content()
            
            self.snake = [(int(self.settings.get("notification_cols", 25) / 2), int(self.settings.get("notification_rows", 20) / 2))]
            self.foods = [self.spawn_food() for _ in range(3)]
            self.running = True
        elif symbol == arcade.key.ESCAPE:
            self.data["snake"]["high_score"] = self.high_score
            with open("data.json", "w") as file:
                file.write(json.dumps(self.data, indent=4))

            from menus.main import Main
            self.window.show_view(Main(self.pypresence_client))