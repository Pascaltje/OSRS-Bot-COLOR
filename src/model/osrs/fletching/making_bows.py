import random
import time
import utilities.api.item_ids as ids
from model.osrs.osrs_bot import OSRSBot
from model.osrs.puntil.pbank import PBANK
from utilities.api.morg_http_client import MorgHTTPSocket
import utilities.color as clr
from model.osrs.puntil.puntil import PUNTIL
import pyautogui as pag
import utilities.random_util as rd


class POSRSMAKEBOWS(OSRSBot):
    def __init__(self):
        title = "Fletch bows"
        description = "Fletch bows, start with knife in inventory, and the logs visible on the bank tab."
        super().__init__(bot_title=title, description=description)
        self.running_time = 1

        self.api_m = MorgHTTPSocket()
        self.error_count = 0
        self.puntil = PUNTIL(self, self.api_m)
        self.pbank = PBANK(self, self.api_m)

        self.knife = ids.KNIFE
        self.logs = ids.MAPLE_LOGS
        self.logs_image = "Maple_logs_bank.png"
        self.action = "3"

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_dropdown_option("craft_item", "What should i make?", ["Yew Longbows", "Maple Longbows"])

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "craft_item":
                if options[option] == "Yew Longbows":
                    self.logs = ids.YEW_LOGS
                    self.logs_image = "Yew_logs_bank.png"
                    self.action = "3"
                elif options[option] == "Maple Longbows":
                    self.logs = ids.MAPLE_LOGS
                    self.logs_image = "Maple_logs_bank.png"
                    self.action = "3"
            else:
                self.log_msg(f"Unknown option: {option}")
                print(
                    "Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.options_set = True

    def _setup(self):
        # Add check to see if inventory is selected
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
                if self.puntil.check_needed_items([self.knife]) and self.puntil.check_needed_items([self.logs]):
                    self._do_craft()
                else:
                    self._do_bank()
            else:
                self.take_break(5, 30)

    def _do_craft(self):
        knife = self.api_m.get_inv_item_indices(self.knife)
        logs = self.api_m.get_inv_item_indices(self.logs)

        if len(knife) > 0 and len(logs) > 0:
            knifeIndex = knife[random.randint(0, len(knife) - 1)]
            logsIndex = logs[random.randint(0, len(logs) - 1)]
            spots = [
                self.win.inventory_slots[knifeIndex].random_point(),
                self.win.inventory_slots[logsIndex].random_point()
            ]

            self._click_spots_random_order(spots)

            time.sleep(rd.fancy_normal_sample(0.5, 2))
            pag.press(self.action)
            if rd.random_chance(.14):
                self.log_msg("Take long break")
                self.take_break(20, 90)
            else:
                self.take_break(10, 15)

    def _do_bank(self):
        if self.puntil.click_tag(clr.YELLOW, "Bank not found...", 5):
            time.sleep(0.3)
            self.puntil.wait_for_idle()
            self.pbank.bank_deposit_all_except(self.knife)
            self.pbank.bank_withdraw_items([self.logs_image])
            self.pbank.close()

    def _click_spots_random_order(self, spots):
        random.shuffle(spots)
        if rd.random_chance(.008):
            self.take_break()
        for spot in spots:
            self.mouse.move_to(spot)
            self.mouse.click()
            if rd.random_chance(.008):
                self.take_break()
            time.sleep(rd.fancy_normal_sample(0.1, 0.3))
