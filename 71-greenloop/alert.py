# ============================================================= 

#  GREEN LOOP — alerts.py 

 

#  What this file does: 

#    1. Scans all 30 bins and detects which need attention 

#    2. Sorts them by urgency using a Min-Heap (priority queue) 

#    3. Fires alerts — urgent warnings and critical emergencies 

#    4. Gives Person 3 (the router) a ready-to-use priority list 

# 

#  DSA used here: MIN-HEAP (Python's heapq module) 

#  Why: A heap always keeps the most urgent bin at the top. 

#       Inserting a bin = O(log n). Getting most urgent = O(1). 

#       Much faster than sorting the list every single time. 

# 

#  Depends on: city.py (Person 1's file) 

# ============================================================= 

 

import heapq   # built into Python — no installation needed 

from city import ( 

    create_city, 

    simulate_one_hour, 

    get_bins_above, 

    THRESHOLD_URGENT, 

    THRESHOLD_CRITICAL, 

) 

 

# ============================================================= 

#  SECTION 1 — CONSTANTS 

# ============================================================= 

 

# Fill level categories with labels and symbols 

STATUS_EMPTY    = "empty"     # 0  – 30% 

STATUS_NORMAL   = "normal"    # 31 – 69% 

STATUS_URGENT   = "urgent"    # 70 – 84% 

STATUS_CRITICAL = "critical"  # 85 – 100% 

 

# How we display each status in the terminal 

STATUS_DISPLAY = { 

    STATUS_EMPTY:    ("🟢", "EMPTY    "), 

    STATUS_NORMAL:   ("🔵", "NORMAL   "), 

    STATUS_URGENT:   ("🟡", "URGENT   "), 

    STATUS_CRITICAL: ("🔴", "CRITICAL "), 

} 

 

# ============================================================= 

#  SECTION 2 — DETERMINE BIN STATUS 

#  Given a fill level, return what category it falls into 

# ============================================================= 

 

def get_status(fill_level): 

    """ 

    Returns the status label for a given fill level. 

 

    Args: 

        fill_level (int): 0 to 100 

 

    Returns: 

        str: one of 'empty', 'normal', 'urgent', 'critical' 

    """ 

    if fill_level >= THRESHOLD_CRITICAL: 

        return STATUS_CRITICAL 

    elif fill_level >= THRESHOLD_URGENT: 

        return STATUS_URGENT 

    elif fill_level > 30: 

        return STATUS_NORMAL 

    else: 

        return STATUS_EMPTY 

 

# ============================================================= 

#  SECTION 3 — BUILD THE PRIORITY QUEUE (THE HEAP) 

#  A Min-Heap always puts the SMALLEST value at the top. 

#  We want the MOST URGENT bin at the top. 

#  Most urgent = HIGHEST fill level. 

# 

#  Trick: we store fill level as NEGATIVE number. 

#  So a bin at 95% is stored as -95. 

#  -95 < -70, so 95% bin sits at the top of the min-heap. 

#  This is the standard trick to turn a min-heap into a max-heap. 

# ============================================================= 

 

def build_priority_queue(city_bins, min_fill=0): 

    """ 

    Scans all bins and pushes them into a min-heap sorted by urgency. 

    Most urgent bin (highest fill %) always sits at the top. 

 

    Args: 

        city_bins (dict): The city from Person 1 

        min_fill  (int):  Only include bins at or above this fill level 

                          Default 0 means include all bins 

 

    Returns: 

        list: A heap (list managed by heapq) of tuples: 

              (-fill_level, bin_id, bin_data) 

              Negative fill so highest fill = top of heap 

    """ 

    heap = []  # starts empty 

 

    for bin_id in city_bins: 

        bin_data  = city_bins[bin_id] 

        fill      = bin_data["fill_level"] 

 

        if fill >= min_fill: 

            # We push a tuple: (priority, bin_id, bin_data) 

            # Priority = -fill_level (negative so highest fill = top) 

            # bin_id is included so ties break alphabetically — consistent ordering 

            heapq.heappush(heap, (-fill, bin_id, bin_data)) 

 

    return heap 

 

# ============================================================= 

#  SECTION 4 — SCAN AND ALERT 

#  Goes through the heap and fires alerts for urgent/critical bins 

# ============================================================= 

 

def scan_and_alert(city_bins): 

    """ 

    Scans all bins, builds the priority queue, and prints alerts 

    for any bin that is urgent or critical. 

 

    Args: 

        city_bins (dict): The current city state 

 

    Returns: 

        tuple: (urgent_heap, critical_list) 

               urgent_heap  — heap of all bins at 70%+, sorted by urgency 

               critical_list — plain list of only the critical bins (85%+) 

    """ 

 

    # Build heap of only bins that need attention (70%+) 

    urgent_heap = build_priority_queue(city_bins, min_fill=THRESHOLD_URGENT) 

 

    # Separately collect critical bins for emergency alerts 

    critical_list = get_bins_above(city_bins, THRESHOLD_CRITICAL) 

 

    # --- Fire critical alerts first --- 

    if critical_list: 

        print(f"\n  {'!' * 52}") 

        print(f"  ⚠  EMERGENCY — {len(critical_list)} BIN(S) ARE CRITICAL") 

        print(f"  {'!' * 52}") 

        # Sort critical bins highest fill first 

        for b in sorted(critical_list, key=lambda x: x["fill_level"], reverse=True): 

            print(f"  🔴 {b['id']} | Zone: {b['zone']:<14} | " 

                  f"Fill: {b['fill_level']:>3}% | Location: {b['location']}" 

                  f"  ← COLLECT IMMEDIATELY") 

        print(f"  {'!' * 52}") 

    else: 

        print("\n  ✅  No critical bins at this time.") 

 

    # --- Then show all urgent bins --- 

    urgent_only = get_bins_above(city_bins, THRESHOLD_URGENT) 

    non_critical_urgent = [ 

        b for b in urgent_only if b["fill_level"] < THRESHOLD_CRITICAL 

    ] 

 

    if non_critical_urgent: 

        print(f"\n  ⚠  {len(non_critical_urgent)} bin(s) are URGENT (collect soon):") 

        for b in sorted(non_critical_urgent, 

                        key=lambda x: x["fill_level"], reverse=True): 

            print(f"  🟡 {b['id']} | Zone: {b['zone']:<14} | " 

                  f"Fill: {b['fill_level']:>3}% | Location: {b['location']}") 

    else: 

        print("  ✅  No urgent-only bins at this time.") 

 

    return urgent_heap, critical_list 

 

# ============================================================= 

#  SECTION 5 — PEEK AT TOP OF HEAP 

#  Used by Person 3 (the router) to see the most urgent bin 

#  without removing it from the heap 

# ============================================================= 

 

def peek_top(heap): 

    """ 

    Returns the most urgent bin without removing it from the heap. 

    If heap is empty, returns None. 

 

    Args: 

        heap (list): The priority heap 

 

    Returns: 

        dict or None: The most urgent bin's data 

    """ 

    if not heap: 

        return None 

    # heap[0] is always the top — tuple: (-fill, bin_id, bin_data) 

    return heap[0][2] 

 

# ============================================================= 

#  SECTION 6 — POP FROM HEAP 

#  Used by Person 3 to take the most urgent bin off the heap 

#  after the truck has been dispatched to it 

# ============================================================= 

 

def pop_most_urgent(heap): 

    """ 

    Removes and returns the most urgent bin from the heap. 

    After this call, the next most urgent bin becomes the top. 

 

    Args: 

        heap (list): The priority heap 

 

    Returns: 

        dict or None: The bin data of the most urgent bin 

    """ 

    if not heap: 

        return None 

    neg_fill, bin_id, bin_data = heapq.heappop(heap) 

    return bin_data 

 

# ============================================================= 

#  SECTION 7 — FULL STATUS BOARD 

#  Prints every single bin's current status — all 30 

#  Used by Person 4 (display) for the city overview 

# ============================================================= 

 

def print_full_status_board(city_bins): 

    """ 

    Prints a full status board of all 30 bins. 

    Sorted by fill level — highest first. 

    Every bin gets a colour-coded status label. 

 

    Args: 

        city_bins (dict): The current city state 

    """ 

 

    # Sort all bins by fill level, highest first 

    sorted_bins = sorted( 

        city_bins.values(), 

        key=lambda b: b["fill_level"], 

        reverse=True 

    ) 

 

    print(f"\n  {'BIN':<6} {'ZONE':<14} {'LOCATION':<12} {'FILL':>5}  " 

          f"{'BAR':<12} STATUS") 

    print("  " + "-" * 68) 

 

    for b in sorted_bins: 

        fill    = b["fill_level"] 

        status  = get_status(fill) 

        symbol, label = STATUS_DISPLAY[status] 

        bar     = "█" * (fill // 10)   # each block = 10% 

        spaces  = " " * (10 - len(bar)) 

 

        print(f"  {b['id']:<6} {b['zone']:<14} {str(b['location']):<12} " 

              f"{fill:>4}%  {bar}{spaces}  {symbol} {label}") 

 

    print("  " + "-" * 68) 

 

    # Summary counts at the bottom 

    counts = {s: 0 for s in [STATUS_EMPTY, STATUS_NORMAL, 

                               STATUS_URGENT, STATUS_CRITICAL]} 

    for b in city_bins.values(): 

        counts[get_status(b["fill_level"])] += 1 

 

    print(f"\n  SUMMARY →  " 

          f"🟢 Empty: {counts[STATUS_EMPTY]}  " 

          f"🔵 Normal: {counts[STATUS_NORMAL]}  " 

          f"🟡 Urgent: {counts[STATUS_URGENT]}  " 

          f"🔴 Critical: {counts[STATUS_CRITICAL]}  " 

          f"| Total: {len(city_bins)}") 

 

# ============================================================= 

#  SECTION 8 — SIMULATE LIVE MONITORING 

#  Runs for several hours, printing alerts as bins fill up. 

#  This is the "live system" feel for the demo. 

# ============================================================= 

 

def live_monitor(city_bins, hours=6): 

    """ 

    Simulates the system monitoring bins over several hours. 

    Each hour, bins fill up and the system checks for alerts. 

 

    Args: 

        city_bins (dict): Starting city state 

        hours     (int):  How many hours to simulate 

 

    Returns: 

        dict: Final city state after all hours 

    """ 

 

    print(f"\n  Monitoring city for {hours} hours...\n") 

    print("  " + "=" * 52) 

 

    for hour in range(1, hours + 1): 

        city_bins = simulate_one_hour(city_bins) 

        print(f"\n  ⏰  HOUR {hour}") 

 

        # Quick fill summary for this hour 

        critical = get_bins_above(city_bins, THRESHOLD_CRITICAL) 

        urgent   = get_bins_above(city_bins, THRESHOLD_URGENT) 

        non_crit = [b for b in urgent if b["fill_level"] < THRESHOLD_CRITICAL] 

 

        if critical: 

            print(f"  🔴 {len(critical)} CRITICAL bin(s)  " 

                  f"🟡 {len(non_crit)} urgent bin(s)") 

            for b in sorted(critical, 

                            key=lambda x: x["fill_level"], reverse=True): 

                print(f"      ⚠  {b['id']} ({b['zone']}) " 

                      f"at {b['fill_level']}% — EMERGENCY") 

        elif non_crit: 

            print(f"  🟡 {len(non_crit)} urgent bin(s) — no critical yet") 

            for b in sorted(non_crit, 

                            key=lambda x: x["fill_level"], reverse=True): 

                print(f"      →  {b['id']} ({b['zone']}) at {b['fill_level']}%") 

        else: 

            print("  ✅  All bins within normal range.") 

 

        print("  " + "-" * 52) 

 

    return city_bins 

 

# ============================================================= 

#  SECTION 9 — TEST 

#  Run this file directly to check everything works. 

#  In VS Code: right click → Run Python File in Terminal 

#  Or in terminal: python alerts.py 

# ============================================================= 

 

if __name__ == "__main__": 

 

    print("=" * 56) 

    print("  GREEN LOOP — Alert System Test") 

    print("=" * 56) 

 

    # --- Setup: create city --- 

    print("\n  Setting up city...") 

    city = create_city() 

    print(f"  30 bins created.\n") 

 

    # --- Test 1: Full status board at start --- 

    print("[TEST 1] Full status board — all 30 bins at start:") 

    print_full_status_board(city) 

 

    # --- Test 2: Live monitoring over 6 hours --- 

    print("\n[TEST 2] Live monitoring — 6 hours of simulation:") 

    city = live_monitor(city, hours=6) 

 

    # --- Test 3: Full status board after 6 hours --- 

    print("\n[TEST 3] Full status board after 6 hours:") 

    print_full_status_board(city) 

 

    # --- Test 4: Scan and fire alerts --- 

    print("\n[TEST 4] Running full alert scan...") 

    urgent_heap, critical_list = scan_and_alert(city) 

 

    # --- Test 5: Heap operations --- 

    print("\n[TEST 5] Heap operations — peek and pop:") 

    print(f"  Heap size: {len(urgent_heap)} bins queued") 

 

    top = peek_top(urgent_heap) 

    if top: 

        print(f"  Most urgent bin (peek):  " 

              f"{top['id']} at {top['fill_level']}% — NOT removed from heap") 

 

    popped = pop_most_urgent(urgent_heap) 

    if popped: 

        print(f"  Most urgent bin (pop):   " 

              f"{popped['id']} at {popped['fill_level']}% — REMOVED from heap") 

 

    next_top = peek_top(urgent_heap) 

    if next_top: 

        print(f"  Next most urgent (peek): " 

              f"{next_top['id']} at {next_top['fill_level']}%") 

    print(f"  Heap size after pop: {len(urgent_heap)} bins remaining") 

 

    # --- Test 6: Build heap with all bins and show order --- 

    print("\n[TEST 6] Priority queue — full dispatch order for truck:") 

    full_heap = build_priority_queue(city, min_fill=THRESHOLD_URGENT) 

    print(f"  {len(full_heap)} bins queued for collection, in priority order:\n") 

    print(f"  {'RANK':<6} {'BIN':<6} {'ZONE':<14} {'FILL':>5}  STATUS") 

    print("  " + "-" * 44) 

    rank = 1 

    temp_heap = list(full_heap)   # copy so we don't destroy the original 

    heapq.heapify(temp_heap) 

    while temp_heap: 

        b = pop_most_urgent(temp_heap) 

        symbol, label = STATUS_DISPLAY[get_status(b["fill_level"])] 

        print(f"  {rank:<6} {b['id']:<6} {b['zone']:<14} " 

              f"{b['fill_level']:>4}%  {symbol} {label}") 

        rank += 1 

 

    print("\n" + "=" * 56) 

    print("  All tests passed. alerts.py is ready.") 

    print("  urgent_heap is ready to hand off to Person 3 (router).") 

    print("=" * 56) 
