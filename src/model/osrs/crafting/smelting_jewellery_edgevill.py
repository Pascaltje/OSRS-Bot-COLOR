import time
from abc import ABC
from enum import Enum
import random

from model.osrs.osrs_bot import OSRSBot
import utilities.game_launcher as launcher
from model.osrs.puntil.pitem import PItem
from model.osrs.puntil.puntil import PUNTIL
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
import utilities.color as clr
import utilities.imagesearch as imsearch
import utilities.random_util as rd
import pyautogui as pag


class OSRSSmeltingJewelleryEdgeVill(OSRSBot):
    api_morg = MorgHTTPSocket()
    api_status = StatusSocket()
    state = -1
    needed_items = [309, 314]
    firstTime = True
    crafting_item: PItem = PItem("", 0, [], "")
    errorCount = 0

    items = [
        PItem("Gold ring", 1635, [2357, 1592], "Gold_bar"),
        PItem("Gold amulet (u)", 2, [2357, 1595], "Gold_amulet_(u)"),
    ]

    # Convert the list of objects to a dictionary with the item names as keys
    item_dict = {item.name: item for item in items}

    def __init__(self):
        bot_title = "Smelting jewellery Edgevill"
        description = (
            "This bot will smelt jewellery at Edgevill"
        )
        super().__init__(bot_title=bot_title, description=description)
        self.state = BotState.Smelting
        self.running_time: int = 30

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_dropdown_option("craft_item", "What should i make?", ["Gold ring", "Gold amulet (u)"])

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "craft_item":
                self.crafting_item = self.item_dict[options[option]]
                print(self.crafting_item)
            else:
                self.log_msg(f"Unknown option: {option}")
                print(
                    "Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return

        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.options_set = True

    def __setup(self):
        self.api_m = MorgHTTPSocket()
        self.api_s = StatusSocket()
        self.puntil = PUNTIL(self, self.api_m, self.api_s)

    def main_loop(self):

        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            if self.errorCount > 10:
                self.stop()

            self._wait_for_idle()
            if self.state == BotState.Banking:
                self.__do_banking()
            elif self.state == BotState.Smelting:
                self.__do_smelting()
            time.sleep(0.1)
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def __do_smelting(self):
        # check for gold bars and ring mount
        # 2357 gold bar
        # 1635 gold ring
        # 1592 ring mount

        if self._check_needed_inventory_items(self.crafting_item.neededItems):
            self.log_msg("click furnace")
            furnace = self.get_nearest_tag(clr.BLUE)
            if furnace:
                self.mouse.move_to(furnace.random_point())
                self.mouse.click()
                self.log_msg("Wait for idle")
                self._wait_for_idle()
                time.sleep(0.1)
                self.__press_smelt_item()
                self.log_msg("Wait for done smelting")
                self._wait_for_idle()
            # wait for furnace popup to open
            # click ring to smelt or press space
            # wait for all bars melt in to rings
        else:
            # out of bars go banking
            self.state = BotState.Banking

    def __press_smelt_item(self):
        if self.firstTime or rd.random_chance(0.3):
            self.log_msg("try to smelt " + self.crafting_item.name)
            deposit_img = imsearch.BOT_IMAGES.joinpath("items", self.crafting_item.image + ".png")
            if deposit_img := imsearch.search_img_in_rect(deposit_img, self.win.game_view):
                self.mouse.move_to(deposit_img.random_point())
                time.sleep(0.1)
                self.mouse.click()
                time.sleep(0.1)
            else:
                self.log_msg(self.crafting_item.name + " not found! :/ pressed space")
                pag.press("space")
                time.sleep(0.3)
                if self.api_morg.get_is_player_idle():
                    self.log_msg("Crafting action failed! :(")
                    self.errorCount = self.errorCount+1
                # self.__press_smelt_item()
        else:
            self.log_msg("press space to smelt")
            pag.press("space")

    def __do_banking(self):
        # open bank
        self.log_msg("Open bank")
        bank = self.get_nearest_tag(clr.YELLOW)
        if bank:
            self.log_msg("Click bank")
            self.mouse.move_to(bank.random_point())
            self.mouse.click()
            # wait for bank opend
            self.log_msg("Wait for bank opens")
            self._wait_for_idle()
            time.sleep(0.1)
            if not self.api_status.get_is_inv_empty():
                if not self.__bank_deposit_all():
                    return False
                time.sleep(0.2)

            items = ["Gold_bar_bank.png"]
            # if not self.api_morg.get_if_item_in_inv(1592):
            #     items.insert(0, "Ring_mould_bank.png")
            self.__bank_withdraw_items(items)
            self.state = BotState.Smelting

            # consider bank as open
            # deposit all or deposit all rings

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

    def _check_needed_inventory_items(self, items_ids):
        for itemId in items_ids:
            if not self.api_morg.get_if_item_in_inv(itemId):
                return False
        return True

    def _check_needed_inventory_items(self, items_ids):
        for itemId in items_ids:
            if not self.api_morg.get_if_item_in_inv(itemId):
                return False
        return True

    def _wait_for_idle(self, location_next_action=None, max_break_time=10):
        moved = False
        while not self.api_morg.get_is_player_idle(poll_seconds=0.9):
            self.take_break(1, max_break_time)
            if location_next_action is not None and not moved:
                self.mouse.move_to(location_next_action)
                moved = True
            # is running energy higher then 10
            if self.get_run_energy() > 10 and rd.random_chance(0.05):
                self.toggle_run(True)

    def __logout(self, msg):
        self.log_msg(msg)
        if rd.random_chance(.3):
            self.logout()
        self.stop()


class BotState(Enum):
    Banking = 1
    Smelting = 2