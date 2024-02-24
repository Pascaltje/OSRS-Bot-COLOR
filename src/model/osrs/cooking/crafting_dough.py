import random
import time

import utilities.color as clr
import utilities.api.item_ids as ids
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from model.osrs.puntil.puntil import PUNTIL
import utilities.imagesearch as imsearch
import pyautogui as pag
import utilities.random_util as rd


class POSRSCRAFTINGDOUGH(OSRSBot):
    def __init__(self):
        title = "Crafting Dough"
        description = "Take 9 pot's of flour with 9 buckets of water to create dough. Tag bank with yellow."
        super().__init__(bot_title=title, description=description)
        self.running_time = 1
        self.enable_breaks = True

        self.api_m = MorgHTTPSocket()
        self.api_s = StatusSocket()
        self.error_count = 0
        self.craft_option = 1
        self.puntil = PUNTIL(self, self.api_m)
        self.needables = [ids.BUCKET_OF_WATER, ids.POT_OF_FLOUR]

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_dropdown_option("craft_item", "What should i make?",
                                                 ["Bread dough", "Pastry dough", "Option 3"])
        self.options_builder.add_checkbox_option("break", "Disable Take breaks?", [" "])

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "break":
                self.enable_breaks = len(options[option]) == 1
            elif option == "craft_item":
                self.craft_option = options[option]
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

    def main_loop(self):  # sourcery skip: low-code-quality
        # Main loop
        self._setup()
        start_time = time.time()
        end_time = self.running_time * 60
        time.sleep(1)
        while time.time() - start_time < end_time:
            self.log_msg(f"main Loop")
            if self.api_m.get_is_player_idle():
                if self.puntil.check_needed_items(self.needables):
                    self._do_craft()
                else:
                    self._do_bank()

    def _do_craft(self):
        buckets = self.api_m.get_inv_item_indices(ids.BUCKET_OF_WATER)
        pots = self.api_m.get_inv_item_indices(ids.POT_OF_FLOUR)

        if len(buckets) > 0 and len(pots) > 0:
            index = buckets[random.randint(0, len(buckets) - 1)]
            self.mouse.move_to(self.win.inventory_slots[index].random_point())
            self.mouse.click()
            time.sleep(0.2)
            index = pots[random.randint(0, len(pots) - 1)]
            self.mouse.move_to(self.win.inventory_slots[index].random_point())
            self.mouse.click()
            time.sleep(rd.fancy_normal_sample(1.5, 5))
            pag.press("1")
            if rd.random_chance(.14):
                self.log_msg("Take long break")
                self.take_break(20, 90)
            else:
                self.take_break(10, 15)

    def _do_bank(self):
        if self.puntil.click_tag(clr.YELLOW, "Bank not found...", 5):
            self.puntil.wait_for_idle()
            if not self.api_s.get_is_inv_empty():
                self.__bank_deposit_all()
            withdraw_items = ["Pot_of_flour_bank.png", "Bucket_of_water_bank.png"]
            if rd.random_chance(.45):
                withdraw_items.reverse()
            self.__bank_withdraw_items(withdraw_items)
            time.sleep(.5)
            pag.press("esc")

    def __bank_withdraw_items(self, items):
        for item in items:
            self.log_msg("Try to withdraw " + item)
            deposit_img = imsearch.BOT_IMAGES.joinpath("items", item)
            if deposit_img := imsearch.search_img_in_rect(deposit_img, self.win.game_view):
                self.mouse.move_to(deposit_img.random_point())
                time.sleep(0.1)
                self.mouse.click()
                time.sleep(0.1)
            else:
                self.log_msg("Could not found item " + item)
                self.stop()

    def __bank_deposit_all(self) -> bool:
        deposit_img = imsearch.BOT_IMAGES.joinpath("bank", "deposit_inventory.png")
        if deposit_img := imsearch.search_img_in_rect(deposit_img, self.win.game_view):
            self.mouse.move_to(deposit_img.random_point())
            self.mouse.click()
            return True
        else:
            self.log_msg("Could not deposit items")
            self.errorCount = self.errorCount + 1
            return False
