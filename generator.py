import random
from typing import List, Tuple, Optional

class MazeGenerator:
    """
    A maze generator using the DFS Algorithm
    """
    def __init__(
            self,
            width: int,
            height: int,
            seed: Optional[int]= None
            ) -> None:
        """Initialize the generator with dimensions and an optional seed."""
        self.width: int = width
        self.height: int = height
        if seed is not None:
            random.seed(seed)
        #In the grid all walls closed by (15: 1111)
        self.grid: List[List[int]] = [
            [15 for _ in range(width)] for _ in range(height)
        ]
        self.visited: List[List[bool]] = [
            [False for _ in range(width)] for _ in range(height)
        ]
    

    def _get_neighbors(
            self,
            x: int,
            y: int
    ) -> List[Tuple[int, int, int, int]]:
        """Find unvisited neighbors and the wall bits between them.
        The output is the list of neighbors which we can destroy them"""
        neighbors = []
        # North
        #It means if the row is more than 0 and the north neighbor is not visited we'll go to north with this changes on bits and position
        #(new column, new row, distroying bit(wall) for current pos, destroying bit(wall) for new pos)
        if y > 0 and not self.visited[y-1][x]:
            neighbors.append((x, y-1, 0, 2))
        # East
        if x < self.width - 1 and not self.visited[y][x+1]:
            neighbors.append((x+1, y, 1, 3))
        # South
        if y < self.height - 1 and not self.visited[y+1][x]:
            neighbors.append((x, y+1, 2, 0))
        # West
        if x > 0 and not self.visited[y][x-1]:
            neighbors.append((x-1, y, 3, 1))

        return neighbors
    
    #DFS
    def generate(self, start_x: int, start_y: int) -> None:
        """Creates a perfect maze using Recursive Backtracking (DFS)."""
        self.visited[start_y][start_x] = True

        #find all unvisited neighbors
        neighbors = self._get_neighbors(start_x, start_y)
        #Choose the neighbr randomly
        random.shuffle(neighbors)
        for nx, ny, b_curr, b_next in neighbors:
            #check again if neighbor was visited by another recursive call
            if not self.visited[ny][nx]:
                #remove th b_curr bit(wall) from current pos
                self.grid[start_y][start_x] &= ~(1 << b_curr)
                #remove th b_next bit(wall) from new pos (slected neighbor)
                self.grid[ny][nx] &= ~(1 << b_next)
                #Move to next cell recursively
                self.generate(nx, ny)

    '''
    def get_grid(self) -> List[List[int]]:
        """ REturn the generated maz"""
        return self.grid
    '''
    #Other methods should be written
    #BFS (Shortest path algorith)
    #Constructing path
    #Hex representaion
    #Reserving 42 cells in grid



