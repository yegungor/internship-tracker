"""
Demo Seed Script - Populate database with fictional applications.
Optional: Run this to see the app with sample data.

Usage:
    python3 seed_data.py

To reset and reseed:
    rm tracker.db
    python3 app.py &
    python3 seed_data.py
"""

from app import app, db
from models import Application, Contact, Update
from datetime import datetime, timedelta

# All 15 demo applications
applications_data = [
    # ===== MOVIES & TV =====
    {
        "company": "Stark Industries",
        "job_title": "Arc Reactor Engineering Intern",
        "status": "interviewing",
        "location": "Malibu, CA",
        "position_level": "internship",
        "requirements": "Quantum physics, clean energy systems, MATLAB, must not be afraid of heights, arc reactor exposure training provided",
        "tags": "On-site, CleanTech, Paid",
        "notes": "Phone screen went great. Tony seemed distracted but impressed with my miniaturization ideas.",
        "date_applied": datetime.now() - timedelta(days=7),
        "contacts": [
            {"name": "Pepper Potts", "title": "Head of Operations", "email": "pepper@starkindustries.com"}
        ]
    },
    {
        "company": "Tyrell Corporation",
        "job_title": "Replicant Systems Engineer",
        "status": "saved",
        "location": "Los Angeles, CA (2019)",
        "position_level": "internship",
        "requirements": "Bioengineering, neural networks, empathy testing protocols, Voight-Kampff certification preferred",
        "tags": "On-site, AI/ML, Research",
        "notes": "More human than human. Need to review ethics policy before applying.",
        "contacts": [
            {"name": "Eldon Tyrell", "title": "CEO", "email": "eldon@tyrellcorp.com"}
        ]
    },
    {
        "company": "Vault-Tec",
        "job_title": "Post-Apocalyptic Resource Economist",
        "status": "applied",
        "location": "Remote (Underground)",
        "position_level": "internship",
        "requirements": "Resource allocation, survival economics, radiation tolerance, Excel, optimism",
        "tags": "Remote, Research, Paid",
        "notes": "1000-year contract seems long but benefits are good.",
        "date_applied": datetime.now() - timedelta(days=4),
        "contacts": [
            {"name": "Vault Boy", "title": "Recruitment Mascot", "email": "thumbsup@vaultec.com"}
        ]
    },
    {
        "company": "Umbrella Corporation",
        "job_title": "Biotech Engineering Intern",
        "status": "rejected",
        "location": "Raccoon City, CO",
        "position_level": "internship",
        "requirements": "Virology, genetic engineering, T-virus handling (training provided), NDA required",
        "tags": "On-site, Biotech, Research",
        "notes": "Rejected due to 'ethical concerns' I raised in interview. Dodged a bullet?",
        "date_applied": datetime.now() - timedelta(days=14),
        "contacts": [
            {"name": "Albert Wesker", "title": "Head of Research", "email": "wesker@umbrella.com"}
        ]
    },
    {
        "company": "Massive Dynamic",
        "job_title": "Fringe Economics Researcher",
        "status": "saved",
        "location": "New York, NY",
        "position_level": "internship",
        "requirements": "Econometrics, parallel universe theory, pattern recognition, comfortable with ambiguity",
        "tags": "Hybrid, Research, Paid",
        "notes": "Company seems to be involved in everything. Literally everything.",
        "contacts": [
            {"name": "Nina Sharp", "title": "COO", "email": "nina.sharp@massivedynamic.com"}
        ]
    },
    {
        "company": "Dunder Mifflin",
        "job_title": "Supply Chain Optimization Intern",
        "status": "applied",
        "location": "Scranton, PA",
        "position_level": "internship",
        "requirements": "Excel, logistics, paper industry knowledge, tolerance for workplace humor",
        "tags": "On-site, Paid",
        "notes": "They keep calling it a 'family' which is concerning but sweet.",
        "date_applied": datetime.now() - timedelta(days=5),
        "contacts": [
            {"name": "Michael Scott", "title": "Regional Manager", "email": "michael.scott@dundermifflin.com"}
        ]
    },
    {
        "company": "Pied Piper",
        "job_title": "Compression Algorithm Engineer",
        "status": "interviewing",
        "location": "Palo Alto, CA",
        "position_level": "internship",
        "requirements": "Python, C++, information theory, Weissman Score optimization, must hate Hooli",
        "tags": "On-site, AI/ML, Startup",
        "notes": "Technical interview was awkward but I think it went well? Hard to tell.",
        "date_applied": datetime.now() - timedelta(days=10),
        "contacts": [
            {"name": "Richard Hendricks", "title": "CEO", "email": "richard@piedpiper.com"}
        ]
    },
    {
        "company": "Los Pollos Hermanos",
        "job_title": "Operations Research Intern",
        "status": "saved",
        "location": "Albuquerque, NM",
        "position_level": "internship",
        "requirements": "Supply chain management, logistics optimization, Spanish preferred, discretion required",
        "tags": "On-site, Paid",
        "notes": "Great chicken. Very professional interview. Something feels off but can't explain it.",
        "contacts": [
            {"name": "Gustavo Fring", "title": "Owner", "email": "gus@lospolloshermanos.com"}
        ]
    },
    
    # ===== BOOKS =====
    {
        "company": "Foundation",
        "job_title": "Psychohistory Research Analyst",
        "status": "offer",
        "location": "Terminus",
        "position_level": "internship",
        "requirements": "Advanced mathematics, statistical mechanics, galactic population modeling, 10,000 year planning mindset",
        "tags": "Remote, Research, Paid",
        "notes": "They predicted I would accept the offer. Creepy but impressive.",
        "date_applied": datetime.now() - timedelta(days=20),
        "contacts": [
            {"name": "Hari Seldon", "title": "Founder", "email": "seldon@foundation.gal"}
        ]
    },
    {
        "company": "Hitchhiker's Guide Editorial",
        "job_title": "Probability & Improbability Intern",
        "status": "saved",
        "location": "Mostly Harmless (Earth)",
        "position_level": "internship",
        "requirements": "Infinite improbability theory, towel management, must know where towel is at all times, panic resistance",
        "tags": "Remote, Research",
        "notes": "Don't forget to bring a towel. Also the answer is 42.",
        "contacts": [
            {"name": "Ford Prefect", "title": "Senior Researcher", "email": "ford@h2g2.com"}
        ]
    },
    {
        "company": "Ministry of Truth",
        "job_title": "Data Reconciliation Engineer",
        "status": "rejected",
        "location": "Airstrip One, Oceania",
        "position_level": "internship",
        "requirements": "Doublethink, historical revision, SQL, memory flexibility, loyalty to Big Brother",
        "tags": "On-site, Government",
        "notes": "Rejected. They said I 'thought too much.' Probably for the best.",
        "date_applied": datetime.now() - timedelta(days=15),
        "contacts": [
            {"name": "O'Brien", "title": "Senior Party Member", "email": "obrien@minitrue.gov"}
        ]
    },
    {
        "company": "Iron Bank of Braavos",
        "job_title": "Risk Assessment Analyst",
        "status": "applied",
        "location": "Braavos, Essos",
        "position_level": "internship",
        "requirements": "Financial modeling, debt collection strategies, Valyrian a plus, must understand 'a Lannister always pays his debts'",
        "tags": "On-site, FinTech, Paid",
        "notes": "Their repayment terms are strict. Very strict.",
        "date_applied": datetime.now() - timedelta(days=3),
        "contacts": [
            {"name": "Tycho Nestoris", "title": "Senior Banker", "email": "tycho@ironbank.bra"}
        ]
    },
    {
        "company": "Willy Wonka Industries",
        "job_title": "Confectionery Engineering Intern",
        "status": "saved",
        "location": "Unknown (Factory)",
        "position_level": "internship",
        "requirements": "Food science, chemical engineering, imagination, must sign extensive liability waiver",
        "tags": "On-site, Research, Paid",
        "notes": "Need golden ticket to apply. Working on it.",
        "contacts": [
            {"name": "Willy Wonka", "title": "Founder", "email": "wonka@wonkaindustries.com"}
        ]
    },
    {
        "company": "Monsters, Inc.",
        "job_title": "Scream Energy Optimization Engineer",
        "status": "offer",
        "location": "Monstropolis",
        "position_level": "internship",
        "requirements": "Energy systems, acoustic engineering, child psychology, must not be afraid of closets",
        "tags": "On-site, CleanTech, Paid",
        "notes": "They're pivoting to laugh energy. Love the sustainable approach!",
        "date_applied": datetime.now() - timedelta(days=25),
        "contacts": [
            {"name": "James P. Sullivan", "title": "CEO", "email": "sulley@monstersinc.com"}
        ]
    },
    {
        "company": "Jurassic World Genetics",
        "job_title": "De-extinction Cost Analyst",
        "status": "rejected",
        "location": "Isla Nublar",
        "position_level": "internship",
        "requirements": "Genetic engineering economics, risk modeling, chaos theory, must sign life insurance waiver",
        "tags": "On-site, Biotech, Research",
        "notes": "Rejected after I asked about their safety budget. They said I 'worry too much.'",
        "date_applied": datetime.now() - timedelta(days=12),
        "contacts": [
            {"name": "Dr. Henry Wu", "title": "Chief Geneticist", "email": "hwu@jurassicworld.com"}
        ]
    }
]


def seed_database():
    with app.app_context():
        print("\n🌱 Seeding database with demo data...\n")
        
        for app_data in applications_data:
            # Create application
            application = Application(
                company=app_data["company"],
                job_title=app_data["job_title"],
                status=app_data["status"],
                location=app_data.get("location", ""),
                position_level=app_data.get("position_level", ""),
                requirements=app_data.get("requirements", ""),
                tags=app_data.get("tags", ""),
                notes=app_data.get("notes", ""),
                date_applied=app_data.get("date_applied"),
                deadline=app_data.get("deadline")
            )
            db.session.add(application)
            db.session.flush()  # Get the ID
            
            # Add contacts
            for contact_data in app_data.get("contacts", []):
                contact = Contact(
                    application_id=application.id,
                    name=contact_data["name"],
                    title=contact_data.get("title", ""),
                    email=contact_data.get("email", ""),
                    linkedin_url=contact_data.get("linkedin_url", ""),
                    notes=contact_data.get("notes", "")
                )
                db.session.add(contact)
            
            print(f"  ✅ {app_data['company']} - {app_data['job_title']}")
        
        db.session.commit()
        
        print("\n" + "="*50)
        print("🎉 Demo data loaded successfully!")
        print("="*50)
        print(f"\n📊 Summary:")
        print(f"   • 15 applications added")
        print(f"   • 15 contacts added")
        print(f"   • 2 offers, 2 interviewing, 4 applied")
        print(f"   • 4 saved, 3 rejected")
        print(f"\n🚀 Run the app: python3 app.py")
        print(f"🌐 Open: http://127.0.0.1:1453\n")


if __name__ == "__main__":
    seed_database()
