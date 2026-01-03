import json
import requests as re


# Class Graph to store a Co-actor Network
# - Nodes = actors (id, name)
# - Edges = acted together in a movie (undirected)
class Graph:

    def __init__(self, nodes_file=None, edges_file=None):
        """
            option 1:  init as an empty graph and add nodes
            option 2: init by specifying a path to nodes & edges files
        """
        self.nodes = [] #list
        self.edges = set() # prevent duplicates, set of tuples
        self.degrees = {} #dict: key=node, value=degree

    # helpter function to get degree of a node
    def get_degree(self, node):
        """
            return the degree of a node
        """
        # build a dictionary of degrees
        degrees = {node_id: 0 for node_id, _ in self.nodes} # _ to ignore the name
        for u, v in self.edges:
            degrees[u] += 1
            degrees[v] += 1

        return degrees

    def add_node(self, id: str, name: str) -> None:
        if not isinstance(id, str):
            raise TypeError("The variable 'id' is not a string.")
        if not isinstance(name, str):
            raise TypeError("The variable 'name' is not a string.")

        name = name.replace(",", "")  # FIXED

        if (id, name) not in self.nodes:
            self.nodes.append((id, name))
            self.degrees[id] = 0

    def add_edge(self, id1: str, id2: str) -> None:
        if not isinstance(id1, str): 
            raise TypeError("The variable 'id' is not a string.")
        if not isinstance(id2, str): 
            raise TypeError("The variable 'id' is not a string.")

        if id1 != id2:
            edge = (min(id1, id2), max(id1, id2))

            if edge not in self.edges:
                self.edges.add(edge)
                self.degrees[id1] += 1
                self.degrees[id2] += 1

    def total_nodes(self) -> int:
        """
        Returns an integer value for the total number of nodes in the graph
        """
        return len(self.nodes)
    

    def total_edges(self) -> int:
        """
        Returns an integer value for the total number of edges in the graph
        """
        return len(self.edges)
    

    def max_degree_nodes(self) -> dict:
        """
        Return the node(s) with the highest degree
        Return multiple nodes in the event of a tie
        Format is a dict where the key is the node_id and the value is an integer for the node degree
        e.g. {'a': 8}
        or {'a': 22, 'b': 22}
        """
        if not self.degrees:
            return {}
        max_degree = max(self.degrees.values())
        return {node: degree for node, degree in self.degrees.items() if degree == max_degree}

    def print_nodes(self):
        """
        No further implementation required
        May be used for de-bugging if necessary
        """
        print(self.nodes)


    def print_edges(self):
        """
        No further implementation required
        May be used for de-bugging if necessary
        """
        print(self.edges)


        # source = where an edge starts
        # target = where an edge ends
        # source,target

    def write_edges_file(self, path="edges.csv")->None:
        """
        write all edges out as .csv
        :param path: string
        :return: None
        """
        edges_path = path
        edges_file = open(edges_path, 'w', encoding='utf-8')

        edges_file.write("source" + "," + "target" + "\n")

        for e in self.edges:
            edges_file.write(e[0] + "," + e[1] + "\n")

        edges_file.close()
        print("finished writing edges to csv")


    # Do not modify
    def write_nodes_file(self, path="nodes.csv")->None:
        """
        write all nodes out as .csv
        :param path: string
        :return: None
        """
        nodes_path = path
        nodes_file = open(nodes_path, 'w', encoding='utf-8')

        nodes_file.write("id,name" + "\n")
        for n in self.nodes:
            nodes_file.write(n[0] + "," + n[1] + "\n")
        nodes_file.close()
        print("finished writing nodes to csv")

    
# fetch the data from TMDB API
class TMDBAPIUtils:

    def __init__(self, api_key:str):
        self.api_key=api_key

    def get_movie_cast(self, movie_id: str, limit: int=None, exclude_ids: list=None) -> list:
        """A list of dictionaries, each representing a cast member. 
        [
            {...},  # cast member 1
            {...}   # cast member 2
        ]"""

        url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={self.api_key}"
        response = re.get(url)
        data = json.loads(response.text)
        cast = data.get("cast", []) # Get the cast list, default to empty list if not found
        results = []

        for actor in cast:
            if exclude_ids is not None and actor["id"] in exclude_ids:
                continue
            results.append(actor)
            if limit is not None and actor.get("order", float("inf")) < limit:
                results.append(actor)  
        return results
    
        return results
    
    def get_movie_credits_for_person(self, person_id: str, vote_avg_threshold: float = None) -> list:
        url = f"https://api.themoviedb.org/3/person/{person_id}/movie_credits?language=en-US&api_key={self.api_key}"
        headers = {"accept": "application/json"}

        response = re.get(url, headers=headers)
        data = json.loads(response.text)

        # safely extract cast list
        cast_list = data.get("cast", [])
        return_list = []

        for cast in cast_list:
            # if no threshold is specified, return all movie credits
            if vote_avg_threshold is None:
                return_list.append(cast)
            else:
                # keep only movies meeting the vote average threshold
                if cast.get("vote_average", 0) >= vote_avg_threshold:
                    return_list.append(cast)

        return return_list

if __name__ == "__main__":
    graph = Graph()
    # Root node
    graph.add_node(id='2975', name='Laurence Fishburne')
    api_key = "c2c8709fe12d3c11008eb151099c975c"
    tmdb_api_utils = TMDBAPIUtils(api_key)

    # expand the graph by adding co-actors of Laurence Fishburne
    movie_credits = tmdb_api_utils.get_movie_credits_for_person('2975', 8.0)

    new_nodes = set()

    for movie_credit in movie_credits:
        movie_id = str(movie_credit['id'])
        movie_cast = tmdb_api_utils.get_movie_cast(movie_id, limit=3)
        if not movie_cast:   # catches None and []
            continue
        for cast_member in movie_cast:
            actor_id = str(cast_member['id'])
            actor_name = cast_member['name']
            if actor_id != '2975' and (actor_id, actor_name) not in new_nodes:
                new_nodes.add((actor_id, actor_name))
                graph.add_node(actor_id, actor_name)
                graph.add_edge('2975', actor_id)
    
    print(f"Total # Nodes: {graph.total_nodes()}, Total # Edges: {graph.total_edges()}")

    # Laurence Fishburne
    # His co-actors
    # Co-actors of co-actors
    # Co-actors of co-actors of co-actors

    for _ in range(1):

        current_new_nodes = new_nodes.copy()
        new_nodes.clear()

        for node_id, node_name in current_new_nodes:
            try:
                movie_credits = tmdb_api_utils.get_movie_credits_for_person(node_id, 8.0)
            except KeyError:
                print(f"movie_credits of movie w/ id {node_id} does not contain cast.")
                continue
            for movie_credit in movie_credits:
                movie_id = str(movie_credit['id'])
                movie_cast = tmdb_api_utils.get_movie_cast(movie_id, limit=3)
                if not movie_cast:   # catches None and []
                    continue
                for cast_member in movie_cast:
                    actor_id = str(cast_member['id'])
                    actor_name = cast_member['name']
                    if (actor_id, actor_name) not in new_nodes:
                        new_nodes.add((actor_id, actor_name))
                        graph.add_node(actor_id, actor_name)
                        graph.add_edge(node_id, actor_id)
        print(f"Total # Nodes: {graph.total_nodes()}, Total # Edges: {graph.total_edges()}")
    
    graph.write_edges_file()
    graph.write_nodes_file()