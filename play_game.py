import numpy as np
from matplotlib import pyplot as plt

from Risk_board_game import Risk, get_move_list


def step(r, player, prob_random_move = 1.0, model=None, animate=True):
    
    if model is None and prob_random_move != 1.0:
        raise ValueError("Without a model, can only make 100% random moves.")
    
    results, flag = get_move_list(r)
    
    print(list(np.roll(r.get_num_territories_owned(), player)))
    

    if model is not None:
        print(list(np.roll(get_winning_chances(r, model), player)))
    
    if animate:
        plt.clf()
        r.draw_map(player)
        plt.pause(0.001)
    
    if flag:
        print("END PLAYER {} TURN".format(player))
        player = (player + 1) % 3
        
        
    if np.random.rand() < prob_random_move:
        """
        choose a move at random
        """
        i = np.random.choice(range(len(results)))
    
    
    else:
        """
        choose the move with the highest associated winning odds
        """
        winning_odds = [get_winning_chances_stochastic(a, model) for a in results]
        my_winning_odds = [i[0] for i in winning_odds]
        #print(my_winning_odds)
        i = np.argmax(my_winning_odds)
    
    selected_move = results[i]
    boards = [i[0] for i in selected_move]
    probs = [i[1] for i in selected_move]
    
    r = np.random.choice(boards, 1, p=probs)
    r = r[0]
    
    return r, player
    

from torch_geometric.data import Data
import torch

edge_list = list(Risk().map.edges())
# include both directions of edges
edge_list += [tuple(reversed(i)) for i in edge_list]

edge_index = torch.tensor(edge_list, dtype=torch.long).t().contiguous()

def encode(r):
    a,b = r.encode()
    d = [np.concatenate([a,i]) for i in b]
    x = torch.tensor(d, dtype=torch.float)
    
    return Data(x=x, edge_index=edge_index)


#device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
#model = Net().to(device)

def get_winning_chances(r, model):
    d = encode(r)
    d.batch = torch.tensor([0 for _ in d.x])
    
    res = model(d).exp().detach()
    res = res.numpy().ravel()
    
    return res

"""
for when the outcome of your move is stochastic.
this averages your expected return over the possible outcomes
"""
def get_winning_chances_stochastic(outcomes, model):
    res = 0
    
    for tmp in outcomes:
        r, prob = tmp
        res += get_winning_chances(r, model) * prob
        
    return res
    


def play_game(_=None):
    player = 0
    
    r = Risk()
    
    board_list = []
    player_turn_list = []
    while r.check_winner() is None:
        board_list.append(encode(r))
        player_turn_list.append(player)
        
        r, player = step(r, player)
        

    
    
    print("PLAYER {} WINS!".format(player))
    
    
    winner = one_hot_encoding(player, 3)
    
    winner_prediction_gt = [np.roll(winner, -i) for i in player_turn_list]
    
    # add the correct outcome to the data object
    for d,y in zip(board_list, winner_prediction_gt):
        #d.y = torch.LongTensor([np.nonzero(y)[0][0]])
        d.y = torch.tensor([y]).float()

    return board_list




#board_list = play_game()

"""
from multiprocessing import Pool
p = Pool(1)

if __name__ == '__main__':

    board_list = []
    for i in p.map(play_game, range(1)):
        board_list += i
"""

board_list = []
for i in range(1):
    board_list += play_game()







