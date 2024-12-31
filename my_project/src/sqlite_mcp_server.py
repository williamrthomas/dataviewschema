#!/usr/bin/env node
import sqlite3
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
import json

class SQLiteMetadataServer:
    def __init__(self, db_path: str = "schema_metadata.db"):
        """Initialize the SQLite server with schema metadata"""
        self.db_path = db_path
        self.conn = None
        self.setup_database()

    def setup_database(self) -> None:
        """Create the database schema and load initial data"""
        self.conn = sqlite3.connect(self.db_path)
        
        # Create tables
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS tables (
            schema_name TEXT,
            table_name TEXT,
            description TEXT,
            category TEXT,
            data_model TEXT,
            PRIMARY KEY (schema_name, table_name)
        );

        CREATE TABLE IF NOT EXISTS columns (
            schema_name TEXT,
            table_name TEXT,
            column_name TEXT,
            data_type TEXT,
            is_primary_key BOOLEAN,
            is_foreign_key BOOLEAN,
            references_schema TEXT,
            references_table TEXT,
            references_column TEXT,
            description TEXT,
            PRIMARY KEY (schema_name, table_name, column_name)
        );

        CREATE TABLE IF NOT EXISTS domains (
            domain_name TEXT PRIMARY KEY,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS table_domains (
            schema_name TEXT,
            table_name TEXT,
            domain_name TEXT,
            PRIMARY KEY (schema_name, table_name, domain_name),
            FOREIGN KEY (domain_name) REFERENCES domains(domain_name),
            FOREIGN KEY (schema_name, table_name) REFERENCES tables(schema_name, table_name)
        );

        -- Indexes for performance
        CREATE INDEX IF NOT EXISTS idx_tables_category ON tables(category);
        CREATE INDEX IF NOT EXISTS idx_tables_data_model ON tables(data_model);
        CREATE INDEX IF NOT EXISTS idx_columns_refs ON columns(references_schema, references_table);
        """)
        
        # Create views for common queries
        self.conn.executescript("""
        -- View for table relationships
        CREATE VIEW IF NOT EXISTS table_relationships AS
        SELECT 
            c.schema_name,
            c.table_name,
            c.column_name,
            c.references_schema,
            c.references_table,
            c.references_column,
            t1.category as from_category,
            t2.category as to_category
        FROM columns c
        JOIN tables t1 ON c.schema_name = t1.schema_name AND c.table_name = t1.table_name
        LEFT JOIN tables t2 ON c.references_schema = t2.schema_name AND c.references_table = t2.table_name
        WHERE c.is_foreign_key = 1;

        -- View for domain-based table grouping
        CREATE VIEW IF NOT EXISTS domain_tables AS
        SELECT 
            d.domain_name,
            d.description as domain_description,
            t.schema_name,
            t.table_name,
            t.description as table_description,
            t.category
        FROM domains d
        JOIN table_domains td ON d.domain_name = td.domain_name
        JOIN tables t ON td.schema_name = t.schema_name AND td.table_name = t.table_name;
        """)

    def load_metadata(self, table_descriptions_path: Path) -> None:
        """Load metadata from CSV file"""
        df = pd.read_csv(table_descriptions_path)
        
        # Insert into tables table
        df.to_sql('tables', self.conn, if_exists='replace', index=False,
                  dtype={
                      'schema_name': 'TEXT',
                      'table_name': 'TEXT',
                      'description': 'TEXT',
                      'category': 'TEXT',
                      'data_model': 'TEXT'
                  })
        
        # Extract and insert domains based on categories
        domains = df['category'].unique()
        domains_data = [(d, f"Tables related to {d}") for d in domains if pd.notna(d)]
        
        self.conn.executemany(
            "INSERT OR REPLACE INTO domains (domain_name, description) VALUES (?, ?)",
            domains_data
        )
        
        # Create domain mappings
        domain_mappings = []
        for _, row in df.iterrows():
            if pd.notna(row['category']):
                domain_mappings.append((
                    row['SCHEMANAME'],
                    row['TABLE NAME'],
                    row['category']
                ))
        
        self.conn.executemany(
            """INSERT OR REPLACE INTO table_domains 
               (schema_name, table_name, domain_name) VALUES (?, ?, ?)""",
            domain_mappings
        )

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific table"""
        cursor = self.conn.cursor()
        
        # Get table details
        cursor.execute("""
            SELECT schema_name, table_name, description, category, data_model
            FROM tables 
            WHERE table_name = ?
        """, (table_name,))
        
        table_info = cursor.fetchone()
        if not table_info:
            return {}
            
        # Get columns
        cursor.execute("""
            SELECT column_name, data_type, is_primary_key, is_foreign_key,
                   references_schema, references_table, references_column, description
            FROM columns
            WHERE table_name = ?
        """, (table_name,))
        
        columns = cursor.fetchall()
        
        # Get relationships
        cursor.execute("""
            SELECT DISTINCT references_table, column_name
            FROM columns
            WHERE table_name = ? AND is_foreign_key = 1
        """, (table_name,))
        
        relationships = cursor.fetchall()
        
        return {
            "table": {
                "schema": table_info[0],
                "name": table_info[1],
                "description": table_info[2],
                "category": table_info[3],
                "data_model": table_info[4]
            },
            "columns": [{
                "name": col[0],
                "type": col[1],
                "is_primary_key": col[2],
                "is_foreign_key": col[3],
                "references": {
                    "schema": col[4],
                    "table": col[5],
                    "column": col[6]
                } if col[3] else None,
                "description": col[7]
            } for col in columns],
            "relationships": [{
                "referenced_table": rel[0],
                "via_column": rel[1]
            } for rel in relationships]
        }

    def get_domain_tables(self, domain: str) -> List[Dict[str, Any]]:
        """Get tables in a specific domain"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT t.schema_name, t.table_name, t.description, t.category, t.data_model
            FROM tables t
            JOIN table_domains td ON t.schema_name = td.schema_name 
                AND t.table_name = td.table_name
            WHERE td.domain_name = ?
        """, (domain,))
        
        return [{
            "schema": row[0],
            "name": row[1],
            "description": row[2],
            "category": row[3],
            "data_model": row[4]
        } for row in cursor.fetchall()]

    def search_tables(self, pattern: str) -> List[Dict[str, Any]]:
        """Search for tables matching a pattern"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT schema_name, table_name, description, category
            FROM tables
            WHERE table_name LIKE ? OR description LIKE ?
        """, (f"%{pattern}%", f"%{pattern}%"))
        
        return [{
            "schema": row[0],
            "name": row[1],
            "description": row[2],
            "category": row[3]
        } for row in cursor.fetchall()]

    def get_related_tables(self, table_name: str, depth: int = 1) -> Dict[str, Any]:
        """Get tables directly related to a given table"""
        cursor = self.conn.cursor()
        
        def get_relationships(table: str, current_depth: int, visited: set) -> Dict[str, Any]:
            if current_depth > depth or table in visited:
                return {}
                
            visited.add(table)
            
            # Get outgoing relationships (foreign keys from this table)
            cursor.execute("""
                SELECT DISTINCT references_table, column_name
                FROM columns
                WHERE table_name = ? AND is_foreign_key = 1
            """, (table,))
            outgoing = cursor.fetchall()
            
            # Get incoming relationships (foreign keys to this table)
            cursor.execute("""
                SELECT DISTINCT table_name, column_name
                FROM columns
                WHERE references_table = ? AND is_foreign_key = 1
            """, (table,))
            incoming = cursor.fetchall()
            
            result = {
                "outgoing": [{
                    "table": rel[0],
                    "via_column": rel[1],
                    "relationships": get_relationships(rel[0], current_depth + 1, visited)
                } for rel in outgoing],
                "incoming": [{
                    "table": rel[0],
                    "via_column": rel[1],
                    "relationships": get_relationships(rel[0], current_depth + 1, visited)
                } for rel in incoming]
            }
            
            return result
            
        return get_relationships(table_name, 1, set())

    def analyze_table_usage(self) -> Dict[str, Any]:
        """Analyze table relationships and usage patterns"""
        cursor = self.conn.cursor()
        
        # Get tables with most relationships
        cursor.execute("""
            WITH relationship_counts AS (
                SELECT table_name, COUNT(*) as ref_count
                FROM columns
                WHERE is_foreign_key = 1
                GROUP BY table_name
                
                UNION ALL
                
                SELECT references_table as table_name, COUNT(*) as ref_count
                FROM columns
                WHERE is_foreign_key = 1 AND references_table IS NOT NULL
                GROUP BY references_table
            )
            SELECT table_name, SUM(ref_count) as total_relationships
            FROM relationship_counts
            GROUP BY table_name
            ORDER BY total_relationships DESC
            LIMIT 10
        """)
        
        central_tables = [{
            "table": row[0],
            "relationship_count": row[1]
        } for row in cursor.fetchall()]
        
        # Get isolated tables (no relationships)
        cursor.execute("""
            SELECT t.table_name
            FROM tables t
            LEFT JOIN columns c1 ON t.table_name = c1.table_name AND c1.is_foreign_key = 1
            LEFT JOIN columns c2 ON t.table_name = c2.references_table
            WHERE c1.table_name IS NULL AND c2.table_name IS NULL
        """)
        
        isolated_tables = [row[0] for row in cursor.fetchall()]
        
        return {
            "central_tables": central_tables,
            "isolated_tables": isolated_tables
        }

if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # Initialize server
    server = SQLiteMetadataServer()
    
    # Load metadata if path provided
    if len(sys.argv) > 1:
        metadata_path = Path(sys.argv[1])
        if metadata_path.exists():
            server.load_metadata(metadata_path)
            print(f"Loaded metadata from {metadata_path}")
        else:
            print(f"Error: File not found - {metadata_path}")
            sys.exit(1)
    
    # Keep connection open for MCP server
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nShutting down server...")
        if server.conn:
            server.conn.close()
