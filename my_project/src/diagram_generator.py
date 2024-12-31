from pathlib import Path
from typing import Dict, Any, List
from prompt_utils import query_llm, log_activity

class DiagramGenerator:
    def __init__(self, output_dir: Path = Path("outputs/final")):
        """
        Initialize the diagram generator.
        
        Args:
            output_dir (Path): Directory to save generated diagrams
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_diagram(self, content: str, filename: str) -> None:
        """
        Save a diagram to a markdown file.
        
        Args:
            content (str): The diagram content (including Mermaid markup)
            filename (str): Name of the file to save
        """
        # Format the markdown file with proper headers and content
        formatted_content = f"""# {filename.replace('.md', '').replace('_', ' ').title()}

{content}
"""
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        log_activity(f"Generated diagram: {filename}")

    def generate_ecosystem_overview(self, domain_data: Dict[str, Any]) -> None:
        """
        Generate Artifact #1: High-level ecosystem overview diagram.
        Shows main domains and their relationships.
        
        Args:
            domain_data (Dict[str, Any]): Domain classification data
        """
        try:
            prompt = f"""
            Create a high-level Mermaid diagram showing the clinical data ecosystem:
            {domain_data}

            Requirements:
            1. Use subgraphs to represent main domains (Patient, Clinical, Billing)
            2. Show major relationships between domains with descriptive labels
            3. Use minimal detail, focus on clarity
            4. Add a title 'Clinical Data Ecosystem Overview'
            5. Include a legend explaining the diagram elements
            6. Use consistent color coding for different domain types

            Return only the Mermaid diagram code wrapped in ```mermaid``` tags.
            """
            
            diagram = query_llm(prompt)
            self.save_diagram(diagram, "01_ecosystem_overview.md")
        except Exception as e:
            log_activity(f"Error generating ecosystem overview: {str(e)}")
            raise

    def generate_patient_domain(self, schema_data: Dict[str, Any]) -> None:
        """
        Generate Artifact #2: Patient & Demographics Domain diagram.
        Shows patient-related tables and their relationships.
        
        Args:
            schema_data (Dict[str, Any]): Schema data
        """
        try:
            prompt = f"""
            Create a Mermaid diagram for the Patient & Demographics domain:
            {schema_data}

            Requirements:
            1. Focus on patient-related tables and attributes
            2. Highlight primary demographic data points
            3. Show relationships to other domains
            4. Use clear visual hierarchy
            5. Include data types and key indicators
            6. Add notes for important relationships

            Return only the Mermaid diagram code wrapped in ```mermaid``` tags.
            """
            
            diagram = query_llm(prompt)
            self.save_diagram(diagram, "02_patient_domain.md")
        except Exception as e:
            log_activity(f"Error generating patient domain diagram: {str(e)}")
            raise

    def generate_encounters_domain(self, schema_data: Dict[str, Any]) -> None:
        """
        Generate Artifact #3: Encounters & Appointments Domain diagram.
        Shows encounter/appointment structures and scheduling relations.
        
        Args:
            schema_data (Dict[str, Any]): Schema data
        """
        try:
            prompt = f"""
            Create a Mermaid diagram for the Encounters & Appointments domain:
            {schema_data}

            Requirements:
            1. Show appointment and encounter tables
            2. Include scheduling relationships
            3. Highlight temporal aspects
            4. Show provider relationships
            5. Include status tracking
            6. Add notes for scheduling rules

            Return only the Mermaid diagram code wrapped in ```mermaid``` tags.
            """
            
            diagram = query_llm(prompt)
            self.save_diagram(diagram, "03_encounters_domain.md")
        except Exception as e:
            log_activity(f"Error generating encounters domain diagram: {str(e)}")
            raise

    def generate_clinical_documentation(self, schema_data: Dict[str, Any]) -> None:
        """
        Generate Artifact #4: Clinical Documentation & Results Domain diagram.
        Shows how diagnoses and clinical documents interconnect.
        
        Args:
            schema_data (Dict[str, Any]): Schema data
        """
        try:
            prompt = f"""
            Create a Mermaid diagram for the Clinical Documentation domain:
            {schema_data}

            Requirements:
            1. Show clinical document types and structures
            2. Include diagnosis code relationships
            3. Show result tracking
            4. Highlight document versioning
            5. Include provider annotations
            6. Show document status workflows

            Return only the Mermaid diagram code wrapped in ```mermaid``` tags.
            """
            
            diagram = query_llm(prompt)
            self.save_diagram(diagram, "04_clinical_documentation.md")
        except Exception as e:
            log_activity(f"Error generating clinical documentation diagram: {str(e)}")
            raise

    def generate_billing_domain(self, schema_data: Dict[str, Any]) -> None:
        """
        Generate Artifact #5: Billing & Claims Domain diagram.
        Shows billing entities and insurance relationships.
        
        Args:
            schema_data (Dict[str, Any]): Schema data
        """
        try:
            prompt = f"""
            Create a Mermaid diagram for the Billing & Claims domain:
            {schema_data}

            Requirements:
            1. Show claim processing workflow
            2. Include insurance package relationships
            3. Show payment tracking
            4. Include fee schedules
            5. Show claim status transitions
            6. Add notes for key billing rules

            Return only the Mermaid diagram code wrapped in ```mermaid``` tags.
            """
            
            diagram = query_llm(prompt)
            self.save_diagram(diagram, "05_billing_domain.md")
        except Exception as e:
            log_activity(f"Error generating billing domain diagram: {str(e)}")
            raise

    def generate_patient_encounter_path(self, schema_data: Dict[str, Any]) -> None:
        """
        Generate Artifact #6: Patient to Encounters & Diagnoses pathway diagram.
        Shows how to trace patient's clinical data.
        
        Args:
            schema_data (Dict[str, Any]): Schema data
        """
        try:
            prompt = f"""
            Create a Mermaid diagram showing the path from Patient to Diagnoses:
            {schema_data}

            Requirements:
            1. Show step-by-step path: patient → appointment → encounter → diagnosis
            2. Include key fields for joins
            3. Add notes for common queries
            4. Show cardinality of relationships
            5. Include temporal aspects
            6. Highlight primary/foreign key relationships

            Return only the Mermaid diagram code wrapped in ```mermaid``` tags.
            """
            
            diagram = query_llm(prompt)
            self.save_diagram(diagram, "06_patient_encounter_path.md")
        except Exception as e:
            log_activity(f"Error generating patient-encounter path diagram: {str(e)}")
            raise

    def generate_claim_payment_path(self, schema_data: Dict[str, Any]) -> None:
        """
        Generate Artifact #7: Encounter to Payment pathway diagram.
        Shows financial flow from encounter to payment.
        
        Args:
            schema_data (Dict[str, Any]): Schema data
        """
        try:
            prompt = f"""
            Create a Mermaid diagram showing the path from Encounter to Payment:
            {schema_data}

            Requirements:
            1. Show workflow: encounter → claim → payment batch
            2. Include status transitions
            3. Show payment processing steps
            4. Include validation rules
            5. Show error handling paths
            6. Add notes for payment reconciliation

            Return only the Mermaid diagram code wrapped in ```mermaid``` tags.
            """
            
            diagram = query_llm(prompt)
            self.save_diagram(diagram, "07_claim_payment_path.md")
        except Exception as e:
            log_activity(f"Error generating claim-payment path diagram: {str(e)}")
            raise

    def generate_audit_quality(self, schema_data: Dict[str, Any]) -> None:
        """
        Generate Artifact #8: Data Quality & Audit Trails diagram.
        Shows how audit tables link to main entities.
        
        Args:
            schema_data (Dict[str, Any]): Schema data
        """
        try:
            prompt = f"""
            Create a Mermaid diagram showing Data Quality & Audit relationships:
            {schema_data}

            Requirements:
            1. Show audit table relationships
            2. Include data validation rules
            3. Show quality check points
            4. Include error tracking
            5. Show audit log structure
            6. Add notes for compliance requirements

            Return only the Mermaid diagram code wrapped in ```mermaid``` tags.
            """
            
            diagram = query_llm(prompt)
            self.save_diagram(diagram, "08_audit_quality.md")
        except Exception as e:
            log_activity(f"Error generating audit-quality diagram: {str(e)}")
            raise

    def generate_patient_timeline(self, schema_data: Dict[str, Any]) -> None:
        """
        Generate Artifact #9: Integrated Patient Timeline diagram.
        Shows patient journey through the health system.
        
        Args:
            schema_data (Dict[str, Any]): Schema data
        """
        try:
            prompt = f"""
            Create a Mermaid diagram showing an Integrated Patient Timeline:
            {schema_data}

            Requirements:
            1. Show timeline of patient interactions
            2. Include appointments, encounters, claims
            3. Show parallel workflows
            4. Include status changes
            5. Show document creation points
            6. Add notes for key events

            Return only the Mermaid diagram code wrapped in ```mermaid``` tags.
            """
            
            diagram = query_llm(prompt)
            self.save_diagram(diagram, "09_patient_timeline.md")
        except Exception as e:
            log_activity(f"Error generating patient timeline diagram: {str(e)}")
            raise

    def generate_relationship_heatmap(self, schema_data: Dict[str, Any]) -> None:
        """
        Generate Artifact #10: Entity-Relationship Heatmap diagram.
        Shows connection intensity between entities.
        
        Args:
            schema_data (Dict[str, Any]): Schema data
        """
        try:
            prompt = f"""
            Create a Mermaid diagram showing Entity Relationship patterns:
            {schema_data}

            Requirements:
            1. Show connection intensity between entities
            2. Use color coding for relationship types
            3. Include relationship cardinality
            4. Show data flow direction
            5. Highlight central entities
            6. Add legend for relationship types

            Return only the Mermaid diagram code wrapped in ```mermaid``` tags.
            """
            
            diagram = query_llm(prompt)
            self.save_diagram(diagram, "10_relationship_heatmap.md")
        except Exception as e:
            log_activity(f"Error generating relationship heatmap: {str(e)}")
            raise

    def generate_all_artifacts(
        self,
        schema_data: Dict[str, Any],
        domain_data: Dict[str, Any],
        relationship_data: Dict[str, Any]
    ) -> None:
        """
        Generate all 10 artifacts in sequence.
        
        Args:
            schema_data (Dict[str, Any]): Schema data
            domain_data (Dict[str, Any]): Domain classification data
            relationship_data (Dict[str, Any]): Relationship analysis data
        """
        try:
            # 1. High-level overview
            self.generate_ecosystem_overview(domain_data)
            
            # 2-5. Domain-specific diagrams
            self.generate_patient_domain(schema_data)
            self.generate_encounters_domain(schema_data)
            self.generate_clinical_documentation(schema_data)
            self.generate_billing_domain(schema_data)
            
            # 6-8. Pathway and query-oriented diagrams
            self.generate_patient_encounter_path(schema_data)
            self.generate_claim_payment_path(schema_data)
            self.generate_audit_quality(schema_data)
            
            # 9-10. Advanced integrative views
            self.generate_patient_timeline(schema_data)
            self.generate_relationship_heatmap(schema_data)
            
            log_activity("Completed generation of all artifacts")
        except Exception as e:
            log_activity(f"Error in artifact generation: {str(e)}")
            raise
