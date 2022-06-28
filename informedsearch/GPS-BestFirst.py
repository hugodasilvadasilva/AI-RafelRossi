
'''
This block of code implements a GPS to find a route between 2 cities by using Best First algorithm,
which uses the least estimated distance to destination to choose the next node to be analysed.
Its main difference from Greedy Best First is that this one stores into fringe all possible routes 
for each neighbour, while Greedy Best First only stores one route which is the one that is been
used to reach destination.
By storing all neighbours routes into fringe, this algorithm will always find a solution, if it
existes.
'''

import enum
import unittest
import logging

"""
Description
---------
Set log configuration at formmat `dd/mm/aaaa hh:mn:ss am/pm message`.
The log level must be informe at `level` variable.

Levels
----------
Define log level by setting `level` variable with some of the followings
values:
- logging.DEBUG,
- logging.INFO,
- logging.WARNING,
- logging.ERROR,
- logging.CRITICAL.

"""
level = logging.INFO

logging.basicConfig(format="%(asctime)s # At %(funcName)s # Line %(lineno)d # %(message)s", level=level, datefmt='%d/%m/%Y %I:%M:%S %p')

logging.debug("Log de debug registrado")
logging.info("Log de info registrado")
logging.warning("Log de warning registrado")
logging.error("Log de error registrado")
logging.critical("Log crítico registrado")

class City:
    '''
    This class implements a City which is a concrete implementation of a node (for grapho)
    or state (for search algorithm), where each City has a Id, latitude, longitude and 
    a list of neighbour cities.
    '''

    def __init__(self, id, lat: float, lon: float, neighbours: list):
        self.__id = id
        self.__lat = lat
        self.__lon = lon
        self.__neighbours = neighbours

    @property
    def id(self):
        return self.__id

    @property
    def latitude(self):
        return self.__lat

    @property
    def longitude(self):
        return self.__lon

    @property
    def neighbours(self):
        return self.__neighbours

    def __eq__(self, __o: object) -> bool:
        return self.id == __o.id

    def __repr__(self) -> str:
        return self.id
    
class Map(enum.Enum):
    '''
    The Map is a concrete implementation of a grapho. In this case, the Map
    has a list of City.
    GPSGreedyBestFirst use this class to analyse routes and find path between origin
    and destination.
    '''

    Goiania = City("Goiania", -16.69, -49.25, ["Hidrolandia", "BelaVista"])
    Hidrolandia = City("Hidrolandia", -16.97, -49.22, ["Goiania", "ProfJamil", "BelaVista"])
    BelaVista = City("BelaVista", -16.97, -48.97, ["Goiania", "Hidrolandia", "Piracanjuba", "Cristianopolis"])
    ProfJamil = City("ProfJamil", -17.25, -49.25, ["Hidrolandia", "Morrinhos", "Piracanjuba"])
    Cristianopolis = City("Cristianopolis", -17.19, -48.70, ["BelaVista", "Piracanjuba", "CaldasNovas"])
    Piracanjuba = City("Piracanjuba", -17.30, -49.02, ["BelaVista", "ProfJamil", "CaldasNovas", "Cristianopolis", "Formiga"])
    Formiga = City("Formiga", -17.65, -49.08, ["Piracanjuba"])
    Morrinhos = City("Morrinhos", -17.73, -49.12, ["ProfJamil", "CaldasNovas"])
    CaldasNovas = City("CaldasNovas", -17.74, -48.62, ["Cristianopolis", "Piracanjuba", "Morrinhos"])

    def get_neighbours(id: str)-> list:
        '''
        Gives a list having the name of neighbours of the city informed as parameter.

        ## Parameters
        `- id: str` having the city's id which neighbours are requested.
        `- return: list` having the neighbours's id. If city id doesn't exist return a empty list.
        '''
        for city in (Map):
            if city.value.id == id:
                return city.value.neighbours
        return []
    
    def calc_cartesian_distance(id_a: str, id_b: str):
        '''
        Calculate the cartesian distance between two cities by using their latitute
        and longitude.
        The cartesian distance is defined by calculating the square root of the sum
        of each side at power of two.

        ## Parameters
        `- id_a: str` having the Id of CityA;
        `- id_b: str` having the Id of CityB;
        `- return: float` having the cartesian distance between `id_a` and `id_b`
        '''
        cityA = Map[id_a].value
        cityB = Map[id_b].value

        dist = ((cityA.latitude - cityB.latitude) ** 2 + (cityA.longitude - cityB.longitude)**2)**(1/2)
        return dist

class Route:

    def __init__(self, cities_ids: list, cost: float, evaluation: float):
        self.__cities_ids = cities_ids
        self.__cost = cost
        self.__evaluation = evaluation

    @property
    def cities_ids(self):
        return self.__cities_ids

    @property
    def cost(self):
        return self.__cost

    @property
    def evaluation(self):
        return self.__evaluation

    @property
    def heuristic(self):
        return self.cost + self.evaluation

    @property
    def last_city_id(self):
        return self.__cities_ids[-1]

    def __repr__(self) -> str:
        return f"Route: cities Ids = {self.cities_ids}; cost = {self.cost}; evaluation = {self.evaluation}; heuristic = {self.heuristic}"

class GPSGreedyBestFirst:

    def __init__(self, map: Map):
        self.__map = map
        self.__fringe = []
        self.__visited = []

    def next_route(self) -> Route:
        '''
        Returns the next route to be analysed
        '''
        return self.__fringe.pop(-1)

    def add_route(self, route: Route):
        '''
        Add a route to fringe at a position acording to its
        heuristic
        '''
        for index, curr_route in enumerate(self.__fringe):
            if curr_route.heuristic < route.heuristic:
                self.__fringe.insert(index, route)
                logging.debug(f"Route {route.cities_ids} added into fringe at index {index}")
                logging.debug(f"New fringe is {self.__fringe}")
                break
        else:
            self.__fringe.append(route)
            logging.debug(f"Route {route.cities_ids} added into fringe at index 0")
            logging.debug(f"New fringe is {self.__fringe}")

    
    def add_routes_for_neighbours(self, route: Route, destination: City):
        
        '''Add into fringe a new route for all neighbour's of the last city's `route`.
        Destination must be informed so evaluation function (distance to destination)
        can be calculated.

        ## Parameters
        `- route: Route` which last city's neighbours you wish to add new route
        `- destination: City` that search algorithm is trying to find a route to.
        '''

        list_of_neighbours_ids = Map.get_neighbours(route.last_city_id)

        for neighbour_id in list_of_neighbours_ids:

            # check if neighbour has already been visited
            if neighbour_id in self.__visited:
                logging.debug(f"No route will be add to {neighbour_id} as it has already been visited")
                continue

            distance_from_last_city = Map.calc_cartesian_distance(route.last_city_id, neighbour_id)
            distance_to_destination = Map.calc_cartesian_distance(destination.id, neighbour_id)


            neighbour_route = Route(route.cities_ids + [neighbour_id], distance_from_last_city + route.cost, distance_to_destination)

            self.add_route(neighbour_route)

    def search(self, origin: City, destination: City) -> Route:

        logging.info(f"Starting to search a route from {origin} to {destination}")

        # create a route from origin to destination and add to fringe
        distance_to_destination = Map.calc_cartesian_distance(origin.id, destination.id)
        ini_route = Route([origin.id], 0, distance_to_destination)

        self.add_route(ini_route)

        #start searching
        while self.__fringe:
            
            # get next route on the line/fringe
            curr_route = self.next_route()
            logging.info(f"Analysing route {curr_route.cities_ids}")

            # check if it is destination
            if curr_route.last_city_id == destination.id:
                logging.info(f"Route to destination found by using {curr_route}")
                return curr_route
            
            # add last_city's route to visited cities
            self.__visited.append(curr_route.last_city_id)
            logging.debug(f"{curr_route.last_city_id} added to visited cities")

            # create new routes for neighbours
            self.add_routes_for_neighbours(route=curr_route, destination=destination)

        else:
            logging.info(f"No route found from {origin} to {destination}")
            return None

if __name__ == "__main__":

    searcher = GPSGreedyBestFirst(Map)

    print("############################ SEARCH 1")
    print("In this search origin and destination are the same")
    print("############################")
    route = searcher.search(Map.Goiania.value, Map.Goiania.value)
    print("############################ SEARCH 2")
    print("This search destination is a origin's neighbours")
    print("############################")
    route2 = searcher.search(Map.Goiania.value, Map.BelaVista.value)
    print("############################ SEARCH 3")
    print("This is common search")
    print("############################")
    route3 = searcher.search(Map.Goiania.value, Map.CaldasNovas.value)
    print("############################ SEARCH 4")
    print("this is a search where closer city has no route to destination")
    print("############################")
    route3 = searcher.search(Map.Piracanjuba.value, Map.Morrinhos.value)
