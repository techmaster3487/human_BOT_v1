"""
SERP (Search Engine Results Page) Simulator
Simulates realistic search engine interactions
"""

import random
import time
from typing import Dict, List
from loguru import logger


class SERPSimulator:
    """Simulates realistic SERP interactions"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.search_engines = ['google', 'bing']
        
    def simulate_search(self, query: str, user_agent: str) -> Dict:
        """Simulate a complete search interaction"""
        
        search_engine = random.choice(self.search_engines)
        
        # Simulate search timing
        search_start = time.time()
        
        # Simulate results page load
        time.sleep(random.uniform(0.5, 1.5))
        
        # Generate mock SERP results
        results = self._generate_mock_results(query, search_engine)
        
        search_duration = time.time() - search_start
        
        interaction = {
            'query': query,
            'search_engine': search_engine,
            'user_agent': user_agent,
            'results_count': len(results),
            'search_duration': round(search_duration, 2),
            'results': results,
            'timestamp': time.time()
        }
        
        logger.debug(f"Search performed: '{query}' on {search_engine} ({len(results)} results)")
        
        return interaction
    
    def _generate_mock_results(self, query: str, search_engine: str) -> List[Dict]:
        """Generate mock search results"""
        
        num_results = random.randint(8, 10)
        results = []
        
        for i in range(num_results):
            result = {
                'position': i + 1,
                'title': f"Result {i+1} for {query}",
                'url': f"https://example-{i+1}.com/{query.replace(' ', '-')}",
                'snippet': f"This is a relevant snippet about {query}...",
                'display_url': f"example-{i+1}.com",
                'is_ad': i < 2 and random.random() < 0.3  # First 2 positions might be ads
            }
            results.append(result)
        
        return results
    
    def simulate_click_pattern(self, results: List[Dict], clicks_count: int) -> List[Dict]:
        """
        Simulate realistic click pattern on SERP results
        Users tend to click higher-ranked results more often
        """
        
        if not results:
            return []
        
        clicks_count = min(clicks_count, len(results))
        clicked_results = []
        
        # Weight clicks toward top positions (realistic user behavior)
        # Position 1-3: high probability, 4-7: medium, 8-10: low
        weights = []
        for i, result in enumerate(results):
            if i < 3:
                weight = 10
            elif i < 7:
                weight = 5
            else:
                weight = 2
            
            # Reduce weight for ads (some users avoid ads)
            if result.get('is_ad'):
                weight *= 0.5
            
            weights.append(weight)
        
        # Select results to click (without replacement)
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        # Randomly select which results to click
        available_indices = list(range(len(results)))
        
        for _ in range(clicks_count):
            if not available_indices:
                break
            
            # Get weights for available indices
            available_weights = [normalized_weights[i] for i in available_indices]
            total = sum(available_weights)
            normalized_available = [w / total for w in available_weights]
            
            # Select index
            selected_idx = random.choices(available_indices, weights=normalized_available)[0]
            clicked_result = results[selected_idx].copy()
            clicked_result['click_order'] = len(clicked_results) + 1
            
            clicked_results.append(clicked_result)
            available_indices.remove(selected_idx)
        
        logger.debug(f"Generated click pattern: {[r['position'] for r in clicked_results]}")
        
        return clicked_results
    
    def simulate_result_interaction(self, result: Dict, behavior_config: Dict) -> Dict:
        """
        Simulate interaction with a clicked search result
        Includes page load, dwell time, scrolling
        """
        
        interaction_start = time.time()
        
        # Simulate page load time
        page_load_time = random.uniform(0.8, 2.5)
        time.sleep(page_load_time)
        
        # Determine dwell time (using config from behavior simulator)
        import numpy as np
        mean = behavior_config.get('dwell_time_mean', 45)
        stddev = behavior_config.get('dwell_time_stddev', 15)
        dwell_time = max(5, np.random.normal(mean, stddev))
        
        # Simulate actual browsing (we don't wait full dwell time in simulation)
        # Just track it for logging
        
        # Determine if user scrolls
        did_scroll = random.random() < behavior_config.get('scroll_probability', 0.8)
        scroll_depth = random.randint(20, 80) if did_scroll else 0
        
        # Determine bounce (quick exit)
        is_bounce = dwell_time < 10 and random.random() < 0.2
        
        interaction = {
            'url': result['url'],
            'title': result['title'],
            'position': result['position'],
            'page_load_time': round(page_load_time, 2),
            'dwell_time': round(dwell_time, 2),
            'did_scroll': did_scroll,
            'scroll_depth_percent': scroll_depth,
            'is_bounce': is_bounce,
            'interaction_duration': round(time.time() - interaction_start, 2)
        }
        
        logger.debug(f"Result interaction: pos={result['position']}, dwell={dwell_time:.1f}s, "
                    f"scroll={scroll_depth}%, bounce={is_bounce}")
        
        return interaction
    
    def simulate_serp_refinement(self, original_query: str) -> str:
        """
        Simulate query refinement (user modifying search)
        This happens when user doesn't find what they want
        """
        
        refinement_patterns = [
            f"{original_query} tutorial",
            f"{original_query} guide",
            f"how to {original_query}",
            f"{original_query} 2026",
            f"best {original_query}",
        ]
        
        return random.choice(refinement_patterns)
    
    def should_refine_search(self, clicked_results: List[Dict]) -> bool:
        """
        Determine if user should refine their search
        Based on click behavior and bounce rates
        """
        
        if not clicked_results:
            return random.random() < 0.4  # No clicks = likely to refine
        
        # Check if user is bouncing from results
        bounce_count = sum(1 for r in clicked_results if r.get('is_bounce', False))
        bounce_rate = bounce_count / len(clicked_results)
        
        # High bounce rate = more likely to refine search
        if bounce_rate > 0.5:
            return random.random() < 0.6
        
        return random.random() < 0.15  # Normal refinement rate