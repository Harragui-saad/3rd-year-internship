import numpy as np
import time
from typing import List, Dict, Any, Tuple
from config import QL_CONFIG, WAREHOUSE_CONFIG

class QLearningOptimizer:
    """
    Q-Learning based route optimizer for warehouse picking operations
    """
    
    def __init__(self):
        self.learning_rate = QL_CONFIG['learning_rate']
        self.discount_factor = QL_CONFIG['discount_factor']
        self.epsilon = QL_CONFIG['epsilon']
        self.max_iterations = QL_CONFIG['max_iterations']
        self.zones = WAREHOUSE_CONFIG['zones']
        self.priority_weights = {
            'urgent': 3.0,
            'normal': 2.0,
            'low': 1.0
        }
        
        # Initialize Q-table
        self.q_table = {}
        self.distance_matrix = self._initialize_distance_matrix()
        
    def _initialize_distance_matrix(self) -> Dict[str, Dict[str, float]]:
        """Initialize distance matrix between zones"""
        distances = {}
        for zone1 in self.zones:
            distances[zone1] = {}
            for zone2 in self.zones:
                if zone1 == zone2:
                    distances[zone1][zone2] = 0.0
                else:
                    # Simple distance calculation (can be enhanced with actual coordinates)
                    zone1_num = int(zone1.replace('Zone', ''))
                    zone2_num = int(zone2.replace('Zone', ''))
                    distances[zone1][zone2] = abs(zone1_num - zone2_num) * 10.0
        return distances
    
    def _get_state_key(self, current_zone: str, remaining_products: List[Dict[str, Any]]) -> str:
        """Generate state key for Q-learning"""
        if not remaining_products:
            return f"{current_zone}_empty"
        
        # Create a simplified state representation
        zone_counts = {}
        priority_sum = 0
        
        for product in remaining_products:
            zone = product['zone']
            priority = product['priority']
            zone_counts[zone] = zone_counts.get(zone, 0) + 1
            priority_sum += self.priority_weights.get(priority, 1.0)
        
        # Create state key
        zone_str = "_".join([f"{zone}:{count}" for zone, count in sorted(zone_counts.items())])
        priority_str = f"p{int(priority_sum)}"
        
        return f"{current_zone}_{zone_str}_{priority_str}"
    
    def _get_action_space(self, current_zone: str, remaining_products: List[Dict[str, Any]]) -> List[str]:
        """Get available actions (next zones to visit)"""
        if not remaining_products:
            return []
        
        # Get unique zones from remaining products
        available_zones = list(set([product['zone'] for product in remaining_products]))
        
        # Add current zone if there are products there
        if any(product['zone'] == current_zone for product in remaining_products):
            available_zones.append(current_zone)
        
        return available_zones
    
    def _calculate_reward(self, current_zone: str, next_zone: str, 
                         products_in_zone: List[Dict[str, Any]]) -> float:
        """Calculate reward for moving from current_zone to next_zone"""
        if not products_in_zone:
            return -1.0  # Penalty for visiting empty zone
        
        # Distance penalty
        distance_penalty = self.distance_matrix[current_zone][next_zone] * 0.1
        
        # Priority reward
        priority_reward = sum(
            self.priority_weights.get(product['priority'], 1.0) * product['quantity']
            for product in products_in_zone
        )
        
        # Quantity reward
        quantity_reward = sum(product['quantity'] for product in products_in_zone) * 0.1
        
        return priority_reward + quantity_reward - distance_penalty
    
    def _choose_action(self, state: str, action_space: List[str]) -> str:
        """Choose action using epsilon-greedy policy"""
        if np.random.random() < self.epsilon:
            # Exploration: random action
            return np.random.choice(action_space)
        else:
            # Exploitation: best action based on Q-values
            q_values = [self.q_table.get(f"{state}_{action}", 0.0) for action in action_space]
            max_q = max(q_values)
            best_actions = [action for action, q in zip(action_space, q_values) if q == max_q]
            return np.random.choice(best_actions)
    
    def _update_q_value(self, state: str, action: str, reward: float, next_state: str):
        """Update Q-value using Q-learning update rule"""
        state_action = f"{state}_{action}"
        current_q = self.q_table.get(state_action, 0.0)
        
        # Get max Q-value for next state
        next_q_values = []
        for zone in self.zones:
            next_q_values.append(self.q_table.get(f"{next_state}_{zone}", 0.0))
        
        max_next_q = max(next_q_values) if next_q_values else 0.0
        
        # Q-learning update formula
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[state_action] = new_q
    
    def optimize_route(self, products: List[Dict[str, Any]], start_zone: str = "Zone1", timeout: float = 5.0) -> Tuple[List[str], float]:
        """
        Optimize picking route using Q-learning
        
        Args:
            products: List of products to pick
            start_zone: Starting zone for the route
            timeout: Maximum time to spend on optimization
            
        Returns:
            Tuple of (optimized_route, total_distance)
        """
        start_time = time.time()
        current_zone = start_zone
        remaining_products = products.copy()
        route = [start_zone]
        total_distance = 0.0
        
        # Q-learning iterations
        for iteration in range(self.max_iterations):
            if not remaining_products:
                break
                
            # Check timeout constraint
            if time.time() - start_time > timeout:
                print("Warning: Optimization timeout reached, using greedy approach")
                return self.greedy_route(products, start_zone)
            
            # Get current state
            state = self._get_state_key(current_zone, remaining_products)
            action_space = self._get_action_space(current_zone, remaining_products)
            
            if not action_space:
                break
            
            # Choose action
            next_zone = self._choose_action(state, action_space)
            
            # Get products in the next zone
            products_in_zone = [p for p in remaining_products if p['zone'] == next_zone]
            
            # Calculate reward
            reward = self._calculate_reward(current_zone, next_zone, products_in_zone)
            
            # Move to next zone
            distance = self.distance_matrix[current_zone][next_zone]
            total_distance += distance
            current_zone = next_zone
            
            # Remove picked products
            remaining_products = [p for p in remaining_products if p['zone'] != next_zone]
            
            # Get next state
            next_state = self._get_state_key(current_zone, remaining_products)
            
            # Update Q-value
            self._update_q_value(state, next_zone, reward, next_state)
            
            # Add to route
            if next_zone not in route:
                route.append(next_zone)
        
        return route, total_distance
    
    def greedy_route(self, products, start_zone):
        """Simple greedy algorithm for route optimization"""
        if not products:
            return [], 0.0
        
        # Group products by zone
        zone_products = {}
        for product in products:
            zone = product['zone']
            if zone not in zone_products:
                zone_products[zone] = []
            zone_products[zone].append(product)
        
        # Start from the specified zone
        current_zone = start_zone
        route = [current_zone]
        total_distance = 0.0
        unvisited_zones = set(zone_products.keys()) - {start_zone}
        
        # Visit zones greedily (nearest neighbor)
        while unvisited_zones:
            nearest_zone = min(unvisited_zones, 
                             key=lambda z: self.distance_matrix.get((current_zone, z), float('inf')))
            
            distance = self.distance_matrix.get((current_zone, nearest_zone), 1.0)
            total_distance += distance
            
            route.append(nearest_zone)
            current_zone = nearest_zone
            unvisited_zones.remove(nearest_zone)
        
        return route, total_distance
    
    def hybrid_route(self, products, start_zone, timeout=5.0):
        """Hybrid approach: try Q-Learning first, fallback to greedy if timeout"""
        try:
            # Try Q-Learning with timeout
            route, distance = self.optimize_route(products, start_zone, timeout)
            if route and len(route) > 1:
                return route, distance
        except:
            pass
        
        # Fallback to greedy
        return self.greedy_route(products, start_zone)
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        return {
            'q_table_size': len(self.q_table),
            'zones_count': len(self.zones),
            'learning_rate': self.learning_rate,
            'discount_factor': self.discount_factor,
            'epsilon': self.epsilon
        }
    
    def reset_q_table(self):
        """Reset Q-table for fresh learning"""
        self.q_table = {}
    
    def save_q_table(self, file_path: str):
        """Save Q-table to file"""
        try:
            np.save(file_path, self.q_table)
            print(f"Q-table saved to {file_path}")
        except Exception as e:
            print(f"Error saving Q-table: {e}")
    
    def load_q_table(self, file_path: str):
        """Load Q-table from file"""
        try:
            self.q_table = np.load(file_path, allow_pickle=True).item()
            print(f"Q-table loaded from {file_path}")
        except Exception as e:
            print(f"Error loading Q-table: {e}")
