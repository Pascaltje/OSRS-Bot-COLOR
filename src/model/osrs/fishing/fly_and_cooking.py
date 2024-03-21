import time
from abc import ABC
from enum import Enum
import random

from model.osrs.osrs_bot import OSRSBot
import utilities.game_launcher as launcher
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
import utilities.color as clr
import utilities.imagesearch as imsearch
import utilities.random_util as rd
import pyautogui as pag


class OSRSFLYCooking(OSRSBot, launcher.Launchable):
    api_morg = MorgHTTPSocket()
    api_status = StatusSocket()
    state = -1
    needed_items = [309, 314]

    def __init__(self):
        bot_title = "Fly Fisher"
        description = (
            "This bot will fly fish, cook the fish, drop the fish repeat! Mark the Fire Yellow, fhising spots CYAN"
        )
        super().__init__(bot_title=bot_title, description=description)
        self.state = BotState.FISHING
        self.running_time: int = 30

    def _has_needed_items(self) -> bool:
        # 309 fishing rod
        # 314 feathers
        if not self._check_needed_inventory_items(self.needed_items):
            self.log_msg("Fishing rod or feathers a missing! Make sure they are in the inventory!")
            self.stop()
            return False
        return True

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

        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()

        self.state = BotState.FISHING
        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time and self._has_needed_items():

            if self.state == BotState.FISHING:
                self.log_msg("DoFishing")
                self.do_fishing()
            elif self.state == BotState.COOKING:
                self.log_msg("DoCooking")
                self.do_cooking()
            elif self.state == BotState.DROPPING:
                self.log_msg("Dropping")
                positions = self.api_morg.get_inv_item_indices(self.needed_items)
                self.drop_all(skip_slots=positions)
                self.state = BotState.FISHING
            time.sleep(0.1)
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def do_fishing(self):
        # search for fishing spots
        if self.api_status.get_is_inv_full():
            self.state = BotState.COOKING
        else:
            if self.api_morg.get_is_player_idle():
                self.log_msg("Search for fishing spot and click")
                spot = self.get_nearest_tag(clr.CYAN)
                if spot:
                    self.mouse.move_to(spot.random_point())
                    time.sleep(0.2)
                    if not self.mouseover_text(contains="Lure", color=clr.OFF_WHITE):
                        return
                    self.mouse.click()
                    time.sleep(2)
            else:
                self.take_break(0, 30, True)

    def do_cooking(self):
        fish_ids = [335, 331]
        # cook the fish
        # search the fire
        cooking_range = self.get_nearest_tag(clr.YELLOW)
        if cooking_range:
            # lets click a fish first and the fire pot to cook the fish
            positions = self.api_morg.get_inv_item_indices(fish_ids)
            if len(positions) > 0:
                self.mouse.move_to(self.win.inventory_slots[self.__get_fish_position(positions)].random_point())
                self.mouse.click()
                time.sleep(0.1)
                self.mouse.move_to(cooking_range.random_point())
                time.sleep(0.3)
                if not self.mouseover_text(contains="Fire"):
                    return
                self.mouse.click()
                time.sleep(3)
                self._wait_for_idle()
                pag.press("space")
                self._wait_for_idle(self.win.game_view.random_point())
            else:
                self.state = BotState.DROPPING

    def __get_fish_position(self, positions) -> int:
        # select random from first 8 aviable or less
        selectable = 20
        if len(positions) < selectable:
            selectable = len(positions) - 1
        return positions[random.randint(0, selectable)]

    def _check_needed_inventory_items(self, items_ids):
        for itemId in items_ids:
            if not self.api_morg.get_if_item_in_inv(itemId):
                return False
        return True

    def _wait_for_idle(self, location_next_action=None):
        moved = False
        while not self.api_morg.get_is_player_idle(poll_seconds=0.9):
            time.sleep(0.2)
            if location_next_action is not None and not moved:
                self.mouse.move_to(location_next_action)
                moved = True

    def __logout(self, msg):
        self.log_msg(msg)
        if rd.random_chance(.3):
            self.logout()
        self.stop()


class BotState(Enum):
    FISHING = 1
    COOKING = 2
    DROPPING = 3
