class PItem:
    def __init__(self, name: str, item_id: int,  image: str, needed_item_ids: list[int], needed_item_images: list[str]):
        self.name = name
        self.itemId = item_id
        self.image = image
        self.needed_item_ids = needed_item_ids
        self.needed_item_images = needed_item_images
