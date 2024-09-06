class Product:
    def __init__(self, dict: dict, now_str: str) -> None:
        self.name: str = dict.get('name', '')
        self.product_id: str = dict.get('productID', '')
        self.price: float = dict.get('offers', {}).get('price', 0)
        self.now_str: str = now_str

    def is_valid(self):
        return bool(self.product_id) and bool(self.price) and bool(self.name)

    def get_output(self):
        return [self.now_str, self.product_id, self.name, self.price]
    
    def __str__(self) -> str:
        return f'{self.name}, {self.product_id}, {self.price}'