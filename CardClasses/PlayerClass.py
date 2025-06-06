class Player:
    """
    Player is a container class for the three objects that belong to it:
       - PlayerHand
       - CollectedCards
       - Bet
    """

    def __init__(self, hand, collected_cards, bet):
        self.hand = hand
        self.collected = collected_cards
        self.bet = bet
        self.value = 0
