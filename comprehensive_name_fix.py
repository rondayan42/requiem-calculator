import json
import os
import re
from difflib import SequenceMatcher

def get_wiki_skill_names(wiki_cache_path):
    skill_map = {}
    wiki_skills = []
    
    for filename in os.listdir(wiki_cache_path):
        match = re.match(r"site_pages_[A-Z0-9]_(.+)\.html\.html", filename)
        if match:
            skill_name_underscore = match.group(1)
            correct_name = skill_name_underscore.replace('_', ' ')
            wiki_skills.append(correct_name)
    
    return wiki_skills

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_best_match(skill_name, wiki_skills, threshold=0.7):
    best_match = None
    best_score = 0
    
    for wiki_skill in wiki_skills:
        score = similarity(skill_name, wiki_skill)
        if score > best_score and score >= threshold:
            best_score = score
            best_match = wiki_skill
    
    return best_match, best_score

def get_manual_corrections():
    """Manual corrections for names that can't be automatically matched"""
    return {
        # Frame -> Flame corrections
        "Frame Nova": "Flame Nova",
        "Frame Thrower": "Flame Thrower", 
        "Frame Stone": "Flame Stone",
        
        # Give -> specific skill corrections  
        "Give Cold Lightning": "Cold Lightning",
        "Give Curse Flame": "Cursed Flame",
        
        # Throw -> specific corrections
        "Throw Cold Lightning": "Cold Lightning Throw",
        "Throw Hydrogen": "Hydrogen Throw",
        "Throw Pollution": "Pollution Throw",
        "Throw Wide": "Wide Throw",
        
        # Other obvious corrections
        "Spining Slash": "Spinning Slash",
        "Bears Stamina": "Bear Stamina",
        "BloodNailTime": "Blood Nail Time",
        
        # DNA skill corrections that might have been missed
        "Unimia": "Stealth", # This might be wrong, keeping as is for now
        
        # Job/class names
        "Battle Magician": "Druid",  # This might need verification
        
        # Common typos
        "Shield Sence": "Shield Sense",
    }

def fix_all_names():
    data_file_path = 'data.json'
    wiki_cache_path = 'wiki_cache'
    
    wiki_skills = get_wiki_skill_names(wiki_cache_path)
    manual_corrections = get_manual_corrections()
    
    with open(data_file_path, 'r') as f:
        data = json.load(f)
    
    updated_count = 0
    corrections_made = {}
    
    # Fix skill names in skills section
    for job_id, skills_list in data['skills'].items():
        for skill in skills_list:
            original_name = skill['name']
            new_name = None
            
            # Check manual corrections first
            if original_name in manual_corrections:
                new_name = manual_corrections[original_name]
                corrections_made[original_name] = f"{new_name} (manual)"
            else:
                # Try fuzzy matching with wiki skills
                best_match, score = find_best_match(original_name, wiki_skills, threshold=0.8)
                if best_match and score > 0.8:
                    new_name = best_match
                    corrections_made[original_name] = f"{new_name} (match: {score:.2f})"
            
            if new_name and skill['name'] != new_name:
                print(f"Updating '{skill['name']}' to '{new_name}'")
                skill['name'] = new_name
                updated_count += 1
    
    # Fix DNA skill names
    for job_id, skills_list in data['dna'].items():
        for skill in skills_list:
            original_name = skill['name']
            new_name = None
            
            # Check manual corrections first
            if original_name in manual_corrections:
                new_name = manual_corrections[original_name]
                corrections_made[original_name] = f"{new_name} (manual)"
            else:
                # Try fuzzy matching with wiki skills
                best_match, score = find_best_match(original_name, wiki_skills, threshold=0.8)
                if best_match and score > 0.8:
                    new_name = best_match
                    corrections_made[original_name] = f"{new_name} (match: {score:.2f})"
            
            if new_name and skill['name'] != new_name:
                print(f"Updating DNA '{skill['name']}' to '{new_name}'")
                skill['name'] = new_name
                updated_count += 1
    
    # Fix job and spec names
    for group in data.get('jobs', {}).values():
        for job in group:
            original_name = job['name']
            new_name = None
            
            if original_name in manual_corrections:
                new_name = manual_corrections[original_name]
            else:
                best_match, score = find_best_match(original_name, wiki_skills, threshold=0.9)
                if best_match and score > 0.9:
                    new_name = best_match
            
            if new_name and job['name'] != new_name:
                print(f"Updating job '{job['name']}' to '{new_name}'")
                job['name'] = new_name
                updated_count += 1
            
            for spec in job.get('specs', []):
                original_spec_name = spec['name']
                spec_new_name = None
                
                if original_spec_name in manual_corrections:
                    spec_new_name = manual_corrections[original_spec_name]
                else:
                    best_match, score = find_best_match(original_spec_name, wiki_skills, threshold=0.9)
                    if best_match and score > 0.9:
                        spec_new_name = best_match
                
                if spec_new_name and spec['name'] != spec_new_name:
                    print(f"Updating spec '{spec['name']}' to '{spec_new_name}'")
                    spec['name'] = spec_new_name
                    updated_count += 1
    
    if updated_count > 0:
        with open(data_file_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\nUpdated {updated_count} names in {data_file_path}")
        
        print(f"\nSummary of corrections made:")
        for original, correction in corrections_made.items():
            print(f"  {original} -> {correction}")
    else:
        print("No names needed updating.")

if __name__ == '__main__':
    fix_all_names()
