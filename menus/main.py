import arcade, arcade.gui, asyncio, pypresence, time, copy, json
from utils.preload import button_texture, button_hovered_texture
from utils.constants import big_button_style, discord_presence_id
from utils.utils import FakePyPresence

class Main(arcade.gui.UIView):
    def __init__(self, pypresence_client=None):
        super().__init__()

        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout())
        self.box = self.anchor.add(arcade.gui.UIBoxLayout(space_between=10), anchor_x='center', anchor_y='center')

        self.pypresence_client = pypresence_client

        with open("settings.json", "r") as file:
            self.settings_dict = json.load(file)

        if self.settings_dict.get('discord_rpc', True):
            if self.pypresence_client == None: # Game has started
                try:
                    asyncio.get_event_loop()
                except:
                    asyncio.set_event_loop(asyncio.new_event_loop())
                try:
                    self.pypresence_client = pypresence.Presence(discord_presence_id)
                    self.pypresence_client.connect()
                    self.pypresence_client.start_time = time.time()
                except:
                    self.pypresence_client = FakePyPresence()
                    self.pypresence_client.start_time = time.time()

            elif isinstance(self.pypresence_client, FakePyPresence): # the user has enabled RPC in the settings in this session.
                # get start time from old object
                start_time = copy.deepcopy(self.pypresence_client.start_time)
                try:
                    self.pypresence_client = pypresence.Presence(discord_presence_id)
                    self.pypresence_client.connect()
                    self.pypresence_client.start_time = start_time
                except:
                    self.pypresence_client = FakePyPresence()
                    self.pypresence_client.start_time = start_time

            self.pypresence_client.update(state='In Menu', details='In Main Menu', start=self.pypresence_client.start_time)
        else: # game has started, but the user has disabled RPC in the settings.
            self.pypresence_client = FakePyPresence()
            self.pypresence_client.start_time = time.time()

        self.pypresence_client.update(state='In Menu', details='In Main Menu', start=self.pypresence_client.start_time)

    def on_show_view(self):
        super().on_show_view()

        self.title_label = self.box.add(arcade.gui.UILabel(text="NotifPlayground", font_name="Roboto", font_size=48))

        self.snake_button = self.box.add(arcade.gui.UITextureButton(text="Snake", texture=button_texture, texture_hovered=button_hovered_texture, width=self.window.width / 2, height=self.window.height / 10, style=big_button_style))
        self.snake_button.on_click = lambda event: self.snake()

        self.flappy_bird_button = self.box.add(arcade.gui.UITextureButton(text="Flappy Bird", texture=button_texture, texture_hovered=button_hovered_texture, width=self.window.width / 2, height=self.window.height / 10, style=big_button_style))
        self.flappy_bird_button.on_click = lambda event: self.flappy_bird()

        self.pong_button = self.box.add(arcade.gui.UITextureButton(text="Pong", texture=button_texture, texture_hovered=button_hovered_texture, width=self.window.width / 2, height=self.window.height / 10, style=big_button_style))
        self.pong_button.on_click = lambda event: self.pong()

        self.space_invaders_button = self.box.add(arcade.gui.UITextureButton(text="Space Invaders", texture=button_texture, texture_hovered=button_hovered_texture, width=self.window.width / 2, height=self.window.height / 10, style=big_button_style))
        self.space_invaders_button.on_click = lambda event: self.space_invaders()

        self.wps_test_button = self.box.add(arcade.gui.UITextureButton(text="WPS Test", texture=button_texture, texture_hovered=button_hovered_texture, width=self.window.width / 2, height=self.window.height / 10, style=big_button_style))
        self.wps_test_button.on_click = lambda event: self.wps_test()

        self.maze_button = self.box.add(arcade.gui.UITextureButton(text="Maze", texture=button_texture, texture_hovered=button_hovered_texture, width=self.window.width / 2, height=self.window.height / 10, style=big_button_style))
        self.maze_button.on_click = lambda event: self.maze()

        self.settings_button = self.box.add(arcade.gui.UITextureButton(text="Settings", texture=button_texture, texture_hovered=button_hovered_texture, width=self.window.width / 2, height=self.window.height / 10, style=big_button_style))
        self.settings_button.on_click = lambda event: self.settings()

    def pong(self):
        from game.pong import Game
        self.window.show_view(Game(self.pypresence_client))

    def flappy_bird(self):
        from game.flappy_bird import Game
        self.window.show_view(Game(self.pypresence_client))

    def snake(self):
        from game.snake import Game
        self.window.show_view(Game(self.pypresence_client))

    def space_invaders(self):
        from game.space_invaders import Game
        self.window.show_view(Game(self.pypresence_client))
    
    def wps_test(self):
        from game.wps_test import Game
        self.window.show_view(Game(self.pypresence_client))

    def maze(self):
        from game.maze import Game
        self.window.show_view(Game(self.pypresence_client))

    def settings(self):
        from menus.settings import Settings
        self.window.show_view(Settings(self.pypresence_client))
