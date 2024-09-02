import heapq

class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.g = float('inf')  
        self.h = 0
        self.parent = None
    
    def __lt__(self, other):
        return (self.g + self.h) < (other.g + other.h)

class AStar:
    def __init__(self, grid):
        self.grid = grid
    
    def find_path(self, start_pos, goal_pos):
        start = Node(start_pos[0], start_pos[1])
        goal = Node(goal_pos[0], goal_pos[1])
        
        open_list = []
        heapq.heappush(open_list, start)
        
        closed_set = [[False for _ in range(len(self.grid[0]))] for _ in range(len(self.grid))]
        
        start.g = 0
        start.h = self.heuristic(start, goal)
        
        while open_list:
            current_node = heapq.heappop(open_list)
            
            if current_node.row == goal.row and current_node.col == goal.col:
                path = []
                while current_node.parent:
                    path.append((current_node.row, current_node.col))
                    current_node = current_node.parent
                path.append((start.row, start.col))
                path.reverse()
                return path
            
            closed_set[current_node.row][current_node.col] = True
            
            neighbors = self.get_neighbors(current_node)
            for neighbor in neighbors:
                if closed_set[neighbor.row][neighbor.col]:
                    continue
                
                tentative_g = current_node.g + 1
                if tentative_g < neighbor.g:
                    neighbor.g = tentative_g
                    neighbor.h = self.heuristic(neighbor, goal)
                    neighbor.parent = current_node
                    heapq.heappush(open_list, neighbor)
        
        return []  # No path found
    
    def heuristic(self, node, goal):
        return abs(node.row - goal.row) + abs(node.col - goal.col)
    
    def get_neighbors(self, node):
        neighbors = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        rows = len(self.grid)
        cols = len(self.grid[0])
        
        for dr, dc in directions:
            r = node.row + dr
            c = node.col + dc
            if 0 <= r < rows and 0 <= c < cols and self.grid[r][c] == 0:
                neighbors.append(Node(r, c))
        
        return neighbors

# Example usage:
if __name__ == "__main__":
    grid = [
        [0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 1, 1, 0],
        [0, 0, 0, 0, 0]
    ]

    astar = AStar(grid)
    start_pos = (0, 0)
    goal_pos = (4, 4)
    
    path = astar.find_path(start_pos, goal_pos)
    
    if path:
        print("Shortest path found:")
        for node in path:
            print(node)
    else:
        print("No path found!")
