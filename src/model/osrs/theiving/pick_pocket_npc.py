import random
import time

import utilities.color as clr
import utilities.api.item_ids as ids
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from model.osrs.puntil.puntil import PUNTIL
import utilities.random_util as rd


class POSRSPICKPOCKET(OSRSBot):
    def __init__(self):
        title = "PSimple Pick pocket"
        description = "This bot will pickpocket the tagged NPC with CYAN"
        super().__init__(bot_title=title, description=description)
        self.running_time = 1

        self.api_m = MorgHTTPSocket()
        self.error_count = 0
        self.puntil = PUNTIL(self, self.api_m)

        self._set_coin_pouch()
        self.actionsDone = 0

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

    def _setup(self):
        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()

    def main_loop(self):
        # Main loop
        # self._setup()
        start_time = time.time()
        end_time = self.running_time * 60
        time.sleep(1)
        while time.time() - start_time < end_time:
            self.log_msg(f"main Loop")

            if self.api_m.get_is_player_idle() and self.actionsDone >= self.coinPouch:
                self._do_open_pouch()
            elif self.api_m.get_is_player_idle():
                self._do_pickpocket()
            else:
                if rd.random_chance(0.10):
                    self.take_break(30, 60, True)
                else:
                    time.sleep(0.5)

    def _do_pickpocket(self):
        if self.api_m.get_is_player_idle():
            # search for rock
            if self.puntil.click_tag(clr.CYAN, "NPC not found", 1):
                self.actionsDone += 1
                # time.sleep(1)  # sleeping 1 second to make sure something is happing before checking agian.
            else:
                self.puntil.simple_error("NPC not found", 1)
                time.sleep(1)

    def _do_open_pouch(self):
        index = self.api_m.get_inv_item_indices(ids.coin_pouches)
        self.mouse.move_to(self.win.inventory_slots[index].random_point())
        self.mouse.click()
        self.actionsDone = 0
        self._set_coin_pouch()

    def _set_coin_pouch(self):
        self.coinPouch = rd.fancy_normal_sample(1, 28)
