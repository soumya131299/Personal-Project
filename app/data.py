from typing import List

from .models import Founder, VC, PortfolioCompany


def seed_founders() -> List[Founder]:
    return [
        Founder(
            id="fnd_001",
            name="Ava Thompson",
            hometown_city="Austin",
            hometown_country="USA",
            background=["ex-Stripe PM", "CS @ UT Austin"],
            bio="Building B2B fintech infrastructure for embedded lending.",
            sectors=["fintech", "b2b", "infrastructure"],
            stages=["pre-seed", "seed"],
        ),
        Founder(
            id="fnd_002",
            name="Noah Patel",
            hometown_city="Toronto",
            hometown_country="Canada",
            background=["ex-Shopify engineer", "AI researcher"],
            bio="AI agents for e-commerce merchandising and pricing.",
            sectors=["ai", "ecommerce", "saas"],
            stages=["seed", "series-a"],
        ),
        Founder(
            id="fnd_003",
            name="Lina Chen",
            hometown_city="London",
            hometown_country="UK",
            background=["PhD Bioinformatics", "ex-DeepMind"],
            bio="Applying ML to protein design for therapeutics.",
            sectors=["bio", "ai", "healthtech"],
            stages=["pre-seed", "seed"],
        ),
    ]


def seed_vcs() -> List[VC]:
    return [
        VC(
            id="vc_101",
            name="Harper Lee",
            fund_name="Catalyst Ventures",
            hq_city="San Francisco",
            hq_country="USA",
            geographies=["usa", "canada"],
            sectors=["fintech", "saas", "devtools"],
            stages=["pre-seed", "seed"],
            backgrounds=["ex-PayPal", "operator turned investor"],
            investment_thesis="Backing founders building the next-gen B2B fintech rails.",
            portfolio=[
                PortfolioCompany(name="LedgerLoop", sectors=["fintech", "b2b"], description="AR automation"),
                PortfolioCompany(name="StackForge", sectors=["devtools", "saas"], description="Dev platform"),
            ],
        ),
        VC(
            id="vc_102",
            name="Mateo García",
            fund_name="NorthBridge Capital",
            hq_city="Toronto",
            hq_country="Canada",
            geographies=["canada", "usa", "global"],
            sectors=["ecommerce", "ai", "marketplaces"],
            stages=["seed", "series-a"],
            backgrounds=["ex-Amazon", "ML"],
            investment_thesis="AI-native applications for commerce and logistics.",
            portfolio=[
                PortfolioCompany(name="CartGenius", sectors=["ecommerce", "ai"], description="Personalization"),
                PortfolioCompany(name="WarehouseIQ", sectors=["logistics", "ai"], description="Optimization"),
            ],
        ),
        VC(
            id="vc_103",
            name="Sofia Rossi",
            fund_name="BioNova Partners",
            hq_city="London",
            hq_country="UK",
            geographies=["uk", "europe"],
            sectors=["bio", "healthtech", "ai"],
            stages=["pre-seed", "seed"],
            backgrounds=["PhD Biology", "biotech operator"],
            investment_thesis="Computational biology and platform therapeutics.",
            portfolio=[
                PortfolioCompany(name="ProteinFlow", sectors=["bio", "ai"], description="Protein design"),
                PortfolioCompany(name="ClinicOS", sectors=["healthtech", "saas"], description="Clinical ops"),
            ],
        ),
    ]

