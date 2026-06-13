import csv
import os
from datetime import datetime
import pandas as pd
from jobspy import scrape_jobs

print("Running production-ready automated 2-hour split-network scrape with custom column ordering...")

current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 1. Configuration
combined_search = '"devops engineer" OR "site reliability engineer"'
locations = ["Gurgaon", "Noida", "Delhi", "Jaipur", "Hyderabad", "Bengaluru", "Pune", "Mumbai"]
output_file = f"jobs/jobs:{current_timestamp}.csv"

# Webshare rotating proxy (Used for LinkedIn AND Naukri to prevent blocks)
my_rotating_proxy = ["http://muujtxkt-rotate:qwq0ievoiu53@p.webshare.io:80"]

current_run_list = []


# 2. Loop Physical Cities
for city in locations:
    print(f"\n--- Checking fresh jobs in: {city} ---")
    
    # Simplified Google search query to avoid "initial cursor not found" warnings
    simplified_google_search = f"devops site reliability engineer jobs near {city}"
    
    # Indeed & Google Jobs (Clean, unproxied)
    try:
        clean_jobs = scrape_jobs(
            site_name=["indeed", "google"],
            search_term=combined_search,                        
            google_search_term=simplified_google_search,          
            location=city,
            results_wanted=20,                     
            hours_old=2, # Set strictly to 2 hours                          
            country_indeed='India',
            enforce_annual_salary=False, 
            verbose=1                             
        )
        if not clean_jobs.empty:
            clean_jobs['is_remote_flag'] = 'Onsite/Hybrid'
            current_run_list.append(clean_jobs)
    except Exception as e:
        print(f"[{city}] Error fetching Indeed/Google: {e}")

    # Naukri (Isolated with Proxy to bypass 406 reCAPTCHA)
    try:
        naukri_jobs = scrape_jobs(
            site_name=["naukri"],
            search_term=combined_search,
            location=city,
            results_wanted=20,
            hours_old=2, # Set strictly to 2 hours
            proxies=my_rotating_proxy,
            verbose=1
        )
        if not naukri_jobs.empty:
            naukri_jobs['is_remote_flag'] = 'Onsite/Hybrid'
            current_run_list.append(naukri_jobs)
    except Exception as e:
        print(f"[{city}] Error fetching Naukri: {e}")

    # LinkedIn via Proxy
    try:
        linkedin_jobs = scrape_jobs(
            site_name=["linkedin"],
            search_term=combined_search,                                  
            location=city,
            results_wanted=20,                    
            hours_old=2, # Set strictly to 2 hours                         
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

# Indeed & Google Jobs Remote
try:
    remote_clean = scrape_jobs(
        site_name=["indeed", "google"],
        search_term=combined_search,
        google_search_term="remote devops site reliability engineer jobs India",
        location="India",                         
        is_remote=True,                           
        results_wanted=20,                        
        hours_old=2, # Set strictly to 2 hours
        country_indeed='India',
        enforce_annual_salary=False,
        verbose=1
    )
    if not remote_clean.empty:
        remote_clean['is_remote_flag'] = 'Remote'
        current_run_list.append(remote_clean)
except Exception as e:
    print(f"[Remote] Error fetching clean remote jobs: {e}")

# Naukri Remote via Proxy
try:
    remote_naukri = scrape_jobs(
        site_name=["naukri"],
        search_term=combined_search,
        location="India",
        is_remote=True,
        results_wanted=20,
        hours_old=2, # Set strictly to 2 hours
        proxies=my_rotating_proxy,
        verbose=1
    )
    if not remote_naukri.empty:
        remote_naukri['is_remote_flag'] = 'Remote'
        current_run_list.append(remote_naukri)
except Exception as e:
    print(f"[Remote] Error fetching Naukri remote jobs: {e}")

# LinkedIn Remote via Proxy
try:
    remote_linkedin = scrape_jobs(
        site_name=["linkedin"],
        search_term=combined_search,
        location="India",                         
        is_remote=True,                           
        results_wanted=20,                        
        hours_old=2, # Set strictly to 2 hours
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
    
    # 5. Dynamic Column Reordering Block
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
    print("\nNo new jobs posted in the last 2 hours across the targeted zones.")
