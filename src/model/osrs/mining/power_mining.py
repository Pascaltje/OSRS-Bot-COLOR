import random
import time

import utilities.color as clr
import utilities.api.item_ids as ids
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from model.osrs.puntil.puntil import PUNTIL
import utilities.random_util as rd


class POSNRPowerMiner(OSRSBot):
    def __init__(self):
        title = "PPowerMiner"
        description = "This bot will mine the Green tagged ore and drops it on the spot."
        super().__init__(bot_title=title, description=description)
        self.running_time = 1
        self.enable_breaks = True

        self.api_m = MorgHTTPSocket()
        self.error_count = 0
        self.puntil = PUNTIL(self, self.api_m)

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_checkbox_option("break", "Disable Take breaks?", [" "])

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "break":
                self.enable_breaks = len(options[option]) == 1
            else:
                self.log_msg(f"Unknown option: {option}")
                print(
                    "Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg(f"Take Breaks: {self.enable_breaks}.")
        self.options_set = True

    def _setup(self):
        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()

        if not self.puntil.check_needed_items(ids.pickaxes):
            self.log_msg("Make sure an Axe is equipped or in inventory")
            self.stop()

    def main_loop(self):  # sourcery skip: low-code-quality
        # Main loop
        self._setup()
        start_time = time.time()
        end_time = self.running_time * 60
        time.sleep(1)
        while time.time() - start_time < end_time:
            self.log_msg(f"main Loop")

            if self.api_s.get_is_player_idle() and not self.api_m.get_is_inv_full():
                self._do_mining()
            elif self.api_m.get_is_inv_full():
                # drop items
                self.puntil.drop_items_by_id(ids.ores)
            else:
                if rd.random_chance(0.10):
                    self.take_break(30, 60, True)
                else:
                    self.take_break(1, 5, True)

    def _do_mining(self):
        self.log_msg("Mine some ore!")

        if self.api_m.get_is_player_idle() and not self.api_m.get_is_inv_full():
            # search for rock
            if self.puntil.click_tag(clr.GREEN, "Ore not found, needs to respawn??", 1):
                time.sleep(1)  # sleeping 1 second to make sure something is happing before checking agian.
            else:
                self.puntil.simple_error("Ore not found", 1)
                time.sleep(1)
