import csv
import sys

from util import StackFrontier

class Node():
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action
    def __eq__(self, other): #nodes are equal if they have the same actor and movie
        return self.state==other.state #and self.action==other.action

class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node
    def contains_state1(self, state): #checks if state is in 1st spot in frontier
        first=self.frontier[0]
        return state == first.state
    def search(self, state): #returns 1st node in frontier for a given state
        return next(node for node in self.frontier if node.state==state)
    def remove_all(self):#returns frontier as list that clears it completely
        to_explored=[]
        for node in self.frontier:
            to_explored.append(node)
        self.frontier.clear()
        return to_explored
# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")

def search_for_parent(list,parent):
    """
searches a list by a node's parent and returns the parent node
    """
    return next(node for node in list if node.state==parent)
def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    ##for testing
    # source=person_id_for_name("Lupita Nyong'o")
    # target=person_id_for_name("Joan Cusack")
    ## 
    explored=[]
    frontier=QueueFrontier()
    init_state=Node(state=source,parent=None,action=None)
    frontier.add(init_state)
    success=None
    while frontier.empty ==False or success is None:
        if frontier.contains_state(target) == True:
            success=frontier.search(target)
            print("success")
        else:
            removal=frontier.remove_all()
            for node in removal:
                for i in neighbors_for_person(node.state):
                    n=Node(i[1],node.state,i[0])
                    if any(node==n for node in explored)==False and\
                    frontier.contains_state(n.state)==False:
                        frontier.add(n)
                explored.append(node)
            removal.clear()
    if frontier.empty==True:
        return None
    elif success.parent==source:
        return [(success.action,success.state)]
    else:
        movie_path=[(success.action,success.state)]
        node_path=[success]
        while node_path[0].parent != source:
           p_node=search_for_parent(explored,node_path[0].parent) 
           movie_path.insert(0,(p_node.action,p_node.state))
           node_path.insert(0,p_node)
           return movie_path

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
    
