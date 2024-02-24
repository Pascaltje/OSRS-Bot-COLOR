import random
import time

import utilities.color as clr
import utilities.api.item_ids as ids
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from model.osrs.puntil.puntil import PUNTIL
import utilities.random_util as rd
import pyautogui as pag


class POSRSCamodaFishOffering(OSRSBot):
    def __init__(self):
        title = "Camoda Fish Offering"
        description = "This bot will fish, prepare and then offer the fish/nMark the fishing spot Cyan, prepare yellow and alter Red"
        super().__init__(bot_title=title, description=description)
        self.running_time = 1
        self.enable_breaks = True

        self.api_m = MorgHTTPSocket()
        self.api_s = StatusSocket()
        self.error_count = 0
        self.puntil = PUNTIL(self, self.api_m)
        self.needables = [ids.SMALL_FISHING_NET, ids.KNIFE]
        self.raw_fish = [25658, 25664, 25652]
        self.cooked_fish = [25660, 25666, ]
        self.drop_items = [25668]

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

        if not self.puntil.check_needed_items(self.needables):
            self.log_msg("Make sure a small fishing net and a knife is equipped or in inventory")
            self.stop()

    def main_loop(self):  # sourcery skip: low-code-quality
        # Main loop
        self._setup()
        start_time = time.time()
        end_time = self.running_time * 60
        time.sleep(1)
        while time.time() - start_time < end_time:
            self.log_msg(f"main Loop")

            if self.api_s.get_is_player_idle() and self.api_m.get_if_item_in_inv(self.cooked_fish):
                self._do_offer()
            elif self.api_m.get_is_inv_full():
                # drop items
                self._do_prepare()
            else:
                self._do_offer()

    def _do_fishing(self):
        self.log_msg("fishing")

        if self.api_m.get_is_player_idle() and not self.api_m.get_is_inv_full():
            # search for rock
            if self.puntil.click_tag(clr.CYAN, "Ore not found, needs to respawn??", 1):
                time.sleep(1)  # sleeping 1 second to make sure something is happing before checking agian.
            else:
                time.sleep(1)

    def _do_prepare(self):
        self.log_msg("Prepare food")

        if self.api_m.get_is_player_idle() and self.puntil.check_needed_items(self.raw_fish):
            # search for rock
            if self.puntil.click_tag(clr.YELLOW, "Prepare table not found??", 3):
                time.sleep(1)  # sleeping 1 second to make sure something is happing before checking agian.
                self.puntil.wait_for_idle()
                pag.press("space")
            else:
                time.sleep(1)

    def _do_offer(self):
        self.log_msg("Offer food")

        if self.api_m.get_is_player_idle() and self.puntil.check_needed_items(self.cooked_fish):
            # search for rock
            if self.puntil.click_tag(clr.RED, "Prepare table not found??", 3):
                time.sleep(1)  # sleeping 1 second to make sure something is happing before checking agian.
                self.puntil.wait_for_idle()
                pag.press("space")
            else:
                time.sleep(1)
