import random
import time

import utilities.color as clr
import utilities.api.item_ids as ids
from model.osrs.osrs_bot import OSRSBot
from model.osrs.puntil.pbank import PBANK
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from model.osrs.puntil.puntil import PUNTIL
import utilities.random_util as rd


class POSRSMotherLoadMiner(OSRSBot):
    def __init__(self):
        title = "PMotherLoad Miner"
        description = "Mine ore veins at the motherload mine, wash the ores and bank them."
        super().__init__(bot_title=title, description=description)
        self.running_time = 1

        self.api_m = MorgHTTPSocket()
        self.error_count = 0
        self.puntil = PUNTIL(self, self.api_m)
        self.pbank = PBANK(self, self.api_m)

        # Some settings
        self.colorVein = clr.YELLOW
        self.colorOreHopper = clr.RED
        self.colorOrePickUp = clr.GREEN
        self.colorDepositBox = clr.PURPLE
        # helpers
        self.colorVeinTile = clr.BLUE

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
        self.puntil.setup()
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

            if self.api_m.get_is_inv_empty():
                # When inventory is empty
                if self.puntil.is_tag_visible(self.colorOrePickUp):
                    # Search for the orePickUp (Green color), when found click it (what if it is out of view? :/)
                    self.pick_up_ore()
                else:
                    # Not found search for mining vein
                    self.mine_vein(mine_nearest=False)
            elif self.api_m.get_is_inv_full() and self.api_m.get_if_item_in_inv(ids.PAYDIRT):
                # when inventory full, click the hopper to deposit the ore
                self.dump_dirt()
            else:
                if self.api_m.get_if_item_in_inv(ids.PAYDIRT):
                    self.mine_vein()
                else:
                    self.deposit_ores()

    def mine_vein(self, mine_nearest=True):
        self.click_and_wait_for_idle(self.colorVein, "Mining vein", "Vein not found, they can be not available",
                                     click_nearest=mine_nearest)
        self.puntil.wait_for_idle(min_idle_time=2)

    def dump_dirt(self):
        if self.puntil.click_tag(self.colorOreHopper, "Error clicking/ finding the hopper"):
            self.log_msg("Dumping ore into hopper")
            self.take_break(1, 3)
            self.puntil.wait_for_idle()
        else:
            self.click_and_wait_for_idle(self.colorVeinTile, "Walking to helper tile",
                                         "helper tile not found, they can be not available", click_nearest=False)

    def pick_up_ore(self):
        self.click_and_wait_for_idle(self.colorOrePickUp, "Pickup ore from sack",
                                     "Error clicking/ finding the sack")

    def deposit_ores(self):
        self.click_and_wait_for_idle(self.colorDepositBox, "Deposit ores to bank",
                                     "Error clicking/ finding the deposit box")
        self.puntil.wait_for_idle()
        self.pbank.bank_deposit_loot()
        self.pbank.close()

    def click_and_wait_for_idle(self, color, message, error_message, click_nearest=rd.random_chance(0.6)):
        if self.puntil.click_tag(color, error_message, click_nearest):
            self.log_msg(message)
            self.take_break(1, 3)
            self.puntil.wait_for_idle()
            return True
        else:
            return False
