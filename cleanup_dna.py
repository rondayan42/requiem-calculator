#!/usr/bin/env python3
import json
from pathlib import Path

DATA_JSON = Path(__file__).resolve().parent / 'data.json'

def main():
    data = json.loads(DATA_JSON.read_text(encoding='utf-8'))
    
    total_removed = 0
    total_kept = 0
    
    # Clean up DNA entries
    for spec_id, dna_list in (data.get('dna') or {}).items():
        original_count = len(dna_list)
        
        # Filter out generic "DNA Stats" entries and keep only meaningful ones
        filtered_dna = []
        for dna in dna_list:
            name = dna.get('name', '').strip()
            
            # Keep DNA entries that have meaningful names (not just "DNA Stats")
            if name and name != "DNA Stats" and not name.startswith("DNA Stats"):
                filtered_dna.append(dna)
                total_kept += 1
            else:
                total_removed += 1
        
        # Update the DNA list for this spec
        data['dna'][spec_id] = filtered_dna
        
        if original_count != len(filtered_dna):
            print(f"Spec {spec_id}: {original_count} -> {len(filtered_dna)} DNA entries ({original_count - len(filtered_dna)} removed)")
    
    # Save the cleaned data
    if total_removed > 0:
        DATA_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"\nCleaned up DNA data:")
        print(f"- Removed: {total_removed} generic 'DNA Stats' entries")
        print(f"- Kept: {total_kept} meaningful DNA enhancements")
        print(f"- Updated data.json")
    else:
        print("No DNA cleanup needed.")

if __name__ == '__main__':
    main()
