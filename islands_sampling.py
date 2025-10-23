import random
import pandas as pd
from datetime import datetime

class IslandsSampler:
    def __init__(self, random_seed=42):
        self.villages = ['Vardo', 'Colmar', 'Arcadia']
        self.target_per_village = 20
        self.participants = []
        self.potential_participants = {}
        self.random_seed = random_seed
        
        # Set random seed for reproducibility
        random.seed(self.random_seed)
        
        # Initialize tracking for each village
        for village in self.villages:
            self.potential_participants[village] = []
    
    def add_potential_participant(self, village, name, house_number, age=None):
        """Add a potential participant found during village exploration"""
        participant = {
            'village': village,
            'name': name,
            'house_number': house_number,
            'age': age,
            'contacted': False,
            'consented': None,
            'tug_time': None,
            'timestamp': None
        }
        self.potential_participants[village].append(participant)
        print(f"Added {name} from {village}, House {house_number}")
    
    def generate_sampling_order(self, village):
        """Generate randomized sampling order for a village"""
        if village not in self.potential_participants:
            print(f"No data for village: {village}")
            return []
        
        # Shuffle the list randomly (using seed for reproducibility)
        village_list = self.potential_participants[village].copy()
        random.seed(self.random_seed + hash(village))  # Village-specific seed
        random.shuffle(village_list)
        
        print(f"\n=== RANDOM SAMPLING ORDER FOR {village.upper()} ===")
        for i, person in enumerate(village_list, 1):
            status = "✓ COMPLETED" if person['contacted'] else "⏳ PENDING"
            print(f"{i:2d}. {person['name']} (House {person['house_number']}) - {status}")
        
        return village_list
    
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
        """Show current sampling progress"""
        print("\n" + "="*60)
        print("SAMPLING PROGRESS REPORT")
        print("="*60)
        
        for village in self.villages:
            completed = len([p for p in self.participants if p['village'] == village])
            contacted = len([p for p in self.potential_participants[village] if p['contacted']])
            total_potential = len(self.potential_participants[village])
            
            print(f"\n{village}:")
            print(f"  Target: {self.target_per_village}")
            print(f"  Completed: {completed}")
            print(f"  Still need: {max(0, self.target_per_village - completed)}")
            print(f"  Response rate: {contacted}/{total_potential} contacted")
    
    def export_data(self):
        """Export collected data to CSV"""
        if not self.participants:
            print("No data to export yet!")
            return
        
        df = pd.DataFrame(self.participants)
        filename = f"islands_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        df.to_csv(filename, index=False)
        print(f"Data exported to: {filename}")
        
        # Show basic summary
        print(f"\nData Summary:")
        print(f"Total participants: {len(self.participants)}")
        for village in self.villages:
            count = len(df[df['village'] == village])
            print(f"{village}: {count} participants")
    
    def get_next_participants(self, village, n=5):
        """Get next n participants to contact in a village"""
        order = self.generate_sampling_order(village)
        next_contacts = [p for p in order if not p['contacted']][:n]
        
        print(f"\n🎯 NEXT {n} TO CONTACT IN {village.upper()}:")
        for i, person in enumerate(next_contacts, 1):
            print(f"{i}. {person['name']} - House {person['house_number']}")
        
        return next_contacts

# Example usage script
def demo_usage():
    """Demo how to use the sampler"""
    print("🏝️  ISLANDS SAMPLING ASSISTANT")
    print("="*50)
    
    # Create sampler
    sampler = IslandsSampler()
    
    # Phase 1: Exploration (add participants as you find them)
    print("\n📝 PHASE 1: Add participants as you explore villages")
    print("Use: sampler.add_potential_participant(village, name, house_number)")
    
    # Example entries (you'd do this for real)
    sampler.add_potential_participant('Vardo', 'Alice Johnson', 'House 1')
    sampler.add_potential_participant('Vardo', 'Bob Smith', 'House 3')
    sampler.add_potential_participant('Vardo', 'Carol Davis', 'House 5')
    
    # Phase 2: Random sampling
    print("\n🎲 PHASE 2: Generate random sampling order")
    sampler.get_next_participants('Vardo', 3)
    
    # Phase 3: Record results
    print("\n📊 PHASE 3: Record contact attempts")
    sampler.record_contact_attempt('Vardo', 'Alice Johnson', True, 45, 12.3)
    sampler.record_contact_attempt('Vardo', 'Bob Smith', False)
    
    # Phase 4: Track progress
    print("\n📈 PHASE 4: Check progress")
    sampler.get_sampling_status()
    
    return sampler

if __name__ == "__main__":
    # Run demo
    sampler = demo_usage()
    
    print("\n" + "="*60)
    print("HOW TO USE THIS FOR YOUR ASSIGNMENT:")
    print("="*60)
    print("1. Run the script: python islands_sampling.py")
    print("2. Create sampler: sampler = IslandsSampler()")
    print("3. As you explore, add people: sampler.add_potential_participant()")
    print("4. Get random order: sampler.get_next_participants('Vardo')")
    print("5. Record results: sampler.record_contact_attempt()")
    print("6. Check progress: sampler.get_sampling_status()")
    print("7. Export data: sampler.export_data()")