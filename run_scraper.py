import csv
import os
from datetime import datetime
import pandas as pd
from jobspy import scrape_jobs

print("Running production-ready automated 4-hour split-network scrape with new custom column ordering...")

# 1. Configuration
combined_search = '"devops engineer" OR "site reliability engineer"'
locations = ["Gurgaon", "Noida", "Delhi", "Jaipur", "Hyderabad", "Bengaluru", "Pune", "Mumbai"]
output_file = "jobs.csv"

# Webshare rotating proxy (Used ONLY for LinkedIn)
my_rotating_proxy = ["http://muujtxkt-rotate:qwq0ievoiu53@p.webshare.io:80"]

current_run_list = []
current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 2. Loop Physical Cities
for city in locations:
    print(f"\n--- Checking fresh jobs in: {city} ---")
    combined_google_search = f'("devops engineer" OR "site reliability engineer") jobs near {city} past 4 hours'
    
    # Indeed & Google Jobs
    try:
        clean_jobs = scrape_jobs(
            site_name=["indeed", "google"],
            search_term=combined_search,                        
            google_search_term=combined_google_search,          
            location=city,
            results_wanted=20,                     
            hours_old=1,                          
            country_indeed='India',
            enforce_annual_salary=True,
            verbose=1                             
        )
        if not clean_jobs.empty:
            clean_jobs['is_remote_flag'] = 'Onsite/Hybrid'
            current_run_list.append(clean_jobs)
    except Exception as e:
        print(f"[{city}] Error fetching Indeed/Google: {e}")

    # LinkedIn via Proxy (10 results wanted)
    try:
        linkedin_jobs = scrape_jobs(
            site_name=["linkedin"],
            search_term=combined_search,                                  
            location=city,
            results_wanted=20,                    
            hours_old=1,                          
            proxies=my_rotating_proxy,            
            linkedin_fetch_description=False,     
            verbose=1                             
        )
        if not linkedin_jobs.empty:
            linkedin_jobs['is_remote_flag'] = 'Onsite/Hybrid'
            current_run_list.append(linkedin_jobs)
    except Exception as e:
        print(f"[{city}] Error fetching LinkedIn: {e}")

# 3. Check Dedicated Remote Channels
print("\n--- Checking fresh Remote jobs ---")
try:
    remote_clean = scrape_jobs(
        site_name=["indeed", "google"],
        search_term=combined_search,
        google_search_term='("devops engineer" OR "site reliability engineer") remote jobs past 4 hours',
        location="India",                         
        is_remote=True,                           
        results_wanted=20,                        
        hours_old=1,
        country_indeed='India',
        enforce_annual_salary=True,
        verbose=1
    )
    if not remote_clean.empty:
        remote_clean['is_remote_flag'] = 'Remote'
        current_run_list.append(remote_clean)
except Exception as e:
    print(f"[Remote] Error fetching clean remote jobs: {e}")

# LinkedIn Remote via Proxy (20 results wanted)
try:
    remote_linkedin = scrape_jobs(
        site_name=["linkedin"],
        search_term=combined_search,
        location="India",                         
        is_remote=True,                           
        results_wanted=20,                        
        hours_old=1,
        proxies=my_rotating_proxy,
        linkedin_fetch_description=False,
        verbose=1
    )
    if not remote_linkedin.empty:
        remote_linkedin['is_remote_flag'] = 'Remote'
        current_run_list.append(remote_linkedin)
except Exception as e:
    print(f"[Remote] Error fetching proxy remote jobs: {e}")

# 4. Smart Merge & Append Processing
if current_run_list:
    new_incoming_df = pd.concat(current_run_list, ignore_index=True)
    
    # Inject the runtime timestamp to every row
    new_incoming_df['scrape_timestamp'] = current_timestamp

    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        print("\nMerging with existing jobs.csv...")
        existing_df = pd.read_csv(output_file)
        master_df = pd.concat([existing_df, new_incoming_df], ignore_index=True)
    else:
        print("\nCreating fresh jobs.csv...")
        master_df = new_incoming_df

    # Deduplicate entries based on their unique target job link
    if 'job_url' in master_df.columns:
        master_df.drop_duplicates(subset=['job_url'], keep='first', inplace=True)
    
    # 5. Dynamic Column Reordering Block (Updated Layout Setup)
    desired_order = [
        'id', 'site', 'is_remote_flag', 'work_from_home_type', 'emails', 'job_url', 
        'title', 'company', 'location', 'date_posted', 'job_type', 'is_remote', 
        'job_level', 'company_url', 'skills', 'experience_range',
        'company_rating', 'company_reviews_count', 'vacancy_count', 
        'scrape_timestamp', 'job_url_direct', 'description'
    ]
    
    existing_desired = [col for col in desired_order if col in master_df.columns]
    remaining_columns = [col for col in master_df.columns if col not in desired_order]
    
    final_column_layout = existing_desired + remaining_columns
    master_df = master_df[final_column_layout]
        
    master_df.to_csv(output_file, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
    print(f"Scrape successful! Master dataset size: {len(master_df)} unique ordered jobs.")
else:
    print("\nNo new jobs posted in the last 4 hours across the targeted zones.")
