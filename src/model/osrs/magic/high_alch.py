import random
import time

import utilities.api.item_ids as ids
import utilities.imagesearch as imsearch
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from model.osrs.puntil.control_panel_tab import ControlPanelTab
from model.osrs.puntil.puntil import PUNTIL
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.geometry import Rectangle


class OSRSHIGHALCH(OSRSBot):
    api_morg = MorgHTTPSocket()

    def __init__(self):
        bot_title = "High alchemy"
        description = (
            "High alch every item in the inventory, except coins en nature runes."
        )
        super().__init__(bot_title=bot_title, description=description)
        self.running_time: int = random.randint(45, 200)
        self.item_index: int = 0

        self.current_item_id = -1
        self.current_item_index = -1
        self.puntil = PUNTIL(self, self.api_morg)

        self.ignore_items_list = ids.coins
        self.ignore_items_list.append(ids.NATURE_RUNE)

        self.spell_location = None
        self.spell_item_rectangle: Rectangle | None = None  # The overlap between spell and inventory slot
        self.click_pos = None
        self.click_pos_times = random.randint(0, 35)
        self.click_pos_count = 0

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)

    def save_options(self, options: dict):
        self.options_set = True
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

    def setup(self):
        self.spell_location = None
        self.spell_item_rectangle: Rectangle | None = None
        self.click_pos = None
        self.click_pos_times = random.randint(0, 35)
        self.click_pos_count = 0

    def setup_high_alchemy_spot(self):
        self.get_spell_location()

    def main_loop(self):
        # Main loop
        self.setup()
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            self.has_nature_rune()
            self.setup_high_alchemy_spot()
            isStarting = self._set_item_in_alch_spot()
            self.set_click_pos(force=isStarting)
            self.do_high_alch()

            time.sleep(0.1)
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def _set_item_in_alch_spot(self):
        # Get every item
        items = self.api_morg.get_inv_indices_except_ignore(self.ignore_items_list)
        if len(items) == 0:
            self.log_msg("Items not found")
            self.stop()
        else:
            if self.item_index not in items:
                self.select_inv_tab()
                self.log_msg("Drag item to alch spot")
                # move item to alch spot
                index = items[random.randint(0, len(items) - 1)]
                self.mouse.drag(self.win.inventory_slots[index].random_point(), self.win.inventory_slots[self.item_index].random_point())
                return True
            else:
                return False

    def do_high_alch(self):
        self.select_magic_tab()
        self.mouse.move_to(self.click_pos)
        time.sleep(0.1)
        self.mouse.click()  # Click spell in magic book
        self.puntil.wait_for_selected_tab(ControlPanelTab.inventory)
        time.sleep(0.1)
        self.set_click_pos()
        self.click_pos_count = self.click_pos_count + 1
        # 3. klik item
        self.mouse.move_to(self.click_pos)
        self.mouse.click()  # Click item in inv
        self.api_morg.wait_til_gained_xp("Magic")
        time.sleep(0.15)
        self.set_click_pos()
        self.click_pos_count = self.click_pos_count + 1

    def get_spell_location(self) -> Rectangle:
        if not self.spell_location:
            self.select_magic_tab()
            spell_img = imsearch.BOT_IMAGES.joinpath("spellbooks").joinpath("normal", "high_alchemy.png")
            if spell_img_result := imsearch.search_img_in_rect(spell_img, self.win.control_panel):
                self.spell_location = spell_img_result
                self.item_index, self.spell_item_rectangle = self.find_index_with_max_overlap(self.spell_location)
                self.set_click_pos(force=True)
        return self.spell_location

    def set_click_pos(self, force: bool = False):
        if self.spell_item_rectangle and force or self.click_pos_count >= self.click_pos_times:
            self.click_pos = self.spell_item_rectangle.random_point()
            self.click_pos_count = 0
            self.click_pos_times = random.randint(15, 150)

    def has_nature_rune(self):
        if not self.api_morg.get_if_item_in_inv(ids.NATURE_RUNE):
            self.log_msg("Out of nature runes")
            self.stop()

    def select_inv_tab(self):
        if not self.puntil.is_control_panel_selected(ControlPanelTab.inventory):
            self.log_msg("Selecting inventory...")
            self.mouse.move_to(self.win.cp_tabs[3].random_point())
            self.mouse.click()

    def select_magic_tab(self):
        if not self.puntil.is_control_panel_selected(ControlPanelTab.magic):
            self.mouse.move_to(self.win.cp_tabs[6].random_point())
            self.mouse.click()
            time.sleep(.5)

    def find_index_with_max_overlap(self, searchfor: Rectangle) -> tuple[int, Rectangle]:
        max_overlap_area = 0
        item_index = -1
        item_overlap_rectangle: Rectangle | None = None

        for index, slot in enumerate(self.win.inventory_slots):
            overlap_rect = self.find_overlap_rectangle(searchfor, slot)
            if overlap_rect:
                overlap_area = overlap_rect.width * overlap_rect.height
                if overlap_area > max_overlap_area:
                    max_overlap_area = overlap_area
                    item_index = index
                    item_overlap_rectangle = overlap_rect
        return item_index, item_overlap_rectangle

    def find_overlap_rectangle(self, rect1: Rectangle, rect2: Rectangle) -> Rectangle:
        # Calculate the (left, top) and (right, bottom) for each rectangle
        left1, top1, right1, bottom1 = rect1.left, rect1.top, rect1.left + rect1.width, rect1.top + rect1.height
        left2, top2, right2, bottom2 = rect2.left, rect2.top, rect2.left + rect2.width, rect2.top + rect2.height

        # Find overlap coordinates
        overlap_left = max(left1, left2)
        overlap_top = max(top1, top2)
        overlap_right = min(right1, right2)
        overlap_bottom = min(bottom1, bottom2)

        # Check if there is an actual overlap
        if overlap_left < overlap_right and overlap_top < overlap_bottom:
            # There is an overlap, so return the overlapping rectangle
            return Rectangle(
                left=overlap_left,
                top=overlap_top,
                width=overlap_right - overlap_left,
                height=overlap_bottom - overlap_top
            )
        else:
            # No overlap
            return None

    def __logout(self, msg):
        self.log_msg(msg)
        if rd.random_chance(.3):
            self.logout()
        self.stop()
