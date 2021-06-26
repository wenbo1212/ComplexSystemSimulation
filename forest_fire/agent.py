from mesa import Agent
import numpy as np


class TreeCell(Agent):
    """
    A tree cell.

    Attributes:
        x, y: Grid coordinates
        condition: Can be "Fine", "On Fire", or "Burned Out"
        unique_id: (x,y) tuple.

    unique_id isn't strictly necessary here, but it's good
    practice to give one to each agent anyway.
    """

    def __init__(self, pos, model):
        """
        Create a new tree.
        Args:
            pos: The tree's coordinates on the grid.
            model: standard model reference for agent.
        """
        super().__init__(pos, model)
        self.pos = pos
        self.unique_id = pos
        self.condition = "Fine"
        self.starter_stage = model.start_stage
        print(pos, model)
        if self.model.distribution == 'uniform':
            self.flamebility = np.random.randint(2, 50)/100
        elif self.model.distribution == 'normal':
            self.flamebility = TreeCell.generateNormal(26, 13)
        elif self.model.distribution == 'bimodal':
            self.flamebility = TreeCell.generateBimodal(13, 38, 6.5)
        elif self.model.distribution == 'constant':
            self.flamebility = 1
        self.neighbor_on_fire = 0

    def variate_flamebility(self):
        if(self.model.distribution == "constant"):
            self.flamebility = 1
        else:
            self.flamebility = ((0.02*self.flamebility)+1)*self.flamebility

    def step(self):
        '''
        If the tree is on fire, spread it to fine trees nearby.
        '''
        if self.condition == "On Fire":
            for neighbor in self.model.grid.neighbor_iter(self.pos):
                if neighbor.condition == "Fine":
                    neighbor.neighbor_on_fire += 1
                    if(np.random.random() < (1-(1-neighbor.flamebility)**min(neighbor.neighbor_on_fire, 8))):
                        neighbor.condition = "On Fire"
            self.condition = "Burned Out"

        # Question: at each timestep, is there an inherent probability of catching on fire?
        # Does it result in logical dynamics?
        # Also, if looking at bond percolation: do not include this part
        elif self.condition == 'Fine' and not self.starter_stage:
            if (np.random.random() < ((1/(90*100)) * self.flamebility)):
                self.condition = 'On Fire'
#                 print('A fire started out of nowhere')
        self.variate_flamebility()

        # Cap flamebility at 1:
        if (self.flamebility > 1):
            self.flamebility = 1

    @staticmethod
    def generateNormal(mu, sigma):
        value = np.random.normal(mu, sigma)
        while(value < 0 or value > mu*2):
            value = np.random.normal(mu, sigma)
        return value/100

    @staticmethod
    def generateBimodal(mu1, mu2, sigma):
        if np.random.random() > 0.5:
            value = TreeCell.generateNormal(mu1, sigma)
        else:
            value = TreeCell.generateNormal(mu2, sigma)
        return value
