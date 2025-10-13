# 🔐 Configurare Securizată API Keys

Această documentație explică cum să configurezi în siguranță cheile API pentru AI-WebAgent-Extractor folosind noul sistem centralizat.

## 📁 Structura de Configurare

```
AI-webagent_extractor/
├── config/
│   ├── .env.example          # Template pentru configurare
│   ├── .env                  # Configurarea ta reală (NU o commite!)
│   ├── env_config.py         # Sistem centralizat de configurare
│   └── migrate_config.py     # Script de migrare
└── .gitignore               # Asigură că .env nu este committată
```

## 🚀 Setup Rapid

### 1. Copiază template-ul
```bash
cd AI-webagent_extractor
cp config/.env.example config/.env
```

### 2. Editează cu cheile tale reale
```bash
# Deschide config/.env și actualizează cu cheile tale
notepad config/.env  # Windows
nano config/.env     # Linux/Mac
```

### 3. Configurează cheile API
```env
# AI API Keys (setează cel puțin una)
OPENAI_API_KEY=sk-proj-your-real-openai-key-here
GEMINI_API_KEY=your-real-gemini-key-here

# Traffic Analysis API Keys (opțional)
SEMRUSH_API_KEY=your-semrush-key-here
SIMILARWEB_API_KEY=your-similarweb-key-here

# Configurare Scraping
DEFAULT_DELAY=2
MAX_RETRIES=3
MAX_WORKERS=5

# Selecția providerului AI (openai, gemini, auto)
AI_PROVIDER=auto
```

## 🔧 Utilizare în Cod

### Import Simplificat
```python
from config.env_config import get_environment_config, validate_environment

# Obține configurarea
config = get_environment_config()

# Obține chei API specifice
openai_key = config.get_openai_api_key()
gemini_key = config.get_gemini_api_key()

# Auto-selectează cel mai bun provider disponibil
provider, api_key = config.select_ai_provider()
```

### Validare Configurare
```python
from config.env_config import validate_environment

# Verifică configurarea
validation = validate_environment()

if validation['valid']:
    print(f"✅ Configurare validă! Provideri disponibili: {validation['available_providers']}")
else:
    print("❌ Probleme cu configurarea:")
    for error in validation['errors']:
        print(f"  - {error}")
```

### Utilizare în Scraper
```python
from darwin_scraper_complete import DarwinProductScraper

# Inițializează scraper-ul - va folosi automat configurarea centralizată
scraper = DarwinProductScraper()

# Sau specifică manual providerul
scraper = DarwinProductScraper(ai_provider="gemini")
```

## 🛡️ Securitate

### ✅ Bune Practici
- ✅ Folosește `config/.env` pentru configurarea locală
- ✅ Nu commita niciodată fișiere `.env` cu chei reale
- ✅ Folosește `AI_PROVIDER=auto` pentru selecție automată
- ✅ Folosește funcția `validate_environment()` pentru verificări

### ❌ Evită
- ❌ Nu pune chei API în cod
- ❌ Nu commita fișiere `.env` în git
- ❌ Nu lăsa chei în comentarii sau log-uri
- ❌ Nu împărți chei API prin email sau chat

## 🔄 Migrare de la Configurarea Veche

Dacă ai deja fișiere `.env` în locații vechi, folosește scriptul de migrare:

```bash
python config/migrate_config.py
```

Acest script va:
1. Găsi toate fișierele `.env` existente
2. Migrează cheile în `config/.env`
3. Actualizează `.gitignore`
4. Testează noua configurare

## 🧪 Testare Configurare

### Test Rapid
```bash
python config/env_config.py
```

### Test Detaliat
```python
from config.env_config import validate_environment

validation = validate_environment()
print(f"Status: {'✅ Valid' if validation['valid'] else '❌ Invalid'}")
print(f"Provideri disponibili: {validation['available_providers']}")
print(f"Provider selectat: {validation['config']['selected_provider']}")
```

## 📊 Prioritatea Configurării

Sistemul încarcă configurarea în următoarea ordine de prioritate:

1. **Variabile de mediu** (prioritate maximă)
2. **Streamlit secrets** (dacă rulezi în Streamlit)  
3. **config/.env** (configurarea locală)

## 🚨 Depanare

### Probleme Comune

**"No AI API keys configured"**
```bash
# Verifică că ai setat cel puțin o cheie API
grep -E "(OPENAI|GEMINI)_API_KEY" config/.env
```

**"Import env_config could not be resolved"**
```python
# Asigură-te că calea config/ este în sys.path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'config'))
```

**"Configuration valid: False"**
```python
# Rulează testul pentru detalii
from config.env_config import validate_environment
print(validate_environment())
```

## 📝 Exemple de Configurare

### Doar OpenAI
```env
OPENAI_API_KEY=sk-proj-your-key-here
AI_PROVIDER=openai
```

### Doar Gemini  
```env
GEMINI_API_KEY=your-gemini-key-here
AI_PROVIDER=gemini
```

### Ambele (auto-selecție)
```env
OPENAI_API_KEY=sk-proj-your-openai-key-here
GEMINI_API_KEY=your-gemini-key-here
AI_PROVIDER=auto
```

### Cu Traffic Analysis
```env
OPENAI_API_KEY=sk-proj-your-key-here
SEMRUSH_API_KEY=your-semrush-key-here
SIMILARWEB_API_KEY=your-similarweb-key-here
```

## 🎯 Beneficii

- ✅ **Securitate maximă** - chei separate de cod
- ✅ **Configurare centralizată** - un singur loc pentru toate cheile
- ✅ **Auto-selecție provider** - alege automat cel mai bun AI disponibil
- ✅ **Validare automată** - verifică configurarea la pornire
- ✅ **Backward compatibility** - funcționează cu codul existent
- ✅ **Flexibilitate** - suportă multiple surse de configurare

---

Pentru mai multe detalii, consultă [env_config.py](./env_config.py) sau rulează `python config/env_config.py` pentru test.