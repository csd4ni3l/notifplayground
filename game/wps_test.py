import arcade, arcade.gui, time, random, os, json

from plyer import notification

from utils.constants import ROWS, COLS
from utils.preload import words

class Game(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()

        self.pypresence_client = pypresence_client
        self.pypresence_client.update(state="Doing a WPS Test inside notifications!")

        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))
        self.info_label = self.anchor.add(arcade.gui.UILabel("Press keys inside this window to interact with the app\nYou can see the app inside notifications!", font_size=24, multiline=True))

        self.running = True

        if not os.path.exists("data.json"):
            self.data = {}
        else:
            with open("data.json", "r") as file:
                self.data = json.load(file)

        if not "wps_test" in self.data:
            self.data["wps_test"] = {"highest_wpm": 0}

        self.highest_wpm = self.data["wps_test"]["highest_wpm"]
        
        self.words = [random.choice(words) for _ in range(500)]
        self.time_start = time.perf_counter()
        self.last_manual_notification_update = time.perf_counter()

        self.current_typing = ""
        self.wpm = 0
        self.accuracy = 100
        self.current_index = 0

        self.words_done = 0

        self.total_chars = 0
        self.valid_chars = 0

        self.text = " ".join(self.words[0:15])

        self.trigger_notification()

    def on_update(self, delta_time):
        if self.running and time.perf_counter() - self.time_start >= 60:
            self.running = False
            self.wpm = self.words_done

            if self.wpm > self.highest_wpm:
                self.highest_wpm = self.wpm

            self.trigger_notification()
            self.info_label.text = f"WPS Test Over.\nWPM: {self.wpm}\nAccuracy: {self.accuracy}%\nHigh Score: {self.highest_wpm}\nPress r to restart."
        
        if self.running and time.perf_counter() - self.last_manual_notification_update >= 1:
            self.last_manual_notification_update = time.perf_counter()
            self.trigger_notification()

    def trigger_notification(self):
        if self.running:
            notification.notify(
                title=f"Accuracy: {self.accuracy}% | Time left: {60 - int(time.perf_counter() - self.time_start)}",
                message=self.text
            )
        else:
            notification.notify(
                title="WPS Test done!",
                message=f"WPM: {self.wpm}\nAccuracy: {self.accuracy}%\nHigh Score: {self.highest_wpm}"
            )

    def update_words(self):
        self.trigger_notification()

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.data["wps_test"]["highest_wpm"] = self.highest_wpm
            with open("data.json", "w") as file:
                file.write(json.dumps(self.data, indent=4))
            
            from menus.main import Main
            self.window.show_view(Main(self.pypresence_client))
        elif self.running and 97 <= symbol <= 122:
            self.total_chars += 1

            if chr(symbol) == self.words[0][self.current_index]:
                self.current_typing += chr(symbol)
                self.current_index += 1
                self.valid_chars += 1
                self.text = self.text[1:]
                self.update_words()

            self.accuracy = int((self.valid_chars / self.total_chars) * 100)
        elif self.running and symbol == 32 and self.current_typing == self.words[0]:
            self.words = self.words[1:]
            self.current_typing = ""
            self.words_done += 1
            self.text = " ".join(self.words[0:15])
            self.current_index = 0

            self.update_words()
        elif not self.running and symbol == arcade.key.R:
            self.words = [random.choice(words) for _ in range(500)]
            self.time_start = time.perf_counter()

            self.current_typing = ""
            self.wpm = 0
            self.accuracy = 100
            self.current_index = 0

            self.words_done = 0

            self.total_chars = 0
            self.valid_chars = 0

            self.text = " ".join(self.words[0:15])

            self.trigger_notification()

            self.running = True