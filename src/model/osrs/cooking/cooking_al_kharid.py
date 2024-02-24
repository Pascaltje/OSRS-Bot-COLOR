import random
import time

import utilities.color as clr
import utilities.api.item_ids as ids
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from model.osrs.puntil.puntil import PUNTIL
from model.osrs.puntil.pbank import PBANK
import utilities.imagesearch as imsearch
import pyautogui as pag
import utilities.random_util as rd


class POSRSCOOKINGALKHARID(OSRSBot):
    def __init__(self):
        title = "Cooking at Al Kharid"
        description = "Takes the raw food from the bank, cooks it at the range. Tag bank Yellow, Range BLUE and the closed door Red"
        super().__init__(bot_title=title, description=description)
        self.running_time = 1
        self.enable_breaks = True

        self.api_m = MorgHTTPSocket()
        self.api_s = StatusSocket()
        self.error_count = 0
        self.craft_option = 1
        self.puntil = PUNTIL(self, self.api_m)
        self.pbank = PBANK(self, self.api_m)
        self.needables = [ids.BREAD_DOUGH]

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_dropdown_option("craft_item", "What should take to cook?",
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
            if self.api_m.get_is_player_idle():
                self.log_msg(f"main Loop + idle")
                if self.puntil.check_needed_items(self.needables):
                    self._do_cook()
                else:
                    self._do_bank()

    def _do_cook(self):
        self._open_door()

        if self.puntil.click_tag(clr.BLUE, "Range not found? :( "):
            self.puntil.wait_for_idle()
            time.sleep(0.3)
            pag.press("space")
            self._wait_for_cooking_done()

    def _wait_for_cooking_done(self):
        self.take_break()
        if not self.api_m.get_is_player_idle():
            self._wait_for_cooking_done()

    def _open_door(self):
        if self.puntil.is_tag_visible(clr.RED):
            if self.puntil.click_tag(clr.RED, "Door not found? :/", 1):
                self.puntil.wait_for_idle()

    def _do_bank(self):
        self._open_door()
        if self.puntil.click_tag(clr.YELLOW, "Bank not found...", 5):
            self.puntil.wait_for_idle()
            if not self.api_s.get_is_inv_empty():
                self.pbank.bank_deposit_all()
            withdraw_items = ["Bread_dough_bank.png"]
            if rd.random_chance(.45):
                withdraw_items.reverse()
            self.pbank.bank_withdraw_items(withdraw_items)
            time.sleep(.5)
            if rd.random_chance(.30):
                pag.press("esc")
