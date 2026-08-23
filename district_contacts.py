# ============================================================
# ATHENA — DISTRICT ESCALATION CONTACTS (KG SEED DATA)
# ============================================================

"""
District -> Sakhi/One Stop Centre escalation contact directory, used
by kg.py to resolve an escalation_contact for a reported district.

Provenance: Telangana entries (all 33 districts) are transcribed
directly from data/sources/Sakhi-OSC Contact list Updated _list.pdf
(Telangana WCD Department's published contact list). The handful of
non-Telangana entries are transcribed from
data/sources/Helplines&CounsellingservicesforWomenandGirlsincrisisinIndia.pdf
(a consolidated national directory). Nothing here is invented --
every phone/email is what those source documents actually say --
but this is NOT full national coverage. That directory PDF covers
every state/UT across 30 pages; the text extraction from it is messy
enough (columns interleave inconsistently across states) that
auto-parsing the rest reliably wasn't safe to do unsupervised for a
safety-critical contact list -- a wrong phone number here is worse
than a missing one. Extending this to more states is a data-entry
task against that PDF (ideally with a second person spot-checking
each row against the source), not a technical blocker.

Keyed by district name lowercased, no state qualifier -- a known
simplification. District names aren't guaranteed unique across
India (e.g. more than one state has a "Bijapur"); with today's data
there's no actual collision, but a composite (state, district) key
would be the correct fix before this scales much further.
"""

TELANGANA_DISTRICTS = {

    "adilabad": {
        "district": "Adilabad", "state": "Telangana",
        "address": "Survey No. 348 & 351, Besides Officers Club, Old Housing Board Colony, Collector Chowk, 504001",
        "phone": "08732-223272", "email": "sakhiadb.mitra@gmail.com",
        "contact_person": "Saraswathi", "contact_person_phone": "9542433320",
    },
    "bhadradri kothagudem": {
        "district": "Bhadradri Kothagudem", "state": "Telangana",
        "address": "SCCl. Q No.C1, C2, Babu Camp, Opp Chuchupalli Police Station, 507101",
        "phone": "08744-248222", "email": "sakhi.bktdm@gmail.com",
        "contact_person": "J. Subha Sree", "contact_person_phone": "9985875566",
    },
    "hyderabad": {
        "district": "Hyderabad", "state": "Telangana",
        "address": "H.No.9-1-127, 1st & 2nd floor, Madava Nursing Home Line, S.D Road, Secunderabad-500003",
        "phone": "040-27714881", "email": "sakhihyderabad@divyadisha.org",
        "contact_person": "G. Anitha Reddy", "contact_person_phone": "8885028615",
    },
    "jagtial": {
        "district": "Jagtial", "state": "Telangana",
        "address": "H.No. 1-5-130, Bypass Road, Beside Bachpan School, Govindhpally Road, Jagtial-505327",
        "phone": "08724-295235", "email": "sakhijgl2019@gmail.com",
        "contact_person": "V. Maneela", "contact_person_phone": "9000575774",
    },
    "jangaon": {
        "district": "Jangaon", "state": "Telangana",
        "address": "Devadula Camp Office, Wadlakonda Road, Jangaon, 506167",
        "phone": "9347186918", "email": "sakhijangaon@gmail.com",
        "contact_person": "Renuka", "contact_person_phone": "9573049364",
    },
    "jayashankar bhupalapally": {
        "district": "Jayashankar Bhupalapally", "state": "Telangana",
        "address": "H.No. 8-143/3, LB Nagar, Opp. RTC Bus Stand, Jayashankar Bhupalapally",
        "phone": "8500009433", "email": "sakhicentrebhpl@gmail.com",
        "contact_person": "Gayathri", "contact_person_phone": "9989407018",
    },
    "jogulamba gadwal": {
        "district": "Jogulamba Gadwal", "state": "Telangana",
        "address": "H.No. 1-3-75/5/6, Sunkaalamma Mettu, Jogulamba Gadwal",
        "phone": "08456-272250", "email": "sakhigadwal@gmail.com",
        "contact_person": "K. Harshitha", "contact_person_phone": "7093486331",
    },
    "kamareddy": {
        "district": "Kamareddy", "state": "Telangana",
        "address": "H.No: 1-5-442, Ramareddy Road, Opp: Vaishnavi Hospital, Kamareddy-503111",
        "phone": "08468-223232", "email": "sakhikamareddy2019@gmail.com",
        "contact_person": "Pedda Sayavva", "contact_person_phone": "7893181512",
    },
    "karimnagar": {
        "district": "Karimnagar", "state": "Telangana",
        "address": "H.No: 2-3-189, Raghavendra Mess Road, Near Old Post Office, Mukarampura, Karimnagar",
        "phone": "0878-2244644", "email": "sakhicentrekarimnagar@gmail.com",
        "contact_person": "D. Laxmi", "contact_person_phone": "9642333464",
    },
    "khammam": {
        "district": "Khammam", "state": "Telangana",
        "address": "Govt Main Hospital Premises, Khammam-507002",
        "phone": "08742-298234", "email": "sakhikhammam@gmail.com",
        "contact_person": "Sravani", "contact_person_phone": "7893979292",
    },
    "kumuram bheem asifabad": {
        "district": "Kumuram Bheem Asifabad", "state": "Telangana",
        "address": "Beside Old RTO Office, Jankapur, KB Asifabad-504293",
        "phone": "8500240181", "email": "sakhiasifabad@gmail.com",
        "contact_person": "Soujanya", "contact_person_phone": "7674910709",
    },
    "mahabubabad": {
        "district": "Mahabubabad", "state": "Telangana",
        "address": "Cabin Road, 3rd Line, Mahabubabad-506101",
        "phone": "9397677770", "email": "sakhioscmhbd@gmail.com",
        "contact_person": "N. Sravani", "contact_person_phone": "9100792105",
    },
    "mahabubnagar": {
        "district": "Mahabubnagar", "state": "Telangana",
        "address": "Beside Central Medicine Stores, Govt Hospital, Mahabubnagar-509001",
        "phone": "08542-223181", "email": "sakhi.mbnr17@gmail.com",
        "contact_person": "K. Manjula", "contact_person_phone": "6301615611",
    },
    "mancherial": {
        "district": "Mancherial", "state": "Telangana",
        "address": "Near Government Degree College, College Road, Mancherial-504208",
        "phone": "08736-250181", "email": "sakhimncl2019@gmail.com",
        "contact_person": "Srilatha", "contact_person_phone": "7382323666",
    },
    "medak": {
        "district": "Medak", "state": "Telangana",
        "address": "H.No.1-12-24/A/163, Road No.1, Opp: MGM Park, Indirapuri Colony, Medak-502101",
        "phone": "08452-295181", "email": "sakhioscmedak@gmail.com",
        "contact_person": None, "contact_person_phone": "9346146580",
    },
    "medchal malkajigiri": {
        "district": "Medchal Malkajgiri", "state": "Telangana",
        "address": "Sakhi OSC Balika Sadan, Near Indira Gandhi Statue, Beside Hanuman Temple, Old Alwal, 500010",
        "phone": "9121166390", "email": "sakhimedchal@gmail.com",
        "contact_person": "G. Anita Reddy", "contact_person_phone": "7013420750",
    },
    "mulugu": {
        "district": "Mulugu", "state": "Telangana",
        "address": "Near Gattamma Temple, Opp: Govt Guest House, Govt Degree College Road, Mulugu-506343",
        "phone": "7013745008", "email": "sakhimulugu@gmail.com",
        "contact_person": "G. Kalpana (in-charge)", "contact_person_phone": "8186892507",
    },
    "nagarkurnool": {
        "district": "Nagarkurnool", "state": "Telangana",
        "address": "Sakhi OSC, Opposite New Collectorate, Beside Vaibhav Garden, Deshitkyal, Nagarkurnool-509209",
        "phone": "9951940181", "email": "sakhingkl2019@gmail.com",
        "contact_person": "P. Sunitha", "contact_person_phone": "9494631248",
    },
    "nalgonda": {
        "district": "Nalgonda", "state": "Telangana",
        "address": "R & B Building, Prakhasham Bazar, Old AJC Building, Nalgonda-508001",
        "phone": "08682-234088", "email": "sakhi.nlg@gmail.com",
        "contact_person": "Mandakini", "contact_person_phone": "8985191120",
    },
    "narayanpet": {
        "district": "Narayanpet", "state": "Telangana",
        "address": "Srinivasa Colony, Near Amrutha Sai Temple, Narayanpet-509210",
        "phone": "08506-295181", "email": "sakhi.21nprt@gmail.com",
        "contact_person": "Niharika Reddy", "contact_person_phone": "8096718168",
    },
    "nirmal": {
        "district": "Nirmal", "state": "Telangana",
        "address": "Nagar, Nirmal-504106",
        "phone": "8500540181", "email": "sakhicenternirmal@gmail.com",
        "contact_person": "P. Mamatha", "contact_person_phone": "9959271856",
    },
    "nizamabad": {
        "district": "Nizamabad", "state": "Telangana",
        "address": "Sakhi/One Stop Centre, Government General Hospital Premises, Nizamabad-503001",
        "phone": "08462-225181", "email": "sakhiosc.nzb@gmail.com",
        "contact_person": "Y. Lavanya (I/C Centre admin)", "contact_person_phone": "9948630367",
    },
    "peddapalli": {
        "district": "Peddapalli", "state": "Telangana",
        "address": "505174",
        "phone": "9441792181", "email": "sakhipeddapally@gmail.com",
        "contact_person": "D. Swapna", "contact_person_phone": "8008841002",
    },
    "rajanna sircilla": {
        "district": "Rajanna Sircilla", "state": "Telangana",
        "address": "Sircilla, 505301",
        "phone": "08723-295181", "email": "sakhisiricilla@gmail.com",
        "contact_person": "B. Roja", "contact_person_phone": "8977772235",
    },
    "rangareddy": {
        "district": "Rangareddy", "state": "Telangana",
        "address": "Plot No. 177, Road No.6, Vanasthali Hills, Vanasthalipuram, Rangareddy-500070",
        "phone": "040-29800821", "email": "sakhirrdist@gmail.com",
        "contact_person": "P. Mariya Susheela", "contact_person_phone": "9440413076",
    },
    "sangareddy": {
        "district": "Sangareddy", "state": "Telangana",
        "address": "Survey No.203, Maila Pranganam, Bypass Road, Sangareddy-502001",
        "phone": "9490129740", "email": "sakhi.sangareddy@gmail.com",
        "contact_person": None, "contact_person_phone": None,
    },
    "siddipet": {
        "district": "Siddipet", "state": "Telangana",
        "address": "Old MCH Building 1st Floor, Near Buruju, Siddipet",
        "phone": "8886108181", "email": "sakhisiddipet181@gmail.com",
        "contact_person": "P. Prathima", "contact_person_phone": "7702708905",
    },
    "suryapet": {
        "district": "Suryapet", "state": "Telangana",
        "address": "Opp. Sumangali Function Hall, Near Community Hall, Jammigadda, Suryapet-508213",
        "phone": "9490265525", "email": "sakhisuryapet181@gmail.com",
        "contact_person": "Ch. Hemaltha", "contact_person_phone": "9948862274",
    },
    "vikarabad": {
        "district": "Vikarabad", "state": "Telangana",
        "address": "H.No.4-1-208, New Gandhi Gunj, Bank of Baroda Lane, Vikarabad",
        "phone": "08416-295181", "email": "sakhivikarabad@gmail.com",
        "contact_person": None, "contact_person_phone": "8331050181",
    },
    "wanaparthy": {
        "district": "Wanaparthy", "state": "Telangana",
        "address": "H.No.39-113, Bandar Nagar, Wanaparthy-509103",
        "phone": "08545-233441", "email": "sakhioscwnpdist@gmail.com",
        "contact_person": "Sk. Shireen", "contact_person_phone": "9154395164",
    },
    "warangal rural": {
        "district": "Warangal (Rural)", "state": "Telangana",
        "address": "Warangal Rural",
        "phone": "0870-2935014", "email": "sakhiwarangalrural@gmail.com",
        "contact_person": "V. Sreelatha", "contact_person_phone": "8106326320",
    },
    "hanumakonda": {
        "district": "Hanumakonda", "state": "Telangana",
        "address": "506001",
        "phone": "0870-2452112", "email": "syosakhi@gmail.com",
        "contact_person": "S. Hymavathi", "contact_person_phone": "9866825998",
    },
    "yadadri bhuvanagiri": {
        "district": "Yadadri Bhuvanagiri", "state": "Telangana",
        "address": "Colony, Bhongir, Yadadri Bhongir-508116",
        "phone": "08685-295181", "email": "sakhiyadadri@gmail.com",
        "contact_person": "CH. Lavanya Devi", "contact_person_phone": "9550184877",
    },
}

# Representative sample from other states, transcribed from the
# national directory PDF -- NOT complete coverage for these states,
# just proof this isn't hardcoded to Telangana only. See module
# docstring.
OTHER_STATE_DISTRICTS = {

    "krishna": {
        "district": "Krishna", "state": "Andhra Pradesh",
        "address": "One Stop Centre, Old Government Hospital, Opp: Tummalapalli Kalakshetram, Vijayawada City, Krishna District",
        "phone": "9398914772", "email": "apsrcw@gmail.com",
        "contact_person": None, "contact_person_phone": None,
    },
    "chittoor": {
        "district": "Chittoor", "state": "Andhra Pradesh",
        "address": "One Stop Centre, RIMS-General Hospital, Municipal Maternity Ward, Chittoor City",
        "phone": "9959776697", "email": "apsrcw@gmail.com",
        "contact_person": None, "contact_person_phone": None,
    },
    "patna": {
        "district": "Patna", "state": "Bihar",
        "address": "One Stop Centre, Chajjubagh Executive Bungalow, Patna District",
        "phone": "8210713745", "email": "support@wcdbihar.org.in",
        "contact_person": None, "contact_person_phone": None,
    },
}

DISTRICT_CONTACTS = {**TELANGANA_DISTRICTS, **OTHER_STATE_DISTRICTS}
