import copy
from yatzy import Yatzy

# A Yatzy game in which a player trains the neural nets
class TrainingGame(Yatzy):
    def __init__(self, player):
        super().__init__([ player ])
        self.player = player
    
    def playN(self, N):
        self.average_score = 0
        self.high_score = 0
        game_scores = []
        for current_play in range(1, N + 1):
            score = self.play(current_play, N)
            game_scores.append(score)
            divisor = 100 if len(game_scores) > 100 else len(game_scores)
            self.average_score = sum(game_scores[len(game_scores) - 100:]) / divisor
            if self.high_score < score:
                self.high_score = score
            print('\tcurrent average score:', self.average_score)

    def play(self, current_play = 1, N = 1):
        self.history.clear_history()
        self.history.initiate_game()
        self.player.reset_board()

        print("TRAINING GAME", current_play, "/", N, '(played by', 'model)' if self.player.strategy.strategy == 'model' else 'random generator)')
        for round in range(1, 16):
            print("\tROUND", round)
            self.history.game.initiate_play(self.player.score_fields)

            # the player throws all dice
            self.throw_dice([ 0, 1, 2, 3, 4 ])

            print("\t\tthrow 1", self.die)

            for throw_number in range(1, 3):
                # the result is added to the history
                self.history.game.play.add_dice(self.die)

                # the player makes a decision to throw dice based on the result
                decision = self.player.decide_dice_throw(throw_number, self.die)

                # throw dice again according to desicion
                self.throw_dice(decision)

                print("\t\tthrow", throw_number + 1, self.die)

            # the last result is added to the history
            self.history.game.play.add_dice(self.die)
            
            # the player makes a decision about what field on the score board should be filled with what value
            field_index, score = self.player.decide_score_logging(self.die)
            print("\t\tput", score, "points on", self.idx_to_name(field_index))

            # log the score
            self.set_score_field(self.player, field_index, score)

            # the chosen scoring is saved in the history
            self.history.game.play.add_scoring(field_index, score)

            # save play to history
            self.history.game.commit_play()

        total_score = self.count_points(self.player)

        print("\ttotal score:", total_score)

        self.history.commit_game(total_score)

        # train the players models with history
        self.player.strategy.diceModel.train(self.history)
        self.player.strategy.scoreModel.train(self.history)

        return total_score