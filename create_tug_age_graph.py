import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import seaborn as sns

# Set style for professional appearance
plt.style.use('default')
sns.set_palette("husl")

# Read the dataset
df = pd.read_csv('dataset.csv')

# Clean column names (remove BOM if present)
df.columns = df.columns.str.replace('\ufeff', '')

# Create the figure with proper size for clarity
fig, ax = plt.subplots(figsize=(10, 8))

# Create scatter plot with village-specific colors
village_colors = {'Vardo': '#2E86AB', 'Colmar': '#A23B72', 'Arcadia': '#F18F01'}

for village in df['Village'].unique():
    village_data = df[df['Village'] == village]
    ax.scatter(village_data['Age (years)'], 
              village_data['Timed up and go test (seconds)'],
              c=village_colors[village], 
              label=village,
              alpha=0.7,
              s=60,
              edgecolors='white',
              linewidth=0.5)

# Add trend line using linear regression
x = df['Age (years)']
y = df['Timed up and go test (seconds)']
slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

# Create trend line
line_x = np.linspace(x.min(), x.max(), 100)
line_y = slope * line_x + intercept
ax.plot(line_x, line_y, color='black', linestyle='--', linewidth=2, alpha=0.8, label=f'Trend line (r = {r_value:.3f})')

# Customize the plot with proper formatting
ax.set_xlabel('Age (years)', fontsize=14, fontweight='bold')
ax.set_ylabel('Timed Up and Go Test (seconds)', fontsize=14, fontweight='bold')
ax.set_title('Relationship between Age and Timed Up and Go Test Performance\nIsland Mobility Study (N=60)', 
             fontsize=16, fontweight='bold', pad=20)

# Set axis limits with appropriate padding
ax.set_xlim(15, 105)
ax.set_ylim(5, 18)

# Add grid for better readability
ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)

# Customize legend
ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, fontsize=12)

# Add correlation information as text box
textstr = f'Pearson correlation: r = {r_value:.3f}\np-value = {p_value:.4f}\nSample size: n = {len(df)}'
props = dict(boxstyle='round', facecolor='lightgray', alpha=0.8)
ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=11,
        verticalalignment='top', bbox=props)

# Ensure tick labels are clear and appropriately sized
ax.tick_params(axis='both', which='major', labelsize=12)

# Set spine properties for clean appearance
for spine in ax.spines.values():
    spine.set_linewidth(1.2)

# Tight layout to prevent label cutoff
plt.tight_layout()

# Save the plot as high-quality image
plt.savefig('tug_age_relationship.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig('tug_age_relationship.pdf', bbox_inches='tight', facecolor='white')

# Display the plot
plt.show()

# Print summary statistics for reference
print("Summary Statistics:")
print(f"Age range: {x.min():.0f} - {x.max():.0f} years")
print(f"TUG test range: {y.min():.1f} - {y.max():.1f} seconds")
print(f"Correlation coefficient: r = {r_value:.3f}")
print(f"R-squared: {r_value**2:.3f}")
print(f"Statistical significance: p = {p_value:.4f}")

# Interpretation
if p_value < 0.05:
    print(f"\nThe correlation between age and TUG test time is statistically significant (p < 0.05).")
else:
    print(f"\nThe correlation between age and TUG test time is not statistically significant (p ≥ 0.05).")

if r_value > 0:
    print("There is a positive relationship: TUG test time tends to increase with age.")
else:
    print("There is a negative relationship: TUG test time tends to decrease with age.")