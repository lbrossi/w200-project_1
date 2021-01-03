import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')

class PlayingCard:
    '''
    This class represents a PlayingCard, with a rank in
    ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    and a suit in ["♠", "♥", "♦", "♣"].

    Class Attributes:
    value_dict
    rank
    suit
    value

    Class Methods:
    __init__
    __repr__
    '''

    value_dict = {
        "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
        "10": 10, "J": 10, "Q": 10, "K": 10, "A": 11}

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = PlayingCard.value_dict[self.rank]

    def __repr__(self):
        return self.rank + " of " + self.suit

class CardDeck:
    '''
    This class represents one or more decks of PlayingCards.

    Class attributes:
    deck

    Class methods:
    __init__
    shuffle_deck
    deal_card
    '''

    valid_ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10",
                "J", "Q", "K", "A"]
    valid_suits = ["♦", "♠", "♥", "♣"]

    def __init__(self, num_decks):
        self.deck = num_decks * [PlayingCard(rank, suit) for suit in
                                CardDeck.valid_suits for rank in
                                CardDeck.valid_ranks]
        self.shuffle_deck()

    def shuffle_deck(self):
        from random import sample
        self.deck = sample(self.deck, len(self.deck))

    def deal_card(self):
        card = self.deck.pop(0)
        return card

class CardHand:
    '''This class represents a hand of cards - either of a player,
    or of the dealer, in a Blackjack game round.

    Class attributes:
    hand
    bet
    stop
    abandon

    Class methods:
    __init__
    score
    score_type
    blackjack_check
    bust_check
    splittable
    hit
    stand
    double_down
    surrender
    '''

    def __init__(self, bet):
        self.hand = []
        self.bet = bet
        self.stop = False
        self.abandon = False

    def score(self):
        score = 0
        num_A = 0
        for card in self.hand:
            score += PlayingCard.value_dict[card.rank]
            if card.rank == "A":
                num_A += 1
        for x in range(0, num_A):
            if score > 21:
                score -= 10
        return score

    def score_type(self):
        score = 0
        num_A = 0
        for card in self.hand:
            score += PlayingCard.value_dict[card.rank]
            if card.rank == "A":
                num_A += 1
        if num_A > 0:
            if score - self.score() == 10 * num_A:
                return "hard"
            else:
                return "soft"
        else:
            return "hard"

    def blackjack_check(self):
        if self.score() == 21:
            return True
        else:
            return False

    def bust_check(self):
        if self.score() > 21:
            return True
        else:
            return False

    def splittable(self):
        if len(self.hand) == 2 and self.hand[0].value == self.hand[1].value:
            return True

    def hit(self, deck):
        self.hand.append(deck.deal_card())

    def stand(self):
        self.stop = True

    def double_down(self, deck):
        self.bet += self.bet
        self.hit(deck)
        self.stand()

    def surrender(self):
        self.bet -= .5 * self.bet
        self.abandon = True

class GameRound:
    '''
    This class represents a one-player round of a Blackjack game.

    Class attributes:
    player
    dealer
    split_count
    insurance
    winnings
    split1
    split2
    split3
    hand_list
    result_list

    Class methods:
    deal_cards
    setup_split
    insurable
    insure
    split
    getbet
    settable
    dealer_turn
    settle_insurance
    settle_hands
    settle
    print_hands
    print_dealerhand
    print_playerhands
    print_finalhands
    print_scores
    print_settle
    '''

    def __init__(self, deck, bet):
        self.player = CardHand(bet)
        self.dealer = CardHand(0)
        self.deal_cards(deck)
        self.split_count = 0
        self.setup_split(bet)
        self.insurance = 0
        self.winnings = 0

    def deal_cards(self, deck):
        self.player.hit(deck)
        self.dealer.hit(deck)
        self.player.hit(deck)
        self.dealer.hit(deck)

    def setup_split(self, bet):
        self.split1 = CardHand(bet)
        self.split2 = CardHand(bet)
        self.split3 = CardHand(bet)
        self.hand_list = [self.player, self.split1, self.split2, self.split3]
        self.result_list = []

    def insurable(self):
        if self.dealer.hand[0].rank in ["10", "J", "Q", "K", "A"]:
            return True

    def insure(self):
        if self.insurable():
            self.insurance = self.player.bet / 2

    def split(self, hand, deck):
        if hand.splittable() and self.split_count < 3:
            card = hand.hand.pop()
            self.hand_list[self.split_count + 1].hand.append(card)
            if hand.hand[0].rank == "A":
                hand.hit(deck)
                hand.stand()
                self.hand_list[self.split_count + 1].hit(deck)
                self.hand_list[self.split_count + 1].stand()
            else:
                hand.hit(deck)
                self.hand_list[self.split_count + 1].hit(deck)
            self.split_count += 1

    def getbet(self):
        bet = 0
        for hand in self.hand_list:
            if len(hand.hand) > 0:
                bet += hand.bet
        return bet

    def settable(self):
        ready_to_settle = 0
        for hand in self.hand_list:
            if hand.stop or hand.abandon or len(hand.hand) == 0:
                ready_to_settle += 1
        if ready_to_settle == 4:
            return True

    def dealer_turn(self, deck):
        not_play = True
        for hand in self.hand_list:
            if len(hand.hand) > 0 and not hand.bust_check() and not hand.abandon:
                not_play = False
        if self.dealer.stop == False and not_play == False:
            while (self.dealer.score() < 17
                    or self.dealer.score_type() == "soft"
                    and not self.dealer.blackjack_check()):
                self.dealer.hit(deck)
            self.dealer.stand()

    def settle_insurance(self):
        if len(self.dealer.hand) == 2 and self.dealer.blackjack_check():
            self.winnings += 3 * self.insurance

    def settle(self, deck):
        if self.settable():
            self.settle_insurance()
            self.dealer_turn(deck)
            for hand in self.hand_list:
                if len(hand.hand) > 0:
                    x = self.settle_hands(hand)
                    self.result_list.append(x)

    def settle_hands(self, hand):
        if hand.abandon:
            self.winnings += 0
            return "surrendered"
        elif self.dealer.blackjack_check() and hand.blackjack_check():
            self.winnings += hand.bet
            return "tied"
        elif self.dealer.blackjack_check():
            self.winnings += 0
            return "lost"
        elif hand.blackjack_check():
            self.winnings += hand.bet + 3/2 * hand.bet
            return "won"
        elif hand.bust_check():
            self.winnings += 0
            return "lost"
        elif self.dealer.bust_check():
            self.winnings += 2 * hand.bet
            return "won"
        elif self.dealer.score() == hand.score():
            self.winnings += hand.bet
            return "tied"
        elif self.dealer.score() > hand.score():
            self.winnings += 0
            return "lost"
        elif self.dealer.score() < hand.score():
            self.winnings += 2 * hand.bet
            return "won"

    def print_hands(self):
        print("Dealer's hand:", self.dealer.hand[0], "? of ?")
        print(80 * "-")
        self.print_playerhands()

    def print_dealerhand(self):
        print("Dealer's hand:", *self.dealer.hand)
        if self.dealer.blackjack_check():
            print("It's a Blackjack!")
        if self.dealer.bust_check():
            print("It's a Bust!")
        print(80 * "-")

    def print_playerhands(self):
        print("Your hand:", *self.player.hand)
        if self.player.blackjack_check():
            print("It's a Blackjack!")
        if self.player.bust_check():
            print("It's a Bust!")
        if self.split_count > 0:
            print(80 * "-")
            for split in self.hand_list[1:]:
                if len(split.hand) > 0:
                    print("Your split hand:", *split.hand)
                    if split.blackjack_check():
                        print("It's a Blackjack!")
                    if split.bust_check():
                        print("It's a Bust!")
        print("")

    def print_finalhands(self):
        self.print_dealerhand()
        self.print_playerhands()

    def print_scores(self):
        print("Dealer score:", self.dealer.score())
        print("Your hand score:", self.player.score())
        print("You {}!".format(self.result_list[0]))
        for index in range(1, len(self.hand_list)):
            if len(self.hand_list[index].hand) > 0:
                print("Your split hand score:", self.hand_list[index].score())
                print("You {}!".format(self.result_list[index]))
        print("")

    def print_settle(self):
        print("This round is settled:")
        print("")
        not_print = True
        for hand in self.hand_list:
            if len(hand.hand) > 0 and not hand.bust_check() and not hand.abandon:
                not_print = False
        if not_print == False:
            self.print_finalhands()
            self.print_scores()
        print("Your bet for this round was: ${:,.2f}".format(self.getbet()))
        if self.insurance > 0:
            print("Your insurance for this round was: ${:,.2f}".format(self.insurance))
        print("Your winnings for this round are: ${:,.2f}".format(self.winnings))
        print("")

class GameAction:
    '''
    This class handles all the interactions with the user,
    and represents a full game of Blackjack.

    Class attributes:
    round
    user_name
    user_age
    game_mode
    deck
    initial_balance
    balance
    roundx

    Class methods:
    __init__
    welcome_script
    game_script
    round_script
    bet_script
    insurance_script
    split_script
    hit_script
    settle_script
    '''

    def __init__(self):
        print(80 * "-")
        print("{:^80s}".format("♦ ♠ ♥ ♣ BLACKJACK ♣ ♥ ♠ ♦"))
        print(80 * "-")
        print("{:>80s}".format("\u00A9 2020 Lucas Brossi"))
        print("{:>80s}".format("All rights reserved"))
        print("")
        self.welcome_script()
        self.round = 0
        self.game_script()

    def welcome_script(self):
        print("Hi, welcome to BlackJack! The most thrilling casino game!")
        self.user_name = input("What's your name? ")
        print("")
        print("Nice to meet you, {}!".format(self.user_name))
        while True:
            try:
                user_age = int(input("What's your age? "))
                if 0 < user_age < 100:
                    break
                else:
                    print("Sorry, this seems to be an invalid age.")
            except:
                print("Sorry, this seems to be an invalid age.")
                print("")
        print("")
        if user_age < 21:
            print("Oh, you are under 21!")
            print("Ok, let's move on, but don't tell mom or dad, hein?")
        else:
            print("Great, let's start!")
        print("")
        loop = True
        while loop:
            self.game_mode = input("""Press D to play until Deck is over | R to play a limited number of Rounds. """).upper()
            if self.game_mode == "D" or self.game_mode == "R":
                loop = False
            else:
                print("Sorry, this is not a valid command.")
                print("")
        print("")
        if self.game_mode == "D":
            while True:
                try:
                    num_decks = int(input("Choose any number of decks up to 12: "))
                    if 0 < num_decks < 13:
                        break
                    else:
                        print("Sorry, this seems to be an invalid number of decks.")
                except:
                    print("Sorry, this seems to be an invalid number of decks.")
                    print("")
        else:
            while True:
                try:
                    self.num_rounds = int(input("Choose any number of rounds up to 60: "))
                    if 0 < self.num_rounds < 61:
                        break
                    else:
                        print("Sorry, this seems to be an invalid number of rounds.")
                except:
                    print("Sorry, this seems to be an invalid number of rounds.")
                    print("")
            num_decks = self.num_rounds * 10 // 52 + 1
        self.deck = CardDeck(num_decks)
        print("")
        while True:
            try:
                self.initial_balance = int(input("Ok, how much $$$ are you going to bet in this match? "))
                self.balance = self.initial_balance
                if self.balance > 0:
                    break
                else:
                    print("Sorry, we only accept positive integer bets here.")
            except:
                print("Sorry, we only accept positive integer bets here.")
        print("")
        print("I fell today is going to be THE DAY for you, hein?")
        print("")

    def game_script(self):
        if self.game_mode == "D":
            while len(self.deck.deck) > 10 and self.balance > 1:
                self.round_script()
        else:
            while (self.num_rounds - self.round) > 0 and self.balance > 1:
                self.round_script()
        print("End of game! You've played " + str(self.round) + " rounds!")
        print(80 * '-')
        print("You invested: ${:,.2f} | Your final balance: ${:,.2f}".format(self.initial_balance, self.balance))
        print('')

    def round_script(self):
        self.round += 1
        print(80 * "#")
        print("{:^80s}".format("♦ ♠ ♥ ♣ ROUND " + str(self.round) + " ♣ ♥ ♠ ♦"))
        print(80 * "#")
        if self.game_mode == "D":
            print("{:>80s}".format("There are " + str(len(self.deck.deck)) + " cards remaining in the deck"))
        else:
            print("{:>80s}".format("There are " + str(self.num_rounds - self.round) + " remaining rounds"))
        print("{:>80s}".format("Your balance is ${:,.2f}".format(self.balance)))
        print("")
        self.bet_script()
        self.roundx.print_hands()
        self.insurance_script()
        if self.roundx.dealer.blackjack_check():
            self.roundx.player.stand()
            self.settle_script()
        elif self.roundx.player.blackjack_check():
            self.roundx.player.stand()
            self.roundx.dealer.stand()
            self.settle_script()
        else:
            self.split_script()
            for hand in self.roundx.hand_list:
                if len(hand.hand) > 0 and hand.blackjack_check():
                    hand.stand()
                elif len(hand.hand) > 0 and hand.stop == False:
                    self.hit_script(hand)
            self.settle_script()

    def bet_script(self):
        while True:
            try:
                user_bet = int(input("Place your bet for this round: "))
                if 0 < user_bet <= self.balance:
                    break
                elif user_bet <= 0:
                    print("Sorry, we only accept positive integer bets.")
                    print("")
                elif user_bet > self.balance:
                    print("You don't have enough balance to bet this amount.")
                    print("Your current balance is: ", self.balance)
                    print("")
            except:
                print("Sorry, we only accept positive integer bets.")
                print("")
        print("")
        self.balance -= user_bet
        self.roundx = GameRound(self.deck, user_bet)

    def insurance_script(self):
        if self.roundx.insurable() and self.balance >= (self.roundx.player.bet / 2):
            user_insure = input("Press I to buy Insurance of ${:,.2f} or any other key to skip".format(self.roundx.player.bet / 2)).upper()
            print("")
            if user_insure == "I":
                self.roundx.insure()
                self.balance -= self.roundx.player.bet / 2

    def split_script(self):
        if self.roundx.player.splittable() and self.balance >= self.roundx.player.bet:
            user_action = input("Press S to Split or any other key to skip. ").upper()
            print("")
            if user_action == "S":
                self.balance -= self.roundx.player.bet
                self.roundx.split(self.roundx.player, self.deck)
                self.roundx.print_playerhands()
                if self.roundx.player.splittable() and self.balance >= self.roundx.player.bet:
                    user_action = input("Press S to Split or any other key to skip. ").upper()
                    print("")
                    if user_action == "S":
                        self.balance -= self.roundx.player.bet
                        self.roundx.split(self.roundx.player, self.deck)
                        self.roundx.print_playerhands()
                        if self.roundx.player.splittable() and self.balance >= self.roundx.player.bet:
                            user_action = input("Press S to Split or any other key to skip. ").upper()
                            print("")
                            if user_action == "S":
                                self.balance -= self.roundx.player.bet
                                self.roundx.split(self.roundx.player, self.deck)
                                self.roundx.print_playerhands()
                        if self.roundx.split2.splittable() and self.balance >= self.roundx.player.bet:
                            user_action = input("Press S to Split or any other key to skip. ").upper()
                            print("")
                            if user_action == "S":
                                self.balance -= self.roundx.player.bet
                                self.roundx.split(self.roundx.split2, self.deck)
                                self.roundx.print_playerhands()
                if self.roundx.split1.splittable() and self.balance >= self.roundx.player.bet:
                    user_action = input("Press S to Split or any other key to skip. ").upper()
                    print("")
                    if user_action == "S":
                        self.balance -= self.roundx.player.bet
                        self.roundx.split(self.roundx.split1, self.deck)
                        self.roundx.print_playerhands()
                        if self.roundx.split1.splittable() and self.balance >= self.roundx.player.bet:
                            user_action = input("Press S to Split or any other key to skip. ").upper()
                            print("")
                            if user_action == "S":
                                self.balance -= self.roundx.player.bet
                                self.roundx.split(self.roundx.split1, self.deck)
                                self.roundx.print_playerhands()
                        if self.roundx.split2.splittable() and self.balance >= self.roundx.player.bet:
                            user_action = input("Press S to Split or any other key to skip. ").upper()
                            print("")
                            if user_action == "S":
                                self.balance -= self.roundx.player.bet
                                self.roundx.split(self.roundx.split2, self.deck)
                                self.roundx.print_playerhands()

    def hit_script(self, hand):
        if self.balance >= hand.bet and self.roundx.split_count == 0:
            loop = True
            while loop:
                user_action = input("Press H for Hit, S for Stand, DD for Double-Down, or R for suRrender. ").upper()
                if user_action == "H" or user_action == "S" or user_action == "DD" or user_action == "R":
                    loop = False
                else:
                    print("Sorry, this is not a valid command.")
            print("")
            if user_action == "R":
                hand.surrender()
                print("You'll get back half of your bet: ${:,.2f}".format(hand.bet))
                print("")
                self.balance += hand.bet
            elif user_action == "DD":
                self.balance -= hand.bet
                hand.double_down(self.deck)
                self.roundx.print_playerhands()
            elif user_action == "S":
                hand.stand()
            elif user_action == "H":
                hand.hit(self.deck)
                self.roundx.print_playerhands()
                loop = True
                while hand.score() < 21 and loop:
                    loop2 = True
                    while loop2:
                        user_action = input("Press H for Hit, S for Stand, or DD for Double-Down. ").upper()
                        if user_action == "H" or user_action == "S" or user_action == "DD" or user_action == "R":
                            loop2 = False
                        else:
                            print("Sorry, this is not a valid command.")
                    print("")
                    if user_action == "DD":
                        self.balance -= hand.bet
                        hand.double_down(self.deck)
                        self.roundx.print_playerhands()
                        loop = False
                    elif user_action == "S":
                        hand.stand()
                        loop = False
                    elif user_action == "H":
                        hand.hit(self.deck)
                        self.roundx.print_playerhands()
                hand.stand()
        elif self.balance >= hand.bet and self.roundx.split_count > 0:
            loop = True
            while loop:
                user_action = input("Press H for Hit, S for Stand, or DD for Double-Down. ").upper()
                if user_action == "H" or user_action == "S" or user_action == "DD":
                    loop = False
                else:
                    print("Sorry, this is not a valid command.")
            print("")
            if user_action == "DD":
                self.balance -= hand.bet
                hand.double_down(self.deck)
                self.roundx.print_playerhands()
            elif user_action == "S":
                hand.stand()
            elif user_action == "H":
                hand.hit(self.deck)
                self.roundx.print_playerhands()
                loop = True
                while hand.score() < 21 and loop:
                    loop2 = True
                    while loop2:
                        user_action = input("Press H for Hit, S for Stand, or DD for Double-Down. ").upper()
                        if user_action == "H" or user_action == "S" or user_action == "DD":
                            loop2 = False
                        else:
                            print("Sorry, this is not a valid command.")
                    print("")
                    if user_action == "DD":
                        self.balance -= hand.bet
                        hand.double_down(self.deck)
                        self.roundx.print_playerhands()
                        loop = False
                    elif user_action == "S":
                        hand.stand()
                        loop = False
                    elif user_action == "H":
                        hand.hit(self.deck)
                        self.roundx.print_playerhands()
                hand.stand()
        elif self.balance < hand.bet and self.roundx.split_count == 0:
            loop = True
            while loop:
                user_action = input("Press H for Hit, S for Stand, or R for suRrender. ").upper()
                if user_action == "H" or user_action == "S" or user_action == "R":
                    loop = False
                else:
                    print("Sorry, this is not a valid command.")
            print("")
            if user_action == "R":
                hand.surrender()
                print("You'll get back half of your bet: ", hand.bet)
                print("")
                self.balance += hand.bet
            elif user_action == "S":
                hand.stand()
            elif user_action == "H":
                hand.hit(self.deck)
                self.roundx.print_playerhands()
                loop = True
                while hand.score() < 21 and loop:
                    loop2 = True
                    while loop2:
                        user_action = input("Press H for Hit, or S for Stand. ").upper()
                        if user_action == "H" or user_action == "S":
                            loop2 = False
                        else:
                            print("Sorry, this is not a valid command.")
                    print("")
                    if user_action == "S":
                        hand.stand()
                        loop = False
                    elif user_action == "H":
                        hand.hit(self.deck)
                        self.roundx.print_playerhands()
                hand.stand()
        else:
            loop = True
            while loop:
                user_action = input("Press H for Hit, or S for Stand. ").upper()
                if user_action == "H" or user_action == "S":
                    loop = False
                else:
                    print("Sorry, this is not a valid command.")
            print("")
            if user_action == "S":
                hand.stand()
            elif user_action == "H":
                hand.hit(self.deck)
                self.roundx.print_playerhands()
                loop = True
                while hand.score() < 21 and loop:
                    loop2 = True
                    while loop2:
                        user_action = input("Press H for Hit, or S for Stand. ").upper()
                        if user_action == "H" or user_action == "S":
                            loop2 = False
                        else:
                            print("Sorry, this is not a valid command.")
                    print("")
                    if user_action == "S":
                        hand.stand()
                        loop = False
                    elif user_action == "H":
                        hand.hit(self.deck)
                        self.roundx.print_playerhands()
                hand.stand()

    def settle_script(self):
        self.roundx.settle(self.deck)
        self.balance += self.roundx.winnings
        self.roundx.print_settle()

game = GameAction()
