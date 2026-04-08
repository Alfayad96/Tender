STRONG_POSITIVE_GROUPS = [
    {
        "name": "mobile_app",
        "weight": 18,
        "variants": [
            "app",
            "apps",
            "mobile app",
            "mobile-app",
            "mobile application",
            "mobile applications",
            "mobile anwendung",
            "app entwicklung",
            "app-entwicklung",
            "app development",
            "app entwickler",
            "app programmierung"
        ]
    },
    {
        "name": "web_app",
        "weight": 18,
        "variants": [
            "webapp",
            "web-app",
            "web apps",
            "web application",
            "web applications",
            "webapplication",
            "webapplikation",
            "web applikation",
            "web application development",
            "webentwicklung",
            "website",
            "webseite",
            "internetangebot",
            "online portal",
            "online-portal"
        ]
    },
    {
        "name": "software_development",
        "weight": 18,
        "variants": [
            "softwareentwicklung",
            "software-entwicklung",
            "software development",
            "entwicklung",
            "weiterentwicklung",
            "software engineer",
            "software engineering",
            "software solution",
            "software lösung",
            "anwendungsentwicklung",
            "programmierung",
            "implementation",
            "implementierung",
            "custom software",
            "individuell software"
        ]
    },
    {
        "name": "game_development",
        "weight": 22,
        "variants": [
            "game",
            "games",
            "video game",
            "video-game",
            "videospiel",
            "videospiele",
            "spiel",
            "spiele",
            "game development",
            "game design",
            "spielentwicklung",
            "serious game",
            "serious games",
            "lernspiel",
            "lernspiele",
            "educational game",
            "training game",
            "gamified learning",
            "escape game",
            "escape room",
            "visual novel",
            "graphic novel",
            "interactive story",
            "interactive experience"
        ]
    },
    {
        "name": "unity",
        "weight": 24,
        "variants": [
            "unity",
            "unity3d",
            "unity game",
            "unity spiel",
            "unity app",
            "unity entwicklung",
            "unity development"
        ]
    },
    {
        "name": "godot",
        "weight": 24,
        "variants": [
            "godot",
            "godot engine",
            "godot spiel",
            "godot game",
            "godot app",
            "godot entwicklung",
            "godot development"
        ]
    },
    {
        "name": "ar_vr_xr",
        "weight": 24,
        "variants": [
            "vr",
            "ar",
            "xr",
            "virtual reality",
            "augmented reality",
            "extended reality",
            "mixed reality",
            "immersive",
            "immersive experience",
            "3d experience",
            "3d simulation",
            "simulation",
            "vr training",
            "ar application",
            "xr application"
        ]
    },
    {
        "name": "gamification",
        "weight": 22,
        "variants": [
            "gamification",
            "gamifiziert",
            "gamified",
            "spielerisch",
            "spielbasiert",
            "game based",
            "game-based",
            "interactive learning",
            "interaktives lernen"
        ]
    }
]

MEDIUM_POSITIVE_GROUPS = [
    {
        "name": "digitalization",
        "weight": 10,
        "variants": [
            "digitalisierung",
            "digitalisation",
            "digitalization",
            "digital",
            "digitale lösung",
            "digitale loesung",
            "digitale anwendung",
            "digitale plattform",
            "digitale transformation",
            "transformation",
            "modernisierung"
        ]
    },
    {
        "name": "platform_portal",
        "weight": 10,
        "variants": [
            "plattform",
            "platform",
            "portal",
            "online portal",
            "digital portal",
            "kundenerlebnis",
            "customer experience",
            "cx",
            "content platform"
        ]
    },
    {
        "name": "cloud_saas",
        "weight": 8,
        "variants": [
            "cloud",
            "cloudbasiert",
            "cloud based",
            "cloud-based",
            "saas",
            "software as a service",
            "software-as-a-service"
        ]
    },
    {
        "name": "ui_ux_frontend_backend",
        "weight": 8,
        "variants": [
            "frontend",
            "backend",
            "ui",
            "ux",
            "user interface",
            "user experience",
            "responsive",
            "responsive design",
            "cms",
            "content management",
            "content management system"
        ]
    },
    {
        "name": "training_learning",
        "weight": 8,
        "variants": [
            "e-learning",
            "elearning",
            "lernplattform",
            "learning platform",
            "training",
            "schulungssystem",
            "digital learning",
            "interactive training",
            "interaktives training"
        ]
    },
    {
        "name": "sap_related",
        "weight": 6,
        "variants": [
            "sap",
            "sap hana",
            "s/4hana",
            "s4hana",
            "sap successfactors",
            "sap crm",
            "sap customer experience",
            "sap utilities"
        ]
    }
]

STRONG_NEGATIVE_GROUPS = [
    {
        "name": "construction_road",
        "weight": -22,
        "variants": [
            "bau",
            "bauarbeiten",
            "baustelle",
            "baugenehmigung",
            "strasse",
            "straße",
            "strassenzustand",
            "straßenzustand",
            "strassenbau",
            "straßenbau",
            "verkehrsbau"
        ]
    },
    {
        "name": "locks_facility_hardware_delivery",
        "weight": -20,
        "variants": [
            "schließanlage",
            "schliessanlage",
            "schließsystem",
            "schliesssystem",
            "lieferung",
            "beschaffung",
            "hardwarebeschaffung",
            "mobiliar",
            "moebel",
            "möbel",
            "geraete",
            "geräte"
        ]
    },
    {
        "name": "network_telephony_infrastructure",
        "weight": -20,
        "variants": [
            "netzwerktechnik",
            "netzwerk",
            "festnetzanschluss",
            "telefonanlage",
            "infrastruktur",
            "firewall",
            "ngfw",
            "ipam",
            "serverbetrieb",
            "rechenzentrum",
            "layer 2",
            "datenanbindung"
        ]
    },
    {
        "name": "transport_vehicle_sensor",
        "weight": -20,
        "variants": [
            "fahrgastzaehlsystem",
            "fahrgastzählsystem",
            "busse",
            "bus",
            "öpnv",
            "oepnv",
            "fahrzeug",
            "fahrzeuge",
            "sensornetzwerk",
            "verkehrsdatenerhebung",
            "videosysteme fuer busse",
            "videosysteme für busse"
        ]
    }
]

MEDIUM_NEGATIVE_GROUPS = [
    {
        "name": "maintenance_support_only",
        "weight": -10,
        "variants": [
            "wartung",
            "maintenance",
            "lizenzverlaengerung",
            "lizenzverlängerung",
            "renewal",
            "support",
            "betriebsunterstuetzung",
            "betriebsunterstützung"
        ]
    },
    {
        "name": "security_admin_only",
        "weight": -10,
        "variants": [
            "isms",
            "bcms",
            "informationssicherheitsmanagement",
            "it-sicherheit",
            "itsicherheit",
            "sicherheit",
            "datensicherung",
            "backup",
            "identity management",
            "2 faktor authentifizierung",
            "zwei faktor authentifizierung",
            "two factor authentication"
        ]
    },
    {
        "name": "postal_printing_archiving",
        "weight": -10,
        "variants": [
            "postdienstleistung",
            "hybrid-post",
            "druck",
            "aktendigitalisierung",
            "papierakten",
            "archiv",
            "lagerung von fallakten"
        ]
    }
]

HARD_EXCLUDE_STATUS = [
    "vergebener auftrag",
    "ex post veroeffentlichung",
    "ex post veröffentlichung",
    "ex ante veroeffentlichung",
    "ex ante veröffentlichung"
]

SOFT_WARNING_STATUS = [
    "beabsichtigte ausschreibung",
    "vorinformation"
]

MIN_GOOD_DAYS = 14
MIN_ACCEPTABLE_DAYS = 8
MIN_BAD_DAYS = 7