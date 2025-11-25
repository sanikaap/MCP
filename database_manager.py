import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import sqlite3

class DatabaseManager:
    """Manages data storage and retrieval"""
    
    def __init__(self, db_path: str = "contentflow.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Research table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS research (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                sources TEXT,
                insights TEXT,
                knowledge_graph TEXT,
                timestamp TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Content table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                research_id INTEGER,
                platform TEXT NOT NULL,
                content_text TEXT NOT NULL,
                image_path TEXT,
                metadata TEXT,
                timestamp TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (research_id) REFERENCES research (id)
            )
        """)
        
        # Performance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id INTEGER,
                platform TEXT NOT NULL,
                likes INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                impressions INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0.0,
                post_date TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (content_id) REFERENCES content (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def store_research(self, research_data: Dict) -> int:
        """Store research results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO research (topic, sources, insights, knowledge_graph, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                research_data.get("topic", ""),
                json.dumps(research_data.get("sources", {})),
                json.dumps(research_data.get("key_insights", [])),
                json.dumps(research_data.get("knowledge_graph", {})),
                research_data.get("timestamp", datetime.now().isoformat())
            ))
            
            research_id = cursor.lastrowid
            conn.commit()
            return research_id
        
        except Exception as e:
            print(f"Error storing research: {e}")
            conn.rollback()
            return -1
        
        finally:
            conn.close()
    
    def store_content(self, content_package: Dict, research_id: Optional[int] = None) -> List[int]:
        """Store generated content"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        content_ids = []
        
        try:
            for platform, content_data in content_package.get("platforms", {}).items():
                cursor.execute("""
                    INSERT INTO content (research_id, platform, content_text, image_path, metadata, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    research_id,
                    platform,
                    content_data.get("text", ""),
                    content_data.get("image"),
                    json.dumps(content_data.get("metadata", {})),
                    content_package.get("timestamp", datetime.now().isoformat())
                ))
                
                content_ids.append(cursor.lastrowid)
            
            conn.commit()
            return content_ids
        
        except Exception as e:
            print(f"Error storing content: {e}")
            conn.rollback()
            return []
        
        finally:
            conn.close()
    
    def store_performance(self, performance_data: Dict, content_id: int):
        """Store performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO performance (
                    content_id, platform, likes, shares, comments, 
                    impressions, engagement_rate, post_date
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                content_id,
                performance_data.get("platform", ""),
                performance_data.get("likes", 0),
                performance_data.get("shares", 0),
                performance_data.get("comments", 0),
                performance_data.get("impressions", 0),
                performance_data.get("engagement_rate", 0.0),
                performance_data.get("post_date", datetime.now().isoformat())
            ))
            
            conn.commit()
        
        except Exception as e:
            print(f"Error storing performance: {e}")
            conn.rollback()
        
        finally:
            conn.close()
    
    def get_historical_performance(self, platform: Optional[str] = None) -> List[Dict]:
        """Retrieve historical performance data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if platform:
                cursor.execute("""
                    SELECT * FROM performance 
                    WHERE platform = ?
                    ORDER BY created_at DESC
                    LIMIT 50
                """, (platform,))
            else:
                cursor.execute("""
                    SELECT * FROM performance 
                    ORDER BY created_at DESC
                    LIMIT 50
                """)
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
        
        except Exception as e:
            print(f"Error retrieving performance data: {e}")
            return []
        
        finally:
            conn.close()
    
    def get_research_by_topic(self, topic: str) -> Optional[Dict]:
        """Retrieve research by topic"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM research 
                WHERE topic LIKE ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (f"%{topic}%",))
            
            row = cursor.fetchone()
            
            if row:
                columns = [desc[0] for desc in cursor.description]
                result = dict(zip(columns, row))
                
                # Parse JSON fields
                result["sources"] = json.loads(result["sources"]) if result.get("sources") else {}
                result["insights"] = json.loads(result["insights"]) if result.get("insights") else []
                result["knowledge_graph"] = json.loads(result["knowledge_graph"]) if result.get("knowledge_graph") else {}
                
                return result
            
            return None
        
        except Exception as e:
            print(f"Error retrieving research: {e}")
            return None
        
        finally:
            conn.close()
    
    def get_content_by_platform(self, platform: str, limit: int = 10) -> List[Dict]:
        """Retrieve content by platform"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM content 
                WHERE platform = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (platform, limit))
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                content = dict(zip(columns, row))
                content["metadata"] = json.loads(content["metadata"]) if content.get("metadata") else {}
                results.append(content)
            
            return results
        
        except Exception as e:
            print(f"Error retrieving content: {e}")
            return []
        
        finally:
            conn.close()
    
    def export_data(self, format: str = "json") -> str:
        """Export all data in specified format"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            data = {
                "research": [],
                "content": [],
                "performance": []
            }
            
            # Export research
            cursor.execute("SELECT * FROM research ORDER BY created_at DESC")
            columns = [desc[0] for desc in cursor.description]
            for row in cursor.fetchall():
                data["research"].append(dict(zip(columns, row)))
            
            # Export content
            cursor.execute("SELECT * FROM content ORDER BY created_at DESC")
            columns = [desc[0] for desc in cursor.description]
            for row in cursor.fetchall():
                data["content"].append(dict(zip(columns, row)))
            
            # Export performance
            cursor.execute("SELECT * FROM performance ORDER BY created_at DESC")
            columns = [desc[0] for desc in cursor.description]
            for row in cursor.fetchall():
                data["performance"].append(dict(zip(columns, row)))
            
            if format == "json":
                return json.dumps(data, indent=2)
            else:
                return str(data)
        
        except Exception as e:
            print(f"Error exporting data: {e}")
            return "{}"
        
        finally:
            conn.close()
    
    def clear_all_data(self):
        """Clear all data from database (use with caution!)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM performance")
            cursor.execute("DELETE FROM content")
            cursor.execute("DELETE FROM research")
            conn.commit()
            print("All data cleared successfully")
        
        except Exception as e:
            print(f"Error clearing data: {e}")
            conn.rollback()
        
        finally:
            conn.close()