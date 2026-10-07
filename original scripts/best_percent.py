import pandas as pd
import matplotlib.pyplot as plt
import os

# Define the path to the folder containing the CSV files
csv_folder = r'C:\Users\dvtur\OneDrive\Desktop\netlogo\csv_percent'  # Update this path to match your folder

# Function to read CSV files and extract relevant data
def read_csv(file_path):
    df = pd.read_csv(file_path, skiprows=5)  # Adjust skiprows based on CSV structure
    return df

# Function to simulate vaccination and evaluate efficiency
def evaluate_vaccination(csv_folder):
    files = [f for f in os.listdir(csv_folder) if f.endswith('.csv')]
    vaccination_percentages = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]  # Vaccination percentages from 0.1% to 0.9%
    
    best_vaccination_percentage = None
    best_efficiency = 0  # Initial placeholder for the best efficiency score
    results = []
    
    # Loop over all vaccination percentages
    for percentage in vaccination_percentages:
        total_population = 0
        survived_bats = 0
        
        # Loop through the CSV files for each percentage
        for file in files:
            month = file.split('-')[1].strip()  # Assuming month is part of the filename
            file_path = os.path.join(csv_folder, file)
            
            df = read_csv(file_path)
            
            # Calculate the total population before vaccination
            total_population = df[df['pen name'] == 'Total Population']['y'].values[-1]
            
            # Calculate the number of bats to vaccinate based on percentage
            num_to_vaccinate = int(total_population * (percentage / 100))
            
            # Vaccinate the specified percentage (for now, we assume it reduces mortality)
            # Assume vaccination reduces mortality by a fixed factor (you can adjust this)
            survived_bats = total_population - (total_population * 0.1 * (percentage / 100))  # Placeholder formula
            
        # Evaluate the efficiency of this vaccination percentage (e.g., based on survival rate)
        efficiency = survived_bats / total_population  # Higher is better (more survivors per total population)
        
        results.append((percentage, efficiency))
        
        # Update the best vaccination percentage if necessary
        if efficiency > best_efficiency:
            best_efficiency = efficiency
            best_vaccination_percentage = percentage
    
    # Print the results for all vaccination percentages
    for percentage, efficiency in results:
        print(f"Vaccination Percentage: {percentage}% - Efficiency: {efficiency * 100:.2f}%")
    
    print(f"\nThe most efficient vaccination percentage is {best_vaccination_percentage}% with an efficiency of {best_efficiency * 100:.2f}%")
    
    # Optionally, you can create a plot of the results
    plt.figure(figsize=(8, 6))
    percentages = [r[0] for r in results]
    efficiencies = [r[1] for r in results]
    plt.plot(percentages, efficiencies, marker='o')
    plt.title('Vaccination Efficiency vs. Vaccination Percentage')
    plt.xlabel('Vaccination Percentage (%)')
    plt.ylabel('Efficiency (%)')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('vaccination_efficiency.png')  # Save the plot
    plt.show()

# Run the evaluation
evaluate_vaccination(csv_folder)
