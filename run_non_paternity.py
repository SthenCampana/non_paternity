import networkx as nx
import numpy as np
import argparse
import random
import pandas as pd

#Example: python non_pat_atty.py -f test_fam.nx -p test_fam_profile.txt -c .25

#Created flags for user input
def load_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output_prefix', type=str, default = 'NewFile')
    parser.add_argument('-f', '--pedigree_filepath', type=str)
    parser.add_argument('-c', '--probability', type=float, default = .01)
    parser.add_argument('-p', '--profile_filepath', type = str)
    return parser.parse_args()

#Finds nodes that are male and within a 20-50 year age range of an individuals conception and puts them in a list. 
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
  if len(sample_parents) != 0:
    sample_parents = [np.random.choice(sample_parents)]
  return(sample_parents)


#Iterates through each individual. each iteration has a chance (-c, default 1%) of experiencing a non_paternity. 
#If a non-paternity happens, a new father is chosen from a pool of potential parents
def non_paternity(graph, prob, output_name):
  '''
  non_paternity takes a .nx file to simulate the probility of non-paternity events. 
  probability can be specified 
  output file name can be specified
  ''' 
  count = 0 # count for non-paternity events
  probability = prob * 100 # to display the probility
  rem_relations = [] # list of old parent child relations to remove
  add_relations = [] # list of new parent child relations to add
  new_pat_bydict = {}
  new_pat_sexdict = {}
  new_pat = [f'{max([int(i) for i in graph.nodes]) + 1}'] # creates a random individual outside of the pedigree
  

  for indiv in graph.nodes: #For loop around each node(individual) in the graph pedigree
    
    cur_parents = list(graph.predecessors(indiv)) #initializes current parents of individual
    
    # if statement checks if profile was submitted 
    #if profile_filepath != None: #checks for profile user input
    #  potential_parents = list(pot_parents(graph, profile_filepath)) + new_pat
    #else:                      [1,3]             + [16]  = [1,3,16] 
    potential_parents = pot_parents(graph, indiv) + new_pat #lists all nodes
    paternal_event = np.random.choice([0, 1], size=1, p=[1-prob, prob]) # 0:true paternity 1:non paternity
    if paternal_event == 1:
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
        parent_1 = list(graph.predecessors(indiv))[0]
        if nx.get_node_attributes(graph, name='sex')[parent_1] == 'male':
          rep_pat = np.random.choice(potential_parents)
          print(f'{parent_1} is not the father of {indiv}. Their father is {rep_pat}')
          rem_relations.append((male_parent, indiv))
          add_relations.append((rep_pat, indiv))
          if rep_pat == new_pat[0]:
            new_pat_bydict[new_pat[0]] = graph.nodes[female_parent]["birth_year"]
            new_pat_sexdict[new_pat[0]] = 'male'
            new_pat = [str(int(new_pat[0]) + 1)] # increments the newPat and keeps it as a string         
          count += 1
          potential_parents.remove(f'{rep_pat}')
      else:
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
            new_pat_bydict[new_pat[0]] = graph.nodes[female_parent]["birth_year"]
            new_pat_sexdict[new_pat[0]] = 'male'
            print('i worked')
            new_pat = [str(int(new_pat[0]) + 1)] # increments the newPat and keeps it as a string         
          count += 1
          #print(rep_pat)
          potential_parents.remove(f'{rep_pat}')
        else: # True paternity events means we fill the child and parent connection.
          pass
      print(rep_pat, type(rep_pat), new_pat, type(new_pat))
      if rep_pat == new_pat:
        new_pat_bydict[new_pat] = graph.nodes[female_parent]["birth_year"]
        new_pat_sexdict[new_pat] = 'male'
        #example {14 : 1990, 15 : 2000}
    else:
      pass 
  print(f'number of non-paternity events: {count}')
  print(f'Probability of non-paternity event: {probability}%')
  graph.remove_edges_from(rem_relations)
  graph.add_edges_from(add_relations)
  nx.set_node_attributes(graph, new_pat_sexdict, name = "sex")
  nx.set_node_attributes(graph, new_pat_bydict, name = "birth_year")
  nx.write_edgelist(graph, f'{output_name}.nx')

  
  return

if __name__== '__main__':
    user_args = load_args()

    u_output = user_args.output_prefix
    u_prob = user_args.probability
    
    u_graph = nx.read_edgelist(F'{user_args.pedigree_filepath}', create_using = nx.DiGraph())
    profiles = pd.read_csv(f'{user_args.profile_filepath}', sep='\t')
    sex_dict = dict(zip(profiles['ID'].astype(str).to_numpy(), profiles['Sex'].to_numpy()))
    age_dict = dict(zip(profiles['ID'].astype(str).to_numpy(), profiles['Birth_Year'].to_numpy()))
    nx.set_node_attributes(u_graph, values=sex_dict, name="sex")
    nx.set_node_attributes(u_graph, values=age_dict, name="birth_year")

    non_paternity(u_graph, u_prob, u_output)
