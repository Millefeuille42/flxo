"""Stress-test seed: 200 users, 4 offices, random bookings for 150 users.

Usage:
    cd backend/
    uv run python -m tests.seed_stress
"""

import logging
import random
from datetime import date, timedelta

from sqlmodel import Session, SQLModel, create_engine

from flxo.core.security import get_password_hash
from flxo.models.office import Office
from flxo.models.presence import Presence
from flxo.models.seat import Seat
from flxo.models.user import User

logger = logging.getLogger(__name__)

DB_PATH = "stress_test.db"
PASSWORD = get_password_hash("flxo")
NUM_USERS = 200
NUM_BOOKING_USERS = 150

OFFICES = [
    {"name": "Paris Opéra", "address": "Paris", "desk_count": 80, "properties": {}},
    {
        "name": "Lyon Part-Dieu",
        "address": "Lyon",
        "desk_count": 100,
        "properties": {"floor_plan_url": "/open-space-100.svg"},
    },
    {"name": "Grenoble Inovallée", "address": "Grenoble", "desk_count": 20, "properties": {}},
    {"name": "Bordeaux Euratlantique", "address": "Bordeaux", "desk_count": 120, "properties": {}},
]

FIRST_NAMES = [
    "Alice", "Bob", "Charlie", "David", "Eva", "Fiona", "Gilles", "Hugo",
    "Inès", "Jules", "Karine", "Léo", "Marie", "Nathan", "Olivia", "Paul",
    "Quentin", "Rose", "Sophie", "Thomas", "Ugo", "Valérie", "William",
    "Xavier", "Yanis", "Zoé", "Adrien", "Béatrice", "Cédric", "Diane",
    "Émile", "Françoise", "Gaël", "Hélène", "Igor", "Jade", "Kevin",
    "Lucie", "Marc", "Noémie", "Oscar", "Pauline", "Raphaël", "Sabine",
    "Tristan", "Ursule", "Victor", "Wendy", "Yves", "Zara",
]

LAST_NAMES = [
    "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Petit", "Richard",
    "Durand", "Leroy", "Moreau", "Simon", "Laurent", "Lefèvre", "Michel",
    "Garcia", "Fournier", "Lambert", "Bonnet", "François", "Martinez",
]

SLOTS = ["morning", "afternoon"]
STATES = ["confirmed", "maybe"]


def generate_usernames(count: int) -> list[str]:
    return [f"user{i}" for i in range(1, count + 1)]


def get_mondays(weeks: int) -> list[date]:
    """Return Monday dates for the current week ± weeks."""
    today = date.today()
    current_monday = today - timedelta(days=today.weekday())
    return [current_monday + timedelta(weeks=w) for w in range(-4, weeks + 1)]


def seed() -> None:
    logging.basicConfig(level=logging.INFO)
    engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # --- Offices & Seats ---
        office_objs = []
        seat_map: dict[int, list[Seat]] = {}  # office index → seats

        for i, office_data in enumerate(OFFICES):
            office = Office(
                name=office_data["name"],
                address=office_data["address"],
                properties=office_data.get("properties", {}),
            )
            session.add(office)
            session.flush()
            office_objs.append(office)
            logger.info("Created office: %s (id=%d)", office.name, office.id)

            seats = []
            for j in range(1, office_data["desk_count"] + 1):
                seat = Seat(name=f"desk{j}", office_id=office.id)
                session.add(seat)
                seats.append(seat)
            session.flush()
            seat_map[i] = seats
            logger.info("  Created %d seats", len(seats))

        # --- Users ---
        usernames = generate_usernames(NUM_USERS)
        all_names = [
            f"{first} {last[0]}."
            for first in FIRST_NAMES
            for last in LAST_NAMES
        ]
        random.shuffle(all_names)
        users = []
        for i, username in enumerate(usernames):
            user = User(
                username=username,
                hashed_password=PASSWORD,
                properties={"display_name": all_names[i]},
            )
            session.add(user)
            users.append(user)
        session.flush()
        logger.info("Created %d users", len(users))

        # --- Assign each user a "home" office (weighted by desk_count) ---
        weights = [o["desk_count"] for o in OFFICES]
        user_offices = random.choices(range(len(OFFICES)), weights=weights, k=NUM_USERS)

        # --- Bookings ---
        mondays = get_mondays(8)
        booking_users = random.sample(users, NUM_BOOKING_USERS)
        total_presences = 0

        # Track taken seats per (date, slot) to avoid unique constraint violations
        taken_seats: dict[tuple[date, str], set[int]] = {}
        # Track user bookings per (date, slot) to avoid user unique constraint
        taken_user_slots: set[tuple[int, date, str]] = set()

        for user in booking_users:
            home_idx = user_offices[users.index(user)]
            home_office = office_objs[home_idx]
            home_seats = seat_map[home_idx]

            # Each user books 40-80% of available slots in their home office
            booking_rate = random.uniform(0.4, 0.8)

            for monday in mondays:
                for day_offset in range(5):  # Mon-Fri
                    for slot in SLOTS:
                        if random.random() > booking_rate:
                            continue

                        pdate = monday + timedelta(days=day_offset)

                        # Skip if user already booked this slot (another office)
                        if (user.id, pdate, slot) in taken_user_slots:
                            continue

                        state = random.choices(STATES, weights=[85, 15])[0]
                        seat = None
                        if state == "confirmed" and random.random() < 0.6:
                            key = (pdate, slot)
                            taken = taken_seats.get(key, set())
                            available = [s for s in home_seats if s.id not in taken]
                            if available:
                                seat = random.choice(available)
                                taken_seats.setdefault(key, set()).add(seat.id)

                        presence = Presence(
                            user_id=user.id,
                            office_id=home_office.id,
                            date=pdate,
                            slot=slot,
                            state=state,
                            seat_id=seat.id if seat else None,
                        )
                        session.add(presence)
                        taken_user_slots.add((user.id, pdate, slot))
                        total_presences += 1

        session.commit()
        logger.info("Created %d presences for %d users", total_presences, NUM_BOOKING_USERS)
        logger.info("Database written to: %s", DB_PATH)


if __name__ == "__main__":
    seed()
