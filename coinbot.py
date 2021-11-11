#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (C) 2021 GoodData Corporation

# import the random library to help us generate the random numbers
import random


# Create the CoinBot Class
class CoinBot:

    # Create a constant that contains the default text for the message
    COIN_START_BLOCK = "Sure! Flipping a coin....\n\n"

    # Generate a random number to simulate flipping a coin. Then return the
    # crafted slack payload with the coin flip message.
    @staticmethod
    def flip_coin():
        rand_int = random.randint(0, 1)
        if rand_int == 0:
            results = "Heads"
        else:
            results = "Tails"

        return f"The result is {results}"
