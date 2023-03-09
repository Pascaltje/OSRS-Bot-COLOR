import time
from abc import ABC
from enum import Enum

from model.osrs.osrs_bot import OSRSBot
import utilities.game_launcher as launcher
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
import utilities.color as clr
import utilities.imagesearch as imsearch
import utilities.random_util as rd


class OSRSNetFishing(OSRSBot, launcher.Launchable):
    api_morg = MorgHTTPSocket()
    api_status = StatusSocket()
    state = -1

    def __init__(self):
        bot_title = "Net Fisher"
        description = (
            "This bot fish shrimps and cooks them at the range in Al Kharid"
        )
        super().__init__(bot_title=bot_title, description=description)
        self.running_time: int = 1
        self.state = BotState.BANKING

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            else:
                self.log_msg(f"Unknown option: {option}")
                print(
                    "Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return

        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.options_set = True

    def main_loop(self):

        # self.log_msg("Selecting inventory...")
        # self.mouse.move_to(self.win.cp_tabs[3].random_point())
        # self.mouse.click()

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:

            if self.state == BotState.BANKING:
                self.do_banking()
            elif self.state == BotState.FISHING:
                self.do_fishing()
            elif self.state == BotState.COOKING:
                self.do_cooking()
            time.sleep(0.1)

            # fishing
            # Just fishing the marked spots
            # just do an random delay when idle

            # walk to green spot

            # cooking at the range
            # press the fish or spacebare randomly switching

            # bank it
            # just press the deposit all button
            # instead of pressing the close button try to walk to the geen erea (i hope the bot can do this)

            # walk to green spot

            # repeat

    def do_fishing(self):
        # search for fishing spots
        # when not found walk to green area.
        if self.api_status.get_is_inv_full():
            self.state = BotState.BANKING
        else:
            if self.api_status.get_animation_id() == -1:
                spot = self.get_nearest_tag(clr.CYAN)
                if spot:
                    self.mouse.move_to(spot.random_point())
                    self.mouse.click()
                    time.sleep(2)
                else:
                    self.walk_to_green_spot()

    def walk_to_green_spot(self):
        # toto implement
        tiles = self.get_all_tagged_in_rect(self.win.game_view, clr.GREEN)
        if len(tiles) > 0:
            index = int(rd.fancy_normal_sample(0, len(tiles)))
            self.mouse.move_to(tiles[index].random_point())
            self.mouse.click()
            time.sleep(1)

    def do_cooking(self):
        # cook the fish
        cooking_range = self.get_nearest_tag(clr.YELLOW)
        if cooking_range:
            self.mouse.move_to(cooking_range.random_point())
            self.mouse.click()

    def do_banking(self):
        if self.api_morg.get_is_inv_full():
            # do banking
            if self.__bank_is_open():
                self.__bank_deposit_all()
                self.state = BotState.FISHING
            else:
                self.__bank_open()
        else:
            self.state = BotState.FISHING

    def __bank_open(self) -> bool:
        bank_stand = self.get_nearest_tag(clr.PINK)
        if bank_stand:
            self.mouse.move_to(bank_stand.random_point())

            if self.mouse.click(check_red_click=True):
                while not self.__bank_is_open():
                    time.sleep(0.05)
                return self.__bank_is_open()
            else:
                time.sleep(0.05)
                self.__bank_is_open()

        else:
            self.log_msg("Bank stand not found")
            self.stop()

    def __bank_is_open(self) -> bool:
        # search for the deposit open to check if the bank is open
        deposit_img = imsearch.BOT_IMAGES.joinpath("bank", "deposit_inventory.png")
        if deposit_img := imsearch.search_img_in_rect(deposit_img, self.win.game_view):
            return True
        else:
            return False

    def __bank_deposit_all(self):
        deposit_img = imsearch.BOT_IMAGES.joinpath("bank", "deposit_inventory.png")
        if deposit_img := imsearch.search_img_in_rect(deposit_img, self.win.game_view):
            self.mouse.move_to(deposit_img.random_point())
            self.mouse.click()
        else:
            self.log_msg("Could not deposit items")
            self.stop()


class BotState(Enum):
    FISHING = 1
    COOKING = 2
    BANKING = 3
