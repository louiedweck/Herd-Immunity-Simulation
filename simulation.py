from virus import Virus
from logger import Logger
from person import Person
import random
import sys
random.seed(42)


class Simulation(object):
    ''' Main class that will run the herd immunity simulation program.
    Expects initialization parameters passed as command line arguments when file is run.

    Simulates the spread of a virus through a given population.  The percentage of the
    population that are vaccinated, the size of the population, and the amount of initially
    infected people in a population are all variables that can be set when the program is run.
    '''

    def __init__(self, pop_size, vacc_percentage,  virus, initial_infected=1):
        ''' Logger object logger records all events during the simulation.
        Population represents all Persons in the population.
        The next_person_id is the next available id for all created Persons,
        and should have a unique _id value.
        The vaccination percentage represents the total percentage of population
        vaccinated at the start of the simulation.
        You will need to keep track of the number of people currently infected with the disease.
        The total infected people is the running total that have been infected since the
        simulation began, including the currently infected people who died.
        You will also need to keep track of the number of people that have die as a result
        of the infection.

        All arguments will be passed as command-line arguments when the file is run.
        HINT: Look in the if __name__ == "__main__" function at the bottom.
        '''
        self.pop_size = pop_size  # Int
        self.next_person_id = 0  # Int
        self.virus = virus  # Virus object
        self.initial_infected = initial_infected  # Int
        self.total_infected = 0  # Int
        self.current_infected = 0  # Int
        self.vacc_percentage = vacc_percentage  # float between 0 and 1
        self.total_dead = 0  # Int
        self.newly_infected = []
        self.population = self._create_population()
        self.file_name = f'{virus_name}_simulation_pop_{self.pop_size}_vp_{self.vacc_percentage}_infected_{self.initial_infected}.txt'
        self.logger = Logger(self.file_name)
        self.logger.write_metadata(
            self.pop_size, self.vacc_percentage, self.virus.name, self.virus.mortality_rate, self.virus.repro_rate)

    def _create_population(self):
        '''This method will create the initial population.
            self.initial_infected (int): The number of infected people that the simulation
            will begin with.
            Returns:
                list: A list of Person objects.
        '''
        # pop size = 1000
        # initial infected == 50
        # vacc_percentage = 0.10
        # initial_vaccinated = 100

        initial_vaccinated = int(self.pop_size * self.vacc_percentage)
        initial_population = []
        for unique_id in range(self.pop_size):      # pop size = 1000
            if unique_id < self.initial_infected:       # 0 - 50
                # person is not vaccinated and is infected
                new_person = Person(unique_id, False, True)
                self.current_infected += 1
                self.total_infected += 1
            elif unique_id < self.initial_infected + initial_vaccinated:        # 50 - 150
                # person is vaccinated and is not infected
                new_person = Person(unique_id, True, None)
            else:       # 150 - 1000
                # person is not vaccinated and is not infected
                new_person = Person(unique_id, False, None)
            # add the new person to initial_population
            initial_population.append(new_person)
        return initial_population

    def _simulation_should_continue(self):
        ''' The simulation should only end
        if the entire population is dead
        or if everyone is vaccinated.
            Returns:
                bool: True for simulation should continue, False if it should end.
        '''
        if self.current_infected == 0:
            return False
        for person in self.population:
            if person.is_alive and person.is_vaccinated is False:
                return True
        return False

    def run(self):
        ''' This method should run the simulation until all requirements for ending
        the simulation are met.
        '''
        # TODO: Finish this method.  To simplify the logic here, use the helper method
        # _simulation_should_continue() to tell us whether or not we should continue
        # the simulation and run at least 1 more time_step.

        # TODO: Keep track of the number of time steps that have passed.
        # HINT: You may want to call the logger's log_time_step() method at the end of each time step.
        # TODO: Set this variable using a helper
        time_step_counter = 0
        while self._simulation_should_continue():
            # TODO: for every iteration of this loop, call self.time_step() to compute another
            # round of this simulation.
            self.time_step()
            time_step_counter += 1
        self.logger.f.write(
            f'\nSimulation ended with {self.pop_size - self.total_dead} people remaining after {time_step_counter} turns.')
        self.logger.f.close()
        print(f'The simulation has ended after {time_step_counter} turns.')

    def time_step(self):
        ''' This method should contain all the logic for computing one time step
        in the simulation.

        This includes:
            1. 100 total interactions with a randon person for each infected person
                in the population
            2. If the person is dead, grab another random person from the population.
                Since we don't interact with dead people, this does not count as an interaction.
            3. Otherwise call simulation.interaction(person, random_person) and
                increment interaction counter by 1.
            '''

        # TODO: Finish this method.
        for person in self.population:
            # if the person is infected have them interact with 100 non-infected people
            if person.infection is True and person.is_alive is True:
                one_hundred_random_ppl = []
                n = 100
                if self.pop_size - self.total_dead < 100:
                    n = self.pop_size - self.total_dead - 1
                for _ in range(n):
                    random_person = random.choice(self.population)
                    # if the random person is dead or the same as the infected person find a new one
                    while random_person.is_alive is False or random_person._id == person._id:
                        random_person = random.choice(self.population)
                    one_hundred_random_ppl.append(random_person)
                for random_person in one_hundred_random_ppl:
                    self.interaction(person, random_person)
                # next we decide whether to kill or vaccinated the infected person
                did_survive = person.did_survive_infection(
                    self.virus.mortality_rate)
                if not did_survive:
                    self.total_dead += 1
                self.current_infected -= 1
                self.logger.log_infection_survival(person, did_survive)

        self._infect_newly_infected()

    def interaction(self, person, random_person):
        '''This method should be called any time two living people are selected for an
        interaction. It assumes that only living people are passed in as parameters.

        Args:
            person1 (person): The initial infected person
            random_person (person): The person that person1 interacts with.
        '''
        assert person.is_alive == True
        assert random_person.is_alive == True
        did_infect = False
        # if the random person is not vaccinated and not infected
        if random_person.is_vaccinated is False and random_person.infection is None:
            # maybe we can infect them
            if random.random() < self.virus.repro_rate:
                did_infect = True
                if random_person not in self.newly_infected:
                    self.newly_infected.append(random_person)
        self.logger.log_interaction(
            person, random_person, random_person.infection, random_person.is_vaccinated, did_infect)

    def _infect_newly_infected(self):
        ''' This method should iterate through the list of ._id stored in self.newly_infected
        and update each Person object with the disease. '''
        # TODO: Call this method at the end of every time step and infect each Person.
        # TODO: Once you have iterated through the entire list of self.newly_infected, remember
        # to reset self.newly_infected back to an empty list.
        for unlucky_person in self.newly_infected:
            unlucky_person.infection = True
            self.current_infected += 1
        self.newly_infected = []


if __name__ == "__main__":
    params = sys.argv[1:]
    if len(params) > 2:
        virus_name = str(params[0])
        repro_num = float(params[1])
        mortality_rate = float(params[2])
        pop_size = int(params[3])
        vacc_percentage = float(params[4])
        if len(params) == 6:
            initial_infected = int(params[5])
        else:
            initial_infected = 1
    else:
        virus_name = 'Ebola'
        repro_num = 0.25
        mortality_rate = 0.7
        pop_size = 20
        vacc_percentage = 0.10
        initial_infected = 5

    virus = Virus(virus_name, repro_num, mortality_rate)

    sim = Simulation(pop_size, vacc_percentage, virus, initial_infected)
    sim.run()
