import networkx as nx
import numpy as np
import argparse
import random
import pandas as pd

#python non_pat_atty.py -f testfam.nx -p test_fam_profile.txt -c .25
def load_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output_prefix', type=str, default = 'NewFile')
    parser.add_argument('-f', '--pedigree_filepath', type=str)
    parser.add_argument('-c', '--probability', type=float, default = .01)
    parser.add_argument('-p', '--profile_filepath', type = str)
    return parser.parse_args()

def pot_parents(graph, u_indiv):
  sample_parents= []
  sex = nx.get_node_attributes(graph, name = 'sex')
  birth_year = nx.get_node_attributes(graph, name = 'birth_year')
  
  for i in graph.nodes():
    if sex[i] != 'female':
      if birth_year[i] == '*':
        sample_parents.append(i)
      elif 20 <= (int(birth_year[u_indiv]) - int(birth_year[i])) <= 50:
        sample_parents.append(i)
  return(sample_parents)

def non_paternity(graph, prob, output_name, profile_filepath):
  '''
  non_paternity takesa .nx file to silulate the probility of non-paternity events 
  ''' 
  count = 0 # count for non-paternity events
  probability = prob * 100
  rem_relations = [] # list of old parent child relations to remove
  add_relations = [] # list of new parent child relations to add

  new_pat = [f'{max([int(i) for i in graph.nodes]) + 1}']
  

  for indiv in graph.nodes: #For loop around each node(individual) in the graph pedigree
    cur_parents = list(graph.predecessors(indiv)) #initiaklizes current parents of individual
    
    # if statement checks if profile was submitted 
    #if profile_filepath != None: #checks for profile user input
    #  potential_parents = list(pot_parents(graph, profile_filepath)) + new_pat
    #else:
    potential_parents = pot_parents(graph, indiv) + new_pat #lists all nodes
    

    for i in cur_parents:
      if indiv in potential_parents:
        potential_parents.remove(indiv)
      if i in potential_parents:
        potential_parents.remove(i) #removes parents from potential parents list
        #print(i, 'was removed from',indiv, "'s potential parents")
    print(indiv,"potential parents:",potential_parents)
    #  First we will check if the individual is a founder (no parents found in nx.predecessor)
    if len(list(graph.predecessors(indiv))) == 0:
      continue
    elif len(list(graph.predecessors(indiv))) == 1:
      rep_pat = np.random.choice(potential_parents)
      paternal_event = np.random.choice([0, 1], size=1, p=[1-prob, prob]) # 0:true paternity 1:non paternity
      parent_1 = list(graph.predecessors(indiv))[0]
      if nx.get_node_attributes(graph, name='sex')[parent_1] == 'male':
        rep_pat = np.random.choice(potential_parents)
        print(f'{parent_1} is not the father of {indiv}. Their father is {rep_pat}')
        rem_relations.append((male_parent, indiv))
        add_relations.append((rep_pat, indiv))
        if rep_pat == new_pat[0]:
          new_pat = [str(int(new_pat[0]) + 1)] # increments the newPat and keeps it as a string         
        count += 1
        potential_parents.remove(f'{rep_pat}')
    else:
      paternal_event = np.random.choice([0, 1], size=1, p=[1-prob, prob]) # 0:true paternity 1:non paternity
      parent_1 = list(graph.predecessors(indiv))[0]
      parent_2 = list(graph.predecessors(indiv))[1]
      if nx.get_node_attributes(graph, name='sex')[parent_1] == 'male':
        male_parent = parent_1
        female_parent = parent_2
      else:
        male_parent = parent_2
        female_parent = parent_1
      if(paternal_event == 1): # If false then we test one parent connection, 
        rep_pat = np.random.choice(potential_parents)
        print(f'{male_parent} is not the father of {indiv}. Their parents are {rep_pat} and {female_parent}')
        rem_relations.append((male_parent, indiv))
        add_relations.append((rep_pat, indiv))
        if rep_pat == new_pat[0]:
          new_pat = [str(int(new_pat[0]) + 1)] # increments the newPat and keeps it as a string         
        count += 1
        #print(rep_pat)
        potential_parents.remove(f'{rep_pat}')
      else: # True paternity events means we fill the child and parent connection.
        pass
      
  print(f'number of non-paternity events: {count}')
  print(f'Probability of non-paternity event: {probability}%')
  graph.remove_edges_from(rem_relations)
  graph.add_edges_from(add_relations)
  nx.write_edgelist(graph, f'{output_name}.nx')

  
  return

if __name__== '__main__':
    user_args = load_args()

    u_output = user_args.output_prefix
    u_prob = user_args.probability
    
    u_graph = nx.read_edgelist(F'{user_args.pedigree_filepath}', create_using = nx.DiGraph())
    profiles = pd.read_csv(f'{user_args.profile_filepath}', sep='\t')
    sex_dict = dict(zip(profiles['profileid'].astype(str).to_numpy(), profiles['gender'].to_numpy()))
    age_dict = dict(zip(profiles['profileid'].astype(str).to_numpy(), profiles['birth_year'].to_numpy()))
    nx.set_node_attributes(u_graph, values=sex_dict, name="sex")
    nx.set_node_attributes(u_graph, values=age_dict, name="birth_year")

    non_paternity(u_graph, u_prob, u_output, profiles)
