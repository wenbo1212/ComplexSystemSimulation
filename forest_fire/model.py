from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import Grid
from mesa.time import RandomActivation
import numpy as np
from .agent import TreeCell


class ForestFire(Model):
    """
    Simple Forest Fire model.
    """

    def __init__(self, height, width, density, env, distr, start_cells, start_stage):
        '''
        Create a new forest fire model.

        Args:
            height, width: The size of the grid to model
            density: What fraction of grid cells have a tree in them.
        '''
        # Set up model objects
        self.distribution = distr
        self.schedule = RandomActivation(self)
        self.grid = Grid(height, width, torus=False)
        self.datacollector = DataCollector({"Fine": lambda m: self.count_type(m, "Fine"),
                                            "On Fire": lambda m: self.count_type(m, "On Fire"),
                                            "Burned Out": lambda m: self.count_type(m, "Burned Out")
                                            })
        self.environment = env
        self.time = 0
        self.flamebility_over_time = []
        self.burnt_trees = []
        self.anims = []
        self.hist = []
        self.start_cells = start_cells
        self.start_stage = start_stage
        agent_count = 0
        self.canvas = (height, width)
        # Place a tree in each cell with Prob = density
        for x in range(width):
            for y in range(height):
                if self.random.random() < density:
                    # Create a tree
                    new_tree = TreeCell((x, y), self)

                    if(start_cells):
                        if(x == 0):
                            new_tree.condition = "On Fire"
                    elif(start_stage):
                        # # Some trees can already be on fire in the first step:
                        # Changed to 1/90, assuming 90 days for the simulation
                        if(np.random.random() < new_tree.flamebility*(1/90)):
                            new_tree.condition = "On Fire"

                    self.grid[x][y] = new_tree
                    self.schedule.add(new_tree)
                    agent_count += 1
        self.running = True
        self.datacollector.collect(self)

    def step(self):
        '''
        Advance the model by one step.
        '''
        self.burnt_trees.append(self.count_type(self, 'Burned Out'))
        self.flamebility_over_time.append(self.mean_flamebility(self))
        self.schedule.step()
        self.datacollector.collect(self)
        self.time += 1
        # Halt if no more fire
        if (self.time == 90):
            self.running = False

    @staticmethod
    def count_type(model, tree_condition):
        '''
        Helper method to count trees in a given condition in a given model.
        '''
        count = 0
        for tree in model.schedule.agents:
            if tree.condition == tree_condition:
                count += 1
        return count

    @staticmethod
    def mean_flamebility(model):
        '''
        Helper method to count the mean flamebility in the model.
        '''
        flamebility = 0
        nr = 0
        for tree in model.schedule.agents:
            if (tree.condition == 'Fine'):
                flamebility += tree.flamebility
                nr += 1
        if(nr == 0):
            return 0
        else:
            return flamebility / nr

    @staticmethod
    def statistics(model, frames, hists):
        image = np.zeros(model.canvas)
        data = []
        for tree in model.schedule.agents:
            if tree.condition == 'Burned Out':
                image[tree.pos] = -1
            elif tree.condition == 'Fine':
                image[tree.pos] = min(tree.flamebility, 1.0)
                data.append(tree.flamebility)
            elif tree.condition == 'On Fire':
                image[tree.pos] = 2
        frames.append(image)
        hists.append(data)
