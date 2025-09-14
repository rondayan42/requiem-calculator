import json
import os
import re

def get_wiki_skill_names(wiki_cache_path):
    skill_map = {}
    for filename in os.listdir(wiki_cache_path):
        match = re.match(r"site_pages_[A-Z0-9]_(.+)\.html\.html", filename)
        if match:
            skill_name_underscore = match.group(1)
            correct_name = skill_name_underscore.replace('_', ' ')
            normalized_name = correct_name.lower().replace(' ', '')
            skill_map[normalized_name] = correct_name
    return skill_map

def get_dna_name_mappings():
    return {
        "BlessofBody": "Bless of Body",
        "DesireforLife": "Desire for Life",
        "AttentionAccuracy": "Attention Accuracy",
        "ShieldHitAccuracy": "Shield Hit Accuracy",
        "ShieldIntensify": "Shield Intensify",
        "EquilibriumTime": "Equilibrium Time",
        "RemedyCast": "Remedy Cast",
        "ShieldSence": "Shield Sence",
        "SelfHeal": "Self Heal",
        "LightningShield": "Lightning Shield",
        "SelfLightningShockCast": "Self Lightning Shock Cast",
        "BlessofMana": "Bless of Mana",
        "LightHeal": "Light Heal",
        "LightningShockCooltime": "Lightning Shock Cooltime",
        "SelfLightningShock": "Self Lightning Shock",
        "LightHealCast": "Light Heal Cast",
        "LightHealMana": "Light Heal Mana",
        "HolyReflectionAccuracy": "Holy Reflection Accuracy",
        "HolyReflectionTime": "Holy Reflection Time",
        "LightPartyHeal": "Light Party Heal",
        "LastDitch": "Last Ditch",
        "DashCooltime": "Dash Cooltime",
        "HammerTheButcher": "Hammer The Butcher",
        "BlessofBodyTime": "Bless of Body Time",
        "DoubleHandMaster": "Double Hand Master",
        "BurningHell": "Burning Hell",
        "IronPhysics": "Iron Physics",
        "TwoHandMaster": "Two Hand Master",
        "Unblocking": "Unblocking",
        "FireBall": "Fire Ball",
        "FlameThrower": "Flame Thrower",
        "CharmOfMana": "Charm Of Mana",
        "FlameArrow": "Flame Arrow",
        "FlameNova": "Flame Nova",
        "DutchCourage": "Dutch Courage",
        "BurningHellLonger": "Burning Hell Longer",
        "FlameThrowerCast": "Flame Thrower Cast",
        "FlameShield": "Flame Shield",
        "FireTotemCast": "Fire Totem Cast",
        "PlagueCharm": "Plague Charm",
        "FireRain": "Fire Rain",
        "FireRainCast": "Fire Rain Cast",
        "SpeedWeaponTime": "Speed Weapon Time",
        "LegStrikeTime": "Leg Strike Time",
        "ConcentrateTime": "Concentrate Time",
        "RangeWeaponMaster": "Range Weapon Master",
        "ArmourCrashComboTime": "Armour Crash Combo Time",
        "ScrewAttackTime": "Screw Attack Time",
        "BloodBoltTime": "Blood Bolt Time",
        "VampireTouch": "Vampire Touch",
        "PrisonTime": "Prison Time",
        "BloodNailTime": "Blood Nail Time",
        "PoisonNova": "Poison Nova",
        "BloodBusterWide": "Blood Buster Wide",
        "TimeBomb": "Time Bomb"
    }


def convert_names_from_russian():
    data_file_path = 'data.json'

    with open(data_file_path, 'r') as f:
        data = json.load(f)

    updated_count = 0
    
    dna_mappings = get_dna_name_mappings()

    for job_id, skills_list in data['dna'].items():
        for skill in skills_list:
            if skill['name'] in dna_mappings:
                new_name = dna_mappings[skill['name']]
                if skill['name'] != new_name:
                    print(f"Updating '{skill['name']}' to '{new_name}'")
                    skill['name'] = new_name
                    updated_count += 1
            elif "DNA Stats" not in skill['name']:
                # Add spaces before capital letters as a fallback
                new_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', skill['name'])
                if skill['name'] != new_name:
                    print(f"Updating '{skill['name']}' to '{new_name}' (fallback)")
                    skill['name'] = new_name
                    updated_count += 1

    if updated_count > 0:
        with open(data_file_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Updated {updated_count} skill names in {data_file_path}")
    else:
        print("No skill names needed updating.")

def convert_names():
    data_file_path = 'data.json'
    wiki_cache_path = 'wiki_cache'

    wiki_skills = get_wiki_skill_names(wiki_cache_path)

    with open(data_file_path, 'r') as f:
        data = json.load(f)

    updated_count = 0

    for section in ['skills']:
        if section in data:
            for job_id, skills_list in data[section].items():
                for skill in skills_list:
                    original_name = skill['name']
                    normalized_original = original_name.lower().replace(' ', '')
                    if normalized_original in wiki_skills:
                        new_name = wiki_skills[normalized_original]
                        if skill['name'] != new_name:
                            print(f"Updating '{skill['name']}' to '{new_name}'")
                            skill['name'] = new_name
                            updated_count += 1
                    # A special case for Radient -> Radiant
                    elif normalized_original == "radient":
                         if "radiant" in wiki_skills:
                            new_name = wiki_skills["radiant"]
                            if skill['name'] != new_name:
                                print(f"Updating '{skill['name']}' to '{new_name}'")
                                skill['name'] = new_name
                                updated_count += 1


    # Also check job and spec names
    for group in data.get('jobs', {}).values():
        for job in group:
            original_name = job['name']
            normalized_original = original_name.lower().replace(' ', '')
            if normalized_original in wiki_skills and job['name'] != wiki_skills[normalized_original]:
                 print(f"Updating job name '{job['name']}' to '{wiki_skills[normalized_original]}'")
                 job['name'] = wiki_skills[normalized_original]
                 updated_count += 1

            for spec in job.get('specs', []):
                original_spec_name = spec['name']
                normalized_spec = original_spec_name.lower().replace(' ', '')
                if normalized_spec in wiki_skills and spec['name'] != wiki_skills[normalized_spec]:
                    print(f"Updating spec name '{spec['name']}' to '{wiki_skills[normalized_spec]}'")
                    spec['name'] = wiki_skills[normalized_spec]
                    updated_count += 1
                elif normalized_spec == "radient" and "radiant" in wiki_skills:
                    new_name = wiki_skills["radiant"]
                    if spec['name'] != new_name:
                        print(f"Updating '{spec['name']}' to '{new_name}'")
                        spec['name'] = new_name
                        updated_count += 1


    if updated_count > 0:
        with open(data_file_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Updated {updated_count} skill names in {data_file_path}")
    else:
        print("No skill names needed updating.")

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    convert_names()
    convert_names_from_russian()
