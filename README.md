# CS5100 Team 9 FAI Project

## Adaptive Difficulty in Games: Leveraging Reinforcement Learning for Player-Driven Immersion
This is our final project source code for CS5100 Fall 2023 under Professor Rajagopal Venkatesaramani. We proposed a project that aims to use Reinforcement Learning (RL) to create games that adapt to each player’s unique strengths, weaknesses, and preferences of players. We also proposed an Adversarial RL system to test both "player" and "environment" working together, where the player is trying to clear levels with
ease whereas the "environment" is continuously learning the "player"s skills to make levels more difficult. The advantage of this system is twofold, one being making the "player" agent robust against any environment and second is to automate game testing without manual labour.

Run the following files for variations of the system:
- AdverseGame.py : This file is for running the platform generator agent and the player agent together in an adverse way.The platforms are initially set randomly. The player agent learns to traverse platoforms and the platform agent from the player actions.
- Game.py : This file starts the game where the platform generator agent run. The platforms are initially set randomly.The user can play the game using keyboard inputs.The platform agent learns from player actions and makes changes accordingly.
- playerFixelLevel1.py,playerFixedLevel2.py : These files run the player agent on fixed platforms in every game loop.
- playerRandomLevel.py : This file runs the player agent on random platforms in every game loop.

Install requirements with the command:
```
pip install -r requirements.txt
```


