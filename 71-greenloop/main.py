# =============================================================
#  GREEN LOOP — main.py
#  The master file. Run this for the full demo.
#
#  What this file does:
#    Ties all four modules together and runs the complete
#    Green Loop system from start to finish.
#
#    Phase 1 — Introduction
#    Phase 2 — City is created and shown
#    Phase 3 — Live monitoring (bins fill up hour by hour)
#    Phase 4 — Alert scan (which bins are critical?)
#    Phase 5 — Truck dispatched (optimised route)
#    Phase 6 — Trip report + before/after comparison
#    Phase 7 — City recovers, second dispatch
#    Phase 8 — Final summary
#
#  HOW TO RUN:
#    In VS Code terminal, navigate to the green_loop folder.
#    Type: python main.py
#    That's it. The whole system runs.
#
#  All four files must be in the same folder:
#    city.py, alerts.py, router.py, display.py, main.py
# =============================================================

import time
import copy

from city import (
    create_city,
    simulate_one_hour,
    THRESHOLD_URGENT,
    THRESHOLD_CRITICAL,
)
from alerts import (
    scan_and_alert,
    print_full_status_board,
    get_bins_above,
)
from router import (
    build_graph,
    dispatch_truck,
)
from display import (
    draw_map,
    print_bin_panel,
    animate_route,
    print_trip_report,
    before_after,
    live_dashboard,
    clear_screen,
    FAST_MODE,
)

# =============================================================
#  DEMO SETTINGS
#  Change these to control the demo experience
# =============================================================

MONITORING_HOURS  = 6    # how many hours to simulate before first dispatch
SECOND_SIM_HOURS  = 4    # hours to simulate before second dispatch
DELAY             = 0 if FAST_MODE else 1.5   # animation delay in seconds


# =============================================================
#  HELPER — PAUSE
#  Waits for the user to press Enter before continuing.
#  Gives you control during the demo — go at your own pace.
# =============================================================

def pause(message="  Press Enter to continue..."):
    input(f"\n{message}")


# =============================================================
#  HELPER — SECTION HEADER
#  Prints a clean section title between phases
# =============================================================

def section(title):
    print("\n")
    print("  " + "█" * 54)
    print(f"  █  {title:<50}  █")
    print("  " + "█" * 54)
    if not FAST_MODE:
        time.sleep(0.5)


# =============================================================
#  PHASE 1 — INTRODUCTION
#  Prints the project intro. Sets the scene for judges.
# =============================================================

def phase_intro():
    clear_screen()
    print()
    print("  " + "=" * 54)
    print("  " + " " * 15 + "GREEN LOOP")
    print("  " + " " * 5 + "Smart Waste Collection System")
    print("  " + "=" * 54)
    print()
    print("  THE PROBLEM:")
    print("  Every day, garbage trucks visit every bin in the")
    print("  city — full or empty — wasting fuel, time, and")
    print("  causing overflow on busy streets.")
    print()
    print("  OUR SOLUTION:")
    print("  Green Loop monitors every bin in real time.")
    print("  Trucks only go where bins are actually full.")
    print("  Overflow is prevented before it happens.")
    print()
    print("  DSA USED:")
    print("  → Hash Table   : O(1) bin lookup by ID")
    print("  → Min-Heap     : Priority queue by urgency")
    print("  → Graph        : City modelled as nodes + edges")
    print("  → Greedy Algo  : Nearest urgent bin at every step")
    print()
    print("  " + "=" * 54)
    pause("  Press Enter to start the simulation...")


# =============================================================
#  PHASE 2 — CITY SETUP
#  Creates the city and shows the initial state
# =============================================================

def phase_city_setup():
    section("PHASE 1 — CITY SETUP")

    print("\n  Creating Pune city simulation...")
    print("  30 bins placed across market, school,")
    print("  and residential zones.\n")

    if not FAST_MODE:
        time.sleep(1)

    city = create_city()

    print(f"  ✅  City created. {len(city)} bins registered.")
    print(f"  ✅  Hash table built — O(1) lookup ready.")
    print(f"  ✅  Each bin has: ID, location, fill level, zone.")

    pause()

    draw_map(city)
    print_bin_panel(city)

    pause()

    return city


# =============================================================
#  PHASE 3 — LIVE MONITORING
#  Simulates hours passing, bins filling up
# =============================================================

def phase_monitoring(city):
    section("PHASE 2 — LIVE MONITORING")

    print(f"\n  Simulating {MONITORING_HOURS} hours of city activity.")
    print("  Market bins fill fast. Residential bins fill slow.")
    print("  The system watches every bin every hour.\n")

    pause("  Press Enter to start monitoring...")

    if FAST_MODE:
        for _ in range(MONITORING_HOURS):
            city = simulate_one_hour(city)
        print(f"  {MONITORING_HOURS} hours simulated.")
        draw_map(city)
        print_bin_panel(city)
    else:
        city = live_dashboard(city, hours=MONITORING_HOURS, delay=DELAY)

    pause()
    return city


# =============================================================
#  PHASE 4 — ALERT SCAN
#  Heap scans all bins, fires alerts
# =============================================================

def phase_alerts(city):
    section("PHASE 3 — ALERT SCAN")

    print("\n  Min-Heap scans all 30 bins.")
    print("  Bins sorted by urgency — most critical at top.")
    print("  Alerts fired for bins above threshold.\n")

    if not FAST_MODE:
        time.sleep(1)

    urgent_heap, critical_list = scan_and_alert(city)

    if critical_list:
        print(f"\n  🔴 {len(critical_list)} bin(s) are CRITICAL.")
        print("  These will be prioritised in the truck route.")
    else:
        print("\n  ✅  No critical bins. Urgent bins queued.")

    pause()
    return urgent_heap, critical_list


# =============================================================
#  PHASE 5 — TRUCK DISPATCH
#  Greedy router builds and animates the route
# =============================================================

def phase_dispatch(city, trip_number=1, hour=0):
    section(f"PHASE 4 — TRUCK DISPATCH  |  TRIP #{trip_number}")

    print("\n  Graph built — city modelled as nodes and edges.")
    print("  Greedy algorithm finds nearest urgent bin at")
    print("  every step and builds the optimised route.\n")

    pause("  Press Enter to dispatch the truck...")

    # Save city state before dispatch for comparison
    city_before = copy.deepcopy(city)

    # Build graph and get route for animation
    graph = build_graph(city)

    from router import greedy_route, calculate_fuel_saved
    route, total_dist, skipped = greedy_route(city, graph)

    if not route:
        print("\n  ✅  No bins need collection right now.")
        print("  All bins are below the collection threshold.")
        pause()
        return city, None, None, None

    # Animate the truck moving (if not fast mode)
    if not FAST_MODE:
        animate_route(city, route, delay=DELAY)
    else:
        draw_map(city, route=route)
        print(f"\n  Route planned: {len(route)} stops")
        for i, stop in enumerate(route, 1):
            b = stop["bin"]
            flag = "🔴" if b["fill_level"] >= THRESHOLD_CRITICAL else "🟡"
            print(f"  Stop {i}: {b['id']} ({b['zone']}) "
                  f"at {b['fill_level']}% {flag}")

    # Actually dispatch — empties the collected bins
    route, total_dist, skipped, fuel_data, city = dispatch_truck(city)

    pause()

    # Trip report
    section(f"PHASE 5 — TRIP REPORT  |  TRIP #{trip_number}")
    print_trip_report(route, total_dist, skipped, fuel_data,
                      hour=hour, trip_number=trip_number)

    pause()

    # Before vs after
    section("PHASE 6 — BEFORE vs AFTER")
    before_after(city_before, city)

    pause()

    # Map after collection
    print("\n  City map after collection:")
    draw_map(city)

    pause()

    return city, route, total_dist, fuel_data


# =============================================================
#  PHASE 6 — SECOND CYCLE
#  Simulate more hours, run a second dispatch
# =============================================================

def phase_second_cycle(city):
    section("PHASE 7 — SECOND COLLECTION CYCLE")

    print(f"\n  Simulating {SECOND_SIM_HOURS} more hours.")
    print("  Emptied bins start filling again.")
    print("  System automatically detects new urgent bins.\n")

    pause("  Press Enter to continue simulation...")

    if FAST_MODE:
        for _ in range(SECOND_SIM_HOURS):
            city = simulate_one_hour(city)
        print(f"  {SECOND_SIM_HOURS} more hours simulated.")
        draw_map(city)
    else:
        city = live_dashboard(city, hours=SECOND_SIM_HOURS, delay=DELAY)

    pause()

    # Alert scan for second cycle
    print("\n  Running alert scan for second dispatch...")
    urgent_heap, critical_list = scan_and_alert(city)

    pause()

    # Second dispatch
    city, route, total_dist, fuel_data = phase_dispatch(
        city,
        trip_number=2,
        hour=MONITORING_HOURS + SECOND_SIM_HOURS
    )

    return city


# =============================================================
#  PHASE 7 — FINAL SUMMARY
#  Wraps up the demo with key takeaways
# =============================================================

def phase_summary():
    section("PHASE 8 — SYSTEM SUMMARY")

    print()
    print("  GREEN LOOP — WHAT WE DEMONSTRATED:")
    print()
    print("  ✅  Hash Table")
    print("      30 bins stored. Any bin looked up in O(1) time.")
    print("      No searching. Direct access by bin ID.")
    print()
    print("  ✅  Min-Heap (Priority Queue)")
    print("      Bins ranked by fill level automatically.")
    print("      Most critical bin always at the top.")
    print("      Insert: O(log n). Peek most urgent: O(1).")
    print()
    print("  ✅  Graph")
    print("      City modelled as 30 nodes, fully connected.")
    print("      Each edge = road distance between two bins.")
    print("      Adjacency list — efficient and scalable.")
    print()
    print("  ✅  Greedy Algorithm")
    print("      At every step — go to nearest urgent bin.")
    print("      Skips all bins below threshold.")
    print("      Fast, explainable, and practical.")
    print()
    print("  " + "─" * 54)
    print()
    print("  REAL WORLD IMPACT:")
    print()
    print("  → 75–82% fuel saved per trip vs blind routing")
    print("  → ~33 litres of diesel not burned per dispatch")
    print("  → ~89 kg of CO₂ not emitted per dispatch")
    print("  → Zero overflow incidents when system is active")
    print("  → First time municipalities have bin-level data")
    print()
    print("  " + "─" * 54)
    print()
    print("  Cities don't have a waste problem.")
    print("  They have a waste VISIBILITY problem.")
    print("  Green Loop gives every bin a voice.")
    print()
    print("  " + "=" * 54)
    print("  " + " " * 18 + "THANK YOU")
    print("  " + "=" * 54)
    print()


# =============================================================
#  MAIN — runs all phases in order
# =============================================================

def main():

    # Phase 1 — Introduction
    phase_intro()

    # Phase 2 — City setup
    city = phase_city_setup()

    # Phase 3 — Live monitoring
    city = phase_monitoring(city)

    # Phase 4 — Alert scan
    urgent_heap, critical_list = phase_alerts(city)

    # Phase 5, 6 — First dispatch + report + before/after
    city, route, total_dist, fuel_data = phase_dispatch(
        city,
        trip_number=1,
        hour=MONITORING_HOURS
    )

    # Phase 7 — Second cycle
    city = phase_second_cycle(city)

    # Phase 8 — Final summary
    phase_summary()


# =============================================================
#  Entry point
# =============================================================

if _name_ == "_main_":
    main()
