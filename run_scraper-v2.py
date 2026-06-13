import csv
import os
import time
import subprocess
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
from dotenv import load_dotenv
from jobspy import scrape_jobs

# 1. Load Local Untracked Credentials
load_dotenv()
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

# Global Configuration (Expanded Keyword Matrix)
combined_search = (
    '"devops engineer" OR "site reliability engineer" OR "sre" OR '
    '"platform engineer" OR "infrastructure engineer" OR "cloud engineer" OR '
    '"service engineer" OR "cloud service engineer" OR "devsecops"'
)
locations = ["Gurgaon", "Noida", "Delhi", "Jaipur", "Hyderabad", "Bengaluru", "Pune", "Mumbai"]
output_file = "jobs/master_jobs.csv"
my_rotating_proxy = ["http://muujtxkt-rotate:qwq0ievoiu53@p.webshare.io:80"]

# Ensure storage directories exist
os.makedirs("jobs", exist_ok=True)

def send_email_alert(new_jobs_df):
    """Sends a real-time structured HTML summary of newly discovered jobs with a Remote Status column."""
    if not SENDER_EMAIL or not APP_PASSWORD or not RECEIVER_EMAIL:
        print("[Alert Error] Email credentials missing in your local .env file!")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🔥 Real-Time Alert: {len(new_jobs_df)} New DevOps/SRE/Service Jobs Found!"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    # Build sleek HTML Table rows dynamically including Remote Status
    table_rows = ""
    for _, row in new_jobs_df.iterrows():
        # Tag background color dynamically based on location type
        bg_color = "#e8f5e9" if row.get('is_remote_flag') == 'Remote' else "#fff3e0"
        
        table_rows += f"""
        <tr>
            <td style='padding: 8px; border: 1px solid #ddd;'><b>{row.get('title', 'N/A')}</b></td>
            <td style='padding: 8px; border: 1px solid #ddd;'>{row.get('company', 'N/A')}</td>
            <td style='padding: 8px; border: 1px solid #ddd;'>{row.get('location', 'N/A')}</td>
            <td style='padding: 8px; border: 1px solid #ddd; text-align: center;'>
                <span style='background-color: {bg_color}; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;'>
                    {row.get('is_remote_flag', 'Onsite/Hybrid')}
                </span>
            </td>
            <td style='padding: 8px; border: 1px solid #ddd;'>{row.get('site', 'N/A')}</td>
            <td style='padding: 8px; border: 1px solid #ddd;'><a href='{row.get('job_url', '#')}' target='_blank' style='color: #007bff; text-decoration: none;'>Apply Now ↗</a></td>
        </tr>
        """

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #2c3e50;">🎯 New Positions Found in the Last 2 Hours</h2>
            <p>The automated real-time crawler found fresh listings matching your profile:</p>
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                <thead>
                    <tr style="background-color: #f8f9fa; text-align: left;">
                        <th style="padding: 10px; border: 1px solid #ddd;">Title</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Company</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Location</th>
                        <th style="padding: 10px; border: 1px solid #ddd; text-align: center;">Type</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Source</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Link</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
            <br>
            <p style="font-size: 11px; color: #7f8c8d;">This is an automated production scrape run tracking your local pipeline configuration.</p>
        </body>
    </html>
    """
    
    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print(f"📧 Real-time HTML alert dispatched successfully to {RECEIVER_EMAIL}!")
    except Exception as e:
        print(f"[Email Failed] Error sending SMTP notification: {e}")

def run_scrape_cycle():
    """Runs a dedicated 2-hour scan block across networks."""
    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    current_run_list = []

    # Loop Physical Cities
    for city in locations:
        print(f"\n--- Checking fresh jobs in: {city} ---")
        simplified_google_search = f"devops sre platform cloud infrastructure engineer jobs near {city}"
        
        try:
            clean_jobs = scrape_jobs(
                site_name=["indeed", "google"], search_term=combined_search,                        
                google_search_term=simplified_google_search, location=city,
                results_wanted=20, hours_old=2, country_indeed='India',
                enforce_annual_salary=False, verbose=1                             
            )
            if not clean_jobs.empty:
                clean_jobs['is_remote_flag'] = 'Onsite/Hybrid'
                current_run_list.append(clean_jobs)
        except Exception as e:
            print(f"[{city}] Error fetching Indeed/Google: {e}")

        try:
            naukri_jobs = scrape_jobs(
                site_name=["naukri"], search_term=combined_search, location=city,
                results_wanted=20, hours_old=2, proxies=my_rotating_proxy, verbose=1
            )
            if not naukri_jobs.empty:
                naukri_jobs['is_remote_flag'] = 'Onsite/Hybrid'
                current_run_list.append(naukri_jobs)
        except Exception as e:
            print(f"[{city}] Error fetching Naukri: {e}")

        try:
            linkedin_jobs = scrape_jobs(
                site_name=["linkedin"], search_term=combined_search, location=city,
                results_wanted=20, hours_old=2, proxies=my_rotating_proxy,
                linkedin_fetch_description=False, verbose=1                             
            )
            if not linkedin_jobs.empty:
                linkedin_jobs['is_remote_flag'] = 'Onsite/Hybrid'
                current_run_list.append(linkedin_jobs)
        except Exception as e:
            print(f"[{city}] Error fetching LinkedIn: {e}")

    # Check Remote Channels
    print("\n--- Checking fresh Remote jobs ---")
    try:
        remote_clean = scrape_jobs(
            site_name=["indeed", "google"], search_term=combined_search,
            google_search_term="remote devops site reliability engineer platform jobs India",
            location="India", is_remote=True, results_wanted=20, hours_old=2,
            country_indeed='India', enforce_annual_salary=False, verbose=1
        )
        if not remote_clean.empty:
            remote_clean['is_remote_flag'] = 'Remote'
            current_run_list.append(remote_clean)
    except Exception as e:
        print(f"[Remote] Error fetching clean remote jobs: {e}")

    try:
        remote_naukri = scrape_jobs(
            site_name=["naukri"], search_term=combined_search, location="India",
            is_remote=True, results_wanted=20, hours_old=2, proxies=my_rotating_proxy, verbose=1
        )
        if not remote_naukri.empty:
            remote_naukri['is_remote_flag'] = 'Remote'
            current_run_list.append(remote_naukri)
    except Exception as e:
        print(f"[Remote] Error fetching Naukri remote jobs: {e}")

    try:
        remote_linkedin = scrape_jobs(
            site_name=["linkedin"], search_term=combined_search, location="India",
            is_remote=True, results_wanted=20, hours_old=2, proxies=my_rotating_proxy,
            linkedin_fetch_description=False, verbose=1
        )
        if not remote_linkedin.empty:
            remote_linkedin['is_remote_flag'] = 'Remote'
            current_run_list.append(remote_linkedin)
    except Exception as e:
        print(f"[Remote] Error fetching proxy remote jobs: {e}")

    # Process and evaluate new data
    if current_run_list:
        new_incoming_df = pd.concat(current_run_list, ignore_index=True)
        new_incoming_df['scrape_timestamp'] = current_timestamp
        
        # --- 5-Line Data-Cleaning Script for Non-Software Hardware Positions ---
        if 'description' in new_incoming_df.columns:
            ban_words = 'hvac|desktop repair|printer|mechanical|cabling|hardware maintenance|installation technician'
            new_incoming_df['description'] = new_incoming_df['description'].fillna('')
            new_incoming_df = new_incoming_df[~new_incoming_df['description'].str.contains(ban_words, case=False, na=False)]

        # Unique clean within the current run array
        if 'job_url' in new_incoming_df.columns:
            new_incoming_df.drop_duplicates(subset=['job_url'], keep='first', inplace=True)

        new_unique_jobs = pd.DataFrame()

        # Isolate true novel alerts vs master file logs
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            existing_df = pd.read_csv(output_file)
            if 'job_url' in new_incoming_df.columns and 'job_url' in existing_df.columns:
                new_unique_jobs = new_incoming_df[~new_incoming_df['job_url'].isin(existing_df['job_url'])]
            master_df = pd.concat([existing_df, new_incoming_df], ignore_index=True)
        else:
            print("\nInitializing fresh master_jobs.csv database...")
            new_unique_jobs = new_incoming_df
            master_df = new_incoming_df

        # Final Deduplication & Reordering
        if 'job_url' in master_df.columns:
            master_df.drop_duplicates(subset=['job_url'], keep='first', inplace=True)
            
        desired_order = [
            'id', 'site', 'is_remote_flag', 'work_from_home_type', 'emails', 'job_url', 
            'title', 'company', 'location', 'date_posted', 'job_type', 'is_remote', 
            'job_level', 'company_url', 'skills', 'experience_range',
            'company_rating', 'company_reviews_count', 'vacancy_count', 
            'scrape_timestamp', 'job_url_direct', 'description'
        ]
        existing_desired = [col for col in desired_order if col in master_df.columns]
        remaining_columns = [col for col in master_df.columns if col not in desired_order]
        master_df = master_df[existing_desired + remaining_columns]
        
        # Save to File System
        master_df.to_csv(output_file, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
        print(f"✅ Run complete. Master sheet holds {len(master_df)} unique records.")

        # Fire Email Alert if novel listings exist
        if not new_unique_jobs.empty:
            print(f"🔥 Found {len(new_unique_jobs)} completely new job additions!")
            send_email_alert(new_unique_jobs)
            
            # Git Direct-to-Main Push Automation
            try:
                print("Syncing data updates to Git origin branch...")
                subprocess.run(["git", "add", output_file], check=True)
                subprocess.run(["git", "commit", "-m", f"auto-update: master listings synced (+{len(new_unique_jobs)} jobs)"], check=True)
                
                # Pull using rebase right before pushing to guarantee conflict-free writes
                subprocess.run(["git", "pull", "origin", "main", "--rebase"], check=True)
                subprocess.run(["git", "push", "origin", "main"], check=True)
                print("Git remote push successful!")
            except Exception as git_err:
                print(f"[Git Skip] Automated indexing error: {git_err}")
        else:
            print("No completely unindexed jobs discovered this loop cycle.")
    else:
        print("\nNo jobs matching standard arrays returned this pass.")

# --- 2-Hour Daemon Loop Entry Point ---
if __name__ == "__main__":
    print("🚀 Initializing Real-Time Persistent Daemon Engine...")
    while True:
        print(f"\n=================== STARTING RUN: {datetime.now()} ===================")
        run_scrape_cycle()
        print("\n=================== CYCLE COMPLETE ===================")
        print("🕒 Sleeping for exactly 2 hours before the next sync loop...")
        # time.sleep(7200) # 7200 seconds = 2 Hours
        time.sleep(1800) # 1800 seconds = 30 mins
