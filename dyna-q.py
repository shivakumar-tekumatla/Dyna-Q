import numpy as np
import matplotlib.pyplot as plt
from itertools import product
from collections import defaultdict
import random

class Env:
    def __init__(self,environment,start,goal) -> None:
        self.start = start
        self.goal  = goal
        self.environment = environment
        self.actions = {"r":(0,1),
                        "l":(0,-1),
                        "d":(1,0),
                        "u":(-1,0)}  # basically there are four actions ,and these are represented as keys and the values re nothing but the indices by which state will change 
        self.state = self.start # by default the state is start, and it will be updated over the time 

        self.x_limit,self.y_limit = self.environment.shape
        self.states = np.array([state for state in product(np.arange(self.x_limit),np.arange(self.y_limit ))]) # every index of the environment! 
        self.tuple_sum = lambda state,action:tuple(map(sum,zip(state,self.actions[action]))) #does tuple sum 
        pass
    def is_terminal(self,state):
        # state is in the form of indices
        # only goal is treated as the terminal state. When the agent reaches the goal, it return to the start state,and begins new episode 

        if state == self.goal:
            return True 
        return False
    
    def next_state(self,state,action):
        # For each of the four actions, the agent deterministically moves to the neighboring corresponding states
        # except when movement is blocked by an obstacle or the edge of the maze, in which case the agent 
        # remains where it is 

        nxt_state = self.tuple_sum(state,action)
        # check if next state is inside boundary or is not an obstacle 

        if nxt_state in map(tuple,self.states) and self.environment[state] == 0:
            self.state = nxt_state
            return nxt_state
        else:
            self.state = state
            return state 
        
    def reward(self,state,action):
        # Reward is zero on all transitions, except those into the goal state, on which it is +1.
        nxt_state = self.next_state(state,action)
        if nxt_state == self.goal:
            return 1 
        else:
            return 0
    def transition(self,state,action):
        return self.reward(state,action),self.next_state(state,action)
    def reset(self):
        # Whenever the robot transitioned to terminal state , reset the position to start position 
        self.state = self.start
        return  self.state 
class DynaQ:
    def __init__(self,env,gamma,alpha,n,epsilon) -> None:
        self.env = env
        self.gamma = gamma
        self.alpha = alpha
        self.n = n  # number of episodes
        pass
    def initialize(self):
        Q = {}
        Model = defaultdict(dict)
        for state in self.env.states:
            state = tuple(state)
            #checking is that action can be taken because of the boundaries 
            Q[state] = {action:0 for action in self.env.actions}# if self.env.tuple_sum(state,action) in map(tuple,self.env.states) }
            # Model[state] = {action:(0,None) for action in self.env.actions} # initially we do not know the model
        return Q,Model
    
    def dynaQ(self):
        Q,Model = self.initialize()
        # print(Model)
        # Loop Forever
        while True:
            S = self.env.state # (a) S current (non-terminal) state
            A = self.epsilon_greedy(S,Q) # (b) A "-greedy(S,Q)
            R,S_ = self.env.transition(S,A)# (c) Take action A; observe resultant reward, R, and state, S_
            Q[S][A] = Q[S][A] + self.alpha*(R+self.gamma*max(Q[S_].values())-Q[S][A])# (d) Update Q like you do in Q-learning
            Model[S][A] =R,S_ # (e) Model(S,A) R, S0 (assuming deterministic environment)
            #(f) Loop repeat n times:
            for episode in range(self.n):
                S = random.sample(Model.keys(),1)[0] # S - random previously observed state
                A = random.sample(Model[S].keys(),1)[0] # A -  random action previously taken in S
                R,S_ = Model[S][A] # R, S_ from Model(S,A)
                Q[S][A] = Q[S][A] + self.alpha*(R+self.gamma*max(Q[S_].values())-Q[S][A])# Update Q like you do in Q-learning
            if self.env.is_terminal(self.env.state):
                break
        return Q, Model

    def epsilon_greedy(self,S,Q):
        if np.random.random()<=self.epsilon: 
                # Explore 
                A = np.random.choice(list(Q[S]))
        else:
            #Exploit
            A = max(Q[S], key=Q[S].get, default=None)
        return A
def main():
    # actions = [""]
    environment = np.loadtxt("maze.txt")
    start = (2,0)
    goal = (0,8)
    gamma = 0.95
    alpha = 0.1
    epsilon = 0.01
    n_episodes = 1000
    env = Env(environment,start,goal)

    T = DynaQ(env,gamma,alpha,n_episodes,epsilon)
    T.dynaQ()


if __name__ == "__main__":
    main()