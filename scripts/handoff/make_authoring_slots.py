#!/usr/bin/env python3
"""Build locked authoring SLOTS for Gemini 'A1' tasks (packets/A1_NNN.jsonl). Deterministic. usage: make_authoring_slots.py 1  (pilot, 30 slots)"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
PLAN = {   # domain -> [(subdomain, pos list, how many slots, topic hint)]
    "it": [("software_dev", ["noun", "verb"], 3, "programming concepts, version control, debugging"),
           ("networking", ["noun"], 2, "protocols, bandwidth, routing, servers"),
           ("security", ["noun", "verb"], 2, "authentication, encryption, malware"),
           ("data_and_database", ["noun", "verb"], 3, "storage, query, backup, files"),
           ("web_and_apps", ["noun"], 2, "browsers, apps, user interface")],
    "healthcare": [("symptoms_and_conditions", ["noun"], 3, "common symptoms/illnesses a patient reports"),
                   ("hospital_and_departments", ["noun"], 2, "wards, departments, staff, appointments"),
                   ("treatment_and_medication", ["noun", "verb"], 3, "prescriptions, injections, surgery, rehabilitation"),
                   ("body_and_examination", ["noun"], 2, "organs and examinations/tests")],
    "travel": [("airport_and_flight", ["noun"], 2, "check-in, boarding, baggage, customs"),
               ("hotel_and_stay", ["noun"], 2, "reservation, room types, front desk"),
               ("transport_and_directions", ["noun", "verb"], 2, "trains, tickets, transfers, asking the way"),
               ("sightseeing_and_money", ["noun"], 2, "tourist spots, currency exchange, souvenirs")],
}


PLAN2 = {   # waves 2+: different subdomains / topics from the pilot, plus manufacturing
    "it": [("software_dev", ["noun", "verb"], 3, "testing, deployment, code review, libraries (NOT terms already authored: branch, source code, debugger)"),
           ("networking", ["noun"], 2, "wifi, firewall, IP address, connection problems"),
           ("security", ["noun"], 1, "passwords, permissions, backups of accounts"),
           ("data_and_database", ["noun"], 1, "tables, records, spreadsheets, export"),
           ("hardware_and_devices", ["noun"], 3, "servers, storage, peripherals, printers")],
    "healthcare": [("symptoms_and_conditions", ["noun"], 3, "pain, infection, inflammation, chronic illness"),
                   ("hospital_and_departments", ["noun"], 2, "reception, outpatient, ward, emergency room"),
                   ("treatment_and_medication", ["noun", "verb"], 2, "dosage, side effect, injection, surgery steps"),
                   ("body_and_examination", ["noun"], 1, "organs, X-ray, blood pressure, temperature")],
    "travel": [("airport_and_flight", ["noun"], 2, "passport control, delay, transit, seat types"),
               ("hotel_and_stay", ["noun"], 2, "reservation, deposit, amenities, room service"),
               ("transport_and_directions", ["noun", "verb"], 2, "bus, taxi, timetable, transfer, platform"),
               ("sightseeing_and_money", ["noun"], 2, "souvenir, guided tour, currency exchange, receipt")],
    "manufacturing": [("production_and_quality", ["noun"], 3, "assembly line, inspection, defect, tolerance"),
                      ("machines_and_tools", ["noun"], 2, "lathe, drill, welding, conveyor"),
                      ("materials_and_safety", ["noun"], 1, "steel, lubricant, protective gear, hazard")],
}


def main(n):
    slots = []
    for dom, subs in (PLAN if n == 1 else PLAN2).items():
        for sub, pos, cnt, hint in subs:
            for _ in range(cnt):
                slots.append({"domain": dom, "subdomain": sub, "allowed_pos": pos, "topic_hint": hint})
    for i, s in enumerate(slots, 1):
        s["id"] = f"A1_{n:03d}-{i:02d}"
    p = REPO / f"data/phase1_4/handoff/packets/A1_{n:03d}.jsonl"
    p.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in slots), encoding="utf-8")
    print(p.relative_to(REPO), len(slots))


if __name__ == "__main__":
    main(int(sys.argv[1]))
