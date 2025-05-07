import sqlite3
from typing import List, Dict, Optional
import json
from datetime import datetime

class Database:
    def __init__(self, db_name: str = "legal_resources.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_name)

    def init_db(self):
        """Initialize database with required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create legal resources table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS legal_resources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    address TEXT NOT NULL,
                    type TEXT NOT NULL,
                    services TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()

    def add_resource(self, resource: Dict) -> int:
        """Add a new legal resource"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO legal_resources 
                (name, address, type, services, latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                resource['name'],
                resource['address'],
                resource['type'],
                json.dumps(resource['services']),
                resource['coordinates'][0],
                resource['coordinates'][1]
            ))
            conn.commit()
            return cursor.lastrowid

    def get_all_resources(self) -> List[Dict]:
        """Get all legal resources"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM legal_resources')
            rows = cursor.fetchall()
            
            resources = []
            for row in rows:
                resources.append({
                    'id': row[0],
                    'name': row[1],
                    'address': row[2],
                    'type': row[3],
                    'services': json.loads(row[4]),
                    'coordinates': (row[5], row[6]),
                    'created_at': row[7],
                    'updated_at': row[8]
                })
            return resources

    def get_resources_by_type(self, resource_type: str) -> List[Dict]:
        """Get resources by type"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM legal_resources WHERE type = ?', (resource_type,))
            rows = cursor.fetchall()
            
            resources = []
            for row in rows:
                resources.append({
                    'id': row[0],
                    'name': row[1],
                    'address': row[2],
                    'type': row[3],
                    'services': json.loads(row[4]),
                    'coordinates': (row[5], row[6]),
                    'created_at': row[7],
                    'updated_at': row[8]
                })
            return resources

    def update_resource(self, resource_id: int, resource: Dict) -> bool:
        """Update an existing resource"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE legal_resources 
                    SET name = ?, address = ?, type = ?, services = ?, 
                        latitude = ?, longitude = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (
                    resource['name'],
                    resource['address'],
                    resource['type'],
                    json.dumps(resource['services']),
                    resource['coordinates'][0],
                    resource['coordinates'][1],
                    resource_id
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating resource: {str(e)}")
            return False

    def delete_resource(self, resource_id: int) -> bool:
        """Delete a resource"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM legal_resources WHERE id = ?', (resource_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting resource: {str(e)}")
            return False

    def search_resources(self, query: str) -> List[Dict]:
        """Search resources by name or address"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM legal_resources 
                WHERE name LIKE ? OR address LIKE ?
            ''', (f'%{query}%', f'%{query}%'))
            rows = cursor.fetchall()
            
            resources = []
            for row in rows:
                resources.append({
                    'id': row[0],
                    'name': row[1],
                    'address': row[2],
                    'type': row[3],
                    'services': json.loads(row[4]),
                    'coordinates': (row[5], row[6]),
                    'created_at': row[7],
                    'updated_at': row[8]
                })
            return resources

    def import_initial_data(self, resources: Dict):
        """Import initial data from the LEGAL_RESOURCES dictionary"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Clear existing data
            cursor.execute('DELETE FROM legal_resources')
            
            # Insert new data
            for resource_type, resource_list in resources.items():
                for resource in resource_list:
                    cursor.execute('''
                        INSERT INTO legal_resources 
                        (name, address, type, services, latitude, longitude)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        resource['name'],
                        resource['address'],
                        resource['type'],
                        json.dumps(resource['services']),
                        resource['coordinates'][0],
                        resource['coordinates'][1]
                    ))
            
            conn.commit() 