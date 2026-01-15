"""
IP Pool Manager - Handles IP rotation and management
"""

import csv
import random
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class IPAddress:
    """IP Address data structure"""
    address: str
    proxy_type: str = 'residential'
    country: str = 'US'
    reputation_score: float = 1.0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    status: str = 'active'  # active, warning, blocked
    last_used: Optional[datetime] = None


class IPPoolManager:
    """Manages IP pool rotation and selection"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.ip_pool: List[IPAddress] = []
        self.current_index = 0
        self.rotation_strategy = config['ip_pool']['rotation_strategy']
        self.reputation_threshold = config['ip_pool']['reputation_threshold']
        self.max_requests_per_ip = config['ip_pool'].get('max_requests_per_ip', 1000)
        
        self._load_ip_pool()
    
    def _load_ip_pool(self):
        """Load IP addresses from CSV file"""
        csv_path = self.config['ip_pool']['source']
        
        try:
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ip = IPAddress(
                        address=row['ip'],
                        proxy_type=row.get('proxy_type', 'residential'),
                        country=row.get('country', 'US'),
                        reputation_score=float(row.get('reputation_score', 1.0))
                    )
                    self.ip_pool.append(ip)
            
            logger.info(f"Loaded {len(self.ip_pool)} IP addresses from {csv_path}")
            
        except FileNotFoundError:
            logger.warning(f"IP pool file not found: {csv_path}. Creating sample pool.")
            self._create_sample_pool()
    
    def _create_sample_pool(self):
        """Create a sample IP pool for testing"""
        for i in range(10):
            ip = IPAddress(
                address=f"192.168.1.{i+1}",
                proxy_type='residential',
                country='US',
                reputation_score=1.0
            )
            self.ip_pool.append(ip)
        
        logger.info(f"Created sample pool with {len(self.ip_pool)} IPs")
    
    def get_next_ip(self) -> IPAddress:
        """Get next IP based on rotation strategy"""
        
        if self.rotation_strategy == 'round-robin':
            return self._round_robin_selection()
        elif self.rotation_strategy == 'random':
            return self._random_selection()
        elif self.rotation_strategy == 'weighted':
            return self._weighted_selection()
        else:
            logger.warning(f"Unknown strategy: {self.rotation_strategy}. Using round-robin.")
            return self._round_robin_selection()
    
    def _round_robin_selection(self) -> IPAddress:
        """Simple round-robin IP selection"""
        active_ips = [ip for ip in self.ip_pool if ip.status == 'active']
        
        if not active_ips:
            logger.error("No active IPs available!")
            return None
        
        ip = active_ips[self.current_index % len(active_ips)]
        self.current_index += 1
        
        return ip
    
    def _random_selection(self) -> IPAddress:
        """Random IP selection from active pool"""
        active_ips = [ip for ip in self.ip_pool if ip.status == 'active']
        
        if not active_ips:
            logger.error("No active IPs available!")
            return None
        
        return random.choice(active_ips)
    
    def _weighted_selection(self) -> IPAddress:
        """Weighted random selection based on reputation score"""
        active_ips = [ip for ip in self.ip_pool if ip.status == 'active']
        
        if not active_ips:
            logger.error("No active IPs available!")
            return None
        
        # Weight by reputation score
        weights = [ip.reputation_score for ip in active_ips]
        total_weight = sum(weights)
        
        if total_weight == 0:
            return random.choice(active_ips)
        
        normalized_weights = [w / total_weight for w in weights]
        return random.choices(active_ips, weights=normalized_weights)[0]
    
    def update_ip_stats(self, ip_address: str, success: bool):
        """Update IP statistics after request"""
        ip = self._find_ip(ip_address)
        
        if not ip:
            logger.warning(f"IP not found in pool: {ip_address}")
            return
        
        ip.total_requests += 1
        ip.last_used = datetime.utcnow()
        
        if success:
            ip.successful_requests += 1
        else:
            ip.failed_requests += 1
        
        # Update success rate
        if ip.total_requests > 0:
            ip.reputation_score = ip.successful_requests / ip.total_requests
        
        # Update status based on reputation
        self._update_ip_status(ip)
        
        logger.debug(f"IP {ip_address} stats updated: {ip.successful_requests}/{ip.total_requests} "
                    f"(score: {ip.reputation_score:.2f}, status: {ip.status})")
    
    def _update_ip_status(self, ip: IPAddress):
        """Update IP status based on reputation score and usage"""
        
        # Check if IP exceeded max requests
        if ip.total_requests >= self.max_requests_per_ip:
            ip.status = 'blocked'
            logger.warning(f"IP {ip.address} blocked: exceeded max requests ({self.max_requests_per_ip})")
            return
        
        # Check reputation threshold
        if ip.reputation_score < self.reputation_threshold:
            if ip.total_requests >= 10:  # Only after minimum sample size
                ip.status = 'warning'
                logger.warning(f"IP {ip.address} status: WARNING (score: {ip.reputation_score:.2f})")
        
        # Block IPs with very low reputation
        if ip.reputation_score < 0.3 and ip.total_requests >= 20:
            ip.status = 'blocked'
            logger.error(f"IP {ip.address} BLOCKED (score: {ip.reputation_score:.2f})")
    
    def _find_ip(self, ip_address: str) -> Optional[IPAddress]:
        """Find IP object by address"""
        for ip in self.ip_pool:
            if ip.address == ip_address:
                return ip
        return None
    
    def get_pool_stats(self) -> Dict:
        """Get overall pool statistics"""
        active = sum(1 for ip in self.ip_pool if ip.status == 'active')
        warning = sum(1 for ip in self.ip_pool if ip.status == 'warning')
        blocked = sum(1 for ip in self.ip_pool if ip.status == 'blocked')
        
        total_requests = sum(ip.total_requests for ip in self.ip_pool)
        total_success = sum(ip.successful_requests for ip in self.ip_pool)
        
        overall_success_rate = total_success / total_requests if total_requests > 0 else 0
        
        return {
            'total_ips': len(self.ip_pool),
            'active': active,
            'warning': warning,
            'blocked': blocked,
            'total_requests': total_requests,
            'total_success': total_success,
            'success_rate': overall_success_rate
        }
    
    def reset_ip(self, ip_address: str):
        """Reset IP statistics (useful for testing)"""
        ip = self._find_ip(ip_address)
        
        if ip:
            ip.total_requests = 0
            ip.successful_requests = 0
            ip.failed_requests = 0
            ip.reputation_score = 1.0
            ip.status = 'active'
            logger.info(f"IP {ip_address} reset to initial state")
    
    def get_active_ips(self) -> List[IPAddress]:
        """Get list of all active IPs"""
        return [ip for ip in self.ip_pool if ip.status == 'active']