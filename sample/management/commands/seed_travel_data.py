from django.core.management.base import BaseCommand

from sample.models import Buses, Flights


class Command(BaseCommand):
    help = "Seed sample bus and flight records for local booking demos."

    def handle(self, *args, **options):
        buses = [
            {
                "travels": "Skyline Volvo",
                "departure_timeHours": "07",
                "departure_timeMinutes": "30",
                "departure_palce": "Hyderabad",
                "arrival_timeHours": "16",
                "arrival_timeMinutes": "15",
                "arrival_place": "Bangalore",
                "duration": "8h 45m",
                "fare": "1250",
                "seats_available": 16,
                "ac_sleeper": "AC Sleeper",
                "bus_num": "TS09AB1234",
                "date": "15/05/2026",
                "day": "Friday",
            },
            {
                "travels": "Morning Star Express",
                "departure_timeHours": "21",
                "departure_timeMinutes": "00",
                "departure_palce": "Chennai",
                "arrival_timeHours": "06",
                "arrival_timeMinutes": "30",
                "arrival_place": "Hyderabad",
                "duration": "9h 30m",
                "fare": "1100",
                "seats_available": 16,
                "ac_sleeper": "AC Semi Sleeper",
                "bus_num": "TN10CD4567",
                "date": "16/05/2026",
                "day": "Saturday",
            },
            {
                "travels": "Coastal Rider",
                "departure_timeHours": "06",
                "departure_timeMinutes": "45",
                "departure_palce": "Mumbai",
                "arrival_timeHours": "18",
                "arrival_timeMinutes": "20",
                "arrival_place": "Goa",
                "duration": "11h 35m",
                "fare": "1450",
                "seats_available": 16,
                "ac_sleeper": "AC Sleeper",
                "bus_num": "MH12EF7788",
                "date": "17/05/2026",
                "day": "Sunday",
            },
        ]

        flights = [
            {
                "flight": "Indigo 6E-421",
                "departure_timeHours": "08",
                "departure_timeMinutes": "10",
                "departure_palce": "Delhi",
                "arrival_timeHours": "10",
                "arrival_timeMinutes": "25",
                "arrival_place": "Mumbai",
                "duration": "2h 15m",
                "fare": "5200",
                "seats_available": 60,
                "date": "15/05/2026",
                "day": "Friday",
            },
            {
                "flight": "Air India AI-507",
                "departure_timeHours": "13",
                "departure_timeMinutes": "40",
                "departure_palce": "Bangalore",
                "arrival_timeHours": "15",
                "arrival_timeMinutes": "05",
                "arrival_place": "Hyderabad",
                "duration": "1h 25m",
                "fare": "4100",
                "seats_available": 48,
                "date": "16/05/2026",
                "day": "Saturday",
            },
            {
                "flight": "Vistara UK-889",
                "departure_timeHours": "19",
                "departure_timeMinutes": "20",
                "departure_palce": "Mumbai",
                "arrival_timeHours": "20",
                "arrival_timeMinutes": "45",
                "arrival_place": "Goa",
                "duration": "1h 25m",
                "fare": "4600",
                "seats_available": 52,
                "date": "17/05/2026",
                "day": "Sunday",
            },
        ]

        bus_count = 0
        for payload in buses:
            _, created = Buses.objects.get_or_create(travels=payload["travels"], defaults=payload)
            bus_count += int(created)

        flight_count = 0
        for payload in flights:
            _, created = Flights.objects.get_or_create(flight=payload["flight"], defaults=payload)
            flight_count += int(created)

        self.stdout.write(self.style.SUCCESS(f"Seeded {bus_count} buses and {flight_count} flights."))
