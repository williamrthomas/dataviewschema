import csv
from pathlib import Path
from typing import Dict, List, Any

class SchemaLoadError(Exception):
    """Custom exception for schema loading errors"""
    pass

def validate_csv_headers(reader: csv.DictReader, required_fields: List[str], file_path: str) -> None:
    """
    Validate that CSV file has all required headers.
    
    Args:
        reader: CSV DictReader object
        required_fields: List of required header fields
        file_path: Path to CSV file for error messaging
        
    Raises:
        SchemaLoadError: If required headers are missing
    """
    missing_fields = [field for field in required_fields if field not in reader.fieldnames]
    if missing_fields:
        raise SchemaLoadError(
            f"Missing required fields in {file_path}: {', '.join(missing_fields)}"
        )

def load_schema_data(tables_file: Path, columns_file: Path) -> Dict[str, Dict[str, Any]]:
    """
    Load schema metadata from CSV files and structure it into a nested dictionary.
    
    Args:
        tables_file (Path): Path to the CSV file containing table metadata
        columns_file (Path): Path to the CSV file containing column metadata
    
    Returns:
        Dict[str, Dict[str, Any]]: Nested dictionary structure where:
            - First level key is schema_name
            - Second level key is table_name
            - Value contains table description and columns list
            
    Raises:
        SchemaLoadError: If there are issues with CSV files or data validation
    """
    # Required fields for validation
    table_required_fields = ['schema_name', 'table_name']
    column_required_fields = ['schema_name', 'table_name', 'column_name']
    
    try:
        # Load tables
        tables = []
        with open(tables_file, 'r', newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            validate_csv_headers(reader, table_required_fields, str(tables_file))
            for row in reader:
                # Validate required fields have values
                if not all(row.get(field) for field in table_required_fields):
                    raise SchemaLoadError(
                        f"Missing values for required fields in {tables_file}, "
                        f"row: {row}"
                    )
                tables.append(row)

        if not tables:
            raise SchemaLoadError(f"No data found in tables file: {tables_file}")

        # Load columns
        columns = []
        with open(columns_file, 'r', newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            validate_csv_headers(reader, column_required_fields, str(columns_file))
            for row in reader:
                # Validate required fields have values
                if not all(row.get(field) for field in column_required_fields):
                    raise SchemaLoadError(
                        f"Missing values for required fields in {columns_file}, "
                        f"row: {row}"
                    )
                columns.append(row)

        if not columns:
            raise SchemaLoadError(f"No data found in columns file: {columns_file}")

        # Structure data by schema and table
        schema_dict: Dict[str, Dict[str, Any]] = {}
        
        # First pass: Create schema and table structure with descriptions
        for t in tables:
            schema_name = t['schema_name']
            table_name = t['table_name']
            if schema_name not in schema_dict:
                schema_dict[schema_name] = {}
            schema_dict[schema_name][table_name] = {
                'description': t.get('table_description', ''),
                'columns': []
            }

        # Second pass: Add columns to their respective tables
        orphaned_columns = []
        for c in columns:
            schema_name = c['schema_name']
            table_name = c['table_name']
            if (schema_name in schema_dict and 
                table_name in schema_dict[schema_name]):
                schema_dict[schema_name][table_name]['columns'].append(c)
            else:
                orphaned_columns.append(
                    f"{schema_name}.{table_name}.{c['column_name']}"
                )

        if orphaned_columns:
            raise SchemaLoadError(
                "Found columns referencing non-existent tables:\n" +
                "\n".join(orphaned_columns)
            )

        return schema_dict

    except csv.Error as e:
        raise SchemaLoadError(f"CSV parsing error: {str(e)}")
    except UnicodeDecodeError as e:
        raise SchemaLoadError(f"File encoding error: {str(e)}")

def analyze_relationships(schema_dict: Dict[str, Dict[str, Any]]) -> Dict[str, List[Dict[str, str]]]:
    """
    Analyze relationships between tables based on foreign key information.
    
    Args:
        schema_dict (Dict[str, Dict[str, Any]]): The structured schema data
        
    Returns:
        Dict[str, List[Dict[str, str]]]: Dictionary mapping table names to their relationships
    """
    relationships = {}
    invalid_references = []
    
    # Iterate through all schemas and tables
    for schema_name, tables in schema_dict.items():
        for table_name, table_data in tables.items():
            table_key = f"{schema_name}.{table_name}"
            relationships[table_key] = []
            
            # Check each column for foreign key relationships
            for column in table_data['columns']:
                if column.get('is_foreign_key') == 'true':
                    ref_schema = column.get('references_schema')
                    ref_table = column.get('references_table')
                    ref_column = column.get('references_column')
                    
                    if ref_schema and ref_table and ref_column:
                        # Validate reference exists
                        if (ref_schema in schema_dict and 
                            ref_table in schema_dict[ref_schema]):
                            relationships[table_key].append({
                                'from_column': column['column_name'],
                                'to_schema': ref_schema,
                                'to_table': ref_table,
                                'to_column': ref_column
                            })
                        else:
                            invalid_references.append(
                                f"{table_key}.{column['column_name']} -> "
                                f"{ref_schema}.{ref_table}.{ref_column}"
                            )
    
    if invalid_references:
        raise SchemaLoadError(
            "Found invalid foreign key references:\n" +
            "\n".join(invalid_references)
        )
    
    return relationships

def get_table_statistics(schema_dict: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    """
    Calculate statistics about tables such as number of columns, foreign keys, etc.
    
    Args:
        schema_dict (Dict[str, Dict[str, Any]]): The structured schema data
        
    Returns:
        Dict[str, Dict[str, int]]: Statistics for each table
    """
    stats = {}
    
    for schema_name, tables in schema_dict.items():
        for table_name, table_data in tables.items():
            table_key = f"{schema_name}.{table_name}"
            stats[table_key] = {
                'total_columns': len(table_data['columns']),
                'primary_keys': sum(1 for col in table_data['columns'] 
                                  if col.get('is_primary_key') == 'true'),
                'foreign_keys': sum(1 for col in table_data['columns'] 
                                  if col.get('is_foreign_key') == 'true')
            }
    
    return stats
