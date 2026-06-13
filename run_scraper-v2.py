import csv
import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import pandas as pd
from jobspy import scrape_jobs

# --- EMAIL CONFIGURATION ---
SMTP_SERVER = "://gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_email@gmail.com"      # Replace with your Gmail
SENDER_PASSWORD = "xxxx xxxx xxxx xxxx"    # Replace with your 16-digit App Password
RECEIVER_EMAIL = "destination@gmail.com"   # Replace with your alert destination email

# --- SCRAPER CONFIGURATION ---
combined_search = '"devops engineer" OR "site reliability engineer"'
locations = ["Gurgaon", "Noida", "Delhi", "Jaipur", "Hyderabad", "Bengaluru", "Pune", "Mumbai"]
output_file = "jobs_master_database.csv"
my_rotating_proxy = ["http://muujtxkt-rotate:qwq0ievoiu53@p.webshare.io:80"]
CHECK_INTERVAL_SECONDS = 300 # 5 minutes

def send_email_alert(new_jobs_df):
    """Sends an structured HTML email alert containing the newly found jobs."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🚨 ALERT: {len(new_jobs_df)} New DevOps/SRE Jobs Found!"
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL

        # Build clean HTML table for the email body
        html = f"""
        <html>
          <body>
            <h2 style="color: #2e6c80;">Real-Time Job Alert System</h2>
            <p>The automated scraper found <strong>{len(new_jobs_df)} new job listings</strong> matching your criteria within the last check window:</p>
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; font-family: Arial, sans-serif; font-size: 13px;">
              <tr style="background-color: #f2f2f2;">
                <th>Site</th>
                <th>Title</th>
                <th>Company</th>
                <th>Location</th>
                <th>Type</th>
                <th>Link</th>
              </tr>
        """
        for _, row in new_jobs_df.iterrows():
            html += f"""
              <tr>
                <td>{row.get('site', 'N/A')}</td>
                <td><strong>{row.get('title', 'N/A')}</strong></td>
                <td>{row.get('company', 'N/A')}</td>
                <td>{row.get('location', 'N/A')}</td>
                <td>{row.get('is_remote_flag', 'N/A')}</td>
                <td><a href="{row.get('job_url', '#')}" target="_blank">Apply Now</a></td>
              </tr>
            """
        html += """
            </table>
            <br>
            <p style="font-size: 11px; color: #777;">Automated split-network scraper routine engine.</p>
          </body>
        </html>
        """
        msg.attach(MIMEText(html, "html"))

        # Connect and dispatch
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print(f"📧 Success: Real-time email alert dispatched to {RECEIVER_EMAIL}")
    except Exception as e:
        print(f"❌ Failed to dispatch email alert: {e}")

# --- MAIN REAL-TIME MONITORING LOOP ---
print("Initializing production-ready real-time engine loop (Checking every 5 minutes)...")

while True:
    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n=======================================================")
    print(f"RUN STARTED AT: {current_timestamp}")
    print(f"=======================================================")
    
    current_run_list = []

    # 1. Loop Physical Cities
    for city in locations:
        print(f"--- Scanning: {city} ---")
        simplified_google_search = f"devops site reliability engineer jobs near {city}"
        
        # Indeed & Google Jobs
        try:
            clean_jobs = scrape_jobs(
                site_name=["indeed", "google"],
                search_term=combined_search,                        
                google_search_term=simplified_google_search,          
                location=city,
                results_wanted=15,                     
                hours_old=1, # Lowest possible value supported by JobSpy for hyper-fresh jobs [1]                         
                country_indeed='India',
                enforce_annual_salary=False, 
                verbose=0                             
            )
            if not clean_jobs.empty:
                clean_jobs['is_remote_flag'] = 'Onsite/Hybrid'
                current_run_list.append(clean_jobs)
        except Exception as e:
            print(f"[{city}] Error fetching Indeed/Google: {e}")

        # Naukri with Proxy
        try:
            naukri_jobs = scrape_jobs(
                site_name=["naukri"],
                search_term=combined_search,
                location=city,
                results_wanted=15,
                hours_old=1,
                proxies=my_rotating_proxy,
                verbose=0
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
                results_wanted=15,                    
                hours_old=1,                                                 
                proxies=my_rotating_proxy,            
                linkedin_fetch_description=False,     
                verbose=0                             
            )
            if not linkedin_jobs.empty:
                linkedin_jobs['is_remote_flag'] = 'Onsite/Hybrid'
                current_run_list.append(linkedin_jobs)
        except Exception as e:
            print(f"[{city}] Error fetching LinkedIn: {e}")

    # 2. Check Dedicated Remote Channels
    print("--- Scanning: Dedicated Remote India ---")
    try:
        remote_clean = scrape_jobs(
            site_name=["indeed", "google"],
            search_term=combined_search,
            google_search_term="remote devops site reliability engineer jobs India",
            location="India",                         
            is_remote=True,                           
            results_wanted=15,                        
            hours_old=1,
            country_indeed='India',
            enforce_annual_salary=False,
            verbose=0
        )
        if not remote_clean.empty:
            remote_clean['is_remote_flag'] = 'Remote'
            current_run_list.append(remote_clean)
    except Exception as e:
        print(f"[Remote] Error fetching clean remote jobs: {e}")

    try:
        remote_naukri = scrape_jobs(
            site_name=["naukri"],
            search_term=combined_search,
            location="India",
            is_remote=True,
            results_wanted=15,
            hours_old=1,
            proxies=my_rotating_proxy,
            verbose=0
        )
        if not remote_naukri.empty:
            remote_naukri['is_remote_flag'] = 'Remote'
            current_run_list.append(remote_naukri)
    except Exception as e:
        print(f"[Remote] Error fetching Naukri remote jobs: {e}")

    try:
        remote_linkedin = scrape_jobs(
            site_name=["linkedin"],
            search_term=combined_search,
            location="India",                         
            is_remote=True,                           
            results_wanted=15,                        
            hours_old=1,
            proxies=my_rotating_proxy,
            linkedin_fetch_description=False,
            verbose=0
        )
        if not remote_linkedin.empty:
            remote_linkedin['is_remote_flag'] = 'Remote'
            current_run_list.append(remote_linkedin)
    except Exception as e:
        print(f"[Remote] Error fetching proxy remote jobs: {e}")

    # 3. State Tracking and Alert Determination Block
    if current_run_list:
        new_incoming_df = pd.concat(current_run_list, ignore_index=True)
        new_incoming_df['scrape_timestamp'] = current_timestamp

        # Isolate entries to discover what is genuinely new
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            existing_df = pd.read_csv(output_file)
            
            # Find jobs where the job_url doesn't exist in our historical file
            if 'job_url' in existing_df.columns and 'job_url' in new_incoming_df.columns:
                unique_new_jobs = new_incoming_df[~new_incoming_df['job_url'].isin(existing_df['job_url'])]
            else:
                unique_new_jobs = new_incoming_df
                
            master_df = pd.concat([existing_df, new_incoming_df], ignore_index=True)
        else:
            print("First run initialized. Building baseline master file...")
            unique_new_jobs = new_incoming_df
            master_df = new_incoming_df

        # Deduplicate master file logs
        if 'job_url' in master_df.columns:
            master_df.drop_duplicates(subset=['job_url'], keep='first', inplace=True)
        
        # Sort master sheet column orientation structure
        desired_order = [
            'id', 'site', 'is_remote_flag', 'work_from_home_type', 'emails', 'job_url', 
            'title', 'company', 'location', 'date_posted', 'job_type', 'is_remote', 
            'job_level', 'company_url', 'skills', 'experience_range',
            'company_rating', 'company_reviews_count', 'vacancy_count', 
            'scrape_timestamp', 'job_url_direct', 'description'
        ]
        existing_desired = [col for col in desired_order if col in master_df.columns]
