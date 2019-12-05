#!/usr/bin/env python
# coding: utf-8
# author

import pdb
import numpy as np
import matplotlib.pyplot as plt
import time
import pickle

from collections import deque

from unityagents import UnityEnvironment

# Get the DDPG agent
from src.maddpg_agent import MAgent

def train(env,
          max_sim_time=10,
          min_performance=0.5,
          num_episodes=10,
          window_size=100,
          actor_local_save_filename=['actor_local_weights_0.pt',
                                     'actor_local_weights_1.pt'],
          actor_target_save_filename=['actor_target_weights_0.pt',
                                      'actor_target_weights_1.pt'],
          critic_local_save_filename=['critic_local_weights_0.pt',
                                      'critic_local_weights_1.pt'],
          critic_target_save_filename=['critic_target_weights_0.pt',
                                       'critic_target_weights_1.pt'],
          actor_local_load_filename=[],
          critic_local_load_filename=[],
          actor_target_load_filename=[],
          critic_target_load_filename=[],
          random_seed=12345):
    """Train agents using MADDPG Agent.

        Params
        ======
            env                         : Unity environment
            max_sim_time                : maximum number of time steps in an
                                          episode
            num_episodes(int)           : maximum number of episodes to use for
                                          training the agent
            window_size (int)           : the length of the running average
                                          window to compute the average score
            actor_local_save_filename   : the file where the local NN weights
                                          will be saved for each agent
            critic_local_save_filename  : the file where the target NN weights
                                          will be saved for each agent
            actor_target_save_filename  : the file where the local NN weights
                                          will be saved for each agent
            critic_target_save_filename : the file where the target NN weights
                                          will be saved for each agent
            actor_local_load_filename   : if given, the initial weights
                                          of the actor local NN for each agent
            critic_local_load_filename  : if given, the initial weights
                                          of the critic local NN for each agent
            actor_target_load_filename  : if given, the initial weights
                                          of the actor target NN for each agent
            critic_target_load_filename : if given, the initial weights
                                          of the critic target  NN for each agent
       """
    # Environments contain **_brains_** which are responsible for deciding
    # the actions of their associated agents.
    # Here we check for the first brain available,
    # and set it as the default brain we will be controlling from Python.

    # get the default brain
    brain_name = env.brain_names[0]
    brain = env.brains[brain_name]
    # reset the environment
    env_info = env.reset(train_mode=True)[brain_name]

    # number of agents in the environment
    num_agents = len(env_info.agents)
    print('Number of agents:', num_agents)
    # number of actions
    action_size = brain.vector_action_space_size
    print('Number of actions:', action_size)
    states = env_info.vector_observations
    state_size = states.shape[1]
    print('States have length:', state_size)

    pdb.set_trace()
    print('There are {} agents. Each observes a state with length: {}'.
          format(num_agents, state_size))
    print('The state for the first agent looks like:', states[0])
    # Create the agents
    agent = MAgent(state_size, action_size, num_agents, random_seed)

    # Load weights if they exist
    # agent.load(actor_local_load_filename,
    #           actor_target_load_filename,
    #           critic_local_load_filename,
    #           critic_target_load_filename)

    # Loop over number of episodes
    # Storage for scores
    scores = []
    # Storage for the max scores
    max_scores = []
    # Moving average max scores storage
    scores_window = deque(maxlen=window_size)
    for e in range(num_episodes):
        # initialize the score
        score = np.zeros(num_agents)
        # reset the environment
        env_info = env.reset(train_mode=True)[brain_name]
        # get the current state
        states = env_info.vector_observations
        tstart = time.time()
        for sim_t in range(max_sim_time):
            print("""Simulation time: {}""".format(str(sim_t)), end='\r')
            # select an action for each agent
            action = agent.act(states, add_noise=True)
            # Combine the actions and send it to the environment
            # send the action to the environment
            env_info = env.step(action)[brain_name]
            # get the next state
            next_states = env_info.vector_observations
            # get the reward
            rewards = env_info.rewards
            # see if episode has finished
            dones = env_info.local_done

            # update the replay buffer and train if necessary
            agent.step(states,
                       action,
                       rewards,
                       next_states,
                       dones,
                       sim_t)
            # update the score
            score += rewards
            # roll over the state to next time step
            states = next_states
            # exit loop if episode finished
            if np.any(dones):
                break
        ttotal = time.time() - tstart
        # Append the scores
        scores.append(score)
        scores_window.append(np.max(score))
        max_moving_score = np.mean(scores_window)
        max_scores.append(max_moving_score)
        # Check if the minimum threshold for the reward has been achieved
        if (e+1) % 1 == 0:
            print("""Episode: {} Episode Duration: {:.0f}s min_score: {:.2f} max_score: {:.2f} moving_average_max_score: {:.2f}""".format(
                (e+1), ttotal, float(np.min(score)), float(np.max(score)), float(max_moving_score)))
        if max_moving_score >= min_performance and (e+1) > window_size:
            print('\nEnvironment solved in {:d} episodes! \tMoving Average Max Score: {:.2f}'.format((e+1), float(max_moving_score)))
            break

        agent.save(actor_local_save_filename,
                   actor_target_save_filename,
                   critic_local_save_filename,
                   critic_target_save_filename)

    # Save the scores in case of any issues
    with open('training_results.pkl', 'wb') as f:
        pickle.dump([e, max_scores, scores], f)

    # When finished, you can close the environment.
    return(e, max_scores, scores)


def run(env,
        num_episodes=1,
        sim_max_time=1000,
        actor_local_load_filename='actor_local_weights.pt'):
    """
        Params
        ======
            env : Unity environment
            num_episodes(int)           : number of episodes to use
                                          to evaluate the agent
            sim_max_time                : maximum time steps in an episode
            actore_local_load_filename  : the file that contains
                                          the weights of the actor NN
        """
    # Environment Setup
    brain_name = env.brain_names[0]
    brain = env.brains[brain_name]
    # Load the
    env_info = env.reset(train_mode=False)[brain_name]
    # number of actions
    num_agents = len(env_info.agents)
    action_size = brain.vector_action_space_size
    # Get the state space information
    states = env_info.vector_observations
    state_size = states.shape[1]
    # Create the agent with the trained weights
    agent = MAgent(state_size, action_size, num_agents, 12345)
    agent.load(actor_local_load_filename)

    # Create the scores storage
    scores = []
    for e in range(num_episodes):
        # initialize the score
        score = np.zeros(num_agents)
        # reset the environment
        env_info = env.reset(train_mode=False)[brain_name]
        # get the current state
        states = env_info.vector_observations
        for t in range(sim_max_time):
            # select an action
            action = agent.act(states, add_noise=False)
            # send the action to the environment
            env_info = env.step(action)[brain_name]
            # get the next state
            next_states = env_info.vector_observations
            # get the reward
            rewards = env_info.rewards
            # see if episode has finished
            dones = env_info.local_done
            score += rewards
            # roll over the state to next time step
            states = next_states
            # exit loop if episode finished
            if np.any(dones):
                break

        # Append the scores
        scores.append(score)
        return(scores)


def main():
    # Load the unity app
    env = UnityEnvironment(file_name="Tennis.app")
    num_episodes,  moving_max_scores, scores = train(env, num_episodes=2500)
    print("Done training")

    # Plot the training scores
    max_scores = [np.max(m) for m in scores]
    plt.ion()
    fig = plt.figure()
    _ = fig.add_subplot(111)
    plt.plot(np.arange(len(max_scores)), max_scores)
    plt.plot(np.arange(len(moving_max_scores)), moving_max_scores)
    plt.ylabel('Max and Moving Average of Max Scores ')
    plt.xlabel('Episode #')
    plt.legend(['Max Score', 'Moving Average of Max Score'], loc='upper left')
    plt.show()

    scores = run(env,
                 num_episodes=1,
                 actor_local_load_filename='actor_local_weights.pt')
    print("Done simulating")
    env.close()