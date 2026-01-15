"""
Event Logger - Centralized event logging system
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger
from .models import Base, Session as DBSession, Event, IPStats


class EventLogger:
    """Centralized event logging system"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.db_path = config['logging']['database']
        
        # Setup database
        self.engine = create_engine(f'sqlite:///{self.db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        logger.info(f"Event logger initialized with database: {self.db_path}")
    
    def log_event(self, 
                  event_type: str, 
                  session_id: str, 
                  ip_address: str, 
                  data: Dict[str, Any]) -> str:
        """
        Log an event to the database
        
        Args:
            event_type: Type of event (click, page_view, session_start, etc.)
            session_id: Associated session ID
            ip_address: IP address used
            data: Additional event data (flexible JSON)
        
        Returns:
            Event ID
        """
        
        db: Session = self.SessionLocal()
        
        try:
            event = Event(
                event_type=event_type,
                session_id=session_id,
                ip_address=ip_address,
                data=data
            )
            
            db.add(event)
            db.commit()
            db.refresh(event)
            
            logger.debug(f"Event logged: {event_type} | Session: {session_id} | IP: {ip_address}")
            
            return event.id
            
        except Exception as e:
            logger.error(f"Failed to log event: {e}")
            db.rollback()
            return None
        finally:
            db.close()
    
    def log_session_start(self, session: Dict) -> str:
        """Log session start event"""
        return self.log_event(
            event_type='session_start',
            session_id=session['id'],
            ip_address=session['ip_address'],
            data={
                'user_agent': session['user_agent'],
                'device_type': session['device_type'],
                'fingerprint': session['fingerprint'],
                'planned_duration': session['planned_duration'],
                'planned_clicks': session['planned_clicks']
            }
        )
    
    def log_session_end(self, session: Dict) -> str:
        """Log session end event"""
        return self.log_event(
            event_type='session_end',
            session_id=session['id'],
            ip_address=session['ip_address'],
            data={
                'actual_duration': session.get('actual_duration'),
                'actual_clicks': session.get('actual_clicks'),
                'status': session.get('status')
            }
        )
    
    def log_search(self, session_id: str, ip_address: str, search_data: Dict) -> str:
        """Log search event"""
        return self.log_event(
            event_type='search',
            session_id=session_id,
            ip_address=ip_address,
            data={
                'query': search_data['query'],
                'search_engine': search_data['search_engine'],
                'results_count': search_data['results_count'],
                'search_duration': search_data['search_duration']
            }
        )
    
    def log_click(self, session_id: str, ip_address: str, click_data: Dict) -> str:
        """Log click event"""
        return self.log_event(
            event_type='click',
            session_id=session_id,
            ip_address=ip_address,
            data={
                'url': click_data['url'],
                'title': click_data.get('title'),
                'position': click_data.get('position'),
                'click_order': click_data.get('click_order')
            }
        )
    
    def log_page_view(self, session_id: str, ip_address: str, page_data: Dict) -> str:
        """Log page view event"""
        return self.log_event(
            event_type='page_view',
            session_id=session_id,
            ip_address=ip_address,
            data={
                'url': page_data['url'],
                'dwell_time': page_data.get('dwell_time'),
                'did_scroll': page_data.get('did_scroll'),
                'scroll_depth_percent': page_data.get('scroll_depth_percent'),
                'is_bounce': page_data.get('is_bounce')
            }
        )
    
    def log_ip_rotation(self, session_id: str, old_ip: str, new_ip: str) -> str:
        """Log IP rotation event"""
        return self.log_event(
            event_type='ip_rotation',
            session_id=session_id,
            ip_address=new_ip,
            data={
                'old_ip': old_ip,
                'new_ip': new_ip
            }
        )
    
    def log_error(self, session_id: str, ip_address: str, error_data: Dict) -> str:
        """Log error event"""
        return self.log_event(
            event_type='error',
            session_id=session_id,
            ip_address=ip_address,
            data=error_data
        )
    
    def update_ip_stats(self, ip_address: str, success: bool):
        """Update IP statistics in database"""
        
        db: Session = self.SessionLocal()
        
        try:
            # Get or create IP stats
            ip_stats = db.query(IPStats).filter_by(ip_address=ip_address).first()
            
            if not ip_stats:
                ip_stats = IPStats(
                    ip_address=ip_address,
                    total_requests=0,
                    successful_requests=0,
                    failed_requests=0
                )
                db.add(ip_stats)
            
            # Update stats
            ip_stats.total_requests += 1
            ip_stats.last_used = datetime.utcnow()
            
            if success:
                ip_stats.successful_requests += 1
            else:
                ip_stats.failed_requests += 1
            
            # Calculate success rate
            if ip_stats.total_requests > 0:
                ip_stats.success_rate = ip_stats.successful_requests / ip_stats.total_requests
                ip_stats.reputation_score = ip_stats.success_rate
            
            # Update status based on reputation
            reputation_threshold = self.config['ip_pool']['reputation_threshold']
            
            if ip_stats.reputation_score < reputation_threshold and ip_stats.total_requests >= 10:
                ip_stats.status = 'warning'
            
            if ip_stats.reputation_score < 0.3 and ip_stats.total_requests >= 20:
                ip_stats.status = 'blocked'
            
            db.commit()
            
            logger.debug(f"IP stats updated: {ip_address} | Success rate: {ip_stats.success_rate:.2%}")
            
        except Exception as e:
            logger.error(f"Failed to update IP stats: {e}")
            db.rollback()
        finally:
            db.close()
    
    def get_session_events(self, session_id: str) -> list:
        """Get all events for a session"""
        
        db: Session = self.SessionLocal()
        
        try:
            events = db.query(Event).filter_by(session_id=session_id).all()
            return [self._event_to_dict(e) for e in events]
        finally:
            db.close()
    
    def get_recent_events(self, limit: int = 100) -> list:
        """Get most recent events"""
        
        db: Session = self.SessionLocal()
        
        try:
            events = db.query(Event).order_by(Event.timestamp.desc()).limit(limit).all()
            return [self._event_to_dict(e) for e in events]
        finally:
            db.close()
    
    def get_events_by_type(self, event_type: str, limit: int = 100) -> list:
        """Get events by type"""
        
        db: Session = self.SessionLocal()
        
        try:
            events = db.query(Event).filter_by(event_type=event_type).order_by(Event.timestamp.desc()).limit(limit).all()
            return [self._event_to_dict(e) for e in events]
        finally:
            db.close()
    
    def get_ip_statistics(self, ip_address: Optional[str] = None) -> Dict:
        """Get IP statistics"""
        
        db: Session = self.SessionLocal()
        
        try:
            if ip_address:
                ip_stats = db.query(IPStats).filter_by(ip_address=ip_address).first()
                return self._ip_stats_to_dict(ip_stats) if ip_stats else None
            else:
                all_stats = db.query(IPStats).all()
                return [self._ip_stats_to_dict(s) for s in all_stats]
        finally:
            db.close()
    
    def get_summary_statistics(self) -> Dict:
        """Get overall summary statistics"""
        
        db: Session = self.SessionLocal()
        
        try:
            total_events = db.query(Event).count()
            total_sessions = db.query(Event).filter_by(event_type='session_start').count()
            total_clicks = db.query(Event).filter_by(event_type='click').count()
            total_errors = db.query(Event).filter_by(event_type='error').count()
            
            # IP stats summary
            ip_stats = db.query(IPStats).all()
            total_ips = len(ip_stats)
            active_ips = sum(1 for s in ip_stats if s.status == 'active')
            
            total_requests = sum(s.total_requests for s in ip_stats)
            total_success = sum(s.successful_requests for s in ip_stats)
            overall_success_rate = total_success / total_requests if total_requests > 0 else 0
            
            return {
                'total_events': total_events,
                'total_sessions': total_sessions,
                'total_clicks': total_clicks,
                'total_errors': total_errors,
                'total_ips': total_ips,
                'active_ips': active_ips,
                'total_requests': total_requests,
                'overall_success_rate': overall_success_rate
            }
        finally:
            db.close()
    
    def _event_to_dict(self, event: Event) -> Dict:
        """Convert Event object to dictionary"""
        return {
            'id': event.id,
            'timestamp': event.timestamp.isoformat() if event.timestamp else None,
            'event_type': event.event_type,
            'session_id': event.session_id,
            'ip_address': event.ip_address,
            'data': event.data
        }
    
    def _ip_stats_to_dict(self, ip_stats: IPStats) -> Dict:
        """Convert IPStats object to dictionary"""
        return {
            'ip_address': ip_stats.ip_address,
            'proxy_type': ip_stats.proxy_type,
            'country': ip_stats.country,
            'total_requests': ip_stats.total_requests,
            'successful_requests': ip_stats.successful_requests,
            'failed_requests': ip_stats.failed_requests,
            'success_rate': ip_stats.success_rate,
            'reputation_score': ip_stats.reputation_score,
            'status': ip_stats.status,
            'last_used': ip_stats.last_used.isoformat() if ip_stats.last_used else None
        }