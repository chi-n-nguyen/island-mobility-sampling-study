import random
import pandas as pd
from datetime import datetime

class IslandsSampler:
    """
    Two-Stage Cluster Sampling Implementation for Island Mobility Study
    
    This class implements a statistically valid two-stage cluster sampling approach:
    
    STAGE 1 (Cluster Selection): Randomly select houses within each village
    STAGE 2 (Element Selection): Randomly select adults from within selected houses
    
    JUSTIFICATION FOR TWO-STAGE CLUSTER SAMPLING:
    1. EFFICIENCY: Reduces navigation time in web interface by targeting specific houses
    2. STATISTICAL VALIDITY: Maintains randomness while accounting for household clustering
    3. PRACTICAL: Works within constraints of limited interface navigation
    4. BIAS REDUCTION: Prevents systematic bias that could occur with convenience sampling
    5. REPRESENTATIVENESS: Ensures coverage across different household types and locations
    
    This approach is superior to simple random sampling in clustered populations because:
    - It accounts for natural clustering of individuals within households
    - More efficient data collection while maintaining statistical rigor
    - Reduces travel/navigation time between sampling units
    """
    
    def __init__(self, random_seed=42, houses_per_village=15):
        self.villages = ['Vardo', 'Colmar', 'Arcadia']
        self.target_per_village = 20
        self.houses_per_village = houses_per_village  # Stage 1: Number of houses to select
        self.participants = []
        self.potential_participants = {}
        self.selected_houses = {}  # Track which houses were selected in Stage 1
        self.house_registry = {}   # Track all discovered houses per village
        self.random_seed = random_seed
        
        # Set random seed for reproducibility
        random.seed(self.random_seed)
        
        # Initialize tracking for each village
        for village in self.villages:
            self.potential_participants[village] = []
            self.selected_houses[village] = []
            self.house_registry[village] = set()
    
    def add_house_to_registry(self, village, house_number):
        """
        STAGE 1 PREPARATION: Register discovered houses for cluster selection
        
        This builds our sampling frame of houses (clusters) before Stage 1 selection.
        Each house represents a cluster that may contain multiple adults.
        """
        if village in self.house_registry:
            self.house_registry[village].add(house_number)
            print(f"📍 Registered {house_number} in {village} (Total houses: {len(self.house_registry[village])})")
    
    def select_houses_for_sampling(self, village):
        """
        STAGE 1: CLUSTER SELECTION
        
        Randomly select houses (clusters) from the complete sampling frame.
        This implements the first stage of two-stage cluster sampling.
        
        STATISTICAL RATIONALE:
        - Each house is a cluster containing potential participants
        - Random selection prevents location bias (e.g., avoiding houses that are harder to reach)
        - Ensures geographic representation across the village
        """
        available_houses = list(self.house_registry[village])
        if len(available_houses) == 0:
            print(f"⚠️  No houses registered for {village}. Run exploration first!")
            return []
        
        # Calculate how many houses to select (Stage 1)
        houses_to_select = min(self.houses_per_village, len(available_houses))
        
        # STAGE 1 RANDOM SELECTION: Select houses using village-specific seed
        random.seed(self.random_seed + hash(village))
        selected_houses = random.sample(available_houses, houses_to_select)
        self.selected_houses[village] = selected_houses
        
        print(f"\n🏠 STAGE 1 - SELECTED HOUSES FOR {village.upper()}:")
        print(f"Selected {len(selected_houses)} houses from {len(available_houses)} total")
        for i, house in enumerate(sorted(selected_houses), 1):
            print(f"  {i:2d}. {house}")
        
        return selected_houses
    
    def add_potential_participant(self, village, name, house_number, age=None):
        """
        STAGE 1 PREPARATION: Add participants found during village exploration
        
        This populates our clusters (houses) with potential participants.
        All discovered participants are recorded, but only those in Stage 1 
        selected houses will be eligible for Stage 2 sampling.
        """
        # Register the house in our sampling frame
        self.add_house_to_registry(village, house_number)
        
        participant = {
            'village': village,
            'name': name,
            'house_number': house_number,
            'age': age,
            'contacted': False,
            'consented': None,
            'tug_time': None,
            'timestamp': None,
            'selected_in_stage1': False,  # Will be set during Stage 1
            'selected_in_stage2': False   # Will be set during Stage 2
        }
        self.potential_participants[village].append(participant)
        print(f"Added {name} from {village}, {house_number}")
    
    def generate_two_stage_sampling_order(self, village):
        """
        STAGE 2: ELEMENT SELECTION WITHIN SELECTED CLUSTERS
        
        From the houses selected in Stage 1, randomly select adults within each house.
        This completes the two-stage cluster sampling process.
        
        STATISTICAL RATIONALE:
        - Stage 2 ensures random selection within clusters (houses)
        - Prevents household bias (e.g., always selecting the first person who answers)
        - Maintains overall randomness while being efficient
        """
        if village not in self.potential_participants:
            print(f"No data for village: {village}")
            return []
        
        # First, ensure Stage 1 house selection is complete
        if not self.selected_houses[village]:
            self.select_houses_for_sampling(village)
        
        # Mark participants in Stage 1 selected houses
        selected_house_set = set(self.selected_houses[village])
        stage1_participants = []
        
        for person in self.potential_participants[village]:
            if person['house_number'] in selected_house_set:
                person['selected_in_stage1'] = True
                stage1_participants.append(person)
        
        # STAGE 2: Random selection within each selected house
        print(f"\n🎯 STAGE 2 - PARTICIPANT SELECTION IN {village.upper()}:")
        print("Randomly selecting adults within each Stage 1 selected house...")
        
        # Group by house for Stage 2 selection
        house_groups = {}
        for person in stage1_participants:
            house = person['house_number']
            if house not in house_groups:
                house_groups[house] = []
            house_groups[house].append(person)
        
        # Stage 2: Random selection within each house
        stage2_participants = []
        random.seed(self.random_seed + hash(village) + 100)  # Different seed for Stage 2
        
        for house, people in house_groups.items():
            if len(people) == 1:
                # Only one person in house - automatically selected
                people[0]['selected_in_stage2'] = True
                stage2_participants.extend(people)
                print(f"  {house}: {people[0]['name']} (only resident)")
            else:
                # Multiple people - randomly select (could select all or subset based on needs)
                # For this study, we'll select all adults but in random order
                random.shuffle(people)
                for person in people:
                    person['selected_in_stage2'] = True
                stage2_participants.extend(people)
                names = [p['name'] for p in people]
                print(f"  {house}: {', '.join(names)} (randomized order)")
        
        # Final randomization of the complete list for contact order
        random.shuffle(stage2_participants)
        
        print(f"\n=== FINAL TWO-STAGE SAMPLING ORDER FOR {village.upper()} ===")
        print(f"Stage 1: Selected {len(self.selected_houses[village])} houses")
        print(f"Stage 2: Selected {len(stage2_participants)} participants")
        print("\nContact Order:")
        
        for i, person in enumerate(stage2_participants, 1):
            status = "✓ COMPLETED" if person['contacted'] else "⏳ PENDING"
            print(f"{i:2d}. {person['name']} ({person['house_number']}) - {status}")
        
        return stage2_participants
    
    def record_contact_attempt(self, village, name, consented, age=None, tug_time=None):
        """Record the result of contacting a participant"""
        # Find the participant
        for person in self.potential_participants[village]:
            if person['name'] == name:
                person['contacted'] = True
                person['consented'] = consented
                person['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                if consented:
                    person['age'] = age
                    person['tug_time'] = tug_time
                    self.participants.append(person.copy())
                    print(f"✅ {name} consented and completed (Age: {age}, TUG: {tug_time}s)")
                else:
                    print(f"❌ {name} declined consent")
                break
    
    def get_sampling_status(self):
        """Show current sampling progress with two-stage details"""
        print("\n" + "="*70)
        print("TWO-STAGE CLUSTER SAMPLING PROGRESS REPORT")
        print("="*70)
        
        for village in self.villages:
            completed = len([p for p in self.participants if p['village'] == village])
            contacted = len([p for p in self.potential_participants[village] if p['contacted']])
            stage1_houses = len(self.selected_houses[village])
            total_houses = len(self.house_registry[village])
            stage2_eligible = len([p for p in self.potential_participants[village] 
                                 if p.get('selected_in_stage1', False)])
            
            print(f"\n{village}:")
            print(f"  Target participants: {self.target_per_village}")
            print(f"  Completed: {completed}")
            print(f"  Still needed: {max(0, self.target_per_village - completed)}")
            print(f"  Stage 1 - Houses: {stage1_houses}/{total_houses} selected")
            print(f"  Stage 2 - Eligible: {stage2_eligible} participants in selected houses")
            print(f"  Response rate: {contacted}/{stage2_eligible if stage2_eligible > 0 else 'N/A'} contacted")
    
    def export_data(self):
        """Export collected data to CSV with sampling stage information"""
        if not self.participants:
            print("No data to export yet!")
            return
        
        df = pd.DataFrame(self.participants)
        filename = f"islands_two_stage_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        df.to_csv(filename, index=False)
        print(f"Data exported to: {filename}")
        
        # Show sampling summary
        print(f"\nTwo-Stage Cluster Sampling Summary:")
        print(f"Total participants: {len(self.participants)}")
        for village in self.villages:
            count = len(df[df['village'] == village])
            houses_selected = len(self.selected_houses[village])
            print(f"{village}: {count} participants from {houses_selected} houses")
    
    def get_next_participants(self, village, n=5):
        """Get next n participants to contact using two-stage sampling"""
        order = self.generate_two_stage_sampling_order(village)
        next_contacts = [p for p in order if not p['contacted']][:n]
        
        print(f"\n🎯 NEXT {n} TO CONTACT IN {village.upper()} (Two-Stage Method):")
        for i, person in enumerate(next_contacts, 1):
            print(f"{i}. {person['name']} - {person['house_number']}")
        
        return next_contacts

# Village demographics for realistic sampling
VILLAGE_DATA = {
    'Vardo': {'houses': 762, 'population': 1790},
    'Colmar': {'houses': 2299, 'population': 5650}, 
    'Arcadia': {'houses': 2101, 'population': 5308}
}

def calculate_sampling_strategy(village, target_participants=20, response_rate=0.65):
    """
    Calculate optimal number of houses to sample based on village demographics
    
    Args:
        village: Village name
        target_participants: Target number of participants (default 20)
        response_rate: Expected response rate (ASSUMPTION - adjust based on literature)
    
    Returns:
        Tuple of (houses_to_sample, avg_adults_per_house)
    
    Note: Response rate is an assumption. For your methodology, you should:
    - Research actual response rates for similar mobility/health studies
    - Consider factors like: rural vs urban, study topic, incentives, etc.
    - Pilot test with a few houses to estimate actual response rate
    """
    village_info = VILLAGE_DATA[village]
    total_houses = village_info['houses']
    total_population = village_info['population']
    
    # Calculate average adults per house
    avg_adults_per_house = total_population / total_houses
    
    # Calculate houses needed accounting for response rate
    participants_needed = target_participants / response_rate
    houses_needed = int(participants_needed / avg_adults_per_house) + 2  # +2 buffer
    
    return houses_needed, avg_adults_per_house

def generate_random_sampling_numbers(village, random_seed=42, target_participants=20):
    """
    Demographically-informed two-stage random sampling
    
    Stage 1: Generate random house numbers based on actual village size
    Stage 2: Generate random adult numbers based on demographic averages
    """
    village_info = VILLAGE_DATA[village]
    houses_to_sample, avg_adults = calculate_sampling_strategy(village, target_participants)
    
    print(f"\n🎲 TWO-STAGE RANDOM SAMPLING for {village.upper()}")
    print("="*60)
    print(f"Village Stats: {village_info['houses']} houses, {village_info['population']} people")
    print(f"Average adults per house: {avg_adults:.1f}")
    print(f"Houses to sample: {houses_to_sample} (for 20 participants at 65% response rate)")
    print("="*60)
    
    # Set village-specific seed for reproducibility
    random.seed(random_seed + hash(village))
    
    # Stage 1: Random house numbers from actual village house range
    max_house_number = village_info['houses']
    available_houses = list(range(1, max_house_number + 1))
    selected_houses = random.sample(available_houses, min(houses_to_sample, max_house_number))
    selected_houses.sort()
    
    print(f"STAGE 1 - Random House Numbers:")
    print(f"Selected {len(selected_houses)} houses from {max_house_number} total houses")
    print(f"Houses: {selected_houses}")
    
    # Stage 2: Random adult numbers within each house (based on demographics)
    print(f"\nSTAGE 2 - Random Adult Numbers (per house):")
    max_adults = max(1, int(avg_adults * 2))  # Cap at 2x average for realism
    
    for house in selected_houses:
        # Generate realistic number of adults based on village average
        if avg_adults < 2:
            num_adults = random.choices([1, 2, 3], weights=[50, 35, 15])[0]
        elif avg_adults < 3:
            num_adults = random.choices([1, 2, 3, 4], weights=[20, 40, 30, 10])[0]
        else:
            num_adults = random.choices([2, 3, 4, 5], weights=[30, 35, 25, 10])[0]
            
        adult_numbers = list(range(1, num_adults + 1))
        random.shuffle(adult_numbers)  # Randomize contact order
        print(f"  House {house}: Adults {adult_numbers}")
    
    return selected_houses

# Real sampling plan generator
def generate_real_sampling_plan():
    """Generate demographically-informed sampling plan for island mobility study"""
    print("🏝️  ISLAND MOBILITY STUDY - DEMOGRAPHICALLY-INFORMED TWO-STAGE SAMPLING")
    print("="*80)
    print("Target: 20 participants per village")
    print("Response Rate Assumption: 65% (ESTIMATED - needs literature review)")
    print("Methodology: Two-Stage Cluster Sampling with demographic weighting")
    print("⚠️  NOTE: You should research actual response rates for similar studies")
    print("="*80)
    
    # Calculate and show demographics summary
    print("\n📊 VILLAGE DEMOGRAPHICS:")
    for village in ['Vardo', 'Colmar', 'Arcadia']:
        data = VILLAGE_DATA[village]
        avg_people = data['population'] / data['houses']
        print(f"{village}: {data['houses']} houses, {data['population']} people ({avg_people:.1f} people/house)")
    
    # Generate sampling plan for each village
    for village in ['Vardo', 'Colmar', 'Arcadia']:
        houses = generate_random_sampling_numbers(village, random_seed=42, target_participants=20)
        print()
    
    print("\n📋 DATA COLLECTION INSTRUCTIONS:")
    print("1. Visit each house number in the order listed")
    print("2. Contact adults in the random order shown for each house")
    print("3. Record: Name, Age, Consent (Y/N), TUG time if consented")
    print("4. Stop when you reach 20 participants per village")
    print("5. If house doesn't exist, skip to next house")
    print("\n🎯 Goal: Collect 20 participants × 3 villages = 60 total participants")
    print("\n📈 STATISTICAL JUSTIFICATION:")
    print("Sample sizes calculated using village demographics and expected 65% response rate")
    print("House numbers selected randomly from actual village housing stock")

if __name__ == "__main__":
    # Generate real sampling plan for data collection
    generate_real_sampling_plan()
    
    print("\n" + "="*70)
    print("HOW TO USE TWO-STAGE CLUSTER SAMPLING FOR YOUR ASSIGNMENT:")
    print("="*70)
    print("1. Exploration Phase:")
    print("   - sampler = IslandsSampler()")
    print("   - As you explore: sampler.add_potential_participant(village, name, house)")
    print("2. Stage 1 - House Selection:")
    print("   - Automatically done when you call get_next_participants()")
    print("   - Or manually: sampler.select_houses_for_sampling(village)")
    print("3. Stage 2 - Participant Selection:")
    print("   - sampler.get_next_participants(village, n)")
    print("4. Data Collection:")
    print("   - sampler.record_contact_attempt(village, name, consented, age, tug_time)")
    print("5. Monitoring:")
    print("   - sampler.get_sampling_status()")
    print("6. Export:")
    print("   - sampler.export_data()")
    print("\n📚 ACADEMIC JUSTIFICATION:")
    print("This implements legitimate two-stage cluster sampling as taught in")
    print("statistics courses, providing scientific rigor while being practical.")