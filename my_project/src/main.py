import json
from pathlib import Path
from typing import Dict, Any
import sys
import traceback

from schema_loader import load_schema_data, analyze_relationships, get_table_statistics
from prompt_utils import (
    log_activity,
    query_llm,
    save_intermediate_result,
    generate_domain_classification_prompt,
    generate_relationship_analysis_prompt,
    parse_llm_json_response
)
from diagram_generator import DiagramGenerator

def process_schema_metadata(data_dir: Path = Path("data")) -> Dict[str, Any]:
    """
    Process the schema metadata from CSV files.
    
    Args:
        data_dir (Path): Directory containing the CSV files
        
    Returns:
        Dict[str, Any]: Processed schema data
    """
    print("\n🔍 Starting schema metadata processing...")
    log_activity("Starting schema metadata processing")
    
    # Validate input files exist
    tables_path = data_dir / "schema_tables.csv"
    columns_path = data_dir / "schema_columns.csv"
    
    if not tables_path.exists():
        error = f"Error: {tables_path} not found"
        print(f"❌ {error}")
        raise FileNotFoundError(error)
    if not columns_path.exists():
        error = f"Error: {columns_path} not found"
        print(f"❌ {error}")
        raise FileNotFoundError(error)
    
    # Load schema data
    print("📊 Loading schema data from CSV files...")
    schema_data = load_schema_data(tables_path, columns_path)
    print(f"✅ Loaded data for {len(schema_data)} schemas")
    log_activity("Loaded schema data from CSV files")
    
    # Analyze relationships
    print("🔗 Analyzing table relationships...")
    relationships = analyze_relationships(schema_data)
    print(f"✅ Found relationships for {len(relationships)} tables")
    log_activity("Analyzed table relationships")
    
    # Get table statistics
    print("📈 Generating table statistics...")
    statistics = get_table_statistics(schema_data)
    print(f"✅ Generated statistics for {len(statistics)} tables")
    log_activity("Generated table statistics")
    
    # Save intermediate results
    print("💾 Saving processed data...")
    save_intermediate_result(
        {
            "schema_data": schema_data,
            "relationships": relationships,
            "statistics": statistics
        },
        "processed_schema_data.json"
    )
    print("✅ Saved processed data")
    
    return {
        "schema_data": schema_data,
        "relationships": relationships,
        "statistics": statistics
    }

def analyze_domains(processed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze and classify domains using LLM.
    
    Args:
        processed_data (Dict[str, Any]): Processed schema data
        
    Returns:
        Dict[str, Any]: Domain classification results
    """
    print("\n🧠 Starting domain analysis...")
    log_activity("Starting domain analysis")
    
    # Generate and send prompt for domain classification
    print("📝 Generating domain classification prompt...")
    prompt = generate_domain_classification_prompt(processed_data)
    print("🤖 Querying LLM for domain classification...")
    try:
        response = query_llm(prompt)
        print("✅ Received LLM response")
    except Exception as e:
        print(f"❌ LLM query failed: {str(e)}")
        raise
    
    # Parse and save results
    print("📊 Processing domain analysis results...")
    try:
        domain_data = parse_llm_json_response(response)
        save_intermediate_result(domain_data, "domain_analysis.json")
        print("✅ Saved domain analysis results")
    except ValueError as e:
        print(f"❌ Failed to parse LLM response: {str(e)}")
        raise
    
    return domain_data

def analyze_data_patterns(
    processed_data: Dict[str, Any],
    domain_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Analyze data patterns and relationships using LLM.
    
    Args:
        processed_data (Dict[str, Any]): Processed schema data
        domain_data (Dict[str, Any]): Domain classification data
        
    Returns:
        Dict[str, Any]: Pattern analysis results
    """
    print("\n📊 Starting pattern analysis...")
    log_activity("Starting pattern analysis")
    
    # Combine schema and domain data for context
    context_data = {
        "schema": processed_data,
        "domains": domain_data
    }
    
    # Generate and send prompt for relationship analysis
    print("📝 Generating relationship analysis prompt...")
    prompt = generate_relationship_analysis_prompt(context_data)
    print("🤖 Querying LLM for pattern analysis...")
    try:
        response = query_llm(prompt)
        print("✅ Received LLM response")
    except Exception as e:
        print(f"❌ LLM query failed: {str(e)}")
        raise
    
    # Parse and save results
    print("📊 Processing pattern analysis results...")
    try:
        pattern_data = parse_llm_json_response(response)
        save_intermediate_result(pattern_data, "pattern_analysis.json")
        print("✅ Saved pattern analysis results")
    except ValueError as e:
        print(f"❌ Failed to parse LLM response: {str(e)}")
        raise
    
    return pattern_data

def generate_artifacts(
    processed_data: Dict[str, Any],
    domain_data: Dict[str, Any],
    pattern_data: Dict[str, Any]
) -> None:
    """
    Generate all visual artifacts using the diagram generator.
    
    Args:
        processed_data (Dict[str, Any]): Processed schema data
        domain_data (Dict[str, Any]): Domain classification data
        pattern_data (Dict[str, Any]): Pattern analysis data
    """
    print("\n🎨 Starting artifact generation...")
    log_activity("Starting artifact generation")
    
    try:
        generator = DiagramGenerator()
        
        # Generate artifacts in sequence with progress tracking
        artifacts = [
            ("Ecosystem Overview", lambda: generator.generate_ecosystem_overview(domain_data)),
            ("Patient Domain", lambda: generator.generate_patient_domain(processed_data["schema_data"])),
            ("Encounters Domain", lambda: generator.generate_encounters_domain(processed_data["schema_data"])),
            ("Clinical Documentation", lambda: generator.generate_clinical_documentation(processed_data["schema_data"])),
            ("Billing Domain", lambda: generator.generate_billing_domain(processed_data["schema_data"])),
            ("Patient-Encounter Path", lambda: generator.generate_patient_encounter_path(processed_data["schema_data"])),
            ("Claim-Payment Path", lambda: generator.generate_claim_payment_path(processed_data["schema_data"])),
            ("Audit & Quality", lambda: generator.generate_audit_quality(processed_data["schema_data"])),
            ("Patient Timeline", lambda: generator.generate_patient_timeline(processed_data["schema_data"])),
            ("Relationship Heatmap", lambda: generator.generate_relationship_heatmap(processed_data["schema_data"]))
        ]
        
        for i, (name, generator_func) in enumerate(artifacts, 1):
            try:
                print(f"\n📊 Generating {name} ({i}/10)...")
                generator_func()
                print(f"✅ Generated {name}")
            except Exception as e:
                print(f"⚠️  Warning: Failed to generate {name}: {str(e)}")
                log_activity(f"Failed to generate {name}: {str(e)}\n{traceback.format_exc()}")
                # Continue with next artifact despite error
                continue
        
        print("\n✅ Completed artifact generation")
        log_activity("Completed artifact generation")
        
    except Exception as e:
        error_msg = f"Error in artifact generation: {str(e)}"
        print(f"\n❌ {error_msg}")
        log_activity(f"{error_msg}\n{traceback.format_exc()}")
        raise

def main() -> None:
    """
    Main execution function that orchestrates the entire workflow.
    """
    print("\n🚀 Starting metadata knowledge extraction process...")
    try:
        log_activity("Starting metadata knowledge extraction process")
        
        # Process schema metadata
        processed_data = process_schema_metadata()
        
        # Analyze domains
        domain_data = analyze_domains(processed_data)
        
        # Analyze patterns
        pattern_data = analyze_data_patterns(processed_data, domain_data)
        
        # Generate artifacts
        generate_artifacts(processed_data, domain_data, pattern_data)
        
        print("\n✨ Successfully completed metadata knowledge extraction process!")
        log_activity("Successfully completed metadata knowledge extraction process")
        
    except Exception as e:
        error_msg = f"Error in main process: {str(e)}"
        print(f"\n❌ {error_msg}")
        log_activity(f"{error_msg}\n{traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
