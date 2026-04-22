# ============================================================= 

#  GREEN LOOP — city.py 

#  What this file does: 

#    1. Creates a simulated city with 30 bins (the Hash Table) 

#    2. Simulates bins filling up over time 

#    3. Provides helper functions for the rest of the team 

# 

#  DSA used here: HASH TABLE (Python dictionary) 

#  Why: Lets us look up any bin instantly by its ID — O(1) time 

# ============================================================= 

 

import random  

 

# ============================================================= 

#  SECTION 1 — CONSTANTS 

#  These never change while the program runs. 

#  Think of them as the rules of our city. 

# ============================================================= 

 

# How much each zone's bins fill up per simulated hour 

# Format: "zone name": (minimum fill per hour, maximum fill per hour) 

ZONE_FILL_RATES = { 

    "market":      (8, 15),   # busy markets — fills fast 

    "residential": (2, 5),    # homes — slow and steady 

    "school":      (2, 14),   # unpredictable — slow in morning, burst at lunch/home time 

} 

 

# Thresholds — when do we start worrying about a bin? 

THRESHOLD_URGENT   = 70   # above 70% → needs collection soon 

THRESHOLD_CRITICAL = 85   # above 85% → needs collection NOW, health risk 

 

# ============================================================= 

#  SECTION 2 — CREATE THE CITY 

#  This is our Hash Table. 

#  Key   = Bin ID (like "B001") 

#  Value = Dictionary with all the bin's details 

# ============================================================= 

 

def create_city(): 

    """ 

    Builds the city and returns it as a dictionary (hash table). 

    Each bin is stored with a unique ID as the key. 

 

    Returns: 

        dict: The full city — 30 bins, each with id, location, fill_level, zone 

    """ 

 

    city_bins = {}  # our hash table starts empty 

 

    # ---------------------------------------------------------- 

    # Bin definitions — (bin_id, (x, y location), zone_type) 

    # Think of x,y as a grid map of Pune 

    # Grid goes from (0,0) bottom-left to (10,10) top-right 

    # ---------------------------------------------------------- 

 

    bin_definitions = [ 

 

        # --- MARKET ZONE --- near areas like Mandai, Laxmi Road, MG Road 

        # These are the busiest bins — they fill up fastest 

        ("B001", (2, 8),  "market"), 

        ("B002", (3, 7),  "market"), 

        ("B003", (4, 8),  "market"), 

        ("B004", (3, 9),  "market"), 

        ("B005", (5, 8),  "market"), 

 

        # --- SCHOOL ZONE --- near schools and colleges 

        # These are unpredictable — quiet in morning, burst at 4pm 

        ("B006", (2, 6),  "school"), 

        ("B007", (5, 5),  "school"), 

        ("B008", (8, 7),  "school"), 

        ("B009", (7, 8),  "school"), 

        ("B010", (4, 5),  "school"), 

 

        # --- RESIDENTIAL ZONE --- homes in Kothrud, Aundh, Baner etc. 

        # These fill slowly and predictably 

        ("B011", (1, 3),  "residential"), 

        ("B012", (2, 2),  "residential"), 

        ("B013", (1, 5),  "residential"), 

        ("B014", (3, 3),  "residential"), 

        ("B015", (4, 2),  "residential"), 

        ("B016", (6, 3),  "residential"), 

        ("B017", (7, 2),  "residential"), 

        ("B018", (8, 4),  "residential"), 

        ("B019", (9, 3),  "residential"), 

        ("B020", (6, 6),  "residential"), 

        ("B021", (9, 6),  "residential"), 

        ("B022", (8, 2),  "residential"), 

        ("B023", (6, 9),  "residential"), 

        ("B024", (1, 8),  "residential"), 

        ("B025", (5, 1),  "residential"), 

        ("B026", (9, 9),  "residential"), 

        ("B027", (7, 5),  "residential"), 

        ("B028", (3, 1),  "residential"), 

        ("B029", (1, 1),  "residential"), 

        ("B030", (9, 1),  "residential"), 

    ] 

 

    # ---------------------------------------------------------- 

    # Now create each bin and store it in the hash table 

    # This is where the Hash Table is actually built 

    # ---------------------------------------------------------- 

 

    for bin_id, location, zone in bin_definitions: 

        city_bins[bin_id] = { 

            "id":         bin_id, 

            "location":   location, 

            "fill_level": random.randint(10, 45),  # random starting fill 10–45% 

            "zone":       zone, 

        } 

 

    return city_bins 

 

# ============================================================= 

#  SECTION 3 — SIMULATE TIME PASSING 

#  Every time this is called, one "hour" passes in the city. 

#  Bins fill up based on their zone type. 

# ============================================================= 

 

def simulate_one_hour(city_bins): 

    """ 

    Simulates one hour passing. Every bin fills up a little. 

    Market bins fill fast. Residential bins fill slowly. 

    No bin goes above 100%. 

 

    Args: 

        city_bins (dict): The current state of the city 

 

    Returns: 

        dict: The updated city after one hour 

    """ 

 

    for bin_id in city_bins: 

        zone = city_bins[bin_id]["zone"]               # what zone is this bin? 

        min_rate, max_rate = ZONE_FILL_RATES[zone]     # get fill rate for this zone 

        increase = random.randint(min_rate, max_rate)  # random fill within range 

 

        current_fill = city_bins[bin_id]["fill_level"] 

        new_fill = current_fill + increase 

 

        # Never go above 100% 

        city_bins[bin_id]["fill_level"] = min(100, new_fill) 

 

    return city_bins 

 

# ============================================================= 

#  SECTION 4 — HELPER FUNCTIONS 

# ============================================================= 

 

def empty_bin(city_bins, bin_id): 

    """ 

    Empties a bin after the truck collects it. 

    Called by Person 3 (the router) after visiting a bin. 

 

    Args: 

        city_bins (dict): The city 

        bin_id    (str):  Which bin to empty e.g. "B003" 

 

    Returns: 

        dict: Updated city with that bin now at 0% 

    """ 

    city_bins[bin_id]["fill_level"] = 0 

    return city_bins 

 

def get_bins_above(city_bins, threshold): 

    """ 

    Returns all bins whose fill level is at or above a threshold. 

    Called by Person 2 (alerts) and Person 3 (router). 

 

    Args: 

        city_bins (dict): The city 

        threshold (int):  The fill % to check against e.g. 70 

 

    Returns: 

        list: All bin dictionaries at or above that fill level 

    """ 

    result = [] 

    for bin_id in city_bins: 

        if city_bins[bin_id]["fill_level"] >= threshold: 

            result.append(city_bins[bin_id]) 

    return result 

 

def get_bin_by_id(city_bins, bin_id): 

    """ 

    Returns a single bin's data by its ID. 

    This is the Hash Table lookup — instant, O(1). 

 

    Args: 

        city_bins (dict): The city 

        bin_id    (str):  The bin to look up e.g. "B007" 

 

    Returns: 

        dict: That bin's data, or None if not found 

    """ 

    return city_bins.get(bin_id, None) 

 

def get_city_summary(city_bins): 

    """ 

    Returns a summary of the whole city's current state. 

    Useful for Person 4's display. 

 

    Returns: 

        dict: counts of empty, normal, urgent, critical bins 

    """ 

    summary = { 

        "total":    len(city_bins), 

        "empty":    0,   # 0–30% 

        "normal":   0,   # 31–69% 

        "urgent":   0,   # 70–84% 

        "critical": 0,   # 85–100% 

    } 

 

    for bin_id in city_bins: 

        fill = city_bins[bin_id]["fill_level"] 

        if fill <= 30: 

            summary["empty"] += 1 

        elif fill <= 69: 

            summary["normal"] += 1 

        elif fill <= 84: 

            summary["urgent"] += 1 

        else: 

            summary["critical"] += 1 

 

    return summary 

 

# ============================================================= 

#  SECTION 5 — TEST 

#  Run this file directly to make sure everything works. 

#  In VS Code: right click → Run Python File in Terminal 

#  Or in terminal: python city.py 

# ============================================================= 

 

if __name__ == "__main__": 

 

    print("=" * 55) 

    print("  GREEN LOOP — City Module Test") 

    print("=" * 55) 

 

    # --- Test 1: Create the city --- 

    print("\n[TEST 1] Creating city...") 

    city = create_city() 

    print(f"  City created with {len(city)} bins.") 

    print(f"\n  {'BIN':<6} {'ZONE':<14} {'LOCATION':<12} {'FILL':>6}") 

    print("  " + "-" * 42) 

    for bin_id in city: 

        b = city[bin_id] 

        print(f"  {b['id']:<6} {b['zone']:<14} " 

              f"{str(b['location']):<12} {b['fill_level']:>5}%") 

 

    # --- Test 2: Simulate hours passing --- 

    print("\n[TEST 2] Simulating 4 hours passing...") 

    print(f"\n  {'BIN':<6} {'ZONE':<14} {'HOUR 0':>8} {'HOUR 1':>8} " 

          f"{'HOUR 2':>8} {'HOUR 3':>8} {'HOUR 4':>8}") 

    print("  " + "-" * 60) 

 

    # Save starting fills 

    starting_fills = {b: city[b]["fill_level"] for b in city} 

 

    # Save fills after each hour 

    hour_fills = {b: [starting_fills[b]] for b in city} 

    for hour in range(4): 

        city = simulate_one_hour(city) 

        for b in city: 

            hour_fills[b].append(city[b]["fill_level"]) 

 

    # Print ALL 30 bins 

    for bin_id in hour_fills: 

        fills = hour_fills[bin_id] 

        bar = "█" * (fills[-1] // 10) 

        print(f"  {bin_id:<6} {city[bin_id]['zone']:<14} " 

              f"{fills[0]:>7}% {fills[1]:>7}% {fills[2]:>7}% " 

              f"{fills[3]:>7}% {fills[4]:>7}%  {bar}") 

 

    # --- Test 3: Get urgent and critical bins --- 

    print("\n[TEST 3] Checking for urgent and critical bins after 4 hours...") 

    urgent   = get_bins_above(city, THRESHOLD_URGENT) 

    critical = get_bins_above(city, THRESHOLD_CRITICAL) 

    print(f"  Bins at or above {THRESHOLD_URGENT}% (urgent):   {len(urgent)}") 

    print(f"  Bins at or above {THRESHOLD_CRITICAL}% (critical): {len(critical)}") 

    print(f"\n  {'BIN':<6} {'ZONE':<14} {'FILL':>6}  STATUS") 

    print("  " + "-" * 40) 

    for b in sorted(urgent, key=lambda x: x["fill_level"], reverse=True): 

        if b["fill_level"] >= THRESHOLD_CRITICAL: 

            status = "🔴 CRITICAL — collect immediately" 

        else: 

            status = "🟡 URGENT   — collect soon" 

        print(f"  {b['id']:<6} {b['zone']:<14} {b['fill_level']:>5}%  {status}") 

 

    # --- Test 4: Hash table lookup --- 

    print("\n[TEST 4] Hash table lookup — finding B007 directly...") 

    result = get_bin_by_id(city, "B007") 

    if result: 

        print(f"  Found: {result}") 

 

    # --- Test 5: Empty a bin --- 

    print("\n[TEST 5] Truck empties bin B007...") 

    print(f"  Before: Fill = {city['B007']['fill_level']}%") 

    city = empty_bin(city, "B007") 

    print(f"  After:  Fill = {city['B007']['fill_level']}%") 

 

    # --- Test 6: City summary --- 

    print("\n[TEST 6] Overall city summary...") 

    summary = get_city_summary(city) 

    for key, val in summary.items(): 

        print(f"  {key:10}: {val}") 

 

    print("\n" + "=" * 55) 

    print("  All tests passed. city.py is ready.") 

    print("  Hand off city_bins to Persons 2, 3, and 4.") 

    print("=" * 55) 
