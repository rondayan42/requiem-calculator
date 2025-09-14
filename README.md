# Requiem Skill Calculator (English)

A web-based character build planner for **Requiem: Memento Mori** (Desiderium Mortis) MMORPG with full English translation and modern interface.

![Requiem Logo](Requiemlogo.png)

## 🎮 Features

- **Interactive Skill Calculator**: Plan your character builds with real-time validation
- **4 Races Available**: Turian, Bartuk, Kruxena, and Xenoa
- **Multiple Classes & Specializations**: Each race has unique classes with specialization paths
- **Smart Skill Dependencies**: Automatic requirement checking and highlighting
- **DNA Enhancement System**: Plan your DNA upgrades alongside skills
- **Level-Based Point Allocation**: Accurate skill point calculation per character level (1-90)
- **Rich Tooltips**: Detailed skill information with stats, cooldowns, and descriptions
- **Responsive Design**: Works on desktop and mobile devices
- **Dark Theme**: Beautiful Requiem-themed interface

## 🚀 Quick Start

1. **Open the Calculator**: Simply open `index.html` in your web browser
2. **Select Your Race**: Choose from Turian, Bartuk, Kruxena, or Xenoa
3. **Pick Your Class**: Select your primary class and specialization
4. **Set Character Level**: Use the slider to set your target level (1-90)
5. **Allocate Points**: Click +/- buttons to distribute skill points
6. **Plan DNA**: Enhance your build with DNA upgrades

## 📁 Project Structure

```
english-calculator/
├── index.html              # Main web application
├── app.js                  # Calculator logic and UI
├── data.json              # Processed game data
├── Requiemlogo.png        # Game logo
├── sources/               # Raw extracted data files
├── wiki_cache/            # Cached wiki pages
└── data-processing/       # Python scripts for data extraction
    ├── extract_data.py
    ├── scrape_wiki.py
    ├── extract_requirements_from_wiki.py
    ├── enrich_with_skill_stats.py
    ├── enrich_with_full_requirements.py
    ├── convert_skill_names.py
    ├── comprehensive_name_fix.py
    ├── cleanup_dna.py
    ├── fetch_wayback_ajax.py
    └── fetch_wayback_sources.py
```

## 🔧 Data Processing

This project includes a comprehensive data extraction and processing pipeline:

### Data Sources
- **Official Requiem Wiki**: Scraped for skill information and requirements
- **Wayback Machine Archives**: Historical calculator data recovery
- **Game Client Data**: Extracted assets and configurations

### Processing Scripts

| Script | Purpose |
|--------|---------|
| `scrape_wiki.py` | Scrapes the Requiem wiki for skill data |
| `extract_data.py` | Processes archived calculator HTML/JS files |
| `extract_requirements_from_wiki.py` | Extracts skill prerequisites from wiki |
| `enrich_with_skill_stats.py` | Adds detailed skill statistics |
| `enrich_with_full_requirements.py` | Enriches requirement data |
| `convert_skill_names.py` | Standardizes skill names |
| `comprehensive_name_fix.py` | Fixes naming inconsistencies |
| `cleanup_dna.py` | Processes DNA enhancement data |
| `fetch_wayback_*.py` | Retrieves archived data from Wayback Machine |

### Running Data Processing

```bash
# Scrape wiki data
python scrape_wiki.py

# Extract data from archives
python extract_data.py

# Process and enrich data
python extract_requirements_from_wiki.py
python enrich_with_skill_stats.py
python enrich_with_full_requirements.py

# Generate final data.json
python convert_skill_names.py
```

## 🎯 Skill System

### Races & Classes

| Race | Classes |
|------|---------|
| **Turian** | Defender → Commander/Protector<br>Templar → Tempest/Crusader |
| **Bartuk** | Warrior → Berserker/Guardian<br>Shaman → Witch Doctor/Elementalist |
| **Kruxena** | Rogue → Assassin/Shadow<br>Soul Hunter → Reaper/Necromancer |
| **Xenoa** | Hunter → Ranger/Beast Master<br>Battle Magician → Sorcerer/Warlock |

### Point System
- **Skill Points**: Based on character level (1-90)
- **DNA Points**: Fixed allocation for enhancements
- **Requirements**: Level gates and skill prerequisites
- **Dependencies**: Hierarchical skill unlocking

## 🌟 Features in Detail

### Smart Requirement Checking
- Real-time validation of skill prerequisites
- Visual highlighting of unmet requirements  
- Automatic dependency resolution
- Character level gating per skill level

### Interactive Interface
- Hover tooltips with comprehensive skill information
- Click-and-hold for detailed stats
- Keyboard navigation support
- Mobile-responsive design

### Build Planning
- Save/load builds (via browser storage)
- Reset functionality
- Point distribution tracking
- Future level planning

## 🛠️ Technical Details

- **Frontend**: Pure HTML5, CSS3, and JavaScript (ES6+)
- **Data Format**: JSON-based skill and requirement data
- **Processing**: Python 3.7+ with standard library
- **Styling**: Custom CSS with CSS Grid and Flexbox
- **Fonts**: Google Fonts (Cinzel, Inter)

## 📋 Requirements

### For Using the Calculator
- Modern web browser (Chrome, Firefox, Safari, Edge)
- JavaScript enabled
- No server or installation required

### For Data Processing
- Python 3.7 or higher
- Internet connection (for scraping)
- No additional dependencies required

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- **Translations**: Additional language support
- **Data Updates**: Keep skill information current
- **Features**: New calculator functionality
- **Bug Fixes**: Report issues and submit fixes

## 📄 License

This project is a community tool for Requiem players. Game data and assets belong to their respective owners.

## 🔗 Related Links

- [Requiem Wiki](https://rondayan42.github.io/requiem-wiki/) - Primary data source (2009 Archive)

## 📝 Changelog

### Current Version
- Full English translation
- Complete skill trees for all races/classes
- DNA enhancement system
- Modern responsive interface
- Comprehensive requirement validation

---
