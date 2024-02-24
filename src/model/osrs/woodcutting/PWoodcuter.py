import random
import time

import utilities.color as clr
import utilities.api.item_ids as ids
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
import pyautogui as pag


class POSNRWoodcutting(OSRSBot):
    def __init__(self):
        title = "PWoodcutter"
        description = "This bot will chop the trees and bank or drop the logs. Mark the trees with Green and bank " \
                      "with Yellow"
        super().__init__(bot_title=title, description=description)
        self.running_time = 1
        self.enable_breaks = True
        self.banking = True
        self.api_m = MorgHTTPSocket()
        self.api_s = StatusSocket()
        self.error_count = 0
        self.axe = [ids.BRONZE_AXE, ids.IRON_AXE, ids.STEEL_AXE, ids.BLACK_AXE, ids.MITHRIL_AXE, ids.ADAMANT_AXE,
                    ids.RUNE_AXE, ids.GILDED_AXE, ids.DRAGON_AXE, ids.INFERNAL_AXE]

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_dropdown_option("Type", "Powercutting or banking?", ["Banking", "PowerCutting"])
        self.options_builder.add_checkbox_option("break", "Disable Take breaks?", [" "])

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "Type":
                self.enable_breaks = options[option] == "Banking"
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
        if self.banking:
            self.log_msg(f"Type: Banking.")
        else:
            self.log_msg(f"Type: Powercutting.")
        self.options_set = True

    def _setup(self):
        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()

        if not self._check_needed_items():
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
                # if self._pickup_loot():  # returns true when picked up an item, lets go back to the main loop
                #     return
                # else:
                self._do_chopping()
            elif self.api_m.get_is_inv_full():
                self._banking()
            else:
                self.take_break(1, 30, True)

    def _check_needed_items(self):
        if self.api_m.get_if_item_in_inv(self.axe):
            return True

        if self.api_m.get_is_item_equipped(self.axe):
            return True
        return False

    def _do_chopping(self):
        self.log_msg("Chop some trees!")

        if self.api_m.get_is_player_idle() and not self.api_m.get_is_inv_full():
            # search for a tree
            if self._click_tag(clr.GREEN, "Tree not found, needs to respawn??", 1):
                time.sleep(1)  # sleeping 1 second to make sure something is happing before checking agian.
            # else:
                #  tree not found
                #  is bank open?
                #   Close bank (esc)



    def _pickup_loot(self) -> bool:
        self.log_msg("Pickup loot on the ground")
        return False

    def _banking(self):
        self.log_msg("Try to click bank")
        if self._click_tag(clr.YELLOW, "Bank not found?", 2):
            self._wait_for_idle()
            banked_ids = []
            items = self.api_s.get_inv()
            random.shuffle(items)
            for item in items:
                if item["id"] not in self.axe and item["id"] not in banked_ids:
                    self.log_msg(f"Bank itemId: {item['id']} slot: {item['index']}")
                    banked_ids.append(item["id"])
                    self._click_inv_slot(item["index"])
            time.sleep(.3)
            # self.log_msg("Close bank")
            # pag.press("esc")

    def _click_inv_slot(self, slot: int, text="All"):
        self.mouse.move_to(self.win.inventory_slots[slot].random_point())
        self.log_msg(f"MouseOver: {self.mouseover_text()}")
        if self.mouseover_text(contains=[text]):
            self.mouse.click()
            time.sleep(0.1)
        else:
            self.log_msg("Set deposit to All!")

    def _click_tag(self, color: clr.Color, error_msg: str, weight=1) -> bool:
        obj = self.get_nearest_tag(color)
        if obj:
            self._reset_simple_error()
            self.mouse.move_to(obj.random_point())
            self.mouse.click()
            time.sleep(1)  # sleeping 1 second to make sure something is happing before checking agian.
            return True
        else:
            self._simple_error(error_msg, weight)
            return False

    def _simple_error(self, msg: str, weight=1):
        self.error_count = self.error_count + weight
        self.log_msg(f"{msg} ({self.error_count})")
        if self.error_count > 30:
            self.log_msg("Stopping bot error count to high")
            self.stop()

    def _reset_simple_error(self):
        self.error_count = 0

    def _wait_for_idle(self, location_next_action=None):
        moved = False
        while not self.api_m.get_is_player_idle(poll_seconds=0.9):
            time.sleep(0.2)
            if location_next_action is not None and not moved:
                self.mouse.move_to(location_next_action)
                moved = True

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()
