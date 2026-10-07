import pandas as pd
import matplotlib.pyplot as plt
import os

csv_folder = r'C:\Users\dvtur\OneDrive\Desktop\netlogo\csv_months\months'

def read_csv(file_path):
    try:
        df = pd.read_csv(file_path, skiprows=5, on_bad_lines='skip')
        print(f"Columns in {file_path}: {df.columns.tolist()}")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None
    return df

def analyze_best_month(csv_folder):
    files = [f for f in os.listdir(csv_folder) if f.endswith('.csv')]
    best_month = None
    best_vaccine_effect = 0
    
    combined_data = []
    
    for file in files:
        month = file.split('_')[0].strip()
        
        file_path = os.path.join(csv_folder, file)
        
        df = read_csv(file_path)
        if df is None:
            continue
        
        if 'vaccination_month' in df.columns:
            df['vaccination-rate'] = pd.to_numeric(df['vaccination-rate'], errors='coerce')
            total_population = df['vaccination-rate'].values[-1]
        else:
            print(f"Column 'vaccination_month' missing in {file_path}")
            continue
        
        combined_data.append(df)
        
        vaccine_effect = total_population
        
        if vaccine_effect > best_vaccine_effect:
            best_vaccine_effect = vaccine_effect
            best_month = month
    
    plt.figure(figsize=(10, 6))
    
    all_x_vals = []
    all_y_vals = []
    
    for df in combined_data:
        df['vaccination_month'] = df['vaccination_month'].astype(str)  # Convert month to string
        all_x_vals.extend(df['vaccination_month'])
        all_y_vals.extend(df['vaccination-rate'])
        plt.plot(df['vaccination_month'], df['vaccination-rate'], label=month)
    
    plt.xlim(min(all_x_vals), max(all_x_vals))
    plt.ylim(min(all_y_vals), max(all_y_vals))
    
    plt.title('Bat Population over Time for Different Months')
    plt.xlabel('Time (Months)')
    plt.ylabel('Population (Vaccination Rate)')
    plt.legend(loc='upper left')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('combined_graph.png')
    plt.show()
    
    return best_month

best_month = analyze_best_month(csv_folder)
print(f"The best month to apply the vaccine is: {best_month}")
