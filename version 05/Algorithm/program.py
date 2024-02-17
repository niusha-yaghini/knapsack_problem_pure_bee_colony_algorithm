import pandas as pd
import reading_mknapcb as reading_mknapcb
import time
import diagram
from cabc import Classic_Artificial_Bee_Colony

excel_file_path = 'input_output/input.xlsx'
df = pd.read_excel(excel_file_path)

for index, row in df.iloc[:].iterrows():

    # 0-run_id, 1-file_type, 2-category, 3-problem_num, 4-cpu_time_limit, 5-employed_bees_num, 6-max_try_improve, 
    # 7-pc, 8-pm(pm/items), 9-selection_type, 10-k_tournomet, 11-crossover_type

    row_values = list(row.iloc)

    run_id, category, problem_num, cpu_time_limit, employed_bees_num, max_try_improve, pc_onePoint, pc_uniForm, pm, selection_type, k_tournomet, crossover_type = row_values[0], row_values[1], row_values[2], row_values[3], row_values[4], row_values[5], row_values[6], row_values[7], row_values[8], row_values[9], row_values[10], row_values[11]

    # nK = number of knapstacks
    # nI = number of items
    nK, nI, Capacity, Profits, Weights = reading_mknapcb.reading(category, problem_num)
    
    result_file_name = f'input_output/{run_id}.txt'
    result = open(result_file_name, 'a')
    result.write(f"Classic Artificial Bee Colony Algorithm on knapsack\n \n")        
    result.close()

    # 1) writing the results in a text
    # 2) getting the time of algorithm in each iteration
    st = time.time() # get the start time of all     
    
    onlooker_bees_num = employed_bees_num
    
    # creating an abc object
    abc = Classic_Artificial_Bee_Colony(run_id, cpu_time_limit, employed_bees_num, nK, nI, Capacity, Profits, Weights, onlooker_bees_num, max_try_improve, pc_onePoint, pc_uniForm, pm, k_tournomet, selection_type, crossover_type, result_file_name)

    # getting result
    best_fitnesses_of_iterations, best_fitnesses_so_far, best_final_bee, best_final_fitness, total_iteration_num, best_fitness_iteration_num, best_fitness_time, time_number_list = abc.optimize()

    # writing the result in txt
    abc.write_results(best_fitnesses_of_iterations, best_final_bee, best_final_fitness, total_iteration_num, st)

    # writing in excel 
    abc.write_excel(run_id, category, problem_num, cpu_time_limit, employed_bees_num, max_try_improve, pc_onePoint, pc_uniForm, pm, selection_type, k_tournomet, crossover_type, best_final_fitness, best_fitness_iteration_num, best_fitness_time, total_iteration_num)
        
    photo = f"input_output/{run_id}"
    diagram.diagram(time_number_list, best_fitnesses_of_iterations, best_fitnesses_so_far, photo)

# End of program ------------------------
