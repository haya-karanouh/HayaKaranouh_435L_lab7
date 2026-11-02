"""Wallet exercise from Lab 7."""


class InsufficientAmount(Exception):
    pass


class Wallet:
    def __init__(self, initial_amount=0):
        self.balance = initial_amount

    def spend_cash(self, amount):
        if self.balance < amount:
            raise InsufficientAmount(f"Not enough available to spend {amount}")
        self.balance -= amount

    def add_cash(self, amount):
        self.balance += amount
