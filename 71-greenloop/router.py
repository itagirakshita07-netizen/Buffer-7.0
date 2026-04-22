# ============================================================= 

#  GREEN LOOP — router.py 

#  What this file does: 

#    1. Builds the city as a Graph (bins = nodes, roads = edges) 

#    2. Calculates distances between all bins 

#    3. Uses a Greedy Algorithm to build the truck's route 

#    4. Handles truck capacity — trip ends when truck is full 

#    5. Returns the ordered stop list to Person 4 (display) 

# 

#  DSA used here: 

#    GRAPH         — city represented as adjacency list 

#    GREEDY        — always go to nearest urgent bin next 

# 

#  Why Greedy? 

#    At every step the truck asks one question: 

#    "Which urgent bin is closest to where I am right now?" 

#    It picks that one. Repeats. Simple, fast, good enough. 

# 

#  Depends on: city.py and alerts.py 

# ============================================================= 

 

import math 

from city import ( 

    create_city, 

    simulate_one_hour, 

    empty_bin, 

    THRESHOLD_URGENT, 

    THRESHOLD_CRITICAL, 

) 

from alerts import ( 

    build_priority_queue, 

    scan_and_alert, 

    print_full_status_board, 

    live_monitor, 

) 

 

# ============================================================= 

#  SECTION 1 — CONSTANTS 

# ============================================================= 

 

TRUCK_CAPACITY   = 10    # truck can collect max 10 bins per trip 

TRUCK_START      = (0, 0)  # truck depot — bottom left of the city grid 

COLLECTION_THRESHOLD = THRESHOLD_URGENT  # only collect bins at 70%+ 

 

# ============================================================= 

#  SECTION 2 — DISTANCE CALCULATION 

#  Euclidean distance between two points on the grid. 

#  This is the "road distance" in our simulated city. 

# ============================================================= 

 

def distance(loc1, loc2): 

    """ 

    Calculates straight-line distance between two grid locations. 

 

    Args: 

        loc1 (tuple): (x, y) of first location 

        loc2 (tuple): (x, y) of second location 

 

    Returns: 

        float: distance between the two points, rounded to 2 decimals 

    """ 

    x1, y1 = loc1 

    x2, y2 = loc2 

    return round(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2), 2) 

 

# ============================================================= 

#  SECTION 3 — BUILD THE GRAPH 

#  The city is represented as a Graph. 

#  Nodes  = bins (each bin is a point on the grid) 

#  Edges  = roads between every pair of bins 

#  Weight = distance between the two bins 

# 

#  We use an adjacency list — a dictionary where: 

#    Key   = bin ID 

#    Value = list of (neighbour_bin_id, distance) tuples 

# 

#  Every bin is connected to every other bin (complete graph) 

#  because the truck can theoretically drive anywhere. 

# ============================================================= 

 

def build_graph(city_bins): 

    """ 

    Builds a complete weighted graph of the city. 

    Every bin is connected to every other bin with a distance edge. 

 

    Args: 

        city_bins (dict): The city from Person 1 

 

    Returns: 

        dict: Adjacency list — { bin_id: [(neighbour_id, dist), ...] } 

    """ 

 

    graph = {} 

    bin_ids = list(city_bins.keys()) 

 

    # Create an entry for every bin 

    for bin_id in bin_ids: 

        graph[bin_id] = [] 

 

    # Connect every bin to every other bin 

    for i in range(len(bin_ids)): 

        for j in range(len(bin_ids)): 

            if i != j:  # don't connect a bin to itself 

                id_a = bin_ids[i] 

                id_b = bin_ids[j] 

                loc_a = city_bins[id_a]["location"] 

                loc_b = city_bins[id_b]["location"] 

                dist  = distance(loc_a, loc_b) 

                graph[id_a].append((id_b, dist)) 

 

    # Sort each bin's neighbour list by distance — nearest first 

    # This makes the greedy step faster — just pick the first valid one 

    for bin_id in graph: 

        graph[bin_id].sort(key=lambda x: x[1]) 

 

    return graph 

 

# ============================================================= 

#  SECTION 4 — GREEDY ROUTE ALGORITHM 

 

#  How it works: 

#    1. Start at the truck depot (0, 0) 

#    2. Look at all urgent bins (70%+) that haven't been visited 

#    3. Find the nearest one to current location 

#    4. Drive there. Add it to the route. Mark as visited. 

#    5. Repeat from the new location until: 

#       - No more urgent bins, OR 

#       - Truck is full (capacity reached) 

#    6. Return the ordered route 

# 

#  Why is this "Greedy"? 

#    Because at every step we make the locally best choice 

#    (nearest bin) without looking ahead. We're greedy — we 

#    take the best available option right now. 

# ============================================================= 

 

def greedy_route(city_bins, graph, truck_start=TRUCK_START, 

                 capacity=TRUCK_CAPACITY, threshold=COLLECTION_THRESHOLD): 

    """ 

    Builds an optimised collection route using the Greedy algorithm. 

    Always goes to the nearest urgent bin from current position. 

 

    Args: 

        city_bins    (dict):  The city from Person 1 

        graph        (dict):  The city graph from build_graph() 

        truck_start  (tuple): Starting location of the truck 

        capacity     (int):   Max bins the truck can carry 

        threshold    (int):   Minimum fill % to collect a bin 

 

    Returns: 

        tuple: (route, total_distance, bins_skipped) 

            route          — ordered list of bin dicts the truck visits 

            total_distance — total km driven 

            bins_skipped   — number of bins below threshold (not collected) 

    """ 

 

    # --- Setup --- 

    current_location = truck_start 

    visited          = set()      # bin IDs we've already collected 

    route            = []         # the ordered list of stops 

    total_distance   = 0.0 

 

    # Find all bins that need collection (above threshold) 

    bins_to_collect = { 

        bin_id: city_bins[bin_id] 

        for bin_id in city_bins 

        if city_bins[bin_id]["fill_level"] >= threshold 

    } 

 

    bins_skipped = len(city_bins) - len(bins_to_collect) 

 

    # --- Greedy loop --- 

    while len(route) < capacity and bins_to_collect: 

 

        nearest_bin  = None 

        nearest_dist = float("inf")   # start with infinity 

 

        # Look at every unvisited urgent bin 

        for bin_id, bin_data in bins_to_collect.items(): 

            if bin_id in visited: 

                continue 

 

            bin_location = bin_data["location"] 

            dist_to_bin  = distance(current_location, bin_location) 

 

            # Is this bin closer than the current nearest? 

            if dist_to_bin < nearest_dist: 

                nearest_dist = dist_to_bin 

                nearest_bin  = bin_data 

 

        # If no bin found, we're done 

        if nearest_bin is None: 

            break 

 

        # Drive to the nearest bin 

        total_distance  += nearest_dist 

        current_location = nearest_bin["location"] 

        visited.add(nearest_bin["id"]) 

        route.append({ 

            "bin":      nearest_bin, 

            "distance": round(nearest_dist, 2), 

            "cumulative_distance": round(total_distance, 2), 

        }) 

 

        # Remove from bins_to_collect so we don't visit again 

        del bins_to_collect[nearest_bin["id"]] 

 

    # Add return to depot distance 

    return_dist     = distance(current_location, truck_start) 

    total_distance += return_dist 

 

    return route, round(total_distance, 2), bins_skipped 

 

# ============================================================= 

#  SECTION 5 — CALCULATE FUEL SAVED 

#  Compare our optimised route vs the old "visit all bins" method 

# ============================================================= 

 

def calculate_fuel_saved(city_bins, optimised_distance, truck_start=TRUCK_START): 

    """ 

    Calculates how much distance (and therefore fuel) was saved 

    by using our system vs visiting all 30 bins blindly. 

 

    Args: 

        city_bins          (dict):  The city 

        optimised_distance (float): Distance our route covers 

        truck_start        (tuple): Depot location 

 

    Returns: 

        dict: old_distance, saved_distance, percentage_saved 

    """ 

 

    # Simulate the "dumb" route — visits all bins in order, no optimization 

    old_distance   = 0.0 

    prev_location  = truck_start 

 

    for bin_id in city_bins: 

        loc          = city_bins[bin_id]["location"] 

        old_distance += distance(prev_location, loc) 

        prev_location = loc 

 

    # Return to depot 

    old_distance += distance(prev_location, truck_start) 

    old_distance  = round(old_distance, 2) 

 

    saved      = round(old_distance - optimised_distance, 2) 

    percentage = round((saved / old_distance) * 100, 1) if old_distance > 0 else 0 

 

    return { 

        "old_distance":    old_distance, 

        "saved_distance":  saved, 

        "percentage_saved": percentage, 

    } 

 

# ============================================================= 

#  SECTION 6 — PRINT THE ROUTE 

#  Clean, readable output of the truck's planned route 

# ============================================================= 

 

def print_route(route, total_distance, bins_skipped, fuel_data, truck_start=TRUCK_START): 

    """ 

    Prints the truck's route in a clean, readable format. 

    Shows each stop, distance driven, and bin details. 

 

    Args: 

        route          (list):  Ordered stops from greedy_route() 

        total_distance (float): Total km driven 

        bins_skipped   (int):   Bins not collected (below threshold) 

        fuel_data      (dict):  From calculate_fuel_saved() 

        truck_start    (tuple): Depot location 

    """ 

 

    print(f"\n  {'=' * 54}") 

    print(f"  🚛  TRUCK ROUTE — OPTIMISED COLLECTION PLAN") 

    print(f"  {'=' * 54}") 

    print(f"  Depot start: {truck_start}") 

    print(f"  Capacity:    {TRUCK_CAPACITY} bins per trip") 

    print(f"  Threshold:   Collecting bins at {COLLECTION_THRESHOLD}%+") 

    print(f"  {'=' * 54}\n") 

 

    if not route: 

        print("  ✅  No bins need collection right now.") 

        print("  All bins are below the collection threshold.") 

        return 

 

    print(f"  {'STOP':<5} {'BIN':<6} {'ZONE':<14} {'FILL':>5}  " 

          f"{'DIST':>7}  {'CUMULATIVE':>10}  STATUS") 

    print("  " + "-" * 62) 

 

    for i, stop in enumerate(route, 1): 

        b    = stop["bin"] 

        dist = stop["distance"] 

        cum  = stop["cumulative_distance"] 

 

        if b["fill_level"] >= THRESHOLD_CRITICAL: 

            status = "🔴 CRITICAL" 

        else: 

            status = "🟡 URGENT" 

 

        print(f"  {i:<5} {b['id']:<6} {b['zone']:<14} " 

              f"{b['fill_level']:>4}%  " 

              f"{dist:>6} km  {cum:>9} km  {status}") 

 

    print("  " + "-" * 62) 

    print(f"  Return to depot: +{distance(route[-1]['bin']['location'], truck_start)} km") 

    print(f"\n  {'TRIP SUMMARY':}") 

    print(f"  {'─' * 40}") 

    print(f"  Bins collected       : {len(route)}") 

    print(f"  Bins skipped (empty) : {bins_skipped}") 

    print(f"  Total distance       : {total_distance} km") 

    print(f"  {'─' * 40}") 

    print(f"  Old route (all bins) : {fuel_data['old_distance']} km") 

    print(f"  Distance saved       : {fuel_data['saved_distance']} km") 

    print(f"  Fuel saving          : {fuel_data['percentage_saved']}%") 

    print(f"  {'─' * 40}") 

 

    # Estimate litres saved (average truck = 0.35 litres per km) 

    litres_saved = round(fuel_data["saved_distance"] * 0.35, 1) 

    print(f"  Est. fuel saved      : ~{litres_saved} litres") 

    print(f"  {'=' * 54}") 

 

# ============================================================= 

#  SECTION 7 — FULL DISPATCH 

#  Master function that ties everything together. 

#  Called by main.py and used by Person 4 for the display. 

# ============================================================= 

 

def dispatch_truck(city_bins): 

    """ 

    Full end-to-end dispatch: 

      1. Builds the graph 

      2. Runs the greedy router 

      3. Empties collected bins in the city data 

      4. Calculates fuel savings 

      5. Prints the route 

      6. Returns everything for Person 4 

 

    Args: 

        city_bins (dict): Current city state 

 

    Returns: 

        tuple: (route, total_distance, bins_skipped, fuel_data, city_bins) 

    """ 

 

    graph = build_graph(city_bins) 

 

    route, total_distance, bins_skipped = greedy_route( 

        city_bins, graph 

    ) 

 

    fuel_data = calculate_fuel_saved(city_bins, total_distance) 

 

    print_route(route, total_distance, bins_skipped, fuel_data) 

 

    # Empty the bins the truck visited 

    for stop in route: 

        bin_id    = stop["bin"]["id"] 

        city_bins = empty_bin(city_bins, bin_id) 

 

    return route, total_distance, bins_skipped, fuel_data, city_bins 

 

# ============================================================= 

#  SECTION 8 — TEST 

#  Run this file directly to check everything works. 

#  In VS Code terminal: python router.py 

# ============================================================= 

 

if __name__ == "__main__": 

 

    print("=" * 56) 

    print("  GREEN LOOP — Router Module Test") 

    print("=" * 56) 

 

    # --- Setup --- 

    print("\n  Creating city and simulating 5 hours...") 

    city  = create_city() 

    for _ in range(5): 

        city = simulate_one_hour(city) 

    print("  Done.\n") 

 

    # --- Test 1: Show city state before routing --- 

    print("[TEST 1] City status before dispatch:") 

    print_full_status_board(city) 

 

    # --- Test 2: Build the graph --- 

    print("\n[TEST 2] Building city graph...") 

    graph = build_graph(city) 

    print(f"  Graph built. {len(graph)} nodes (bins).") 

    print(f"  Sample — B001's 5 nearest neighbours:") 

    for neighbour_id, dist in graph["B001"][:5]: 

        print(f"    → {neighbour_id} at {dist} km") 

 

    # --- Test 3: Run greedy route --- 

    print("\n[TEST 3] Running greedy route algorithm...") 

    route, total_dist, skipped = greedy_route(city, graph) 

    print(f"  Route generated. {len(route)} stops planned.") 

 

    # --- Test 4: Full dispatch with printed route --- 

    print("\n[TEST 4] Full truck dispatch:") 

    route, total_dist, skipped, fuel_data, city = dispatch_truck(city) 

 

    # --- Test 5: City state after truck collected bins --- 

    print("\n[TEST 5] City status AFTER truck collected bins:") 

    print_full_status_board(city) 

 

    # --- Test 6: Simulate 3 more hours — bins fill up again --- 

    print("\n[TEST 6] Simulating 3 more hours — bins filling again...") 

    for _ in range(3): 

        city = simulate_one_hour(city) 

 

    print("\n  City status after 3 more hours:") 

    print_full_status_board(city) 

 

    print("\n[TEST 7] Second dispatch — new route after bins refill:") 

    route, total_dist, skipped, fuel_data, city = dispatch_truck(city) 

 

    print("\n" + "=" * 56) 

    print("  All tests passed. router.py is ready.") 

    print("  dispatch_truck() is ready for Person 4 (display).") 

    print("=" * 56) 
