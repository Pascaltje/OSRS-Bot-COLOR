from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from model.osrs.osrs_bot import OSRSBot
import utilities.imagesearch as imsearch
import time
import utilities.random_util as rd
import pyautogui as pag


class PBANK:
    def __init__(self, bot: OSRSBot, api_m: MorgHTTPSocket):
        self.bot = bot
        self.api_m = api_m
        self.error_count = 0

    def bank_deposit_all(self, image="deposit_inventory.png") -> bool:
        deposit_img = imsearch.BOT_IMAGES.joinpath("bank", image)
        if deposit_img := imsearch.search_img_in_rect(deposit_img, self.bot.win.game_view):
            self.bot.mouse.move_to(deposit_img.random_point())
            self.bot.mouse.click()
            self.__sleep()
            return True
        else:
            self.bot.log_msg("Could not deposit items")
            return False

    def bank_deposit_loot(self) -> bool:
        return self.bank_deposit_all()

    def bank_deposit_all_except(self, keep_list):
        items = self.api_m.get_inv_indices_except_ignore(keep_list)
        for item in items:
            self._click_inv_slot(item)

    def _click_inv_slot(self, slot):
        spot = self.bot.win.inventory_slots[slot].random_point()
        self.bot.mouse.move_to(spot)
        time.sleep(0.1)
        self.bot.mouse.click()
        time.sleep(0.1)

    def bank_withdraw_items(self, items):
        for item in items:
            self.bot.log_msg("Try to withdraw " + item)
            deposit_img = imsearch.BOT_IMAGES.joinpath("items", item)
            if deposit_img := imsearch.search_img_in_rect(deposit_img, self.bot.win.game_view):
                self.bot.mouse.move_to(deposit_img.random_point())
                self.__sleep()
                self.bot.mouse.click()
                self.__sleep()
            else:
                self.bot.log_msg("Could not found item " + item)
                self.bot.stop()

    def close(self):
        self.__sleep()
        pag.press("esc")
        self.__sleep()

    def __sleep(self):
        if rd.random_chance(.005):
            self.bot.take_break()
        time.sleep(rd.fancy_normal_sample(0.2, 0.5))
