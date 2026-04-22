# ============================================================= 

#  GREEN LOOP — display.py 

#  What this file does: 

#    1. Draws an ASCII map of the city grid with all 30 bins 

#    2. Animates the truck moving through its route stop by stop 

#    3. Prints a live hourly monitoring dashboard 

#    4. Prints the final trip report with all statistics 

#    5. Shows a before vs after comparison of the city 

# 

#  DSA used here: 

#    Uses all three — Hash Table (city lookup), Heap (status 

#    checks), Graph + Greedy (route display) 

#    Person 4 is the layer that makes everything VISIBLE. 

# 

#  Depends on: city.py, alerts.py, router.py 

# ============================================================= 

 

import time 

import os 

from city import ( 

    create_city, 

    simulate_one_hour, 

    THRESHOLD_URGENT, 

    THRESHOLD_CRITICAL, 

) 

from alerts import ( 

    get_status, 

    print_full_status_board, 

    scan_and_alert, 

    STATUS_CRITICAL, 

    STATUS_URGENT, 

    STATUS_NORMAL, 

    STATUS_EMPTY, 

) 

from router import ( 

    dispatch_truck, 

    build_graph, 

    greedy_route, 

    calculate_fuel_saved, 

    TRUCK_START, 

    TRUCK_CAPACITY, 

) 

 

# ============================================================= 

#  SECTION 1 — CONSTANTS AND SYMBOLS 

# ============================================================= 

 

# Grid size — our city is an 11x11 grid (coordinates 0 to 10) 

GRID_SIZE = 11 

 

# Symbols used on the ASCII map 

SYMBOL_EMPTY    = "░"   # bin is fine, below 30% 

SYMBOL_NORMAL   = "▒"   # bin is normal, 31-69% 

SYMBOL_URGENT   = "▓"   # bin needs collection soon, 70-84% 

SYMBOL_CRITICAL = "█"   # bin is critical, 85%+ 

SYMBOL_TRUCK    = "🚛"  # truck's current position 

SYMBOL_DEPOT    = "🏭"  # truck depot 

SYMBOL_VISITED  = "✓"   # bin already collected this trip 

SYMBOL_EMPTY_CELL = "·" # nothing at this grid cell 

 

# ============================================================= 

#  SECTION 2 — CLEAR SCREEN 

#  Clears the terminal for clean animation 

# ============================================================= 

 

def clear_screen(): 

    """Clears the terminal screen.""" 

    os.system("cls" if os.name == "nt" else "clear") 

 

# ============================================================= 

#  SECTION 3 — DRAW THE ASCII CITY MAP 

# 

#  Draws an 11x11 grid. Each cell is either: 

#    - A bin symbol (showing its fill status) 

#    - The truck position 

#    - The depot 

#    - Empty space 

# 

#  The map is the visual centrepiece of the demo. 

# ============================================================= 

 

def draw_map(city_bins, truck_location=TRUCK_START, 

             visited_bins=None, route=None): 

    """ 

    Draws the ASCII city map showing all bins, truck, and depot. 

 

    Args: 

        city_bins     (dict): Current city state 

        truck_location(tuple): Where the truck is right now (x, y) 

        visited_bins  (set):  Bin IDs already collected this trip 

        route         (list): Planned route stops (to show path) 

    """ 

 

    if visited_bins is None: 

        visited_bins = set() 

 

    # Build a lookup: (x, y) → bin data 

    # So we can quickly find what's at each grid cell 

    location_to_bin = {} 

    for bin_id in city_bins: 

        loc = city_bins[bin_id]["location"] 

        location_to_bin[loc] = city_bins[bin_id] 

 

    # Build a set of route locations for path display 

    route_locations = set() 

    if route: 

        for stop in route: 

            route_locations.add(stop["bin"]["location"]) 

 

    print("\n  " + "─" * 50) 

    print("  📍  GREEN LOOP — CITY MAP") 

    print("  " + "─" * 50) 

 

    # Print column numbers across the top 

    print("     ", end="") 

    for x in range(GRID_SIZE): 

        print(f" {x} ", end="") 

    print() 

    print("     " + "───" * GRID_SIZE) 

 

    # Print each row of the grid (top to bottom, y goes 10 down to 0) 

    for y in range(GRID_SIZE - 1, -1, -1): 

        print(f"  {y:2} │", end="")   # row number on left 

 

        for x in range(GRID_SIZE): 

            cell = (x, y) 

 

            if cell == TRUCK_START and cell == truck_location: 

                # Truck is at depot 

                print(" D ", end="") 

 

            elif cell == truck_location: 

                # Truck is here 

                print(" T ", end="") 

 

            elif cell == TRUCK_START: 

                # Depot (truck not here) 

                print(" D ", end="") 

 

            elif cell in location_to_bin: 

                bin_data = location_to_bin[cell] 

                bin_id   = bin_data["id"] 

                fill     = bin_data["fill_level"] 

 

                if bin_id in visited_bins: 

                    print(" ✓ ", end="")   # already collected 

                else: 

                    status = get_status(fill) 

                    if status == STATUS_CRITICAL: 

                        print(" █ ", end="") 

                    elif status == STATUS_URGENT: 

                        print(" ▓ ", end="") 

                    elif status == STATUS_NORMAL: 

                        print(" ▒ ", end="") 

                    else: 

                        print(" ░ ", end="") 

            else: 

                print(" · ", end="")   # empty cell 

 

        print()   # newline after each row 

 

    print("     " + "───" * GRID_SIZE) 

 

    # Legend 

    print() 

    print("  LEGEND:") 

    print("  D = Depot (truck start)    T = Truck location") 

    print("  █ = CRITICAL (85%+)        ▓ = URGENT (70-84%)") 

    print("  ▒ = Normal (31-69%)        ░ = Empty (0-30%)") 

    print("  ✓ = Collected this trip") 

    print("  " + "─" * 50) 

 

# ============================================================= 

#  SECTION 4 — PRINT BIN DETAILS NEXT TO MAP 

#  Shows a quick summary panel beside the map for the demo 

# ============================================================= 

 

def print_bin_panel(city_bins): 

    """ 

    Prints a compact two-column panel of all 30 bins 

    sorted by fill level. 

 

    Args: 

        city_bins (dict): Current city state 

    """ 

 

    sorted_bins = sorted( 

        city_bins.values(), 

        key=lambda b: b["fill_level"], 

        reverse=True 

    ) 

 

    print("\n  " + "─" * 50) 

    print("  📊  BIN STATUS PANEL — ALL 30 BINS") 

    print("  " + "─" * 50) 

    print(f"  {'BIN':<6} {'FILL':>5}  {'BAR':<12}  {'STATUS'}") 

    print("  " + "─" * 50) 

 

    for b in sorted_bins: 

        fill   = b["fill_level"] 

        status = get_status(fill) 

        bar    = "█" * (fill // 10) 

 

        if status == STATUS_CRITICAL: 

            label = "🔴 CRITICAL" 

        elif status == STATUS_URGENT: 

            label = "🟡 URGENT" 

        elif status == STATUS_NORMAL: 

            label = "🔵 Normal" 

        else: 

            label = "🟢 Empty" 

 

        print(f"  {b['id']:<6} {fill:>4}%  {bar:<12}  {label}") 

 

    print("  " + "─" * 50) 

 

# ============================================================= 

#  SECTION 5 — ANIMATE THE TRUCK ROUTE 

#  Shows the truck moving stop by stop through the route. 

#  This is the demo showpiece. 

# ============================================================= 

 

def animate_route(city_bins, route, delay=1.5): 

    """ 

    Animates the truck moving through its route. 

    Each stop: redraws the map with truck at new location, 

    prints what the truck is doing, waits, then moves on. 

 

    Args: 

        city_bins (dict): Current city state 

        route     (list): Ordered stops from router 

        delay     (float): Seconds to wait between stops 

    """ 

 

    visited = set() 

    truck_location = TRUCK_START 

 

    print("\n  🚛  TRUCK DISPATCH STARTING...") 

    print(f"  Truck leaving depot at {TRUCK_START}") 

    time.sleep(delay) 

 

    # Show starting map 

    clear_screen() 

    print("\n  " + "=" * 50) 

    print("  🚛  GREEN LOOP — LIVE TRUCK DISPATCH") 

    print("  " + "=" * 50) 

    draw_map(city_bins, truck_location=TRUCK_START, visited_bins=visited) 

    print(f"\n  🏭  Truck at DEPOT {TRUCK_START} — ready to dispatch") 

    time.sleep(delay) 

 

    # Move through each stop 

    for i, stop in enumerate(route, 1): 

        b    = stop["bin"] 

        dist = stop["distance"] 

        cum  = stop["cumulative_distance"] 

 

        truck_location = b["location"] 

        visited.add(b["id"]) 

 

        clear_screen() 

        print("\n  " + "=" * 50) 

        print("  🚛  GREEN LOOP — LIVE TRUCK DISPATCH") 

        print("  " + "=" * 50) 

 

        draw_map(city_bins, truck_location=truck_location, 

                 visited_bins=visited, route=route) 

 

        print(f"\n  STOP {i} of {len(route)}") 

        print(f"  {'─' * 40}") 

 

        if b["fill_level"] >= THRESHOLD_CRITICAL: 

            print(f"  🔴 CRITICAL BIN COLLECTED") 

        else: 

            print(f"  🟡 URGENT BIN COLLECTED") 

 

        print(f"  Bin:      {b['id']} ({b['zone']})") 

        print(f"  Location: {b['location']}") 

        print(f"  Fill:     {b['fill_level']}% → 0% after collection") 

        print(f"  Distance: {dist} km this leg") 

        print(f"  Total so far: {cum} km") 

        print(f"  {'─' * 40}") 

        print(f"  Bins collected: {i} / {len(route)}") 

        print(f"  Remaining stops: {len(route) - i}") 

 

        time.sleep(delay) 

 

    # Return to depot 

    clear_screen() 

    print("\n  " + "=" * 50) 

    print("  🚛  GREEN LOOP — LIVE TRUCK DISPATCH") 

    print("  " + "=" * 50) 

    draw_map(city_bins, truck_location=TRUCK_START, 

             visited_bins=visited, route=route) 

    print(f"\n  🏭  Truck returned to DEPOT") 

    print(f"  ✅  Trip complete. {len(route)} bins collected.") 

    time.sleep(delay) 

 

# ============================================================= 

#  SECTION 6 — LIVE MONITORING DASHBOARD 

#  Shows the city state changing hour by hour 

# ============================================================= 

 

def live_dashboard(city_bins, hours=6, delay=1.5): 

    """ 

    Shows the city map updating hour by hour as bins fill up. 

    Fires visual alerts when bins go critical. 

 

    Args: 

        city_bins (dict): Starting city state 

        hours     (int):  How many hours to show 

        delay     (float): Seconds between hours 

 

    Returns: 

        dict: Final city state 

    """ 

 

    for hour in range(1, hours + 1): 

        city_bins = simulate_one_hour(city_bins) 

 

        clear_screen() 

        print("\n  " + "=" * 50) 

        print(f"  ⏰  GREEN LOOP — LIVE MONITORING  |  HOUR {hour}") 

        print("  " + "=" * 50) 

 

        draw_map(city_bins) 

 

        # Count statuses 

        counts = {s: 0 for s in 

                  [STATUS_EMPTY, STATUS_NORMAL, STATUS_URGENT, STATUS_CRITICAL]} 

        for b in city_bins.values(): 

            counts[get_status(b["fill_level"])] += 1 

 

        print(f"\n  Hour {hour} summary:") 

        print(f"  🟢 Empty: {counts[STATUS_EMPTY]}  " 

              f"🔵 Normal: {counts[STATUS_NORMAL]}  " 

              f"🟡 Urgent: {counts[STATUS_URGENT]}  " 

              f"🔴 Critical: {counts[STATUS_CRITICAL]}") 

 

        # Fire alerts if needed 

        from alerts import get_bins_above 

        critical = get_bins_above(city_bins, THRESHOLD_CRITICAL) 

        if critical: 

            print(f"\n  {'⚠' * 20}") 

            print(f"  EMERGENCY — {len(critical)} CRITICAL BIN(S):") 

            for b in sorted(critical, 

                            key=lambda x: x["fill_level"], reverse=True): 

                print(f"    🔴 {b['id']} ({b['zone']}) at {b['fill_level']}%") 

            print(f"  {'⚠' * 20}") 

 

        time.sleep(delay) 

 

    return city_bins 

 

# ============================================================= 

#  SECTION 7 — FINAL TRIP REPORT 

#  Printed after every dispatch. The summary card. 

# ============================================================= 

 

def print_trip_report(route, total_distance, bins_skipped, 

                      fuel_data, hour, trip_number): 

    """ 

    Prints a clean, full trip report after a dispatch. 

 

    Args: 

        route          (list):  The route taken 

        total_distance (float): Total km driven 

        bins_skipped   (int):   Bins not collected 

        fuel_data      (dict):  Savings data 

        hour           (int):   What hour this dispatch happened 

        trip_number    (int):   Which trip number this is 

    """ 

 

    print("\n  " + "=" * 54) 

    print(f"  📋  TRIP REPORT — DISPATCH #{trip_number}  |  HOUR {hour}") 

    print("  " + "=" * 54) 

 

    if not route: 

        print("  No bins needed collection this trip.") 

        print("  " + "=" * 54) 

        return 

 

    print(f"\n  ROUTE TAKEN:") 

    print(f"  {'─' * 44}") 

    print(f"  Start → DEPOT {TRUCK_START}") 

    for i, stop in enumerate(route, 1): 

        b = stop["bin"] 

        flag = "🔴" if b["fill_level"] >= THRESHOLD_CRITICAL else "🟡" 

        print(f"  Stop {i:<2} → {b['id']} ({b['zone']:<12}) " 

              f"{b['fill_level']:>3}% {flag}  +{stop['distance']} km") 

    print(f"  End   → DEPOT {TRUCK_START}") 

 

    print(f"\n  STATISTICS:") 

    print(f"  {'─' * 44}") 

    print(f"  Trip number          : #{trip_number}") 

    print(f"  Dispatched at hour   : {hour}") 

    print(f"  Bins collected       : {len(route)}") 

    print(f"  Bins skipped         : {bins_skipped} (below threshold)") 

    print(f"  Total distance       : {total_distance} km") 

    print(f"  {'─' * 44}") 

    print(f"  SAVINGS vs old system:") 

    print(f"  Old route distance   : {fuel_data['old_distance']} km") 

    print(f"  Distance saved       : {fuel_data['saved_distance']} km") 

    print(f"  Fuel saving          : {fuel_data['percentage_saved']}%") 

    litres = round(fuel_data["saved_distance"] * 0.35, 1) 

    co2    = round(fuel_data["saved_distance"] * 0.35 * 2.68, 1) 

    print(f"  Est. fuel saved      : ~{litres} litres") 

    print(f"  Est. CO₂ avoided     : ~{co2} kg") 

    print("  " + "=" * 54) 

 

# ============================================================= 

#  SECTION 8 — BEFORE VS AFTER COMPARISON 

#  Shows the city map before and after truck collection 

# ============================================================= 

 

def before_after(city_before, city_after): 

    """ 

    Prints a side-by-side before and after bin status comparison. 

 

    Args: 

        city_before (dict): City state before dispatch 

        city_after  (dict): City state after dispatch 

    """ 

 

    print("\n  " + "=" * 60) 

    print("  🔄  BEFORE vs AFTER — BIN STATUS COMPARISON") 

    print("  " + "=" * 60) 

    print(f"  {'BIN':<6} {'BEFORE':>8}  {'AFTER':>8}  CHANGE") 

    print("  " + "─" * 50) 

 

    for bin_id in city_before: 

        before_fill = city_before[bin_id]["fill_level"] 

        after_fill  = city_after[bin_id]["fill_level"] 

        change      = after_fill - before_fill 

 

        if change < 0: 

            change_str = f"↓ {abs(change)}%  ✅ collected" 

        elif change == 0: 

            change_str = f"→ no change" 

        else: 

            change_str = f"↑ {change}%" 

 

        print(f"  {bin_id:<6} {before_fill:>7}%  {after_fill:>7}%  {change_str}") 

 

    print("  " + "=" * 60) 

 

# ============================================================= 

#  SECTION 9 — TEST 

#  Run this file directly to see the full visual demo. 

#  In VS Code terminal: python display.py 

# 

#  NOTE: This test uses time.sleep() for animation. 

#        Set FAST_MODE = True below to skip delays. 

# ============================================================= 

 

FAST_MODE = False   # ← Set to False for full animated demo 

                    #   Set to True for instant output (testing) 

 

if __name__ == "__main__": 

 

    DELAY = 0 if FAST_MODE else 1.5   # seconds between frames 

 

    print("=" * 56) 

    print("  GREEN LOOP — Display Module Test") 

    if FAST_MODE: 

        print("  Running in FAST MODE (no animation delays)") 

    else: 

        print("  Running in ANIMATED MODE (1.5s delays)") 

    print("=" * 56) 

 

    # --- Setup --- 

    print("\n  Creating city...") 

    city = create_city() 

    print("  30 bins created.\n") 

 

    # --- Test 1: Draw initial map --- 

    print("[TEST 1] City map at start:") 

    draw_map(city) 

 

    # --- Test 2: Bin status panel --- 

    print("\n[TEST 2] Bin status panel — all 30 bins:") 

    print_bin_panel(city) 

 

    # --- Test 3: Live monitoring for 5 hours --- 

    print("\n[TEST 3] Live dashboard — 5 hours of monitoring:") 

    if FAST_MODE: 

        # In fast mode just simulate and show final state 

        for _ in range(5): 

            city = simulate_one_hour(city) 

        print("  (5 hours simulated)") 

        draw_map(city) 

        print_bin_panel(city) 

    else: 

        city = live_dashboard(city, hours=5, delay=DELAY) 

 

    # --- Test 4: Save city state before dispatch --- 

    import copy 

    city_before = copy.deepcopy(city) 

 

    # --- Test 5: Dispatch and animate --- 

    print("\n[TEST 4] Running alert scan before dispatch:") 

    urgent_heap, critical_list = scan_and_alert(city) 

 

    print("\n[TEST 5] Dispatching truck and animating route:") 

    graph = build_graph(city) 

    route, total_dist, skipped = greedy_route(city, graph) 

 

    if FAST_MODE: 

        # Just show the map with route planned 

        draw_map(city, visited_bins=set(), route=route) 

        print(f"\n  Route planned: {len(route)} stops") 

        for i, stop in enumerate(route, 1): 

            b = stop["bin"] 

            print(f"  Stop {i}: {b['id']} ({b['zone']}) at {b['fill_level']}%") 

    else: 

        animate_route(city, route, delay=DELAY) 

 

    # Actually dispatch (empties bins) 

    route, total_dist, skipped, fuel_data, city = dispatch_truck(city) 

 

    # --- Test 6: Trip report --- 

    print("\n[TEST 6] Trip report:") 

    print_trip_report(route, total_dist, skipped, fuel_data, 

                      hour=5, trip_number=1) 

 

    # --- Test 7: Before vs after --- 

    print("\n[TEST 7] Before vs after comparison:") 

    before_after(city_before, city) 

 

    # --- Test 8: Map after collection --- 

    print("\n[TEST 8] City map AFTER truck collected bins:") 

    draw_map(city) 

 

    # --- Test 9: Simulate more hours and second dispatch --- 

    print("\n[TEST 9] Simulating 4 more hours and running second dispatch...") 

    for _ in range(4): 

        city = simulate_one_hour(city) 

 

    city_before_2 = copy.deepcopy(city) 

    route2, total_dist2, skipped2, fuel_data2, city = dispatch_truck(city) 

    print_trip_report(route2, total_dist2, skipped2, fuel_data2, 

                      hour=9, trip_number=2) 

 

    print("\n[TEST 10] Final city map after second dispatch:") 

    draw_map(city) 

 

    print("\n" + "=" * 56) 

    print("  All tests passed. display.py is ready.") 

    print("  Set FAST_MODE = False for the animated demo.") 

    print("=" * 56) 
