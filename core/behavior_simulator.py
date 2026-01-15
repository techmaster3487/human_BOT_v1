import random
import time
import numpy as np
from typing import Dict, List
from loguru import logger

class BehaviorSimulator:
    """Simulates realistic human browsing behavior"""
    
    def __init__(self, config: Dict):
        self.config = config
        
    def simulate_dwell_time(self) -> float:
        """Generate realistic dwell time using Gaussian distribution"""
        mean = self.config['behavior']['dwell_time_mean']
        stddev = self.config['behavior']['dwell_time_stddev']
        
        # Ensure positive values
        dwell_time = max(5, np.random.normal(mean, stddev))
        return round(dwell_time, 2)
    
    def simulate_click_delay(self) -> float:
        """Time between clicks with human-like variance"""
        delay_range = self.config['behavior']['click_delay_range']
        base_delay = random.uniform(*delay_range)
        
        # Add occasional longer delays (user reading, distraction)
        if random.random() < 0.15:
            base_delay += random.uniform(5, 15)
        
        return round(base_delay, 2)
    
    def should_scroll(self) -> bool:
        """Determine if user scrolls on this page"""
        return random.random() < self.config['behavior']['scroll_probability']
    
    def simulate_scroll_pattern(self) -> List[Dict]:
        """Generate realistic scroll events"""
        if not self.should_scroll():
            return []
        
        scroll_events = []
        num_scrolls = random.randint(2, 8)
        current_position = 0
        
        for i in range(num_scrolls):
            scroll_distance = random.randint(300, 800)
            current_position += scroll_distance
            scroll_time = random.uniform(0.5, 2.0)
            
            scroll_events.append({
                'type': 'scroll',
                'position': current_position,
                'timestamp': time.time(),
                'duration': scroll_time
            })
            
            # Pause between scrolls
            time.sleep(random.uniform(0.3, 1.5))
        
        return scroll_events
    
    def simulate_mouse_movement(self) -> Dict:
        """Generate mouse movement pattern (simplified)"""
        # In real implementation, would generate bezier curves
        return {
            'pattern': 'natural',
            'velocity': random.uniform(100, 400),  # pixels/second
            'path_complexity': random.uniform(0.3, 0.8)
        }
    
    def select_search_query(self) -> str:
        """Select a search query from config or generate random"""
        queries = self.config['behavior'].get('search_queries', [])
        
        if queries:
            return random.choice(queries)
        
        # Fallback generic queries
        generic = [
            "how to",
            "best ways to",
            "tutorial for",
            "reviews of",
            "comparison between"
        ]
        return random.choice(generic) + " " + str(random.randint(1, 100))