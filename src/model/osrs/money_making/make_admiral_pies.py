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


class POSRSMAKEADMIRALPIES(OSRSBot):
    def __init__(self):
        title = "Make raw admiral pies"
        description = "Take 14 pi shells and add every ingredient. Mark the bank Yellow, make sure every ingredient is on the same tab."
        super().__init__(bot_title=title, description=description)
        self.running_time = 1

        self.api_m = MorgHTTPSocket()
        self.api_s = StatusSocket()
        self.error_count = 0
        self.puntil = PUNTIL(self, self.api_m)
        self.pbank = PBANK(self, self.api_m)

        self.step = 1
        self.items_step_1 = [ids.PIE_SHELL, ids.SALMON]
        self.items_step_1_bank = ["Pie_shell_bank.png", "Salmon_bank.png"]
        self.items_step_2 = [ids.PART_ADMIRAL_PIE, ids.TUNA]
        self.items_step_2_bank = ["Tuna_bank.png"]
        self.items_step_3 = [ids.PART_ADMIRAL_PIE, ids.POTATO]
        self.items_step_3_bank = ["Potato_bank.png"]

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
                self.log_msg("Lets go step" + str(self.step))
                if self.step == 1:
                    self._open_bank()
                    self.pbank.bank_deposit_all()
                    self.pbank.bank_withdraw_items(self.items_step_1_bank)
                    self.pbank.close()
                    time.sleep(0.3)
                    self._do_craft(ids.PIE_SHELL, ids.SALMON)
                    self.step = 2
                elif self.step == 2:
                    self._open_bank()
                    self.pbank.bank_withdraw_items(self.items_step_2_bank)
                    self.pbank.close()
                    time.sleep(0.3)
                    self._do_craft(ids.PART_ADMIRAL_PIE, ids.TUNA)
                    self.step = 3
                elif self.step == 3:
                    self._open_bank()
                    self.pbank.bank_withdraw_items(self.items_step_3_bank)
                    self.pbank.close()
                    time.sleep(0.3)
                    self._do_craft(ids.PART_ADMIRAL_PIE_7194, ids.POTATO)
                    self.step = 1
                else:
                    self.log_msg("Error finding out witch step i am")
                    self.stop()

            else:
                self.take_break(5, 30)

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
            withdraw_items = ["Jug_of_water_bank.png", "Grapes_bank.png"]
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



