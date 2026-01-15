"""
Demo Script - Run simulated sessions
Usage: python demo.py --sessions 100 --workers 5
"""

import argparse
import yaml
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from loguru import logger
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.session_engine import SessionEngine
from core.behavior_simulator import BehaviorSimulator
from core.serp_simulator import SERPSimulator
from ip_management.ip_pool import IPPoolManager
from event_logging.event_logger import EventLogger  # Fixed import


class BotOrchestrator:
    """Orchestrates bot sessions with all components"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        # Load config
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize components
        self.session_engine = SessionEngine(config_path)
        self.behavior_simulator = BehaviorSimulator(self.config)
        self.serp_simulator = SERPSimulator(self.config)
        self.ip_manager = IPPoolManager(self.config)
        self.event_logger = EventLogger(self.config)
        
        logger.info("Bot Orchestrator initialized")
    
    def run_single_session(self, session_num: int) -> dict:
        """Run a single bot session with all interactions"""
        
        try:
            # Get IP for this session
            ip = self.ip_manager.get_next_ip()
            if not ip:
                logger.error(f"Session {session_num}: No IP available")
                return {'success': False, 'error': 'No IP available'}
            
            # Generate session
            session = self.session_engine.generate_session(ip.address)
            
            # Log session start
            self.event_logger.log_session_start(session)
            
            logger.info(f"Session {session_num} started: {session['id']}")
            
            # Select search query
            query = self.behavior_simulator.select_search_query()
            
            # Simulate search
            search_result = self.serp_simulator.simulate_search(
                query=query,
                user_agent=session['user_agent']
            )
            
            # Log search
            self.event_logger.log_search(
                session_id=session['id'],
                ip_address=ip.address,
                search_data=search_result
            )
            
            # Determine how many clicks to make
            num_clicks = session['planned_clicks']
            
            # Get click pattern
            clicked_results = self.serp_simulator.simulate_click_pattern(
                results=search_result['results'],
                clicks_count=num_clicks
            )
            
            # Simulate each click and page interaction
            for result in clicked_results:
                # Log click
                self.event_logger.log_click(
                    session_id=session['id'],
                    ip_address=ip.address,
                    click_data=result
                )
                
                # Wait between clicks (human-like delay)
                click_delay = self.behavior_simulator.simulate_click_delay()
                time.sleep(click_delay / 10)  # Reduced for demo speed
                
                # Simulate page interaction
                page_interaction = self.serp_simulator.simulate_result_interaction(
                    result=result,
                    behavior_config=self.config['behavior']
                )
                
                # Log page view
                self.event_logger.log_page_view(
                    session_id=session['id'],
                    ip_address=ip.address,
                    page_data=page_interaction
                )
                
                session['actual_clicks'] += 1
            
            # Check if should refine search
            if self.serp_simulator.should_refine_search(clicked_results):
                refined_query = self.serp_simulator.simulate_serp_refinement(query)
                logger.debug(f"Session {session_num}: Refining search to '{refined_query}'")
                
                # Run one more search (simplified)
                refined_search = self.serp_simulator.simulate_search(
                    query=refined_query,
                    user_agent=session['user_agent']
                )
                
                self.event_logger.log_search(
                    session_id=session['id'],
                    ip_address=ip.address,
                    search_data=refined_search
                )
            
            # End session
            session = self.session_engine.end_session(session['id'])
            
            # Log session end
            self.event_logger.log_session_end(session)
            
            # Update IP stats (success)
            self.ip_manager.update_ip_stats(ip.address, success=True)
            self.event_logger.update_ip_stats(ip.address, success=True)
            
            logger.info(f"Session {session_num} completed successfully")
            
            return {
                'success': True,
                'session_id': session['id'],
                'ip': ip.address,
                'clicks': session['actual_clicks']
            }
            
        except Exception as e:
            logger.error(f"Session {session_num} failed: {e}")
            
            # Update IP stats (failure)
            if ip:
                self.ip_manager.update_ip_stats(ip.address, success=False)
                self.event_logger.update_ip_stats(ip.address, success=False)
            
            # Log error
            if session:
                self.event_logger.log_error(
                    session_id=session['id'],
                    ip_address=ip.address if ip else 'unknown',
                    error_data={'error': str(e), 'session_num': session_num}
                )
            
            return {'success': False, 'error': str(e)}


def run_demo(num_sessions: int, num_workers: int, config_path: str):
    """Run the demo with specified parameters"""
    
    logger.info(f"Starting demo: {num_sessions} sessions with {num_workers} workers")
    logger.info("=" * 60)
    
    # Initialize orchestrator
    orchestrator = BotOrchestrator(config_path)
    
    # Track results
    results = []
    start_time = time.time()
    
    # Run sessions in parallel
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = {
            executor.submit(orchestrator.run_single_session, i): i 
            for i in range(1, num_sessions + 1)
        }
        
        for future in as_completed(futures):
            session_num = futures[future]
            try:
                result = future.result()
                results.append(result)
                
                # Progress update
                completed = len(results)
                if completed % 10 == 0:
                    logger.info(f"Progress: {completed}/{num_sessions} sessions completed")
                    
            except Exception as e:
                logger.error(f"Session {session_num} exception: {e}")
                results.append({'success': False, 'error': str(e)})
    
    # Calculate statistics
    duration = time.time() - start_time
    successful = sum(1 for r in results if r.get('success'))
    failed = len(results) - successful
    
    logger.info("=" * 60)
    logger.info("DEMO COMPLETED")
    logger.info("=" * 60)
    logger.info(f"Total sessions: {num_sessions}")
    logger.info(f"Successful: {successful} ({successful/num_sessions*100:.1f}%)")
    logger.info(f"Failed: {failed} ({failed/num_sessions*100:.1f}%)")
    logger.info(f"Duration: {duration:.2f} seconds")
    logger.info(f"Rate: {num_sessions/duration:.2f} sessions/second")
    logger.info("=" * 60)
    
    # Get IP pool stats
    ip_stats = orchestrator.ip_manager.get_pool_stats()
    logger.info("IP POOL STATISTICS")
    logger.info(f"Total IPs: {ip_stats['total_ips']}")
    logger.info(f"Active: {ip_stats['active']}")
    logger.info(f"Warning: {ip_stats['warning']}")
    logger.info(f"Blocked: {ip_stats['blocked']}")
    logger.info(f"Overall success rate: {ip_stats['success_rate']*100:.1f}%")
    logger.info("=" * 60)
    
    # Get database summary
    db_stats = orchestrator.event_logger.get_summary_statistics()
    logger.info("DATABASE STATISTICS")
    logger.info(f"Total events: {db_stats['total_events']}")
    logger.info(f"Total sessions: {db_stats['total_sessions']}")
    logger.info(f"Total clicks: {db_stats['total_clicks']}")
    logger.info(f"Total errors: {db_stats['total_errors']}")
    logger.info("=" * 60)
    
    logger.info("\n✅ Demo completed! View dashboard with: python dashboard/cli_dashboard.py")


def main():
    parser = argparse.ArgumentParser(description='Human B.O.T Demo Script')
    parser.add_argument('--sessions', type=int, default=100, 
                       help='Number of sessions to simulate (default: 100)')
    parser.add_argument('--workers', type=int, default=5,
                       help='Number of concurrent workers (default: 5)')
    parser.add_argument('--config', type=str, default='config/config.yaml',
                       help='Path to config file (default: config/config.yaml)')
    
    args = parser.parse_args()
    
    # Setup logging
    logger.remove()
    logger.add(sys.stderr, level="INFO", 
              format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")
    logger.add("logs/demo.log", rotation="10 MB", level="DEBUG")
    
    # Run demo
    run_demo(args.sessions, args.workers, args.config)


if __name__ == "__main__":
    main()