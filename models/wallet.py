class Wallet:
    def __init__(self, initial_amount):
        self.balance = float(initial_amount)
        self.history = []
    
    def __str__(self):
        return f"started with {self.history[0]}, nom get {self.balance}"
    
    def get_balance(self):
        return self.balance
    
    def get_historique(self):
        return self.history
    
    def can_bet(self, amount):
        return self.balance >= amount
    
    def bet(self, amount):
        if self.can_bet(amount):
            self.balance -= amount
            self.history.append(f"-{amount}€")
            return True
        return False

    def win(self, gain):
        self.balance += gain
        self.history.append(f"+{gain}€")
