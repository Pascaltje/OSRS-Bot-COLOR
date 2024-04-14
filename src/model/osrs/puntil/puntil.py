import time

import utilities.color as clr
import utilities.imagesearch as imsearch
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from model.osrs.puntil.control_panel_tab import ControlPanelTab
from utilities.api.morg_http_client import MorgHTTPSocket


class PUNTIL:
    def __init__(self, bot: OSRSBot, api_m: MorgHTTPSocket):
        self.bot = bot
        self.api_m = api_m
        self.error_count = 0

    def setup(self):
        self.error_count = 0

    def is_tag_visible(self, color: clr.Color) -> bool:
        obj = self.bot.get_nearest_tag(color)
        if obj:
            return True
        else:
            return False

    def search_tag(self, color: clr.Color) -> bool:
        tries = 0
        while tries < 5:
            tries += 1
            h = int(rd.fancy_normal_sample(-180, 180))
            if h != 0:
                self.bot.move_camera(horizontal=h)
                time.sleep(1)
                if self.is_tag_visible(color):
                    return True
            else:
                tries -= 1
        return False

    def click_tag(self, color: clr.Color, error_msg: str, weight=1, click_nearest=True, mouse_over_text=None,
                  mouse_over_color=None) -> bool:
        if not self.is_tag_visible(color):
            if not self.search_tag(color):
                return False
        if click_nearest:
            obj = self.bot.get_nearest_tag(color)
        else:
            obj = self.bot.get_random_tag(color)

        if obj:
            self.reset_simple_error()
            self.bot.mouse.move_to(obj.random_point())
            if mouse_over_text:
                time.sleep(0.2)
                if not self.bot.mouseover_text(contains=[mouse_over_text]):
                    return False

            self.bot.mouse.click()
            time.sleep(1)  # sleeping 1 second to make sure something is happing before checking agian.
            return True
        else:
            self.simple_error(error_msg, weight)
            return False

    def click_pos(self, pos):
        self.bot.mouse.move_to(pos)
        self.bot.mouse.click()
        time.sleep(rd.fancy_normal_sample(0.1, 0.5))

    def wait_for_idle(self, location_next_action=None, min_idle_time=0):
        moved = False
        while not self.api_m.get_is_player_idle(poll_seconds=0.9):
            time.sleep(0.2)
            if location_next_action is not None and not moved:
                self.bot.mouse.move_to(location_next_action)
                moved = True
            # is running energy higher then 10
            if self.bot.get_run_energy() > 10 and rd.random_chance(0.005):
                self.bot.toggle_run(True)
        if min_idle_time > 0:
            time.sleep(min_idle_time)
            if not self.api_m.get_is_player_idle(poll_seconds=0.9):
                self.wait_for_idle(location_next_action, min_idle_time)

    def check_needed_items(self, items: list[int]) -> bool:
        if self.api_m.get_if_item_in_inv(items):
            return True

        if self.api_m.get_is_item_equipped(items):
            return True
        return False

    def drop_items_by_id(self, items: list[int]):
        positions = self.api_m.get_inv_item_indices(items)
        self.bot.drop(positions)
        time.sleep(1)

    def simple_error(self, msg: str, weight=1):
        self.error_count = self.error_count + weight
        self.bot.log_msg(f"{msg} ({self.error_count})")
        if self.error_count > 30:
            self.bot.log_msg("Stopping bot error count to high")
            self.bot.stop()

    def reset_simple_error(self):
        self.error_count = 0

    def logout(self, msg):
        self.bot.log_msg(msg)
        self.logout()
        self.bot.stop()

    def is_control_panel_selected(self, tab: ControlPanelTab) -> bool:
        tab_img = imsearch.BOT_IMAGES.joinpath("interface").joinpath(tab.value + "_selected.png")
        result = imsearch.search_img_in_rect(tab_img, self.bot.win.control_panel)
        return result is not None

    def wait_for_selected_tab(self, tab: ControlPanelTab, timeout: int = 10000) -> bool:
        start_time = time.time()  # Record the start time

        while (time.time() - start_time) * 1000 < timeout:  # Continue until timeout
            if self.is_control_panel_selected(tab):  # Check if the tab is selected
                return True
            time.sleep(0.1)  # Sleep for 100 ms before checking again

        return False  # Return False if timeout is reached before tab is selected
