import arcade, arcade.gui, time, random, os, json

from plyer import notification

from utils.constants import ROWS, COLS

class Game(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()
        
        self.pypresence_client = pypresence_client
        self.pypresence_client.update(state="Playing Flappy Bird inside notifications!")

        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))
        self.info_label = self.anchor.add(arcade.gui.UILabel("Use space to jump\nYou can see the game inside notifications.", font_size=24, multiline=True), anchor_x="center", anchor_y="center")

        self.running = True
        self.should_jump = False
        self.last_update_time = time.perf_counter()

        self.pipes = []
        self.bird_position = [0, int(ROWS / 2)]
        self.cycles = 0

        if not os.path.exists("data.json"):
            self.data = {}
        else:
            with open("data.json", "r") as file:
                self.data = json.load(file)

        if not "flappy_bird" in self.data:
            self.data["flappy_bird"] = {"high_score": 0}

        self.high_score = self.data["flappy_bird"]["high_score"]
        self.score = 0

    def create_pipe_part(self, size, pipe_type):
        if pipe_type == "bottom":
            bottom = 0
        else:
            bottom = ROWS - size
        
        left = COLS

        for pipe_y in range(bottom, bottom + size):
            self.pipes.append([left, pipe_y])

    def create_pipe(self):
        gap_size = ROWS // 5
        gap_start = random.randint(1, ROWS - gap_size - 1) 

        bottom_height = gap_start
        self.create_pipe_part(bottom_height, "bottom")

        top_height = ROWS - (gap_start + gap_size)
        self.create_pipe_part(top_height, "top")

    def on_update(self, delta_time):
        if self.running and time.perf_counter() - self.last_update_time >= 0.4:
            self.pipes = [[pipe_x - 1, pipe_y] for pipe_x, pipe_y in self.pipes if pipe_x - 1 >= 0]
            
            if self.should_jump:
                jumped = True
                self.bird_position[1] -= 3
                self.should_jump = False
            else:
                jumped = False
                self.bird_position[1] += 2

            if self.bird_position in self.pipes or self.bird_position[1] >= ROWS or self.bird_position[1] <= 0:
                self.info_label.text = "Game Over.\nPress r to restart"
                self.running = False

                notification.notify(
                    title="Flappy Bird inside notifications",
                    message='Game Over!'
                )

                return
            
            for pipe in self.pipes:
                if pipe[0] == self.bird_position[0]:
                    self.score += 1
                    break

            self.last_update_time = time.perf_counter()

            text = ""

            for y in range(ROWS):
                for x in range(COLS):
                    if [x, y] in self.pipes:
                        text += "|"
                    elif [x, y] == self.bird_position:
                        text += "^" if jumped else "^"
                    else:
                        text += "_"

                text += "\n"

            if self.score > self.high_score:
                self.high_score = self.score

            notification.notify(
                title=f"Flappy Bird | Score: {self.score} High Score: {self.high_score}",
                message=text
            )
            
            if self.cycles == 15:
                self.cycles = 0
                self.create_pipe()

            self.cycles += 1

    def on_show_view(self):
        super().on_show_view()
        
        self.create_pipe()

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.data["flappy_bird"]["high_score"] = self.high_score
            with open("data.json", "w") as file:
                file.write(json.dumps(self.data, indent=4))

            from menus.main import Main
            self.window.show_view(Main(self.pypresence_client))
        elif symbol == arcade.key.SPACE:
            self.should_jump = True
        elif symbol == arcade.key.R and not self.running:
            self.info_label.text = "Press keys inside this window to interact with the game\nYou can see the game inside notifications"
            
            self.pipes.clear()
            self.create_pipe()

            self.last_update_time = time.perf_counter()

            self.bird_position = [0, int(ROWS / 2)]
            self.cycles = 0
            self.should_jump = False

            self.running = True