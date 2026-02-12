import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from typing import Dict

def export_domain_mapping_to_excel(domain_mapping_json: str, output_path: str) -> str:
    """
    Export domain mapping comparison to Excel file with formatting.
    
    Args:
        domain_mapping_json: JSON string from domain_mapping_agent
        output_path: Path where to save the Excel file
    
    Returns:
        Path to the created Excel file
    """
    try:
        mapping = json.loads(domain_mapping_json)
    except json.JSONDecodeError:
        # If not JSON, try to extract JSON from markdown
        start = domain_mapping_json.find("{")
        end = domain_mapping_json.rfind("}") + 1
        if start != -1 and end > start:
            mapping = json.loads(domain_mapping_json[start:end])
        else:
            raise ValueError("Could not parse domain mapping JSON")
    
    wb = Workbook()
    
    # Define styles
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # 1️⃣ Summary Sheet
    ws_summary = wb.active
    ws_summary.title = "Summary"
    
    ws_summary['A1'] = "Domain Mapping Summary"
    ws_summary['A1'].font = Font(bold=True, size=16)
    ws_summary.merge_cells('A1:B1')
    
    summary = mapping.get("mappingSummary", {})
    row = 3
    for key, value in summary.items():
        ws_summary[f'A{row}'] = key.replace("_", " ").title()
        ws_summary[f'B{row}'] = value
        ws_summary[f'A{row}'].font = Font(bold=True)
        row += 1
    
    # 2️⃣ Entity Mappings Sheet
    ws_entities = wb.create_sheet("Entity Mappings")
    
    headers = ["Source Entity", "Target Entity", "Mapping Type", "Confidence", "Complexity", "Notes"]
    for col, header in enumerate(headers, 1):
        cell = ws_entities.cell(1, col, header)
        cell.fill = header_fill
        cell.font = header_font
        cell.border = border
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    row = 2
    for entity_map in mapping.get("entityMappings", []):
        ws_entities.cell(row, 1, entity_map.get("sourceEntity", ""))
        ws_entities.cell(row, 2, entity_map.get("targetEntity", ""))
        ws_entities.cell(row, 3, entity_map.get("mappingType", ""))
        ws_entities.cell(row, 4, f"{entity_map.get('confidence', 0)}%")
        ws_entities.cell(row, 5, entity_map.get("migrationComplexity", ""))
        ws_entities.cell(row, 6, entity_map.get("notes", ""))
        
        # Apply borders
        for col in range(1, 7):
            ws_entities.cell(row, col).border = border
        
        # Color code by confidence
        confidence = entity_map.get("confidence", 0)
        if confidence >= 80:
            fill_color = "C6EFCE"  # Green
        elif confidence >= 60:
            fill_color = "FFEB9C"  # Yellow
        else:
            fill_color = "FFC7CE"  # Red
        ws_entities.cell(row, 4).fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
        
        row += 1
    
    # Auto-adjust column widths
    for col in range(1, 7):
        ws_entities.column_dimensions[get_column_letter(col)].width = 20
    
    # 3️⃣ Property Mappings Sheet
    ws_props = wb.create_sheet("Property Mappings")
    
    prop_headers = ["Entity", "Source Property", "Target Property", "Data Type Match", "Transformation", "Confidence"]
    for col, header in enumerate(prop_headers, 1):
        cell = ws_props.cell(1, col, header)
        cell.fill = header_fill
        cell.font = header_font
        cell.border = border
    
    row = 2
    for entity_map in mapping.get("entityMappings", []):
        entity_name = entity_map.get("sourceEntity", "")
        for prop_map in entity_map.get("propertyMappings", []):
            ws_props.cell(row, 1, entity_name)
            ws_props.cell(row, 2, prop_map.get("sourceProperty", ""))
            ws_props.cell(row, 3, prop_map.get("targetProperty", ""))
            ws_props.cell(row, 4, "Yes" if prop_map.get("dataTypeCompatible") else "No")
            ws_props.cell(row, 5, prop_map.get("transformation", "None"))
            ws_props.cell(row, 6, f"{prop_map.get('confidence', 0)}%")
            
            for col in range(1, 7):
                ws_props.cell(row, col).border = border
            
            # Color code data type compatibility
            if prop_map.get("dataTypeCompatible"):
                ws_props.cell(row, 4).fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
            else:
                ws_props.cell(row, 4).fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
            
            row += 1
    
    for col in range(1, 7):
        ws_props.column_dimensions[get_column_letter(col)].width = 18
    
    # 4️⃣ Unmapped Entities Sheet
    ws_unmapped = wb.create_sheet("Unmapped Entities")
    
    ws_unmapped['A1'] = "Source Entities Not Mapped"
    ws_unmapped['A1'].font = Font(bold=True, size=14)
    ws_unmapped.merge_cells('A1:C1')
    
    unmap_headers = ["Entity", "Reason", "Recommendation"]
    for col, header in enumerate(unmap_headers, 1):
        cell = ws_unmapped.cell(2, col, header)
        cell.fill = header_fill
        cell.font = header_font
    
    row = 3
    for unmapped in mapping.get("unmappedSourceEntities", []):
        ws_unmapped.cell(row, 1, unmapped.get("entity", ""))
        ws_unmapped.cell(row, 2, unmapped.get("reason", ""))
        ws_unmapped.cell(row, 3, unmapped.get("recommendation", ""))
        row += 1
    
    row += 2
    ws_unmapped.cell(row, 1, "Target Entities Without Source").font = Font(bold=True, size=14)
    ws_unmapped.merge_cells(f'A{row}:C{row}')
    
    row += 1
    for col, header in enumerate(["Entity", "Reason", "Data Source"], 1):
        cell = ws_unmapped.cell(row, col, header)
        cell.fill = header_fill
        cell.font = header_font
    
    row += 1
    for unmapped in mapping.get("unmappedTargetEntities", []):
        ws_unmapped.cell(row, 1, unmapped.get("entity", ""))
        ws_unmapped.cell(row, 2, unmapped.get("reason", ""))
        ws_unmapped.cell(row, 3, unmapped.get("dataSource", ""))
        row += 1
    
    # 5️⃣ Transformation Rules Sheet
    ws_transform = wb.create_sheet("Transformation Rules")
    
    trans_headers = ["Rule", "Source Pattern", "Target Pattern", "Complexity", "Example"]
    for col, header in enumerate(trans_headers, 1):
        cell = ws_transform.cell(1, col, header)
        cell.fill = header_fill
        cell.font = header_font
    
    row = 2
    for rule in mapping.get("transformationRules", []):
        ws_transform.cell(row, 1, rule.get("rule", ""))
        ws_transform.cell(row, 2, rule.get("sourcePattern", ""))
        ws_transform.cell(row, 3, rule.get("targetPattern", ""))
        ws_transform.cell(row, 4, rule.get("complexity", ""))
        ws_transform.cell(row, 5, rule.get("example", ""))
        row += 1
    
    for col in range(1, 6):
        ws_transform.column_dimensions[get_column_letter(col)].width = 25
    
    # Save the workbook
    wb.save(output_path)
    print(f"✅ Excel file created: {output_path}")
    return output_path


def create_sample_domain_mapping_excel():
    """Create a sample Excel file for testing"""
    sample_mapping = {
        "mappingSummary": {
            "totalSourceEntities": 5,
            "totalTargetEntities": 6,
            "directMappings": 3,
            "transformationRequired": 2,
            "unmappedSource": 1,
            "unmappedTarget": 1,
            "overallCompatibility": "High"
        },
        "entityMappings": [
            {
                "sourceEntity": "Loan",
                "targetEntity": "LoanApplication",
                "confidence": 95,
                "mappingType": "Direct",
                "migrationComplexity": "Low",
                "notes": "Direct mapping with minor field renames",
                "propertyMappings": [
                    {
                        "sourceProperty": "loanId",
                        "targetProperty": "id",
                        "dataTypeCompatible": True,
                        "transformation": None,
                        "confidence": 100
                    },
                    {
                        "sourceProperty": "principalAmount",
                        "targetProperty": "principal",
                        "dataTypeCompatible": True,
                        "transformation": "Rename field",
                        "confidence": 95
                    }
                ]
            }
        ],
        "unmappedSourceEntities": [],
        "unmappedTargetEntities": [],
        "transformationRules": []
    }
    
    output_path = "/mnt/user-data/outputs/domain_mapping_sample.xlsx"
    return export_domain_mapping_to_excel(json.dumps(sample_mapping), output_path)
