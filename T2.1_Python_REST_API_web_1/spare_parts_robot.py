class SparePartsRobot(object):
    """SparePartsRobot Class."""

    def __init__(
        self,
        inventory: dict[str, dict[str, int]],
        max_capacity: int,
        cash_balance: int,
        motd: str,
    ):
        """Setup robot with initial inventory."""
        self.inventory = inventory
        self.max_capacity = max_capacity

        self.current_capacity = 0

        for item in inventory:
            self.current_capacity += inventory[item]["amount"]

        self.cash_balance = cash_balance
        self.motd = motd

    def getContent(self) -> dict[str, dict[str, int]]:
        """Retrieve full inventory of Robot."""
        return self.inventory

    def get_motd(self) -> str:
        """Retrieve motd."""
        return self.motd

    def set_motd(self, motd: str) -> bool:
        """Change motd."""
        self.motd = motd
        return True

    def get_current_capacity(self) -> int:
        """Retrieve current_capacity."""
        return self.current_capacity

    def get_max_capacity(self) -> int:
        """Retrieve max_capacity."""
        return self.max_capacity

    def get_cash_balance(self) -> int:
        """Retrieve cash_balance."""
        return self.cash_balance

    def check_max_capacity_reached(self, amount: int) -> bool:
        """Check if maximum capacity is reached."""
        if self.current_capacity + amount >= self.max_capacity:
            return True
        else:
            return False

    def check_out_of_stock(self, part: str, amount: int) -> bool:
        """Check if out of stock for part is reached."""
        if self.inventory[part]["amount"] - amount < 0:
            return True
        else:
            return False

    def check_out_of_cash_balance(self, cash_amount: int) -> bool:
        """Check if we will go out of cash."""
        if self.cash_balance - cash_amount < 0:
            return True
        else:
            return False

    def add_part(self, part: str, amount: int) -> bool:
        """Add part to robot inventory."""
        if self.check_max_capacity_reached(amount):
            return False
        else:
            if self.check_out_of_cash_balance(self.inventory[part]["price"] * amount):
                return False
            else:
                self.inventory[part]["amount"] += amount
                self.current_capacity += amount
                self.cash_balance -= self.inventory[part]["price"] * amount
                return True

    def remove_part(self, part: str, amount: int) -> bool:
        """Remove part from robot inventory."""
        if self.check_out_of_stock(part, amount):
            return False
        else:
            self.inventory[part]["amount"] -= amount
            self.current_capacity -= amount
            self.cash_balance += self.inventory[part]["price"] * amount
            return True

    def backorder_part(self, part: str, amount: int) -> None:
        """Backorder part from vendor."""
        self.inventory[part]["backorder"] += amount

    def add_cash(self, amount: int) -> bool:
        """Add cash to vending machine."""
        self.cash_balance += amount
        return True

    def remove_cash(self, amount: int) -> bool:
        """Remove cash from machine."""
        if self.check_out_of_cash_balance(amount):
            return False
        else:
            self.cash_balance -= amount
            return True
