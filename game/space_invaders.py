import arcade, arcade.gui, time, random, os, json

from plyer import notification

class Game(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()

        self.pypresence_client = pypresence_client
        self.pypresence_client.update(state="Playing Space Invaders inside notifications!")

        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))
        self.info_label = self.anchor.add(arcade.gui.UILabel("Use arrow keys or WASD to move\nYou can see the game inside notifications!", font_size=24, multiline=True))

        self.running = True
        self.last_update_time = time.perf_counter()

        with open("settings.json", "r") as file:
            self.settings = json.load(file)

        if not os.path.exists("data.json"):
            self.data = {}
        else:
            with open("data.json", "r") as file:
                self.data = json.load(file)

        if not "space_invaders" in self.data:
            self.data["space_invaders"] = {"high_score": 0}

        self.high_score = self.data["space_invaders"]["high_score"]
        self.score = 0

        self.ship_position = arcade.math.Vec2(0, int(self.settings.get("notification_rows", 20) / 2) - 1)
        
        self.ship_direction = arcade.math.Vec2(0, 0)
        
        self.enemies = []
        self.enemy_bullets = []
        self.your_bullets = []

        self.last_enemy_shoot = time.perf_counter()

    def summon_enemies(self):
        self.enemies = [[x, y] for x in range(int(self.settings.get("notification_cols", 25))) for y in range(int(int(self.settings.get("notification_rows", 20) / 2) / 5))]

    def update_enemies(self):
        columns = list(range(self.settings.get("notification_cols", 25)))
        random.shuffle(columns)

        for x in columns:
            max_y = -99999
            for y in range(int(int(self.settings.get("notification_rows", 20) / 2) / 3)):
                if not [x, y] in self.enemies:
                    continue
                
                if y > max_y:
                    max_y = y

            if time.perf_counter() - self.last_enemy_shoot >= 1:
                self.last_enemy_shoot = time.perf_counter()
                self.enemy_bullets.append([x, max_y])

    def on_show_view(self):
        super().on_show_view()

        self.summon_enemies()

    def on_update(self, delta_time):
        if self.running and time.perf_counter() - self.last_update_time >= self.settings.get("notification_timeout", 0.4):
            self.last_update_time = time.perf_counter()

            self.ship_position += self.ship_direction

            if self.ship_position.x < 0:
                self.ship_position = arcade.math.Vec2(0, self.ship_position.y)
            elif self.ship_position.x > self.settings.get("notification_cols", 25):
                self.ship_position = arcade.math.Vec2(self.settings.get("notification_cols", 25), self.ship_position.y)

            self.ship_direction = arcade.math.Vec2(0, 0)

            self.update_enemies()

            new_enemy = [(x, y + 1) for (x, y) in self.enemy_bullets]
            new_yours = [(x, y - 1) for (x, y) in self.your_bullets]

            if tuple(self.ship_position) in new_enemy:
                self.info_label.text = "Game Over.\nPress r to restart"
                self.running = False

                notification.notify(
                    title="Space Invaders inside notifications",
                    message='Game Over!'
                )

                return

            bullets_to_remove = set()
            for b in new_yours:
                if [b[0], b[1]] in self.enemies:
                    self.enemies.remove([b[0], b[1]])
                    bullets_to_remove.add(b)
                elif b in new_enemy:
                    bullets_to_remove.add(b)
                elif b[1] <= 0:
                    bullets_to_remove.add(b)

            for b in new_enemy:
                if b[1] > int(self.settings.get("notification_rows", 20) / 2):
                    bullets_to_remove.add(b)

            self.your_bullets = [b for b in new_yours if b not in bullets_to_remove]
            self.enemy_bullets = [b for b in new_enemy if b not in bullets_to_remove]

            text = ""

            for y in range(int(self.settings.get("notification_rows", 20) / 2)):
                for x in range(self.settings.get("notification_cols", 25)):
                    if [x, y] in self.enemies:
                        text += "~"
                    elif (x, y) in self.enemy_bullets or (x, y) in self.your_bullets:
                        text += "|"
                    elif arcade.math.Vec2(x, y) == self.ship_position:
                        text += "^"
                    else:
                        text += "_"

                text += "\n"

            if self.score > self.high_score:
                self.high_score = self.score

            notification.notify(
                title=f"Space Invaders | Score: {self.score} High Score: {self.high_score}",
                message=text
            )

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.data["space_invaders"]["high_score"] = self.high_score
            with open("data.json", "w") as file:
                file.write(json.dumps(self.data, indent=4))

            from menus.main import Main
            self.window.show_view(Main(self.pypresence_client))
        elif symbol == arcade.key.SPACE:
            self.last_you_shoot = time.perf_counter()
            self.your_bullets.append([self.ship_position.x, self.ship_position.y - 1])
        elif symbol == arcade.key.R:
            self.score = 0

            self.ship_position = arcade.math.Vec2(0, int(self.settings.get("notification_rows", 20) / 2) - 1)
            self.ship_direction = arcade.math.Vec2(0, 0)

            self.enemies = []
            self.enemy_bullets = []
            self.your_bullets = []

            self.last_enemy_shoot = time.perf_counter()
            self.last_you_shoot = time.perf_counter()

            self.summon_enemies()

            self.running = True
        elif symbol == arcade.key.LEFT or symbol == arcade.key.A:
            self.ship_direction = arcade.math.Vec2(-1, 0)
        elif symbol == arcade.key.RIGHT or symbol == arcade.key.D:
            self.ship_direction = arcade.math.Vec2(1, 0)