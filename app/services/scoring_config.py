# app/services/scoring_config.py

# =========================================
# 🟢 STARK POSITIVE GRUPPEN
# =========================================

STRONG_POSITIVE_GROUPS = [
    {
        "name": "game_development",
        "weight": 20,
        "variants": [
            "game",
            "games",
            "spiel",
            "spiele",
            "game development",
            "spieleentwicklung",
            "unity",
            "godot",
            "game engine",
            "gamedesign",
            "interactive game",
            "serious game",
            "lernspiel",
        ],
    },
    {
        "name": "ar_vr_xr",
        "weight": 20,
        "variants": [
            "vr",
            "virtual reality",
            "ar",
            "augmented reality",
            "xr",
            "extended reality",
            "mixed reality",
            "immersive",
            "immersiv",
            "3d experience",
            "vr application",
            "ar application",
        ],
    },
    {
        "name": "simulation_training",
        "weight": 18,
        "variants": [
            "simulation",
            "simulator",
            "training software",
            "training system",
            "gamification",
            "learning app",
            "lernsoftware",
            "education software",
            "edutainment",
            "interactive learning",
            "trainingssoftware",
            "interaktive lernanwendung",
            "digitale lernerfahrung",
        ],
    },
    {
        "name": "mobile_app",
        "weight": 16,
        "variants": [
            "mobile app",
            "app",
            "app entwicklung",
            "android app",
            "ios app",
            "smartphone app",
            "mobile application",
        ],
    },
    {
        "name": "web_app",
        "weight": 16,
        "variants": [
            "web app",
            "web application",
            "webseite",
            "website",
            "frontend",
            "backend",
            "portal",
            "internetangebot",
            "online system",
            "webportal",
            "online portal",
            "plattform",
        ],
    },
    {
        "name": "web_redesign_ux_ui",
        "weight": 18,
        "variants": [
            "redesign",
            "relaunch",
            "web redesign",
            "website redesign",
            "ux",
            "ui",
            "user experience",
            "user interface",
            "usability",
            "frontend design",
            "interface design",
            "visuelles design",
            "webauftritt",
            "digital experience",
            "informationsarchitektur",
        ],
    },
    {
        "name": "software_development",
        "weight": 16,
        "variants": [
            "softwareentwicklung",
            "software development",
            "application development",
            "programmierung",
            "systementwicklung",
            "digital solution",
        ],
    },
    {
        "name": "interactive_systems",
        "weight": 16,
        "variants": [
            "interactive",
            "interaktiv",
            "interface",
            "multimedia",
            "3d",
            "animation",
            "interaktive medien",
            "interaktive anwendung",
            "interactive platform",
            "interactive system",
        ],
    },
    {
        "name": "visitor_experience_apps",
        "weight": 16,
        "variants": [
            "guide",
            "audio guide",
            "besucher",
            "visitor",
            "museum app",
            "zoo app",
            "tourismus app",
            "tourism app",
            "erlebnis",
            "experience app",
            "infoterminal",
            "info app",
        ],
    },
    {
        "name": "gamification",
        "weight": 16,
        "variants": [
            "gamification",
            "serious game",
            "spielbasiert",
            "interaktive lernanwendung",
            "digitale lernerfahrung",
        ],
    },
]

# =========================================
# 🟡 MITTEL POSITIVE GRUPPEN
# =========================================

MEDIUM_POSITIVE_GROUPS = [
    {
        "name": "software_general",
        "weight": 4,
        "variants": [
            "software",
            "digitalisierung",
            "digital",
            "application",
            "system",
            "plattform",
            "portal",
        ],
    },
    {
        "name": "education_learning",
        "weight": 8,
        "variants": [
            "bildung",
            "lernen",
            "lernplattform",
            "unterricht",
            "didaktik",
            "edtech",
            "e learning",
            "elearning",
            "lernumgebung",
            "trainingsumgebung",
        ],
    },
    {
        "name": "creative_media",
        "weight": 8,
        "variants": [
            "medien",
            "multimedia",
            "visualisierung",
            "3d modell",
            "interaktive medien",
            "content",
            "animation",
            "motion design",
        ],
    },
    {
        "name": "public_experience_context",
        "weight": 6,
        "variants": [
            "zoo",
            "museum",
            "ausstellung",
            "tourismus",
            "tourism",
            "besucherinformation",
            "visitor information",
            "kultur",
        ],
    },
]

# =========================================
# 🔴 STARK NEGATIVE GRUPPEN
# =========================================

STRONG_NEGATIVE_GROUPS = [
    {
        "name": "sap_erp_enterprise",
        "weight": -22,
        "variants": [
            "sap",
            "s4hana",
            "hana",
            "sap hana",
            "sap s4",
            "successfactors",
            "erp",
            "crm",
            "utilities transformation",
            "datenmigration",
            "enterprise resource planning",
        ],
    },
    {
        "name": "infrastructure_operations",
        "weight": -20,
        "variants": [
            "infrastruktur",
            "network",
            "netzwerk",
            "server",
            "hosting",
            "datacenter",
            "rechenzentrum",
            "cloud migration",
            "firewall",
            "it betrieb",
            "betrieb",
            "wartung",
            "maintenance",
            "support",
            "24x7",
            "24 7",
            "lizenz",
            "lizenzverlaengerung",
            "renewal",
            "refresh",
            "managed service",
            "managed services",
            "betriebsunterstuetzung",
            "sicherstellung des betriebs",
            "plattformbetrieb",
            "servicebetrieb",
        ],
    },
    {
        "name": "hardware_procurement",
        "weight": -20,
        "variants": [
            "beschaffung",
            "lieferung",
            "hardware",
            "geraete",
            "videosysteme",
            "telefonanlage",
            "monitor",
            "drucker",
            "notebook",
            "laptop",
            "pc system",
            "einzelplatzlizenzen",
        ],
    },
    {
        "name": "construction_facility",
        "weight": -20,
        "variants": [
            "bau",
            "neubau",
            "umbau",
            "liegenschaft",
            "gebaeudemanagement",
            "facility management",
            "cafm",
            "glt",
            "schliessanlage",
            "schliesssystem",
            "gebaeudeautomation",
        ],
    },
    {
        "name": "security_networking",
        "weight": -20,
        "variants": [
            "isms",
            "bcms",
            "it sicherheit",
            "virenschutz",
            "zwei faktor authentifizierung",
            "authentifizierung",
            "wan",
            "layer 2",
            "netzwerktechnik",
            "standortvernetzung",
            "festnetzanschluesse",
        ],
    },
    {
        "name": "enterprise_admin_software",
        "weight": -18,
        "variants": [
            "projektportfoliomanagement",
            "portfoliomanagement",
            "ppm",
            "hr software",
            "personalsoftware",
            "verwaltungssoftware",
            "geschaeftsprozesse",
            "prozessmanagement",
            "workflow management",
            "managementsoftware",
        ],
    },
]

# =========================================
# 🟠 MITTEL NEGATIVE GRUPPEN
# =========================================

MEDIUM_NEGATIVE_GROUPS = [
    {
        "name": "archive_scan_post",
        "weight": -14,
        "variants": [
            "papierakten",
            "aktendigitalisierung",
            "bauaktenarchiv",
            "aktenarchiv",
            "archiv",
            "lagerung",
            "postdienst",
            "hybrid post",
            "hybrid postdienst",
            "scan service",
            "digitalisierung von papierakten",
        ],
    },
    {
        "name": "consulting_only",
        "weight": -14,
        "variants": [
            "consulting",
            "beratung",
            "strategy consulting",
            "prozessberatung",
            "managementberatung",
            "beratungs und unterstuetzungsleistungen",
            "projektbegleitung",
            "begleitung",
            "einfuehrung",
            "etablierung",
            "kompetenzcenter",
        ],
    },
    {
        "name": "outsourcing_services",
        "weight": -12,
        "variants": [
            "outsourcing",
            "it services",
            "managed services",
            "betriebsunterstuetzung",
            "externalisierung",
        ],
    },
    {
        "name": "other_industries",
        "weight": -14,
        "variants": [
            "reinigung",
            "entsorgung",
            "transport",
            "labor",
            "medizin",
            "sicherheitssystem",
            "post",
            "logistik",
            "fahrzeug",
            "busse",
            "fahrgastzaehlsystem",
            "strassenzustand",
            "ridepooling",
            "oepnv",
            "messnetz",
            "smart city",
        ],
    },
]

# =========================================
# ⛔ HARTE AUSSCHLUSS-MARKER
# =========================================

HARD_EXCLUDE_STATUS = [
    "aufgehoben",
    "eingestellt",
    "beendet",
    "nicht vergeben",
    "vergeben",
    "zuschlag erteilt",
    "abgeschlossen",
]

# =========================================
# ⚠️ WEICHE WARNUNGEN
# =========================================

SOFT_WARNING_STATUS = [
    "teilnahmewettbewerb",
    "verhandlungsverfahren",
    "nur teilnahmeantrag",
    "bewerbungsphase",
]

# =========================================
# 📅 FRIST-BEWERTUNG
# =========================================

MIN_GOOD_DAYS = 21
MIN_ACCEPTABLE_DAYS = 10
MIN_BAD_DAYS = 5