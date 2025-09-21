import arcade, arcade.gui, time, random, os, json

from plyer import notification

class Game(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()
        self.pypresence_client = pypresence_client
        self.pypresence_client.update(state="Playing Hot Air Baloon inside notifications!")
        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))
        self.info_label = self.anchor.add(arcade.gui.UILabel("Use arrow keys or WASD to move\nYou can see the game inside notifications.", font_size=24, multiline=True))

        self.running = True
        self.last_update_time = time.perf_counter()
        
        self.spikes = []
        self.points = []

        with open("settings.json", "r") as file:
            self.settings = json.load(file)
        
        self.baloon_position = arcade.math.Vec2(0, self.settings.get("notification_rows", 20) - 1)
        self.baloon_direction = arcade.math.Vec2()
        
        if not os.path.exists("data.json"):
            self.data = {}
        else:
            with open("data.json", "r") as file:
                self.data = json.load(file)
        if "hot_air_baloon" not in self.data:
            self.data["hot_air_baloon"] = {"high_score": 0}
        
        self.score = 0
        self.high_score = self.data["hot_air_baloon"]["high_score"]
        
        self.last_spawn_time = time.perf_counter()
        self.spawn_interval = 0.8
        self.difficulty = 0.4
        self.pattern_cooldown = 0
        self.pattern = []

    def spawn_items(self):
        if self.pattern_cooldown <= 0:
            pattern_type = random.choice(["wave", "gap", "scatter"])
            
            if pattern_type == "wave":
                base = random.randint(0, self.settings.get("notification_cols", 25) - 4)
                self.pattern = [(base + i, 0) for i in range(3)]
            elif pattern_type == "gap":
                gap = random.randint(1, self.settings.get("notification_cols", 25) - 2)
                self.pattern = [(x, 0) for x in range(self.settings.get("notification_cols", 25)) if x != gap]
            else:
                self.pattern = [(random.randint(0, self.settings.get("notification_cols", 25) - 1), 0) for _ in range(random.randint(2, 4))]

            self.pattern_cooldown = random.randint(3, 6)

        for pos in self.pattern:
            if random.random() < self.difficulty:
                self.spikes.append(pos)
            else:
                self.points.append(pos)
        
        self.pattern_cooldown -= 1

    def on_show_view(self):
        super().on_show_view()
        self.spawn_items()

    def on_update(self, delta_time):
        if self.running and time.perf_counter() - self.last_update_time >= self.settings.get("notification_timeout", 0.4):
            self.last_update_time = time.perf_counter()

            self.baloon_position += self.baloon_direction
            self.baloon_direction = arcade.math.Vec2()

            self.baloon_position = arcade.math.Vec2(max(0, min(self.settings.get("notification_cols", 25) - 1, self.baloon_position.x)), max(0, min(self.settings.get("notification_rows", 20) - 1, self.baloon_position.y)))

            self.spikes = [(x, y + 1) for x, y in self.spikes if y < self.settings.get("notification_rows", 20)]
            self.points = [(x, y + 1) for x, y in self.points if y < self.settings.get("notification_rows", 20)]

            if (self.baloon_position.x, self.baloon_position.y) in self.points:
                self.score += 1
                self.points.remove((self.baloon_position.x, self.baloon_position.y))
                self.difficulty = min(0.9, self.difficulty + 0.01)

            elif (self.baloon_position.x, self.baloon_position.y) in self.spikes:
                self.running = False
                self.info_label.text = f"Game Over! Score: {self.score}\nPress r to restart"

            if time.perf_counter() - self.last_spawn_time >= self.spawn_interval:
                self.last_spawn_time = time.perf_counter()
                self.spawn_items()
            
            text = ""
            for y in range(self.settings.get("notification_rows", 20)):
                for x in range(self.settings.get("notification_cols", 25)):
                    if arcade.math.Vec2(x, y) == self.baloon_position:
                        text += "O"
                    elif (x, y) in self.spikes:
                        text += "E"
                    elif (x, y) in self.points:
                        text += "o"
                    else:
                        text += "_"
                text += "\n"

            notification.notify(
                title=f"Hot Air Baloon | Score: {self.score} High Score: {self.high_score}",
                message=text
            )

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            if self.score > self.high_score:
                self.high_score = self.score
            self.data["hot_air_baloon"]["high_score"] = self.high_score
            with open("data.json", "w") as file:
                file.write(json.dumps(self.data, indent=4))
            from menus.main import Main
            self.window.show_view(Main(self.pypresence_client))
        elif symbol == arcade.key.R and not self.running:
            self.info_label.text = "Use arrow keys or WASD to move\nThe game is shown inside notifications."
            self.spikes.clear()
            self.points.clear()
            self.baloon_position = arcade.math.Vec2(0, self.settings.get("notification_rows", 20) - 1)
            self.baloon_direction = arcade.math.Vec2()
            self.score = 0
            self.running = True
            self.difficulty = 0.4
        elif symbol in (arcade.key.LEFT, arcade.key.A):
            self.baloon_direction = arcade.math.Vec2(-1, 0)
        elif symbol in (arcade.key.RIGHT, arcade.key.D):
            self.baloon_direction = arcade.math.Vec2(1, 0)
        elif symbol in (arcade.key.UP, arcade.key.W):
            self.baloon_direction = arcade.math.Vec2(0, -1)
        elif symbol in (arcade.key.DOWN, arcade.key.S):
            self.baloon_direction = arcade.math.Vec2(0, 1)
