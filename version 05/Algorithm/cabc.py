
import copy
import random
import time
import numpy as np
import pandas as pd
from datetime import datetime
from bee import Bee

class Classic_Artificial_Bee_Colony:

    def __init__(self, run_id, cpu_time_limit, employed_bees_num, nK, nI, Capacity, Profits, Weights, onlooker_bees_num, max_try_improve, pc_onePoint, pc_uniForm, pm, k_tournomet, selection_type, crossover_type, result_file_name):
        
        self.run_id = run_id
        self.cpu_time_limit = cpu_time_limit
        self.employed_bees_num = employed_bees_num
        self.nK = nK
        self.nI = nI
        self.capacity = Capacity
        self.profits = np.array(Profits)
        self.weights = np.array(Weights)
        self.onlooker_bees_num = onlooker_bees_num
        self.max_try_improve = max_try_improve
        self.pc_onePoint = pc_onePoint
        self.pc_uniForm = pc_uniForm
        self.pm = pm
        self.k_tournoment = k_tournomet
        self.selection_type = selection_type
        self.crossover_type = crossover_type
        self.result_file_name = result_file_name
        self.bees = []

    def optimize(self):
        self.initialize_population()

        best_fitnesses_of_iteration = []
        best_fitnesses_so_far = []
        best_fitness_so_far = 0
        best_bee_so_far = Bee
        last_best_fitness_of_itration = 0
        time_number_list = []
    
        iteration_num = 0
        best_fitness_iteration_num = iteration_num # getting the last iteration that fitness ever updated

        currentTime = datetime.now().strftime("%H:%M:%S")
        print(f"run_id -> {self.run_id}: {currentTime}")
    
        start_t = time.time() # the start time of algorithm
        end_t = time.time()
        end_t_best_so_far = time.time()
        elapsed_time = 0

        while(elapsed_time<self.cpu_time_limit):

            result = open(self.result_file_name, 'a')    
            iteration_num+=1
            
            self.employed_bees_phase()
            self.onlooker_bees_phase()
            
            best_bee_of_iteration, best_fitness_of_iteration = self.find_best_bee()

            if(best_fitness_of_iteration > best_fitness_so_far):
                best_fitness_so_far = best_fitness_of_iteration
                best_bee_so_far = best_bee_of_iteration
                print(f"best fitness so far: {best_fitness_so_far}")
                best_fitness_iteration_num = iteration_num
                end_t_best_so_far = time.time()
              
            if (last_best_fitness_of_itration != best_fitness_of_iteration):
                end_t = time.time()
                elapsed_best_updated = end_t - start_t
                time_number_list.append(elapsed_best_updated)
                best_fitnesses_of_iteration.append(best_fitness_of_iteration)
                best_fitnesses_so_far.append(best_fitness_so_far)                
                last_best_fitness_of_itration = best_fitness_of_iteration  
                
            self.scout_bees_phase()            

            current_time = time.time()
            elapsed_time = current_time-start_t # calculating the total time for checking limitation
                            
            result.close()    

        best_fitness_time = end_t_best_so_far - start_t

        return best_fitnesses_of_iteration, best_fitnesses_so_far, best_bee_so_far, best_fitness_so_far, iteration_num, best_fitness_iteration_num, best_fitness_time, time_number_list

    def initialize_population(self):
        # making each random solution -> employed bees
        # each random solution is made by randomly choose answers, and make them 1, until it stays feasible

        for _ in range(self.employed_bees_num):
            bee = self.make_a_bee()
            self.bees.append(bee)

    def employed_bees_phase(self):
          
        # we try for improvement one time for each bee, if change happens we add one to improvement-try property of that bee
        for bee in self.bees:
            change_flag = self.try_for_improvement(bee)
            
            if(change_flag == False): 
                bee.try_improve += 1

    def onlooker_bees_phase(self):
        # by rolette wheel precedure we do "onlooker_bees_num" times cross_over and mutation,
        # on solution that employed bees have made
        
        for _ in range(self.onlooker_bees_num):
            
            if (self.selection_type == "Roulette Wheel"):
                # selecting the bee by roulette wheel
                bee = self.roulette_wheel()

            elif(self.selection_type == "Tournoment"):
                # selecting a bee by tournoment procedure
                bee = self.tournoment()
            
            # we try for improvement one time for each bee, if change happens we add one to improvement-try property of that bee
            change_flag = self.try_for_improvement(bee)
            if(change_flag == False): 
                bee.try_improve += 1
                                                             
    def scout_bees_phase(self):
        # in here we select only delete the first bee that we see that has a try_improve larger than max_improvement try,
        # and delete it and replace it with new bee

        first_max_flag = False
        index = 0

        while index < len(self.bees) and first_max_flag == False:
            bee = self.bees[index]
            if bee.try_improve >= self.max_try_improve:
                self.bees.pop(index)
                self.bees.append(self.make_a_bee())
                first_max_flag == True
            index += 1

    def make_a_bee(self):
        # making each random solution -> employed bees
        # each random solution is made by randomly choose answers, and make them 1, until it stays feasible

        bee_main = Bee(self.nI)
        bee_secondary = Bee(self.nI)
        capacity_flag = True

        while(capacity_flag):
            x = random.randint(0, self.nI-1)
            if(bee_secondary.data[x]==0):
                bee_secondary.data[x] = 1
                capacity_flag = self.check_feasiblity(bee_secondary)
                if(capacity_flag):
                    bee_main.data[x] = 1
        
        self.calculate_fitness(bee_main)

        return bee_main

    def check_feasiblity(self, bee):
        # checking feasiblity of the answers that has been made (capacity)
        
        # Now perform the element-wise multiplication
        used_capacities = np.sum(bee.data * self.weights, axis=1)

        return np.all(used_capacities <= self.capacity)

    def try_for_improvement(self, bee):
        # we do the cross over and mutation here
        # we also return that if the process made any changes or not
        
        change_flag = False
        new_bee = copy.deepcopy(bee)
        
        # doing the cross over on selected bee and a neighbor (that will be handled in _cross_over)
        if(self.crossover_type == "one_point"):
            self.crossover_one_point(new_bee)
        elif(self.crossover_type == "uniform"):
            self.crossover_uniform(new_bee)
        
        # doing the mutation on selected bee
        self.mutation(new_bee) 
        
        # checking the feasiblity and improvement
        if(self.check_feasiblity(new_bee)):
           self.calculate_fitness(new_bee)
           if(new_bee.fitness > bee.fitness):
                change_flag = True     
                bee.data = new_bee.data.copy()
                bee.fitness = new_bee.fitness
                bee.try_improve = 0

        return change_flag    

    def crossover_one_point(self, bee):
        # for each answer that employed bees have made, we select a radom neighbor
        # for each answer we also select a random position, and it replaced with its neighbors pos
        # if the changed answer be better than the previous one and it be valid, it will change
        # we also return that if the crossover has done a change or not
        
        x = random.random()

        if(x<=self.pc_onePoint):
            # choosing a random position for change
            random_pos = random.randint(1, self.nI-1)
            
            # choosing a neighbor, and it does not matter if it is the bee itself
            neighbor_bee = random.choice(self.bees)

            # in here we change parts of our "bee.data" base on choosed position,
            # the first part comes from bee.data, and the second part comes from neighbor.data 
            bee.data[random_pos:] = neighbor_bee.data[random_pos:].copy()

    def crossover_uniform(self, bee):
        
        # choosing a neighbor, and it does not matter if it is the bee itself
        neighbor_bee = random.choice(self.bees)

        for item in range(self.nI):
            x = random.random()
            
            if(x<=self.pc_uniForm):            
                bee.data[item] = neighbor_bee.data[item].copy()

    def mutation(self, bee):
        # for each answer that employed bees have made, we select a random position and we change it with 0 or 1 (randomly)
        # only if the changed answer be better than the previous one and it be valid, it will change
        # we also return that if the muatation has done a change or not
        
        random_numbers = np.random.random(self.nI)
        mask = random_numbers <= self.pm
        bee.data[mask] = np.where(bee.data[mask] == 0, 1, 0)

    def calculate_fitness(self, bee):
        # fitness is amount of capacity that the bee can take (the capacity that the answer is occupying)
        bee.fitness = np.sum(self.profits * bee.data)

    def roulette_wheel(self):

        sum_of_fitnesses = sum([bee.fitness for bee in self.bees])

        rand_num = random.uniform(0, sum_of_fitnesses)
        cumulative_fitness = 0
        
        for bee in self.bees:
            cumulative_fitness += bee.fitness
            if cumulative_fitness >= rand_num:
                return bee
        
    def tournoment(self):
        # choosing our bee with tournoment procedure with "k_tournoment" variable
        
        tournoment_list = []
        for i in range(self.k_tournoment):
            tournoment_list.append(random.choice(self.bees))
        max_F = 0
        max_B = None
        for bee in tournoment_list:
            if(bee.fitness>max_F):
                max_F = bee.fitness
                max_B = bee
        return max_B
    
    def find_best_bee(self):
        fitness_values = np.zeros(len(self.bees))

        for i, bee in enumerate(self.bees):
            fitness_values[i] = bee.fitness

        best_index = np.argmax(fitness_values)
        best_bee = self.bees[best_index]
        best_fitness = fitness_values[best_index]

        return best_bee, best_fitness

    def write_results(self, best_fitnesses_of_iterations, best_final_bee, best_final_fitness, total_iteration_num, st):

        result = open(self.result_file_name, 'a')
        result.write("FINAL RESULT \n \n")
            
        fitness_avg = sum(best_fitnesses_of_iterations)/len(best_fitnesses_of_iterations)
        result.write(f"the best final Bee => \ndata: {best_final_bee.data}, fitness: {best_final_fitness} \n")
        result.write(f"the average fitness of all: {fitness_avg} \n \n")

        # end time of all
        et = time.time()

        elapsed_time = et - st
        result.write(f'Execution time of all: {elapsed_time} seconds \n \n')

        result.write("------------------------ \n")
        result.write("COMPARE ANSWER \n \n")
        result.write(f"real answer = \n")
        result.write(f"my answer = {best_final_fitness} \n")

        result.write("------------------------ \n")
        result.write("PARAMETERS \n \n")
        result.write(f"Number of Employed Bees = {self.employed_bees_num}\n")
        result.write(f"Number of Onlooker Bees = {self.employed_bees_num}\n")
        result.write(f"Max improvement try = {self.max_try_improve}\n")
        result.write(f"cross_over type = {self.crossover_type}\n")
        result.write(f"probability of crossover_onePoint = {self.pc_onePoint}\n")
        result.write(f"probability of crossover_uniForm = {self.pc_uniForm}\n")
        result.write(f"probability of mutation = {self.pm}\n")
        result.write(f"K tournoment percent = {self.k_tournoment}\n")
        result.write(f"Precedure Type = {self.selection_type}\n")
        result.write(f"Number of ABC algorithm's iterations = {total_iteration_num}\n")
        result.write(f"Limited Time = {self.cpu_time_limit}")

        result.close()

    def write_excel(self, run_id, category, problem_num, cpu_time_limit, employed_bees_num, max_try_improve, pc_onePoint, pc_uniForm, pm, selection_type, k_tournomet, crossover_type, best_final_fitness, best_fitness_iteration_num, best_fitness_time, total_iteration_num):
        file_path = 'input_output/output.xlsx'

        df = pd.read_excel(file_path)
        new_data = {'run_id': run_id,
                    'category': category, 
                    'problem_num': problem_num, 
                    'cpu_time_limit': cpu_time_limit, 
                    'bees_num': employed_bees_num, 
                    'max_try_improve': max_try_improve, 
                    'pc_onePoint': pc_onePoint, 
                    'pc_uniForm': pc_uniForm, 
                    'pm': pm, 
                    'selection_type': selection_type, 
                    'k_tournomet': k_tournomet,
                    'crossover_type': crossover_type,
                    'best_final_fitness': best_final_fitness,
                    'best_fitness_iteration_num': best_fitness_iteration_num,
                    'best_fitness_time': best_fitness_time,
                    'total_iteration_num': total_iteration_num,
                    }

        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        df.to_excel(file_path, index=False)