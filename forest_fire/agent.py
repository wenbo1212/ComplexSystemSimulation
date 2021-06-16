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
        self.condition = "Fine"
        self.flamebility=np.random.randint(2,50)/100
        self.neighbor_on_fire=0

    def variate_flamebility(self):
        self.flamebility=(self.flamebility+1)*self.flamebility

    def step(self):
        """
        If the tree is on fire, spread it to fine trees nearby.
        """
        if self.condition == "On Fire":
            for neighbor in self.model.grid.neighbor_iter(self.pos):
                if neighbor.condition == "Fine":
                    neighbor.neighbor_on_fire+=1
                    if(np.random.random()<neighbor.flamebility+0.125*neighbor.neighbor_on_fire):
                        neighbor.condition = "On Fire"
            self.condition = "Burned Out"
        self.variate_flamebility()