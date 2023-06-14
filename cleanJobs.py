import json
import csv

# cleaning the jobs for use in online job searches
with open('jobs.json', 'r') as f:
    occs = json.load(f)
f.close()

# select /Legends articles for cleaning, remove duplicates
occs_filt = list(filter(lambda x: "/Legends" in x, occs.keys()))
for i in range(0, len(occs_filt)):
    ind = occs_filt[i].index("/Legends")
    occs_filt[i] = occs_filt[i][:ind]

other = []
# jobs that ONLY have legends pages, want those included in the searches
for job in occs_filt:
    if not occs.get(job):
        other.append(job)

# now for the rest
occs_filt = list(filter(lambda x: "/Legends" not in x, occs.keys()))
occs_filt.extend(other)

# cut parenthesized text from titles
paren = list(filter(lambda x: "(" in x, occs_filt))
for i in range(0, len(paren)):
    ind = paren[i].index("(")
    paren[i] = paren[i][:ind]

# add them back and remove duplicates
occs_filt = list(filter(lambda x: "(" not in x, occs_filt))
occs_filt.extend(paren)
occs_filt = list(set(occs_filt))

with open('job_titles.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(occs_filt)
f.close()
