import random
import time
import utilities.api.item_ids as ids
from model.osrs.osrs_bot import OSRSBot
from model.osrs.puntil.pbank import PBANK
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from model.osrs.puntil.puntil import PUNTIL
import pyautogui as pag
import utilities.random_util as rd


class POSRSHEADLESSARROW(OSRSBot):
    def __init__(self):
        title = "Make headless arrows"
        description = "Add feathers to arrow shafts "
        super().__init__(bot_title=title, description=description)
        self.running_time = 1

        self.api_m = MorgHTTPSocket()
        self.api_s = StatusSocket()
        self.error_count = 0
        self.puntil = PUNTIL(self, self.api_m)
        self.pbank = PBANK(self, self.api_m)
        self.needables = [ids.FEATHER, ids.ARROW_SHAFT]

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
                if self.puntil.check_needed_items(self.needables):
                    self._do_craft()
                else:
                    self.stop()
            else:
                self.take_break(5, 30)

    def _do_craft(self):
        feathers = self.api_m.get_inv_item_indices(ids.FEATHER)
        arrowShafts = self.api_m.get_inv_item_indices(ids.ARROW_SHAFT)

        if len(feathers) > 0 and len(arrowShafts) > 0:
            bucketIndex = feathers[random.randint(0, len(feathers) - 1)]
            grapesIndex = arrowShafts[random.randint(0, len(arrowShafts) - 1)]
            spots = [
                self.win.inventory_slots[bucketIndex].random_point(),
                self.win.inventory_slots[grapesIndex].random_point()
            ]

            self._click_spots_random_order(spots)

            time.sleep(rd.fancy_normal_sample(0.3, 2))
            pag.press("space")
            if rd.random_chance(.14):
                self.log_msg("Take long break")
                self.take_break(20, 90)
            else:
                self.take_break(10, 15)

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
