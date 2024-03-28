import time
from enum import Enum

import pyautogui as pag

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.imagesearch as imsearch
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from model.osrs.puntil.pbank import PBANK
from model.osrs.puntil.pitem import PItem
from model.osrs.puntil.puntil import PUNTIL
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRSSmeltingJewelleryEdgeVill(OSRSBot):
    api_morg = MorgHTTPSocket()
    api_status = StatusSocket()
    state = -1
    needed_items = [309, 314]
    firstTime = True
    crafting_item: PItem = PItem("", 0, "", [], [])
    errorCount = 0

    items = [
        PItem("Gold ring", ids.GOLD_RING, "Gold_ring", [2357, 1592], ["Gold_bar", "Ring_mould"]),
        PItem("Gold amulet (u)", ids.GOLD_AMULET_U, "Gold_amulet_(u)", [2357, 1595], ["Gold_bar", "Amulet_mould"]),
        PItem("Gold necklace", ids.GOLD_NECKLACE, "Gold_necklace", [ids.GOLD_BAR, ids.NECKLACE_MOULD], ["Gold_bar", "Necklace_mould"]),
        PItem("Bronze bar", ids.BRONZE_BAR, "Bronze_bar", [ids.COPPER_ORE, ids.TIN_ORE], ["Copper_ore", "Tin_ore"]),
        PItem("Ruby necklace", ids.RUBY_NECKLACE, "Ruby_necklace", [ids.GOLD_BAR, ids.RUBY, ids.NECKLACE_MOULD], ["Gold_bar", "Ruby", "Necklace_mould"]),
        PItem("Diamond necklace", ids.DIAMOND_NECKLACE, "Diamond_necklace", [ids.GOLD_BAR, ids.DIAMOND, ids.NECKLACE_MOULD], ["Gold_bar", "Diamond", "Necklace_mould"]),
        PItem("Emerald Bracelet", ids.EMERALD_BRACELET, "Emerald_bracelet", [ids.GOLD_BAR, ids.EMERALD, ids.BRACELET_MOULD], ["Gold_bar", "Emerald", "Bracelet_mould"]),

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
        self.api_m = MorgHTTPSocket()
        self.api_s = StatusSocket()
        self.puntil = PUNTIL(self, self.api_m)
        self.pbank = PBANK(self, self.api_m)

    def create_options(self):
        keys = list(self.item_dict.keys())
        print(keys)
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_dropdown_option("craft_item", "What should i make?", keys)

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
        self.state = BotState.Smelting
        self.running_time: int = 30

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

        if self._check_needed_inventory_items(self.crafting_item.needed_item_ids):
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
                    self.errorCount = self.errorCount + 1
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
            # self.pbank.bank_deposit_all_except(self.item.needed_item_ids)
            if not self.api_status.get_is_inv_empty():
                if not self.__bank_deposit_all():
                    return False
                time.sleep(0.2)

            self.__bank_withdraw_items(self.crafting_item.needed_item_images)
            self.state = BotState.Smelting

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
            deposit_img = imsearch.BOT_IMAGES.joinpath("items", item + "_bank.png")
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
