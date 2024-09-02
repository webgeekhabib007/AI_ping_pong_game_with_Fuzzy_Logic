import random
import numpy as np

# Distance matrix for the cities
distance_matrix = np.array([
    [0, 2, 9, 10],
    [1, 0, 6, 4],
    [15, 7, 0, 8],
    [6, 3, 12, 0]
])

num_cities = len(distance_matrix)

def fitness_function(route):
    return 1 / total_distance(route)

def total_distance(route):
    distance = 0
    for i in range(len(route)):
        distance += distance_matrix[route[i-1]][route[i]]
    return distance

def generate_route():
    route = list(range(num_cities))
    random.shuffle(route)
    return route

def selection(population, fitnesses):
    tournament_size = 3
    tournament = random.sample(list(zip(population, fitnesses)), tournament_size)
    tournament.sort(key=lambda x: x[1], reverse=True)
    return tournament[0][0]

def crossover(parent1, parent2):
    size = len(parent1)
    start, end = sorted(random.sample(range(size), 2))
    child = [None] * size
    child[start:end+1] = parent1[start:end+1]
    
    parent2_pos = end + 1
    child_pos = end + 1
    
    while None in child:
        if parent2[parent2_pos % size] not in child:
            child[child_pos % size] = parent2[parent2_pos % size]
            child_pos += 1
        parent2_pos += 1
    
    return child

def mutate(route, mutation_rate):
    for i in range(len(route)):
        if random.random() < mutation_rate:
            j = random.randint(0, len(route) - 1)
            route[i], route[j] = route[j], route[i]
    return route


def genetic_algorithm(pop_size, generations, mutation_rate):
    population = [generate_route() for _ in range(pop_size)]
    
    for generation in range(generations):
        fitnesses = [fitness_function(route) for route in population]
        
        new_population = []
        for _ in range(pop_size // 2):
            parent1 = selection(population, fitnesses)
            parent2 = selection(population, fitnesses)
            offspring1 = crossover(parent1, parent2)
            offspring2 = crossover(parent1, parent2)
            new_population.append(mutate(offspring1, mutation_rate))
            new_population.append(mutate(offspring2, mutation_rate))
        
        population = new_population
    
    best_route = max(population, key=lambda route: fitness_function(route))
    best_distance = total_distance(best_route)
    
    return best_route, best_distance

population_size = 50
number_of_generations = 100
mutation_rate = 0.01


best_route, best_distance = genetic_algorithm(population_size, number_of_generations, mutation_rate)
print(f"Best route: {best_route}")
print(f"Distance of best route: {best_distance}")
