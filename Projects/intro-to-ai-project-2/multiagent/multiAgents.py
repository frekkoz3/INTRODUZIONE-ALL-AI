# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        actualPos = currentGameState.getPacmanPosition()
        actualFood = currentGameState.getFood()
        actualCapsules = currentGameState.getCapsules()
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newGhostPositions = successorGameState.getGhostPositions()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
        newCapsules = successorGameState.getCapsules()
        "*** YOUR CODE HERE ***"

        # BASE CASE 
        
        if successorGameState.isWin():
            return float('inf')
        if successorGameState.isLose():
            return -float('inf')
        
        eval = 0

        # GHOSTS

        # we should implement an evaluation that tells us when we actually eat a ghost

        danger_ghosts, dg_weight = 0, 3
        scared_ghosts_eatable, sge_weight = 0, 5
        scared_ghosts_non_eatable, sgne_weight = 0, 3
        for pos, time in zip(newGhostPositions, newScaredTimes):
          danger_ghosts += ((util.manhattanDistance(pos, newPos) <= 3) and time == 0)
          scared_ghosts_eatable += ((util.manhattanDistance(pos, newPos) < time) and time > 0)
          scared_ghosts_non_eatable += ((util.manhattanDistance(pos, newPos) > time) and time > 0)

        eval -= danger_ghosts * dg_weight
        eval += scared_ghosts_eatable * sge_weight
        eval += scared_ghosts_non_eatable * sgne_weight

        # CAPSULESE

        if len(actualCapsules) > len(newCapsules):
            eval += float('inf')

        # FOOD

        min_distance, md_weight = float('inf'), 1
        if len(actualFood.asList()) == len(newFood.asList()): # if i haven't eat
          for food in newFood.asList():
            min_distance = min(min_distance, util.manhattanDistance(food, newPos))

          def f(dist):
              return 1 / dist
          
          eval += f(min_distance) * md_weight
        else:
            eval += 5

        # STOP

        s_weight = 1
        eval -= (action == 'Stop')*s_weight

        # ALLEY

        # we can think a way to prevent pacman to go into the alley if possible
        
        return eval

def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        "*** YOUR CODE HERE ***"
        def minimimax(gameState, agentindex, depth):
            # case base 
            if depth == 0 or gameState.isWin() or gameState.isLose():
                return [self.evaluationFunction(gameState)]
            # general params
            next_agent = (agentindex + 1)%gameState.getNumAgents()
            possible_action = gameState.getLegalActions(agentindex)
            action_taken = ''
            rew = float('inf')
            # ghosts
            if agentindex > 0:
                for act in possible_action:
                    t = rew
                    rew = min(rew, minimimax(gameState.generateSuccessor(agentindex, act), next_agent, depth-1)[0])
                    action_taken = action_taken if t == rew else act
            # pacman
            else:
                rew = -rew
                for act in possible_action:
                    t = rew
                    rew = max(rew, minimimax(gameState.generateSuccessor(agentindex, act), next_agent, depth-1)[0])
                    action_taken = action_taken if t == rew else act
            return rew, action_taken
        rew = minimimax(gameState, 0, self.depth * gameState.getNumAgents())
        return rew[1]

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        def minimimax_alphabetapruning(gameState, agentindex, depth, alpha, beta):
            # case base 
            if depth == 0 or gameState.isWin() or gameState.isLose():
                return [self.evaluationFunction(gameState)]
            # general params
            next_agent = (agentindex + 1)%gameState.getNumAgents()
            possible_action = gameState.getLegalActions(agentindex)
            action_taken = ''
            rew = float('inf')
            # ghosts
            if agentindex > 0:
                for act in possible_action:
                    t = rew
                    rew = min(rew, minimimax_alphabetapruning(gameState.generateSuccessor(agentindex, act), next_agent, depth-1, alpha, beta)[0])
                    action_taken = action_taken if t == rew else act
                    beta = min(beta, rew)
                    if rew < alpha:
                      return rew, action_taken

            # pacman
            else:
                rew = -rew
                for act in possible_action:
                    t = rew
                    rew = max(rew, minimimax_alphabetapruning(gameState.generateSuccessor(agentindex, act), next_agent, depth-1, alpha, beta)[0])
                    action_taken = action_taken if t == rew else act
                    alpha = max(alpha, rew)
                    if rew > beta:
                        return rew, action_taken
                    
            return rew, action_taken
        rew = minimimax_alphabetapruning(gameState, 0, self.depth * gameState.getNumAgents(), alpha=-float('inf'), beta=float('inf'))
        return rew[1]
        
        

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        def expectimax(gameState, agentindex, depth):
            # case base 
            if depth == 0 or gameState.isWin() or gameState.isLose():
                return [self.evaluationFunction(gameState)]
            # general params
            next_agent = (agentindex + 1)%gameState.getNumAgents()
            possible_action = gameState.getLegalActions(agentindex)
            action_taken = ''
            # ghosts
            if agentindex > 0:
                rew = 0
                for act in possible_action:
                    t = rew
                    rew += expectimax(gameState.generateSuccessor(agentindex, act), next_agent, depth-1)[0]
                rew = rew / len(possible_action)
            # pacman
            else:
                rew = -float('inf')
                for act in possible_action:
                    t = rew
                    rew = max(rew, expectimax(gameState.generateSuccessor(agentindex, act), next_agent, depth-1)[0])
                    action_taken = action_taken if t == rew else act
            return rew, action_taken
        rew = expectimax(gameState, 0, self.depth * gameState.getNumAgents())
        return rew[1]

def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    # Useful information you can extract from a GameState (pacman.py)
    pacman = currentGameState.getPacmanPosition()
    actualFood = currentGameState.getFood()
    actualCapsules = currentGameState.getCapsules()
    ghostsPositions = currentGameState.getGhostPositions()
    ghostsStates = currentGameState.getGhostStates()
    scaredTimes = [ghostState.scaredTimer for ghostState in ghostsStates]

    # BASE CASE

    if currentGameState.isWin():
      return float('inf')
    if currentGameState.isLose():
      return -float('inf')

    eval = currentGameState.getScore() + \
            (10/min([util.manhattanDistance(pos, pacman) for pos in actualFood.asList()])) - \
            (5/min([util.manhattanDistance(g.getPosition(), pacman) if g.scaredTimer == 0 else float('inf') for g in ghostsStates]))

    return eval

# Abbreviation
better = betterEvaluationFunction

