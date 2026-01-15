import random
import time
from datetime import datetime
from typing import Dict, List
import yaml
from fake_useragent import UserAgent
from loguru import logger

class SessionEngine:
    """Core session generation and management engine"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.ua = UserAgent()
        self.active_sessions = {}
        
    def generate_session(self, ip_address: str) -> Dict:
        """Generate a new session with realistic parameters"""
        
        # Device types with probabilities
        device_types = ['desktop', 'mobile', 'tablet']
        device_weights = [0.6, 0.35, 0.05]
        device_type = random.choices(device_types, weights=device_weights)[0]
        
        # Generate fingerprint
        fingerprint = self._generate_fingerprint(device_type)
        
        # Session parameters
        duration_range = self.config['simulation']['session_duration_range']
        clicks_range = self.config['simulation']['clicks_per_session_range']
        
        session = {
            'id': f"session_{int(time.time() * 1000)}_{random.randint(1000, 9999)}",
            'start_time': datetime.utcnow(),
            'ip_address': ip_address,
            'user_agent': fingerprint['user_agent'],
            'device_type': device_type,
            'fingerprint': fingerprint,
            'planned_duration': random.randint(*duration_range),
            'planned_clicks': random.randint(*clicks_range),
            'actual_clicks': 0,
            'status': 'active'
        }
        
        self.active_sessions[session['id']] = session
        logger.info(f"Session created: {session['id']} | IP: {ip_address} | Device: {device_type}")
        
        return session
    
    def _generate_fingerprint(self, device_type: str) -> Dict:
        """Generate realistic device fingerprint"""
        
        fingerprint = {
            'user_agent': self.ua.random,
            'device_type': device_type,
        }
        
        if device_type == 'desktop':
            fingerprint.update({
                'screen_resolution': random.choice(['1920x1080', '2560x1440', '1366x768']),
                'viewport': random.choice(['1920x969', '2560x1329', '1366x657']),
                'timezone': random.choice(['America/New_York', 'America/Los_Angeles', 'America/Chicago']),
            })
        elif device_type == 'mobile':
            fingerprint.update({
                'screen_resolution': random.choice(['390x844', '428x926', '375x667']),
                'viewport': random.choice(['390x664', '428x746', '375x559']),
                'timezone': random.choice(['America/New_York', 'America/Los_Angeles']),
            })
        
        return fingerprint
    
    def end_session(self, session_id: str) -> Dict:
        """Mark session as completed"""
        
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session['end_time'] = datetime.utcnow()
            session['status'] = 'completed'
            session['actual_duration'] = (session['end_time'] - session['start_time']).total_seconds()
            
            logger.info(f"Session ended: {session_id} | Duration: {session['actual_duration']:.1f}s | Clicks: {session['actual_clicks']}")
            
            del self.active_sessions[session_id]
            return session
        
        return None