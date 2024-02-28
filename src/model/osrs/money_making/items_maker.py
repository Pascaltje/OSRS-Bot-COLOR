import random
import time

import utilities.color as clr
import utilities.api.item_ids as ids
from model.osrs.osrs_bot import OSRSBot
from model.osrs.puntil.pbank import PBANK
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from model.osrs.puntil.puntil import PUNTIL
import utilities.imagesearch as imsearch
import pyautogui as pag
import utilities.random_util as rd


class POSRSITEMSMAKE(OSRSBot):
    def __init__(self):
        title = "Make items"
        description = "Select item in option to make, set bank x to 14 and tag bank yellow. Make sure right bank tab is opend."
        super().__init__(bot_title=title, description=description)
        self.running_time = 1

        self.api_m = MorgHTTPSocket()
        self.api_s = StatusSocket()
        self.error_count = 0
        self.puntil = PUNTIL(self, self.api_m)
        self.pbank = PBANK(self, self.api_m)

        # selected recipe
        self.needed_items_ids = [ids.VIAL_OF_WATER, ids.TARROMIN]
        self.item1_bank_image = "Vial_of_water.png"
        self.item2_bank_image = "Tarromin_bank.png"

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

    def main_loop(self):  # sourcery skip: low-code-quality
        # Main loop
        # self._setup()
        start_time = time.time()
        end_time = self.running_time * 60
        time.sleep(1)
        while time.time() - start_time < end_time:
            if self.api_m.get_is_player_idle():
                if self.puntil.check_needed_items(self.needed_items_ids):
                    self._do_craft(self.needed_items_ids[0], self.needed_items_ids[1])
                else:
                    # get items from bank
                    self._do_bank()
            else:
                self.take_break(2, 30)

    def _do_craft(self, shell_id, ingredient_id):
        shell = self.api_m.get_inv_item_indices(shell_id)
        ingredient = self.api_m.get_inv_item_indices(ingredient_id)

        if len(shell) > 0 and len(ingredient) > 0:
            shell_index = shell[random.randint(0, len(shell) - 1)]
            ingredient_Index = ingredient[random.randint(0, len(ingredient) - 1)]

            self.puntil.click_pos(self.win.inventory_slots[shell_index].random_point())
            self.puntil.click_pos(self.win.inventory_slots[ingredient_Index].random_point())

            time.sleep(rd.fancy_normal_sample(0.5, 2))
            pag.press("space")
            if rd.random_chance(.14):
                self.log_msg("Take long break")
                self.take_break(20, 90)
            else:
                self.take_break(15, 25)
        else:
            self.log_msg("Stopping, missing ingredients")
            self.stop()

    def _open_bank(self):
        if self.puntil.click_tag(clr.YELLOW, "Bank not found...", 5):
            self.puntil.wait_for_idle()
            return True
        else:
            return False

    def _do_bank(self):
        if self.puntil.click_tag(clr.YELLOW, "Bank not found...", 5):
            self.puntil.wait_for_idle()
            if not self.api_s.get_is_inv_empty():
                self.pbank.bank_deposit_all()
            withdraw_items = [self.item1_bank_image, self.item2_bank_image]
            if rd.random_chance(.45):
                withdraw_items.reverse()
            self.pbank.bank_withdraw_items(withdraw_items)
            time.sleep(.5)
            pag.press("esc")

    def _click_spots_random_order(self, spots):
        if rd.random_chance(.008):
            self.take_break()
        for spot in spots:
            self.mouse.move_to(spot)
            self.mouse.click()
            if rd.random_chance(.008):
                self.take_break()
            time.sleep(rd.fancy_normal_sample(0.1, 0.3))



