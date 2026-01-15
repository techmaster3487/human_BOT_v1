"""
Storage Module - Database utilities and query helpers
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy import create_engine, func, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger
from .models import Base, Session as DBSession, Event, IPStats


class StorageManager:
    """Database storage manager with query utilities"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        logger.info(f"Storage manager initialized: {db_path}")
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    # ========================================================================
    # SESSION QUERIES
    # ========================================================================
    
    def get_session_by_id(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        db = self.get_session()
        try:
            session = db.query(DBSession).filter_by(id=session_id).first()
            return self._session_to_dict(session) if session else None
        finally:
            db.close()
    
    def get_sessions(self, 
                     status: Optional[str] = None,
                     limit: int = 100,
                     offset: int = 0) -> List[Dict]:
        """Get sessions with optional filtering"""
        db = self.get_session()
        try:
            query = db.query(DBSession)
            
            if status:
                query = query.filter_by(status=status)
            
            sessions = query.order_by(DBSession.start_time.desc()).limit(limit).offset(offset).all()
            return [self._session_to_dict(s) for s in sessions]
        finally:
            db.close()
    
    def get_sessions_by_ip(self, ip_address: str, limit: int = 100) -> List[Dict]:
        """Get all sessions for a specific IP"""
        db = self.get_session()
        try:
            sessions = db.query(DBSession).filter_by(ip_address=ip_address).order_by(DBSession.start_time.desc()).limit(limit).all()
            return [self._session_to_dict(s) for s in sessions]
        finally:
            db.close()
    
    def get_sessions_in_timerange(self, 
                                  start_time: datetime,
                                  end_time: datetime) -> List[Dict]:
        """Get sessions within time range"""
        db = self.get_session()
        try:
            sessions = db.query(DBSession).filter(
                and_(
                    DBSession.start_time >= start_time,
                    DBSession.start_time <= end_time
                )
            ).all()
            return [self._session_to_dict(s) for s in sessions]
        finally:
            db.close()
    
    # ========================================================================
    # EVENT QUERIES
    # ========================================================================
    
    def get_events(self,
                   event_type: Optional[str] = None,
                   session_id: Optional[str] = None,
                   ip_address: Optional[str] = None,
                   limit: int = 100) -> List[Dict]:
        """Get events with optional filtering"""
        db = self.get_session()
        try:
            query = db.query(Event)
            
            if event_type:
                query = query.filter_by(event_type=event_type)
            if session_id:
                query = query.filter_by(session_id=session_id)
            if ip_address:
                query = query.filter_by(ip_address=ip_address)
            
            events = query.order_by(Event.timestamp.desc()).limit(limit).all()
            return [self._event_to_dict(e) for e in events]
        finally:
            db.close()
    
    def get_events_in_timerange(self,
                                start_time: datetime,
                                end_time: datetime,
                                event_type: Optional[str] = None) -> List[Dict]:
        """Get events within time range"""
        db = self.get_session()
        try:
            query = db.query(Event).filter(
                and_(
                    Event.timestamp >= start_time,
                    Event.timestamp <= end_time
                )
            )
            
            if event_type:
                query = query.filter_by(event_type=event_type)
            
            events = query.all()
            return [self._event_to_dict(e) for e in events]
        finally:
            db.close()
    
    def count_events_by_type(self) -> Dict[str, int]:
        """Count events by type"""
        db = self.get_session()
        try:
            results = db.query(
                Event.event_type,
                func.count(Event.id)
            ).group_by(Event.event_type).all()
            
            return {event_type: count for event_type, count in results}
        finally:
            db.close()
    
    # ========================================================================
    # IP STATISTICS QUERIES
    # ========================================================================
    
    def get_ip_stats(self, ip_address: Optional[str] = None) -> Dict:
        """Get IP statistics"""
        db = self.get_session()
        try:
            if ip_address:
                ip_stats = db.query(IPStats).filter_by(ip_address=ip_address).first()
                return self._ip_stats_to_dict(ip_stats) if ip_stats else None
            else:
                all_stats = db.query(IPStats).all()
                return [self._ip_stats_to_dict(s) for s in all_stats]
        finally:
            db.close()
    
    def get_top_performing_ips(self, limit: int = 10) -> List[Dict]:
        """Get top performing IPs by success rate"""
        db = self.get_session()
        try:
            ips = db.query(IPStats).filter(
                IPStats.total_requests >= 10  # Minimum sample size
            ).order_by(IPStats.success_rate.desc()).limit(limit).all()
            
            return [self._ip_stats_to_dict(ip) for ip in ips]
        finally:
            db.close()
    
    def get_ip_by_status(self, status: str) -> List[Dict]:
        """Get IPs by status (active, warning, blocked)"""
        db = self.get_session()
        try:
            ips = db.query(IPStats).filter_by(status=status).all()
            return [self._ip_stats_to_dict(ip) for ip in ips]
        finally:
            db.close()
    
    def get_recently_used_ips(self, hours: int = 24, limit: int = 20) -> List[Dict]:
        """Get recently used IPs"""
        db = self.get_session()
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            ips = db.query(IPStats).filter(
                IPStats.last_used >= cutoff_time
            ).order_by(IPStats.last_used.desc()).limit(limit).all()
            
            return [self._ip_stats_to_dict(ip) for ip in ips]
        finally:
            db.close()
    
    # ========================================================================
    # ANALYTICS QUERIES
    # ========================================================================
    
    def get_hourly_session_counts(self, hours: int = 24) -> Dict[str, int]:
        """Get session counts by hour"""
        db = self.get_session()
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            sessions = db.query(DBSession).filter(
                DBSession.start_time >= cutoff_time
            ).all()
            
            # Group by hour
            hourly_counts = {}
            for session in sessions:
                hour_key = session.start_time.strftime('%Y-%m-%d %H:00')
                hourly_counts[hour_key] = hourly_counts.get(hour_key, 0) + 1
            
            return hourly_counts
        finally:
            db.close()
    
    def get_click_distribution(self) -> Dict[str, int]:
        """Get distribution of clicks per session"""
        db = self.get_session()
        try:
            sessions = db.query(DBSession).all()
            
            distribution = {}
            for session in sessions:
                clicks = session.total_clicks
                distribution[clicks] = distribution.get(clicks, 0) + 1
            
            return distribution
        finally:
            db.close()
    
    def get_device_type_distribution(self) -> Dict[str, int]:
        """Get distribution of device types"""
        db = self.get_session()
        try:
            results = db.query(
                DBSession.device_type,
                func.count(DBSession.id)
            ).group_by(DBSession.device_type).all()
            
            return {device_type: count for device_type, count in results}
        finally:
            db.close()
    
    def get_average_session_duration(self) -> float:
        """Get average session duration"""
        db = self.get_session()
        try:
            result = db.query(func.avg(DBSession.duration)).filter(
                DBSession.duration.isnot(None)
            ).scalar()
            
            return round(result, 2) if result else 0.0
        finally:
            db.close()
    
    def get_success_rate_over_time(self, hours: int = 24) -> List[Dict]:
        """Get success rate trends over time"""
        db = self.get_session()
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            sessions = db.query(DBSession).filter(
                DBSession.start_time >= cutoff_time
            ).all()
            
            # Group by hour and calculate success rate
            hourly_data = {}
            for session in sessions:
                hour_key = session.start_time.strftime('%Y-%m-%d %H:00')
                
                if hour_key not in hourly_data:
                    hourly_data[hour_key] = {'total': 0, 'completed': 0}
                
                hourly_data[hour_key]['total'] += 1
                if session.status == 'completed':
                    hourly_data[hour_key]['completed'] += 1
            
            # Calculate rates
            result = []
            for hour, data in sorted(hourly_data.items()):
                success_rate = data['completed'] / data['total'] if data['total'] > 0 else 0
                result.append({
                    'hour': hour,
                    'total': data['total'],
                    'completed': data['completed'],
                    'success_rate': round(success_rate, 3)
                })
            
            return result
        finally:
            db.close()
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def cleanup_old_data(self, days: int = 30):
        """Delete data older than specified days"""
        db = self.get_session()
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            
            # Delete old events
            deleted_events = db.query(Event).filter(
                Event.timestamp < cutoff_time
            ).delete()
            
            # Delete old sessions
            deleted_sessions = db.query(DBSession).filter(
                DBSession.start_time < cutoff_time
            ).delete()
            
            db.commit()
            
            logger.info(f"Cleaned up old data: {deleted_events} events, {deleted_sessions} sessions")
            
            return {
                'deleted_events': deleted_events,
                'deleted_sessions': deleted_sessions
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Cleanup failed: {e}")
            return None
        finally:
            db.close()
    
    def reset_database(self):
        """Reset all tables (USE WITH CAUTION)"""
        logger.warning("Resetting database - all data will be lost!")
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
        logger.info("Database reset complete")
    
    # ========================================================================
    # CONVERSION HELPERS
    # ========================================================================
    
    def _session_to_dict(self, session: DBSession) -> Dict:
        """Convert Session object to dictionary"""
        if not session:
            return None
        
        return {
            'id': session.id,
            'start_time': session.start_time.isoformat() if session.start_time else None,
            'end_time': session.end_time.isoformat() if session.end_time else None,
            'duration': session.duration,
            'ip_address': session.ip_address,
            'user_agent': session.user_agent,
            'device_type': session.device_type,
            'total_clicks': session.total_clicks,
            'status': session.status
        }
    
    def _event_to_dict(self, event: Event) -> Dict:
        """Convert Event object to dictionary"""
        if not event:
            return None
        
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
        if not ip_stats:
            return None
        
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
            'last_used': ip_stats.last_used.isoformat() if ip_stats.last_used else None,
            'created_at': ip_stats.created_at.isoformat() if ip_stats.created_at else None
        }