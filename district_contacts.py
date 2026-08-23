# ============================================================
# ATHENA — DISTRICT ESCALATION CONTACTS (KG SEED DATA)
# ============================================================

"""
District -> Sakhi/One Stop Centre escalation contact directory, used
by kg.py to resolve an escalation_contact for a reported district.

Provenance, per entry (see each entry's "verification" field):
- "manual": individually transcribed and checked against the source
  PDF -- Telangana's 33 districts (data/sources/Sakhi-OSC Contact
  list Updated _list.pdf) plus a handful of entries from the national
  directory PDF that predate the parsed import below.
- "parsed": machine-extracted from
  data/sources/Helplines&CounsellingservicesforWomenandGirlsincrisisinIndia.pdf
  (30-page national directory, 33 states/UTs) via pdfplumber's
  layout-aware table extraction (2026-08-23) -- NOT individually
  hand-checked row-by-row against the source the way "manual" entries
  are. Nothing here is invented -- every field traces to what
  pdfplumber actually extracted from that table -- but "parsed" means
  a lower confidence tier than "manual", not the same guarantee.
  Consumers that care about this distinction should check the
  "verification" field rather than assuming uniform confidence.

  Extraction notes, for anyone re-running or extending this:
  - An earlier attempt (2026-08-22) used pypdf's plain text-stream
    extraction, which interleaved columns badly enough across state
    boundaries that auto-parsing was judged unsafe and deferred.
    pdfplumber's extract_table() (which uses the PDF's actual table/
    ruling structure, not just linear text flow) produces genuinely
    clean per-cell data -- this is what made the 2026-08-23 import
    possible, not a change in risk tolerance.
  - The source PDF also lists a second table per state ("Protection
    Officers for Domestic Violence") interleaved with the Sakhi-OSC
    listing -- excluded entirely, identified by those rows having no
    numeric S.No of their own.
  - 6 district names collide across different states in this dataset
    (Bilaspur: Chhattisgarh/Himachal Pradesh; Raigarh: Chhattisgarh/
    Maharashtra; Aurangabad: Bihar/Maharashtra; Balrampur:
    Chhattisgarh/Uttar Pradesh; Pratapgarh: Rajasthan/Uttar Pradesh;
    Hamirpur: Himachal Pradesh/Uttar Pradesh). The `district` request
    field (see app.py/kg.py) is a bare name with no state qualifier,
    so these can't be disambiguated today -- deliberately EXCLUDED
    from this file rather than guessing and silently routing a
    reporter to the wrong state's contact. A composite (state,
    district) key would be the real fix if this needs to scale
    further; not attempted here since it would mean changing the
    `district` request field's contract.
  - A handful of district names had an obvious word-wrap artifact in
    the source extraction (e.g. "Thiruvanantha puram" instead of
    "Thiruvananthapuram") -- corrected where the intended word was
    unambiguous; not a systematic re-verification of every name's
    spelling.
  - 33 states/UTs are represented; a few small states/UTs (e.g. Goa,
    Sikkim, Manipur) only have 1-2 districts because that's genuinely
    what the source PDF lists for them, not a parsing gap -- not every
    district in India has a dedicated Sakhi-OSC yet.

Keyed by district name lowercased, no state qualifier (see the
cross-state-collision note above for why that's an intentional gap,
not an oversight).
"""

# All 33 Telangana districts, hand-transcribed and verified against
# data/sources/Sakhi-OSC Contact list Updated _list.pdf.
TELANGANA_DISTRICTS = {
    'adilabad': {
        "district": 'Adilabad', "state": 'Telangana',
        "address": 'Survey No. 348 & 351, Besides Officers Club, Old Housing Board Colony, Collector Chowk, 504001',
        "phone": '08732-223272', "email": 'sakhiadb.mitra@gmail.com',
        "contact_person": 'Saraswathi', "contact_person_phone": '9542433320',
        "verification": 'manual',
    },

    'bhadradri kothagudem': {
        "district": 'Bhadradri Kothagudem', "state": 'Telangana',
        "address": 'SCCl. Q No.C1, C2, Babu Camp, Opp Chuchupalli Police Station, 507101',
        "phone": '08744-248222', "email": 'sakhi.bktdm@gmail.com',
        "contact_person": 'J. Subha Sree', "contact_person_phone": '9985875566',
        "verification": 'manual',
    },

    'hanumakonda': {
        "district": 'Hanumakonda', "state": 'Telangana',
        "address": '506001',
        "phone": '0870-2452112', "email": 'syosakhi@gmail.com',
        "contact_person": 'S. Hymavathi', "contact_person_phone": '9866825998',
        "verification": 'manual',
    },

    'hyderabad': {
        "district": 'Hyderabad', "state": 'Telangana',
        "address": 'H.No.9-1-127, 1st & 2nd floor, Madava Nursing Home Line, S.D Road, Secunderabad-500003',
        "phone": '040-27714881', "email": 'sakhihyderabad@divyadisha.org',
        "contact_person": 'G. Anitha Reddy', "contact_person_phone": '8885028615',
        "verification": 'manual',
    },

    'jagtial': {
        "district": 'Jagtial', "state": 'Telangana',
        "address": 'H.No. 1-5-130, Bypass Road, Beside Bachpan School, Govindhpally Road, Jagtial-505327',
        "phone": '08724-295235', "email": 'sakhijgl2019@gmail.com',
        "contact_person": 'V. Maneela', "contact_person_phone": '9000575774',
        "verification": 'manual',
    },

    'jangaon': {
        "district": 'Jangaon', "state": 'Telangana',
        "address": 'Devadula Camp Office, Wadlakonda Road, Jangaon, 506167',
        "phone": '9347186918', "email": 'sakhijangaon@gmail.com',
        "contact_person": 'Renuka', "contact_person_phone": '9573049364',
        "verification": 'manual',
    },

    'jayashankar bhupalapally': {
        "district": 'Jayashankar Bhupalapally', "state": 'Telangana',
        "address": 'H.No. 8-143/3, LB Nagar, Opp. RTC Bus Stand, Jayashankar Bhupalapally',
        "phone": '8500009433', "email": 'sakhicentrebhpl@gmail.com',
        "contact_person": 'Gayathri', "contact_person_phone": '9989407018',
        "verification": 'manual',
    },

    'jogulamba gadwal': {
        "district": 'Jogulamba Gadwal', "state": 'Telangana',
        "address": 'H.No. 1-3-75/5/6, Sunkaalamma Mettu, Jogulamba Gadwal',
        "phone": '08456-272250', "email": 'sakhigadwal@gmail.com',
        "contact_person": 'K. Harshitha', "contact_person_phone": '7093486331',
        "verification": 'manual',
    },

    'kamareddy': {
        "district": 'Kamareddy', "state": 'Telangana',
        "address": 'H.No: 1-5-442, Ramareddy Road, Opp: Vaishnavi Hospital, Kamareddy-503111',
        "phone": '08468-223232', "email": 'sakhikamareddy2019@gmail.com',
        "contact_person": 'Pedda Sayavva', "contact_person_phone": '7893181512',
        "verification": 'manual',
    },

    'karimnagar': {
        "district": 'Karimnagar', "state": 'Telangana',
        "address": 'H.No: 2-3-189, Raghavendra Mess Road, Near Old Post Office, Mukarampura, Karimnagar',
        "phone": '0878-2244644', "email": 'sakhicentrekarimnagar@gmail.com',
        "contact_person": 'D. Laxmi', "contact_person_phone": '9642333464',
        "verification": 'manual',
    },

    'khammam': {
        "district": 'Khammam', "state": 'Telangana',
        "address": 'Govt Main Hospital Premises, Khammam-507002',
        "phone": '08742-298234', "email": 'sakhikhammam@gmail.com',
        "contact_person": 'Sravani', "contact_person_phone": '7893979292',
        "verification": 'manual',
    },

    'kumuram bheem asifabad': {
        "district": 'Kumuram Bheem Asifabad', "state": 'Telangana',
        "address": 'Beside Old RTO Office, Jankapur, KB Asifabad-504293',
        "phone": '8500240181', "email": 'sakhiasifabad@gmail.com',
        "contact_person": 'Soujanya', "contact_person_phone": '7674910709',
        "verification": 'manual',
    },

    'mahabubabad': {
        "district": 'Mahabubabad', "state": 'Telangana',
        "address": 'Cabin Road, 3rd Line, Mahabubabad-506101',
        "phone": '9397677770', "email": 'sakhioscmhbd@gmail.com',
        "contact_person": 'N. Sravani', "contact_person_phone": '9100792105',
        "verification": 'manual',
    },

    'mahabubnagar': {
        "district": 'Mahabubnagar', "state": 'Telangana',
        "address": 'Beside Central Medicine Stores, Govt Hospital, Mahabubnagar-509001',
        "phone": '08542-223181', "email": 'sakhi.mbnr17@gmail.com',
        "contact_person": 'K. Manjula', "contact_person_phone": '6301615611',
        "verification": 'manual',
    },

    'mancherial': {
        "district": 'Mancherial', "state": 'Telangana',
        "address": 'Near Government Degree College, College Road, Mancherial-504208',
        "phone": '08736-250181', "email": 'sakhimncl2019@gmail.com',
        "contact_person": 'Srilatha', "contact_person_phone": '7382323666',
        "verification": 'manual',
    },

    'medak': {
        "district": 'Medak', "state": 'Telangana',
        "address": 'H.No.1-12-24/A/163, Road No.1, Opp: MGM Park, Indirapuri Colony, Medak-502101',
        "phone": '08452-295181', "email": 'sakhioscmedak@gmail.com',
        "contact_person": None, "contact_person_phone": '9346146580',
        "verification": 'manual',
    },

    'medchal malkajigiri': {
        "district": 'Medchal Malkajgiri', "state": 'Telangana',
        "address": 'Sakhi OSC Balika Sadan, Near Indira Gandhi Statue, Beside Hanuman Temple, Old Alwal, 500010',
        "phone": '9121166390', "email": 'sakhimedchal@gmail.com',
        "contact_person": 'G. Anita Reddy', "contact_person_phone": '7013420750',
        "verification": 'manual',
    },

    'mulugu': {
        "district": 'Mulugu', "state": 'Telangana',
        "address": 'Near Gattamma Temple, Opp: Govt Guest House, Govt Degree College Road, Mulugu-506343',
        "phone": '7013745008', "email": 'sakhimulugu@gmail.com',
        "contact_person": 'G. Kalpana (in-charge)', "contact_person_phone": '8186892507',
        "verification": 'manual',
    },

    'nagarkurnool': {
        "district": 'Nagarkurnool', "state": 'Telangana',
        "address": 'Sakhi OSC, Opposite New Collectorate, Beside Vaibhav Garden, Deshitkyal, Nagarkurnool-509209',
        "phone": '9951940181', "email": 'sakhingkl2019@gmail.com',
        "contact_person": 'P. Sunitha', "contact_person_phone": '9494631248',
        "verification": 'manual',
    },

    'nalgonda': {
        "district": 'Nalgonda', "state": 'Telangana',
        "address": 'R & B Building, Prakhasham Bazar, Old AJC Building, Nalgonda-508001',
        "phone": '08682-234088', "email": 'sakhi.nlg@gmail.com',
        "contact_person": 'Mandakini', "contact_person_phone": '8985191120',
        "verification": 'manual',
    },

    'narayanpet': {
        "district": 'Narayanpet', "state": 'Telangana',
        "address": 'Srinivasa Colony, Near Amrutha Sai Temple, Narayanpet-509210',
        "phone": '08506-295181', "email": 'sakhi.21nprt@gmail.com',
        "contact_person": 'Niharika Reddy', "contact_person_phone": '8096718168',
        "verification": 'manual',
    },

    'nirmal': {
        "district": 'Nirmal', "state": 'Telangana',
        "address": 'Nagar, Nirmal-504106',
        "phone": '8500540181', "email": 'sakhicenternirmal@gmail.com',
        "contact_person": 'P. Mamatha', "contact_person_phone": '9959271856',
        "verification": 'manual',
    },

    'nizamabad': {
        "district": 'Nizamabad', "state": 'Telangana',
        "address": 'Sakhi/One Stop Centre, Government General Hospital Premises, Nizamabad-503001',
        "phone": '08462-225181', "email": 'sakhiosc.nzb@gmail.com',
        "contact_person": 'Y. Lavanya (I/C Centre admin)', "contact_person_phone": '9948630367',
        "verification": 'manual',
    },

    'peddapalli': {
        "district": 'Peddapalli', "state": 'Telangana',
        "address": '505174',
        "phone": '9441792181', "email": 'sakhipeddapally@gmail.com',
        "contact_person": 'D. Swapna', "contact_person_phone": '8008841002',
        "verification": 'manual',
    },

    'rajanna sircilla': {
        "district": 'Rajanna Sircilla', "state": 'Telangana',
        "address": 'Sircilla, 505301',
        "phone": '08723-295181', "email": 'sakhisiricilla@gmail.com',
        "contact_person": 'B. Roja', "contact_person_phone": '8977772235',
        "verification": 'manual',
    },

    'rangareddy': {
        "district": 'Rangareddy', "state": 'Telangana',
        "address": 'Plot No. 177, Road No.6, Vanasthali Hills, Vanasthalipuram, Rangareddy-500070',
        "phone": '040-29800821', "email": 'sakhirrdist@gmail.com',
        "contact_person": 'P. Mariya Susheela', "contact_person_phone": '9440413076',
        "verification": 'manual',
    },

    'sangareddy': {
        "district": 'Sangareddy', "state": 'Telangana',
        "address": 'Survey No.203, Maila Pranganam, Bypass Road, Sangareddy-502001',
        "phone": '9490129740', "email": 'sakhi.sangareddy@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'manual',
    },

    'siddipet': {
        "district": 'Siddipet', "state": 'Telangana',
        "address": 'Old MCH Building 1st Floor, Near Buruju, Siddipet',
        "phone": '8886108181', "email": 'sakhisiddipet181@gmail.com',
        "contact_person": 'P. Prathima', "contact_person_phone": '7702708905',
        "verification": 'manual',
    },

    'suryapet': {
        "district": 'Suryapet', "state": 'Telangana',
        "address": 'Opp. Sumangali Function Hall, Near Community Hall, Jammigadda, Suryapet-508213',
        "phone": '9490265525', "email": 'sakhisuryapet181@gmail.com',
        "contact_person": 'Ch. Hemaltha', "contact_person_phone": '9948862274',
        "verification": 'manual',
    },

    'vikarabad': {
        "district": 'Vikarabad', "state": 'Telangana',
        "address": 'H.No.4-1-208, New Gandhi Gunj, Bank of Baroda Lane, Vikarabad',
        "phone": '08416-295181', "email": 'sakhivikarabad@gmail.com',
        "contact_person": None, "contact_person_phone": '8331050181',
        "verification": 'manual',
    },

    'wanaparthy': {
        "district": 'Wanaparthy', "state": 'Telangana',
        "address": 'H.No.39-113, Bandar Nagar, Wanaparthy-509103',
        "phone": '08545-233441', "email": 'sakhioscwnpdist@gmail.com',
        "contact_person": 'Sk. Shireen', "contact_person_phone": '9154395164',
        "verification": 'manual',
    },

    'warangal rural': {
        "district": 'Warangal (Rural)', "state": 'Telangana',
        "address": 'Warangal Rural',
        "phone": '0870-2935014', "email": 'sakhiwarangalrural@gmail.com',
        "contact_person": 'V. Sreelatha', "contact_person_phone": '8106326320',
        "verification": 'manual',
    },

    'yadadri bhuvanagiri': {
        "district": 'Yadadri Bhuvanagiri', "state": 'Telangana',
        "address": 'Colony, Bhongir, Yadadri Bhongir-508116',
        "phone": '08685-295181', "email": 'sakhiyadadri@gmail.com',
        "contact_person": 'CH. Lavanya Devi', "contact_person_phone": '9550184877',
        "verification": 'manual',
    },

}

# A handful of hand-transcribed, verified entries from the national
# directory PDF -- kept separate from NATIONAL_DISTRICTS below since
# these were individually checked against the source the same way
# Telangana's were, not machine-parsed.
OTHER_STATE_DISTRICTS = {
    'chittoor': {
        "district": 'Chittoor', "state": 'Andhra Pradesh',
        "address": 'One Stop Centre, RIMS-General Hospital, Municipal Maternity Ward, Chittoor City',
        "phone": '9959776697', "email": 'apsrcw@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'manual',
    },

    'krishna': {
        "district": 'Krishna', "state": 'Andhra Pradesh',
        "address": 'One Stop Centre, Old Government Hospital, Opp: Tummalapalli Kalakshetram, Vijayawada City, Krishna District',
        "phone": '9398914772', "email": 'apsrcw@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'manual',
    },

    'patna': {
        "district": 'Patna', "state": 'Bihar',
        "address": 'One Stop Centre, Chajjubagh Executive Bungalow, Patna District',
        "phone": '8210713745', "email": 'support@wcdbihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'manual',
    },

}

# Machine-parsed (pdfplumber table extraction, spot-checked but not
# individually hand-verified per row) from the full national
# directory PDF -- 518 districts across 33 states/UTs. See module
# docstring for the parsing method and what's excluded and why (6
# cross-state ambiguous district names, districts already covered
# above by a manually-verified entry).
NATIONAL_DISTRICTS = {
    'agar malwa': {
        "district": 'Agar Malwa', "state": 'Madhya Pradesh',
        "address": 'District Hospital, Agar Malwa',
        "phone": '8878623878', "email": 'agarmalwaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'agra': {
        "district": 'Agra', "state": 'Uttar Pradesh',
        "address": 'One Stop Centre, Raja MandiChauraha, MahilaChikitsalaya, Asha JyotiKendra, Agra, Agra District, Uttar Pradesh',
        "phone": '7235004607', "email": 'dpo_agra@rediffmmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'ahmadnagar': {
        "district": 'Ahmadnagar', "state": 'Maharashtra',
        "address": 'Dilasa Sakhi One Stop Center,Near Top up Petrol pump Ahamadnager- 414001',
        "phone": '41-2550289', "email": 'oscahmednagar@gmail.com dwcd.nagar@yahoo.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'ahmedabad': {
        "district": 'Ahmedabad', "state": 'Gujarat',
        "address": 'One Stop Centre-Sakhi Civil Hospital Campus, Asarva, Ahmedabad',
        "phone": '7929726400', "email": 'info@grcgujarat.org',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'aizwal': {
        "district": 'Aizwal', "state": 'Mizoram',
        "address": 'One Stop Centre, Durtlang North, ICFAI Road, Aizwal, Mizoram- 796025',
        "phone": '7085091363', "email": 'oscaizwl@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'ajmer': {
        "district": 'Ajmer', "state": 'Rajasthan',
        "address": 'Raj Lok Sewa Ayog, Ajmer',
        "phone": '0145-2627154', "email": 'poweajm@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'akola': {
        "district": 'Akola', "state": 'Maharashtra',
        "address": 'One Stop Centre, Durga Chowk near Mount Carmel School Akola- 444001',
        "phone": '0724-2428549', "email": 'dy.commissionerwd@yahoo.com,o scakola2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'aligarh': {
        "district": 'Aligarh', "state": 'Uttar Pradesh',
        "address": 'Jila Panchayat Near Railway Station, Dcop Hall-202001',
        "phone": '7906246674', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'alirajpur': {
        "district": 'Alirajpur', "state": 'Madhya Pradesh',
        "address": 'District Hospital Complex, First Floor, Shivpuri Road',
        "phone": '9399944391', "email": 'alirajpurosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'allahabad': {
        "district": 'Allahabad', "state": 'Uttar Pradesh',
        "address": 'One Stop Centre, Rani Laxmi Bai Asha Jyoti Kendra, Dr. Kaatju Road, Samira Hotel, Behind ParivarNiyojan Kendra, Adilabad District Uttar Pradesh',
        "phone": '7235004604', "email": 'dpoalld09@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'ambedkar nagar': {
        "district": 'Ambedkar Nagar', "state": 'Uttar Pradesh',
        "address": 'Probatio Karylay Room No 23 Vikas Bhawn-224122',
        "phone": '7234005836', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'amethi': {
        "district": 'Amethi', "state": 'Uttar Pradesh',
        "address": 'Congress Karyalaye K Piche',
        "phone": '6393340831', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'amravati': {
        "district": 'Amravati', "state": 'Maharashtra',
        "address": 'One Stop Centre, District Women Hospital, Shrikrushna Peth,Amravati. Amravati District, Maharashtra- 444606',
        "phone": '0721-2660382', "email": 'dy.commissionerwd@yahoo.com, oscamravati2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'amreli': {
        "district": 'Amreli', "state": 'Gujarat',
        "address": 'One Stop Center-Sakhi,Near Medical Store, Beside ART Center,Civil Hospital Campus, Amreli',
        "phone": '9909926953', "email": 'onestopcenteramreli@gmail.co',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'amritsar': {
        "district": 'Amritsar', "state": 'Punjab',
        "address": 'Civil Hospital, Amritsar',
        "phone": '98728-91364', "email": 'srcwpunjab@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'amroha jyotiba phule nagar': {
        "district": 'Amroha Jyotiba Phule Nagar', "state": 'Uttar Pradesh',
        "address": 'Joya Raod Vikash Bhawan Sp Office',
        "phone": '7235008634', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'anand': {
        "district": 'Anand', "state": 'Gujarat',
        "address": 'One Stop Center-Sakhi 2nd Floor, Nagarpalika Govt. Hospital, Station Road, Anand',
        "phone": '9898909707', "email": 'info@grcgujarat.org',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'anantapur': {
        "district": 'Anantapur', "state": 'Andhra Pradesh',
        "address": 'One Stop Centre, Room No.12 & 13, Trauma Care, Upstairs, Emergency Centre, Govt. General Hospital, Anantapur City, Anantapur District, Andhra Pradesh-515001',
        "phone": '8008053408', "email": 'apsrcw@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'anantnag': {
        "district": 'Anantnag', "state": 'Jammu & Kashmir',
        "address": 'Nai Basti General Bus stand Anantnag,-192101',
        "phone": '9469444334', "email": 'sakhianantnag@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'anjaw': {
        "district": 'Anjaw', "state": 'Arunachal Pradesh',
        "address": 'One Stop Centre, Near Additional Deputy Comm’s Office, Hayuliang, Anjaw-792104',
        "phone": '9436219757', "email": 'cdpohig@gmail.com,sochodeb@g mail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'annupur': {
        "district": 'Annupur', "state": 'Madhya Pradesh',
        "address": 'District Hospital Ward No. 09, Maternity Ward, 2nd Floor room No.- 23- 24, Annupur-484224',
        "phone": '7659298101', "email": 'annupurosc@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'araria': {
        "district": 'Araria', "state": 'Bihar',
        "address": 'District Women Empowerment Officer, Near-SDO Officer, Collectorate Araria-854311',
        "phone": '9771468001', "email": 'whl.araria@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'ariyalur': {
        "district": 'Ariyalur', "state": 'Tamil Nadu',
        "address": 'Ariyalur GH, Old Building, Ariyalur Municipality, Ariyalur',
        "phone": '9842074680', "email": 'srcwtamilnadu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'arwal': {
        "district": 'Arwal', "state": 'Bihar',
        "address": 'District Women Empowerment Officer, Near-Rojapar, Jehanabad Road, Collectorate, Arwal-804401',
        "phone": '9771468002', "email": 'whl.arwal@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'ashok nagar': {
        "district": 'Ashok Nagar', "state": 'Madhya Pradesh',
        "address": 'Near New Collectorate, Om Colony,',
        "phone": '7543220065', "email": 'ashoknagarosc@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'auraiya': {
        "district": 'Auraiya', "state": 'Uttar Pradesh',
        "address": 'Sausaiya Jila Aspatal Chichuli Auraiya-206122',
        "phone": '7234005837', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'azamgarh': {
        "district": 'Azamgarh', "state": 'Uttar Pradesh',
        "address": 'Jila Pobation Karylay 2 Floor Near Nehru Hall-276001',
        "phone": '7388463415', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bagalkote': {
        "district": 'Bagalkote', "state": 'Karnataka',
        "address": 'VisheshaChikistaGhataka,Room No 125 Govt. Civil Hospital, Navanagar, Bagalkot- 587103,',
        "phone": '354235708', "email": 'dd.wcd.bgk@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'baghpat': {
        "district": 'Baghpat', "state": 'Uttar Pradesh',
        "address": 'Collectorate Office Vikas Bhawan Room 10-250609',
        "phone": '7234005839', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bahraich': {
        "district": 'Bahraich', "state": 'Uttar Pradesh',
        "address": 'Room No 19, Mal Kachahari Bahrich',
        "phone": '7234005840', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'baksa': {
        "district": 'Baksa', "state": 'Assam',
        "address": 'Dr. Rup Ram Boro Hospital, PO – Mushalpur, Dist. Baska, Assam',
        "phone": '7399502362', "email": 'dswobak2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'balaghat': {
        "district": 'Balaghat', "state": 'Madhya Pradesh',
        "address": 'ITI Road, Railway Crossing, Janaki Bai Dhuware, Budi Ward No. 1, Balaghat',
        "phone": '07632-240299', "email": 'balaghatosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'ballia': {
        "district": 'Ballia', "state": 'Uttar Pradesh',
        "address": 'Prejari Camps Jila Probation Office- 277001',
        "phone": '7234005841', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'balod': {
        "district": 'Balod', "state": 'Chhattisgarh',
        "address": 'One Stop Centre, Sanjari Sports Club, Front of Civil Line, Balod District - Balod, Chhattisgarh',
        "phone": '752042181', "email": 'sakhibalod@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'baloda bazar': {
        "district": 'Baloda Bazar', "state": 'Chhattisgarh',
        "address": 'One Stop Centre, Collectorate Premises, Baloda Bazaar, Baloda Bazaar District, Chhattisgarh',
        "phone": '7089383268', "email": 'sakhibaloudabazar@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'banakantha': {
        "district": 'Banakantha', "state": 'Gujarat',
        "address": 'One Stop Centre-Sakhi Civil Hospital Campus, Banaskantha, Palanpur',
        "phone": '527074', "email": 'info@grcgujarat.org',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'banda': {
        "district": 'Banda', "state": 'Uttar Pradesh',
        "address": 'One Stop Centre, District Hospital, Civil Lines, Banda, Banda District, Uttar Pradesh-210001',
        "phone": '8052998069', "email": 'sudhiricps@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bangalore rural': {
        "district": 'Bangalore Rural', "state": 'Karnataka',
        "address": 'K.C.General Hospital, Malleshwaram, Bangalore',
        "phone": '1.80043E+11', "email": 'adww.dwcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bangalore urban': {
        "district": 'Bangalore Urban', "state": 'Karnataka',
        "address": 'Government Hospital, K.R.Puram, Bangalore',
        "phone": '080-25611733', "email": 'adww.dwcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'banka': {
        "district": 'Banka', "state": 'Bihar',
        "address": 'Women Helpline, Ground floor, Aapda Niyantrayan Kendra Banka-813102',
        "phone": '71468004', "email": 'whl.banka@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'barabanki': {
        "district": 'Barabanki', "state": 'Uttar Pradesh',
        "address": 'Jila Probation Karyalay Collectorate Tehseel Nawabganj Pin No.225001',
        "phone": '7234005844', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'baragarh': {
        "district": 'Baragarh', "state": 'Odisha',
        "address": 'District Head Quarter Hospital (DHH) Campus, Hospital Road, Dhanger, Bargarh, Odisha 768028',
        "phone": '8280003327', "email": 'dswobaragarh@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'baran': {
        "district": 'Baran', "state": 'Rajasthan',
        "address": 'One Stop Centre, Room No.10,11, First Floor, Mother & Child Health Bhawan, District Hospital, Baran, Baran District, Rajasthan',
        "phone": '9828141425', "email": 'icdsbaran@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bareily': {
        "district": 'Bareily', "state": 'Uttar Pradesh',
        "address": '300, Saiya Vala Sayunkat Jila Chitsalaya, Khuram Gautiya Road, Bareilly- 243001',
        "phone": '7235004602', "email": 'oscbareilly@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'barnala': {
        "district": 'Barnala', "state": 'Punjab',
        "address": 'Sakhi: One Stop Centre, Old Civil Hospital, Kachha College Road, Barnala, Pin Code 148101, Punjab.',
        "phone": '9646594899', "email": 'sakhioscbnl@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'barpeta': {
        "district": 'Barpeta', "state": 'Assam',
        "address": 'OSC, Barpeta , Sonkuchi Colony, PO - Sonkuchi , Dist. Barpeta',
        "phone": '8876607561', "email": 'dswobak2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'barwani': {
        "district": 'Barwani', "state": 'Madhya Pradesh',
        "address": 'Shaskiya Maadhyamik Vidhyalaya Parisar, Ranaji Chouk, Barwani',
        "phone": '7290222171', "email": 'barwaniosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bastar': {
        "district": 'Bastar', "state": 'Chhattisgarh',
        "address": 'One Stop Centre, Behind old BSNL office, Nayapara, Jagdalpur, Bastar, District, Chhattisgarh',
        "phone": '07782-223181', "email": 'jagdalpur@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'basti': {
        "district": 'Basti', "state": 'Uttar Pradesh',
        "address": 'Mahila Hospitel Rain Basera Gandhi Nagar Pakke-272002',
        "phone": '7234005845', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bathinda': {
        "district": 'Bathinda', "state": 'Punjab',
        "address": 'One Stop Centre, D-1 Civil Station, Near Income Tax Office, Bathinda City, Bathinda District, Punjab',
        "phone": '9415440810', "email": 'oscsakhibti2017',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'beed': {
        "district": 'Beed', "state": 'Maharashtra',
        "address": 'B & C Quarters, Chandmari Colony Dhanora Road Beed- 431122',
        "phone": '442-230493', "email": 'oscbeed@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'begusarai': {
        "district": 'Begusarai', "state": 'Bihar',
        "address": 'One Stop Centre, Collectorate Campus, Above DM Begusarai office, Begusarai City, Begusarai District, Bihar',
        "phone": '8406001052', "email": 'support@wcdbihar.org. in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'belgaum': {
        "district": 'Belgaum', "state": 'Karnataka',
        "address": 'District Hospital , Balgaum',
        "phone": '8312421967', "email": 'adww.dwcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bellary': {
        "district": 'Bellary', "state": 'Karnataka',
        "address": 'District Hospital premises, Bellary',
        "phone": '8392274363', "email": 'adww.dwcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bemetara': {
        "district": 'Bemetara', "state": 'Chhattisgarh',
        "address": 'One Stop Centre, District Hospital, New Dharmshala Bhawan,Bemtara, Bemtara District, Chhattisgarh',
        "phone": '7746980632', "email": 'sakhi1stop.bmt25@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'betul': {
        "district": 'Betul', "state": 'Madhya Pradesh',
        "address": 'Old District Panchayat Complex Building, near Bus Stand, Kothi Bazaar, Betul-460001',
        "phone": '07141-234829', "email": 'betulosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bhadohi (sant ravidas nagar)': {
        "district": 'Bhadohi (Sant Ravidas Nagar)', "state": 'Uttar Pradesh',
        "address": 'Old Collectorate, Gyanpur Sant Ravidas Nagar-221304',
        "phone": '7235008663', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bhagalpur': {
        "district": 'Bhagalpur', "state": 'Bihar',
        "address": 'Bhagalpur, S.S.P office, Kachhari Road, Bhagalpur,Pin-812001',
        "phone": '9771468006', "email": 'whl.aurnagabad@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bhandara': {
        "district": 'Bhandara', "state": 'Maharashtra',
        "address": 'One Stop Centre, C/o, Civil Hospital, Bhandara-441904',
        "phone": '07184-253400', "email": 'bdwcd_bhandara@rediffmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bharatpur': {
        "district": 'Bharatpur', "state": 'Rajasthan',
        "address": 'Nagr Nigam Aashray Sthal, District Hospital Campur, Bharatpur-321001',
        "phone": '4337000', "email": 'oscbhilwara@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bharuch': {
        "district": 'Bharuch', "state": 'Gujarat',
        "address": 'One Stop Center-Sakhi General Hospital, Near Trauma Center, Bharuch',
        "phone": '9712137025', "email": 'info@grcgujarat.org',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bhavnagar': {
        "district": 'Bhavnagar', "state": 'Gujarat',
        "address": 'One Stop Centre, Sir T. General Hospital, Second Floor, District TB Centre, Bhavnagar',
        "phone": '9924527074', "email": 'info@grcgujarat.org',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bhilwara': {
        "district": 'Bhilwara', "state": 'Rajasthan',
        "address": 'One Stop Centre, Mahatma Gandhi Hospital Premises, Bhilwara District, Rajasthan -311001',
        "phone": '9828141425', "email": 'po.we.bika@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bhind': {
        "district": 'Bhind', "state": 'Madhya Pradesh',
        "address": 'Parade Chohara, Near Dhanwanti Complex ,2nd Floor , Bhind',
        "phone": '7534234290', "email": 'bhindosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bhiwani': {
        "district": 'Bhiwani', "state": 'Haryana',
        "address": 'One Stop Centre, Old SDM Residence, Near Civil Hospital Ghanta Ghar Chowk',
        "phone": '01664-240044', "email": 'onestopcenter600@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bhojpur': {
        "district": 'Bhojpur', "state": 'Bihar',
        "address": 'Women Helpline-cum-One Stop CentreKG Road, Dr. Rungta Gali, Madhubagh, Nawada (Lalatoli), Arah(Bhojpur) Pin-802301',
        "phone": '9771468007', "email": 'whl.aurnagabad@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bhopal': {
        "district": 'Bhopal', "state": 'Madhya Pradesh',
        "address": 'One Stop Centre, Near State Bank of India, J.P.Hospital premises, Bhopal City, Bhopal District, Madhya Pradesh',
        "phone": '18002332244', "email": 'bhopalosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bhubaneswar': {
        "district": 'Bhubaneswar', "state": 'Odisha',
        "address": 'One Stop Centre, Capital Hospital, Unit 6, Ganga Nagar, Bhubaneswar, Khordha District, Odisha',
        "phone": '674-2397703', "email": 'onestopcentre.bbsr@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bidar': {
        "district": 'Bidar', "state": 'Karnataka',
        "address": 'District Hospital premises, Bidar',
        "phone": '8482225022', "email": 'adww.dwcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bijapur': {
        "district": 'Bijapur', "state": 'Chhattisgarh',
        "address": 'One Stop Centre, Near District Hospital, Bijapur, Bijapur District, Chhattisgarh',
        "phone": '7648057923', "email": 'sakhioscbijapur@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bijnor': {
        "district": 'Bijnor', "state": 'Uttar Pradesh',
        "address": 'Serkari Hospital Hosla Buliding',
        "phone": '9149026038', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bikaner': {
        "district": 'Bikaner', "state": 'Rajasthan',
        "address": 'P.B.M. Hospital premises, Bikaner',
        "phone": '9024109847', "email": 'oscchuru@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'biswanath': {
        "district": 'Biswanath', "state": 'Assam',
        "address": 'Sakhi One Stop Centre , Civil Hospital Campus, P.O. Biswanath Cariali, Dist, Biswanath Pin 784176',
        "phone": '8876607561', "email": 'dswoson2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bokaro': {
        "district": 'Bokaro', "state": 'Jharkhand',
        "address": 'One Stop Centre, Room No. 207, Sadar Hospital, Bokaro',
        "phone": '7366968854', "email": 'bokarodswo@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bongaigaon': {
        "district": 'Bongaigaon', "state": 'Assam',
        "address": 'Sakhi One Stop Centre, Sarvangi Bikash Trust, Majgaon, Bangaigaon - 783380',
        "phone": '9435402434', "email": 'dswobon2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'botad': {
        "district": 'Botad', "state": 'Gujarat',
        "address": 'One Stop Center-Sakhi Near Primary Health Centre, Barvada, Botad District',
        "phone": '99949545', "email": 'info@grcgujarat.org',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'budaun': {
        "district": 'Budaun', "state": 'Uttar Pradesh',
        "address": 'Jila Mahila Hospital Lawela Chouk',
        "phone": '7234005847', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'bulandshahar': {
        "district": 'Bulandshahar', "state": 'Uttar Pradesh',
        "address": 'Kasturba Gandhi Rajkiya Chikitsalay Mahila Hospital',
        "phone": '7234005848', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'buldhana': {
        "district": 'Buldhana', "state": 'Maharashtra',
        "address": 'District civil surgeon, Civil Hospital premises, Buldhana- 443001',
        "phone": '07262-244686', "email": 'Distcollectorosc.bul2018@gmail.co m',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'burhanpur': {
        "district": 'Burhanpur', "state": 'Madhya Pradesh',
        "address": 'One Stop Centre, New District Hospital Premises, Bahadurpur Road, Burhanpur District, Madhya Pradesh',
        "phone": '7325255500', "email": 'burhanpurosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'buxar': {
        "district": 'Buxar', "state": 'Bihar',
        "address": 'Women Helpline-cum-One Stop Centre Ground Floor Collectorate Campus, Buxar Pin-802102',
        "phone": '9771468008', "email": 'whl.aurnagabad@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'cachar': {
        "district": 'Cachar', "state": 'Assam',
        "address": 'One Stop Centre, Panchayat Road, Das Colony , Silchar, Cachar District, Assam',
        "phone": '3842245056', "email": 'srcwassam@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'chaibasa (west singhbhum)': {
        "district": 'Chaibasa (West Singhbhum)', "state": 'Jharkhand',
        "address": 'Aaush office near Sadar Hospital Chaibasa,-833201',
        "phone": '9090700489', "email": 'awc10.monitoring@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'chamarajnagar': {
        "district": 'Chamarajnagar', "state": 'Karnataka',
        "address": 'One Stop Centre, Special Treatment Unit, District Hospital 2nd Floor B.Rachaiah Jodi, Rd. Chamaraja Nagara, ChamarajaNagara District, Karnataka-571313',
        "phone": '08226-224720', "email": 'ddwcdchnagar@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'chamba': {
        "district": 'Chamba', "state": 'Himachal Pradesh',
        "address": 'Village Sarol,Near leprosy Rehabilitation Centre, PO Sarol, District Chamba-176310',
        "phone": '1899220307', "email": 'dpochamba1@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'champaran west': {
        "district": 'Champaran West', "state": 'Bihar',
        "address": 'Women Helpline-cum-One Stop Centre,Ground floor, Collectorate Campus, Near-Vipin High School, Bettiah-845438',
        "phone": '9771468009', "email": 'whl.aurnagabad@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'chandauli': {
        "district": 'Chandauli', "state": 'Uttar Pradesh',
        "address": 'Jagdish Darai Vikash Bhawan K Bagal M Jila Provations Karyalaye',
        "phone": '7234005849', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'chandigarh (ut)': {
        "district": 'Chandigarh (UT)', "state": 'Chandigarh (UT)',
        "address": 'One Stop Centre, Nari Niketan, Sector 26, Chandigarh (UT)',
        "phone": '9771468031', "email": 'sakhichd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'chandrapur': {
        "district": 'Chandrapur', "state": 'Maharashtra',
        "address": 'Run by Saraswati Shikshan Mahila Mandal, Mahatma Jyotiba Fule Sadan Krishna Nagar Chowk, Mul Road, Chandrapur-442605',
        "phone": '07172-274349', "email": 'disttwcdo_cha@rediffmail.com,dist tdwcdocha@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'changlang': {
        "district": 'Changlang', "state": 'Arunachal Pradesh',
        "address": 'One Stop Centre, Old Deputy Commissioner’s Office, Near New Secretariat Office Building, Changland-792120',
        "phone": '9436251043', "email": 'onestopcentre3@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'charaideo': {
        "district": 'Charaideo', "state": 'Assam',
        "address": 'One Stop Centre, Sonari, near Sonari Pukhuri, Ward no, 16 , PO/PS Sonari, Dist – Charaideo',
        "phone": '8638596726', "email": 'dswosiv2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'charkhi-dadri': {
        "district": 'Charkhi-Dadri', "state": 'Haryana',
        "address": 'Loharao Road, Backside Canara Bank, Near Sherawat Hospital',
        "phone": '9813722646', "email": 'Pobhw.wcd@gmail.com, Sunchauhan0007@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'chatra': {
        "district": 'Chatra', "state": 'Jharkhand',
        "address": 'Sadar Hospital Burn Unit (Sakhi- One Stop Center) District- Chatra- 835401',
        "phone": '8757898292', "email": 'awc7.monitoring@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'chennai': {
        "district": 'Chennai', "state": 'Tamil Nadu',
        "address": 'One Stop Centre, Deptt.of Social Welfare, Government Service Home, 8, Home Road, Judge Colony, Tambram Sanatorium, Chennai-600047',
        "phone": '044-22233355', "email": 'ostnchn@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'chhatarpur': {
        "district": 'Chhatarpur', "state": 'Madhya Pradesh',
        "address": 'Building of Shri. Vinod Khare, Panna Road, In front of stadium, near AbhaKharey Hospital, District Chattrapur',
        "phone": '7682244250', "email": 'chhatapurosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'chhittorgarh': {
        "district": 'Chhittorgarh', "state": 'Rajasthan',
        "address": 'RajkiyaSaavliyaji District Hospital, Chittorgarh City, Chittorgarh District, Rajasthan',
        "phone": '9828141425', "email": 'pochittor@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'chikkaballapura': {
        "district": 'Chikkaballapura', "state": 'Karnataka',
        "address": 'District General Hospital Premises, Chilkkaballapur, Near Marala Siddeshwar Temple, M G Road, Chikkaballapur,',
        "phone": '08156-270181', "email": 'adww.dwcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'chikmagalur': {
        "district": 'Chikmagalur', "state": 'Karnataka',
        "address": 'Rukminidevi Maternity Hospital, Belur Road, Chikmagalur,',
        "phone": '8262233940', "email": 'adww.dwcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'chindwada': {
        "district": 'Chindwada', "state": 'Madhya Pradesh',
        "address": 'One Stop Centre,Ekikrit Bal Vikas Sewa Pariyojana, Chindwada Rural, First Floor,P.G.College Road',
        "phone": '62243291', "email": 'chhindwaraosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'chirrang': {
        "district": 'Chirrang', "state": 'Assam',
        "address": 'One Stop Centre, J S B Civil Hospital, P.O KajalgaonDist . Chirrang',
        "phone": '9435325985', "email": 'dswokok2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'chitradurg': {
        "district": 'Chitradurg', "state": 'Karnataka',
        "address": 'One Stop Centre, Special Treatment Unit, District Hospital Chitradurga, Chitradurga District, Karnataka -577501',
        "phone": '08194-234579', "email": 'ddwcdcta@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'chitrakoot': {
        "district": 'Chitrakoot', "state": 'Uttar Pradesh',
        "address": 'District Hospital, Sonepur',
        "phone": '7234005850', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'churu': {
        "district": 'Churu', "state": 'Rajasthan',
        "address": 'Syamsiddha Bhawan, Near Mahila Thana, Churu- 331001',
        "phone": '01562-250919', "email": 'icdsdholpur@yahoo.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'coimbatore': {
        "district": 'Coimbatore', "state": 'Tamil Nadu',
        "address": 'Kenwin Middle School, Mettupalayam Road, Near Flower Market, Coimbatore - 641002',
        "phone": '2555126', "email": 'osccoimbatore@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'cuddalore': {
        "district": 'Cuddalore', "state": 'Tamil Nadu',
        "address": 'Sevai Illam Campus, Semmandalam - Cuddalore',
        "phone": '8525849462', "email": 'srcwtamilnadu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'cuttack': {
        "district": 'Cuttack', "state": 'Odisha',
        "address": 'One Stop Centre, 3rd Floor Mental Health Institute (MHI), building campus of SCB Medical college and Hospital, District',
        "phone": '9437018141', "email": 'osccuttack@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'dadra': {
        "district": 'Dadra', "state": 'Dadra & Nagar Haveli (UT)',
        "address": 'One Stop Centre, 2nd floor, CHC, Rakholi, Dadra & Nagar Haveli',
        "phone": '9499529291', "email": 'onestopcentre2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'dahod': {
        "district": 'Dahod', "state": 'Gujarat',
        "address": 'One Stop Center-Sakhi 1st Floor, Technical School Campus, Near Circuit House, Dahod',
        "phone": '9879348494', "email": 'info@grcgujarat.org',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'dakshina kannada': {
        "district": 'Dakshina Kannada', "state": 'Karnataka',
        "address": 'District Government Lady Ghoshan Hospital Premises, Mangalore',
        "phone": '0824-2443238', "email": 'adww.dwcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'damoh': {
        "district": 'Damoh', "state": 'Madhya Pradesh',
        "address": 'District Hospital, Damoh',
        "phone": '7812225128', "email": 'damohosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'dantewada': {
        "district": 'Dantewada', "state": 'Chhattisgarh',
        "address": 'One Stop Centre, Shakti MahilaSahaktikaran Kendra, Kailash Nagar, Dantewada District, Chhattisgarh',
        "phone": '8435689354', "email": 'sakhidantewada@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'darbhanga': {
        "district": 'Darbhanga', "state": 'Bihar',
        "address": 'One Stop Centre, Collectorate Campus, Darbhanga City, Darbhanga District, Bihar',
        "phone": '9771468010', "email": 'support@wcdbihar.org. in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'darrang': {
        "district": 'Darrang', "state": 'Assam',
        "address": 'Sakhi One Stop Centre , Darrang , Hospital Road , Mangaldoi - 784125',
        "phone": '9864708561', "email": 'dswodar2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'datia': {
        "district": 'Datia', "state": 'Madhya Pradesh',
        "address": 'District Hospital Premises, Women Ward, 2nd Floor, Datia',
        "phone": '75222235544', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'davangere': {
        "district": 'Davangere', "state": 'Karnataka',
        "address": 'Chigateri General Hospital Premises, Near NRC Centre,Davangere',
        "phone": '8192259899', "email": 'adww.dwcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'dehradun': {
        "district": 'Dehradun', "state": 'Uttarakhand',
        "address": 'One Stop Centre, Survey Chowk, Dehradun-2480015, Uttarakhand',
        "phone": '2970403', "email": 'oscdehradun@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'deogarh': {
        "district": 'Deogarh', "state": 'Jharkhand',
        "address": 'Sadar Hospital, Deogarh Campus Building',
        "phone": '72777242497', "email": 'awc17.monitoring@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'deoria': {
        "district": 'Deoria', "state": 'Uttar Pradesh',
        "address": 'Sadar Hospital',
        "phone": '7398731125', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'devbhoomi dwaraka': {
        "district": 'Devbhoomi Dwaraka', "state": 'Gujarat',
        "address": 'One Stop Center-Sakhi Old Mamlatdar Office, Near Kalyanji Mandir, Jamkhambhadia, Devbhumidwarka',
        "phone": '9426123774', "email": 'info@grcgujarat.org',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'dewas': {
        "district": 'Dewas', "state": 'Madhya Pradesh',
        "address": 'One Stop Centre, Near N.R.C., Mahatma Gandhi District Hospital Premises, Dewas, Dewas District, Madhya Pradesh',
        "phone": '9589125215', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'dhalai': {
        "district": 'Dhalai', "state": 'Tripura',
        "address": 'One Stop Centre, Anganwadi Training Centre, Kulai, Dhalai- 7992014',
        "phone": '9436932899', "email": 'tripuracommissionforwomen@gm ail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'dhamtari': {
        "district": 'Dhamtari', "state": 'Chhattisgarh',
        "address": 'One Stop Centre, Old Kendriya Vidhyalaya Bhawan, Collectorate Road,Rudri,Near Police Station Dhamtari, Dhamtari District, Chhattisgarh',
        "phone": '9516611812', "email": 'sakhidmt181@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'dhanbad': {
        "district": 'Dhanbad', "state": 'Jharkhand',
        "address": 'One Stop Centre, One Stop Centre, Red Cross Bhavan, Behind Golf Ground Dhanbad, Dhanbad District, Jharkhand- 831001',
        "phone": '9334261037', "email": 'singh2953@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'dhar': {
        "district": 'Dhar', "state": 'Madhya Pradesh',
        "address": 'Ward No.6, Opposite Trauma Centre,Bhoj Hospital, Dhar',
        "phone": '7292234056', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'dharmapuri': {
        "district": 'Dharmapuri', "state": 'Tamil Nadu',
        "address": 'Village Panchayat Resources Centre, Nallampally Near PHC – Dharmapuri',
        "phone": '8825571751', "email": 'srcwtamilnadu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'dharwad': {
        "district": 'Dharwad', "state": 'Karnataka',
        "address": 'One Stop Center, District Hospital, Special Treatment Unit, KIMS Hospital Hubli, Dharwad, Karnataka - 580020',
        "phone": '8362270020', "email": 'wcdmvcg.udp@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'dhemaji': {
        "district": 'Dhemaji', "state": 'Assam',
        "address": 'Sakhi One Stop Centre, DRDA Campus, Hospital Road, PO & Dist, Dhemaji',
        "phone": '9435186992', "email": 'dswodhe2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'dholpur': {
        "district": 'Dholpur', "state": 'Rajasthan',
        "address": 'District Hospital Premises, Dholpur City, Dholpur District',
        "phone": '05642-220015', "email": 'wedjpcl@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'dhubri': {
        "district": 'Dhubri', "state": 'Assam',
        "address": 'Destitute Home for Women Premises, Dighaltari, Dist. Dhubri',
        "phone": '9435103196', "email": 'dswodhu2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'dhule': {
        "district": 'Dhule', "state": 'Maharashtra',
        "address": 'Sakhi One Stop Centre Gov. Mamta Mahila Vastigruha, 28 Jay Hind Colony Opp. Jayhind High School and JR. College, Deopur , Dhule-424002',
        "phone": '0257-2251748', "email": 'Onestopcentredhule@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'dibang valley': {
        "district": 'Dibang Valley', "state": 'Arunachal Pradesh',
        "address": 'Child Development Project Officer Office Building,PO Anini, District Dibang Valley - 7920102',
        "phone": '9402621051', "email": 'cdpoanini@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'dibrugarh': {
        "district": 'Dibrugarh', "state": 'Assam',
        "address": 'Assam Medical College Hospital Campus, PO - AMC, Dibrugarh - 786002',
        "phone": '9954432706', "email": 'dswodhu2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'dimapur': {
        "district": 'Dimapur', "state": 'Nagaland',
        "address": 'One Stop Centre, District Hospital, Below Anganwadi Centre, Hospital Colony, Dimapur District,Nagaland-797112',
        "phone": '237448', "email": 'nld.srcw@gmail.com, sakhiosc.dmp@',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'dindori': {
        "district": 'Dindori', "state": 'Madhya Pradesh',
        "address": 'Ward No. 2 , Near, Imalkutti, Subkhar, Didori',
        "phone": '7828195167', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'dindugul': {
        "district": 'Dindugul', "state": 'Tamil Nadu',
        "address": 'Annai Sathya, Govt Orphanage Home, Collectorate Campus',
        "phone": '8220649143', "email": 'srcwtamilnadu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'diu': {
        "district": 'Diu', "state": 'Daman & Diu',
        "address": 'One Stop Centre, Govt. Primary Health Center, Near S.T. Bus Station, Diu, Daman & Diu (UT)',
        "phone": '9824829977', "email": 'masskff@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'doda': {
        "district": 'Doda', "state": 'Jammu & Kashmir',
        "address": 'Old RTO Office Doda Near Khan Plaza,- 182202',
        "phone": '7006641890', "email": 'oscdodahope@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'dumka': {
        "district": 'Dumka', "state": 'Jharkhand',
        "address": 'Old Sadar Hospital Campus, Dumka',
        "phone": '9955037013', "email": 'awc23.monitoring@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'durg': {
        "district": 'Durg', "state": 'Chhattisgarh',
        "address": 'One Stop Centre,New Bus Stand, Front of Dakshin Mukhi Hanuman Temple, Tandula jal Sansadhan Parisar, Durg- District,Chhattisgarh',
        "phone": '24261181', "email": 'sakhidurg@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'east garo hills': {
        "district": 'East Garo Hills', "state": 'Meghalaya',
        "address": 'One Stop Centre, District Social Welfare Officer, East Garo Hills, Williamnagar-794111, Meghalaya',
        "phone": '8787620910', "email": 'novareenumdor@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'east godavari': {
        "district": 'East Godavari', "state": 'Andhra Pradesh',
        "address": 'One Stop Centre, Veterinary Hospital Compound, Opp City Inn Hotel near town railway station, Kakinada, East Godavari District',
        "phone": '0884-2380181', "email": 'osc.egdt@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'east jaintia hills': {
        "district": 'East Jaintia Hills', "state": 'Meghalaya',
        "address": 'Residential Quarter, Community Health Centre, Khilehriat, East Jaintia Hills District-793200',
        "phone": '9774296298', "email": 'oscejhd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'east kameng': {
        "district": 'East Kameng', "state": 'Arunachal Pradesh',
        "address": 'Kampu Hollen Orphange, Seppa, Model Village Road, Seppa-790102',
        "phone": '7085691281', "email": 'onestopcentre3@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'east khasi hills': {
        "district": 'East Khasi Hills', "state": 'Meghalaya',
        "address": 'One Stop Centre, Ganesh Das Hospital, Shillong City, Shillong District, Meghalaya',
        "phone": '0364-2591075', "email": 'megoscgdh@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'east siang': {
        "district": 'East Siang', "state": 'Arunachal Pradesh',
        "address": 'One Stop Centre, High Region, Near General Hospital, Pasighat, East Siang District, Arunachal Pradesh',
        "phone": '8915900550', "email": 'welfaresocial71@yahoo.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'east singhbhum': {
        "district": 'East Singhbhum', "state": 'Jharkhand',
        "address": 'One Stop Centre, Red Cross Bhavan 3rd floor –Sakhi,Near Jubilee Park Gate, Jamshedpur, East Singhbhum District, Jharkhand-831001',
        "phone": '7209407209', "email": 'onestopjamshedpur2@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'erode': {
        "district": 'Erode', "state": 'Tamil Nadu',
        "address": 'Centre for Action & Rural Education',
        "phone": '9865129422', "email": 'srcwtamilnadu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'etah': {
        "district": 'Etah', "state": 'Uttar Pradesh',
        "address": 'CMO Office Dakh Bagliya Gt Raod Etah',
        "phone": '9412151589', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'etawah': {
        "district": 'Etawah', "state": 'Uttar Pradesh',
        "address": 'Motijhil Jila Hospital',
        "phone": '7234005854', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'faizabad': {
        "district": 'Faizabad', "state": 'Uttar Pradesh',
        "address": 'Room No 11, 3rd Floor,VikasBhawan, DPO Office, Faizabad',
        "phone": '7234005855', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'faridabad': {
        "district": 'Faridabad', "state": 'Haryana',
        "address": 'One Stop Centre, Kasturba Seva Sadan, Near SBI Bank, Neelam Chowk, Faridabad',
        "phone": '0129-2265199', "email": 'Pofbd.wcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'faridkot': {
        "district": 'Faridkot', "state": 'Punjab',
        "address": 'Sakhi One Stop Centre, Civil Hospital, Near Court Complex Faridkot, Pin Code 151203, Punjab.',
        "phone": '9781803080', "email": 'oscfdk2019@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'farrukhabad': {
        "district": 'Farrukhabad', "state": 'Uttar Pradesh',
        "address": 'State Bank Wali Gali Dr. Bhalla Ki Buliding',
        "phone": '7234005856', "email": 'aapkisakhiajkhq@gmail.co',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'fatehabad': {
        "district": 'Fatehabad', "state": 'Haryana',
        "address": 'DSP, Kothi(Govt. Building. Fatehabad',
        "phone": '01667220551', "email": 'Poftb.wcd@gmail.com, advrenuchandel@gmail.com, Rajendersingh3386@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'fatehgarh': {
        "district": 'Fatehgarh', "state": 'Punjab',
        "address": 'District Hospital, Fatehgarh Sahib.',
        "phone": '9417157290', "email": 'dpofathehgarhsahib@rediffmail.co m',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'fatehpur': {
        "district": 'Fatehpur', "state": 'Uttar Pradesh',
        "address": 'Mahila Jila Hospital 19 No Room',
        "phone": '7234005857', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'fazilika': {
        "district": 'Fazilika', "state": 'Punjab',
        "address": 'Sakhi One Stop Centre, Private Room No.-2, Civil Hospital, Fazilka, Pin No.152123, Punjab.',
        "phone": '01638-260181', "email": 'oscfzk@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'ferozpur': {
        "district": 'Ferozpur', "state": 'Punjab',
        "address": 'Maternity Ward, 2nd floor, Room No.-1, 2, 3, Civil Hospital, Ferozpur',
        "phone": '16343068', "email": 'oscferozpur@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'firozabad': {
        "district": 'Firozabad', "state": 'Uttar Pradesh',
        "address": 'One Stop Centre, Zila Hospital, AapkiSakhi Asha Jyoti Kendra, Near Jain Mandir, OPD SubhashSarayFirozabad',
        "phone": '9410414474', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'gadag': {
        "district": 'Gadag', "state": 'Karnataka',
        "address": 'District Hospital premises, Gadag',
        "phone": '8372297200', "email": 'adww.dwcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'gadchiroli': {
        "district": 'Gadchiroli', "state": 'Maharashtra',
        "address": 'One Stop Centre, Quarter No.46.47, Collector Colony, Sonapur Complex-442605',
        "phone": '07132-222645', "email": 'oscgadchiroli@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'gajapati': {
        "district": 'Gajapati', "state": 'Odisha',
        "address": 'District Headquarter Hospital(DHH) Campus ,PO- Paralakhemundi, Gajapati, Odisha 761200',
        "phone": '06815222025', "email": 'dswogajapati@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'gangtok': {
        "district": 'Gangtok', "state": 'Sikkim',
        "address": 'One Stop Centre, Lumsey, 5th Mile, Tadong, Gangtok District, Sikkim',
        "phone": '9434188310', "email": 'wcdsikkim@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'ganjam': {
        "district": 'Ganjam', "state": 'Odisha',
        "address": 'MKCG Medical College, Derhanpur, Ganjam, Odisha',
        "phone": '7008291415', "email": 'dswoganjam@nic.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'gariyaband': {
        "district": 'Gariyaband', "state": 'Chhattisgarh',
        "address": 'One Stop Centre, Near Govt Veer Surendra sai PG College,Below Kishor Nyay board, Gariyaband District, Chhattisgarh',
        "phone": '7049452410', "email": 'gariyabandsakhi181@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'garwah': {
        "district": 'Garwah', "state": 'Jharkhand',
        "address": 'One Stop Center, Sadar Hospital Premises, Court Road, Garwah- 822114',
        "phone": '8271053001', "email": 'oscsakhirinpas@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'gautambuddh a nagar': {
        "district": 'GautamBuddh a Nagar', "state": 'Uttar Pradesh',
        "address": 'Phase 2 Purani Post Sec 81',
        "phone": '9582406867', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'gaya': {
        "district": 'Gaya', "state": 'Bihar',
        "address": 'Collectorate, Gaya District, Gaya- 823001,Bihar',
        "phone": '9771468011', "email": 'support@wcdbihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'ghaziabad': {
        "district": 'Ghaziabad', "state": 'Uttar Pradesh',
        "address": 'One Stop Centre, MMG Hospital AJK, Near ShambuDayal Degree College Ghaziabad, Ghaziabad District Uttar Pradesh',
        "phone": '7235004603', "email": 'dpoghaziabad2gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'ghazipur': {
        "district": 'Ghazipur', "state": 'Uttar Pradesh',
        "address": 'One Stop Centre, CMO office, AdarshNagar, Gora Bazar, Janpath, Ghazipur District, UP',
        "phone": '7235004600', "email": 'dpogzp94@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'giridih': {
        "district": 'Giridih', "state": 'Jharkhand',
        "address": 'Sakhi- One Stop Center, Livelihood Center, 1 Floor, Dhariyadih, Behind City Police Station, Giridih- 815301',
        "phone": '8340596329', "email": 'dswo.giridih@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'girsomnath': {
        "district": 'Girsomnath', "state": 'Gujarat',
        "address": 'One Stop Centre-Sakhi Civil Hospital Campus, Veraval, Girsomnath',
        "phone": '7046832769', "email": 'osc.girsomnath@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'goalpara': {
        "district": 'Goalpara', "state": 'Assam',
        "address": 'Sakhi One Stop Centre, Bapuji Nagar, PO & Dist. Goalpara',
        "phone": '7035264711', "email": 'dswogoa2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'godda': {
        "district": 'Godda', "state": 'Jharkhand',
        "address": 'One Stop Center, Block Office Campus, Godda, - 814133',
        "phone": '8340156169', "email": 'awc19.monitoring@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'golaghat': {
        "district": 'Golaghat', "state": 'Assam',
        "address": 'OSC, Golaghat, Jiban Tamuly Path, Ward no. 12, 2nd Floor. AWTC building ( Golaghat Nirman Mahila Gut), PO & Dist.Golaghat',
        "phone": '9435012875', "email": 'dswogol2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'gonda': {
        "district": 'Gonda', "state": 'Uttar Pradesh',
        "address": 'Fhorvejganj Cwc Buliding',
        "phone": '7234005861', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'gondia': {
        "district": 'Gondia', "state": 'Maharashtra',
        "address": 'One Stop Centre, C/o. JJB & CWC Building, Near Shivaji Smarak, Old Police Head Quarter, Manohar Chowk, Gondia Dist. Gondia (Maharashtra)- 441601',
        "phone": '07182-251468', "email": 'osc.gondia2019@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'gopalganj': {
        "district": 'Gopalganj', "state": 'Bihar',
        "address": 'Women Helpline-cum-One Stop Centre, Gound Floor, Collectorate Campus, Gopalganj-841428',
        "phone": '9771468012', "email": 'whl.aurnagabad@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'gorakhpur': {
        "district": 'Gorakhpur', "state": 'Uttar Pradesh',
        "address": 'One Stop Centre, BRD Medical College, Thana Gulaahrioya, Gorakhpur, Gorakhpur District, UP',
        "phone": '9889014639', "email": 'provationgkp@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'gulbarga': {
        "district": 'Gulbarga', "state": 'Karnataka',
        "address": 'District Government Hospital premises, Kalburgi',
        "phone": '8472279659', "email": 'adww.dwcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'gumla': {
        "district": 'Gumla', "state": 'Jharkhand',
        "address": 'Science Building, Kutchery Campus, Gumla,- 835207',
        "phone": '9431560250', "email": 'awc3.monitoring@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'guna': {
        "district": 'Guna', "state": 'Madhya Pradesh',
        "address": 'District Hospital Campus, Guna',
        "phone": '8720869727', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'guntur': {
        "district": 'Guntur', "state": 'Andhra Pradesh',
        "address": 'One Stop Centre, Mahila Pranganam, Opp. Zila Parishad Collectorate, Banglore Road, Guntur-522004',
        "phone": '0863-2233525', "email": 'sakhiguntur@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'gurdaspur': {
        "district": 'Gurdaspur', "state": 'Punjab',
        "address": 'One Stop Centre, New Civil Hospital, JeewanwalBabri, Gurdaspur City, Gurdaspur District,Punjab-143521',
        "phone": '01874-240165', "email": 'oscgsp@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'gurugram': {
        "district": 'Gurugram', "state": 'Haryana',
        "address": 'One Stop Centre, Baal Udyan (opposite DC residence)Civil Lines, Gurugram, Haryana',
        "phone": '0124-2331148', "email": 'pogrgwcd.123@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'gwalior': {
        "district": 'Gwalior', "state": 'Madhya Pradesh',
        "address": 'One Stop Centre, J.A.H. Campus, Opp. T.V.Ward Compound, Gwalior City, Gwalior District, Madhya Pradesh',
        "phone": '26228404', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'hailakandi': {
        "district": 'Hailakandi', "state": 'Assam',
        "address": 'Sakhi One Stop Centre for Women, PO - Lakahirbond Dist. Hailakandi',
        "phone": '9957606749', "email": 'dswohai2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'hanumangarh': {
        "district": 'Hanumangarh', "state": 'Rajasthan',
        "address": 'One Stop Centre, Mahatma Gandhi Smriti Zila Hospital Hanumangarh, District Hanumangarh - 230130',
        "phone": '230130', "email": 'sakhihanumangarh@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'hapur': {
        "district": 'Hapur', "state": 'Uttar Pradesh',
        "address": 'Modinagar Road, Kesaw Nagar Chouki K Pass, Probations Karayalaye',
        "phone": '61778839', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'harda': {
        "district": 'Harda', "state": 'Madhya Pradesh',
        "address": 'One Stop Center (Sakhi), Children’s Home(Bal Griha), Bypass crossroad, Indore Road',
        "phone": '7577223817', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'hardoi': {
        "district": 'Hardoi', "state": 'Uttar Pradesh',
        "address": 'Serkari Hospital Emrgency Gate Private Room',
        "phone": '8840643691', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'haridwar': {
        "district": 'Haridwar', "state": 'Uttarakhand',
        "address": 'One Stop Centre, Priyadarshini working, Women Hostel, Near Pramila Guest House, Opposite Inden Gas Plant, Uttarakhand- 249401',
        "phone": '01334-221166', "email": 'haridwar.onestopcentre181@gmail. com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'hassan': {
        "district": 'Hassan', "state": 'Karnataka',
        "address": 'District Chamrajendra Hospital Premises',
        "phone": '8172252222', "email": 'adww.dwcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'hathras': {
        "district": 'Hathras', "state": 'Uttar Pradesh',
        "address": 'Bangla Hospital, Ayush Wing Building, Office No. 2, Aligarh Road,Hathras',
        "phone": '9411939612', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'haveri': {
        "district": 'Haveri', "state": 'Karnataka',
        "address": 'District Hospital Premises,Haveri',
        "phone": '8375249005', "email": 'adww.dwcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'hazaribagh': {
        "district": 'Hazaribagh', "state": 'Jharkhand',
        "address": 'Sakhi- One Stop Center, Sadar Hospital Campus Hazaribagh',
        "phone": '9852352559', "email": 'awc15.monitoring@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'hingoli': {
        "district": 'Hingoli', "state": 'Maharashtra',
        "address": 'Shaskiya Vasahat T-1-1/1 & T-1- 1/2 Opp.SBI Bank Akola Road, Hingoli',
        "phone": '8421036985', "email": 'dwandcdoh@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'hissar': {
        "district": 'Hissar', "state": 'Haryana',
        "address": 'One Stop Centre, Police Hospital in Women Police Station, Hissar District, Haryana -125001',
        "phone": '01662-239097', "email": 'pohsr.wcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'hojai': {
        "district": 'Hojai', "state": 'Assam',
        "address": 'One Stop Centre , Hojai, Lanka , Near Block Primary Health Centre (Opp. Range Forest Office) Pin 782446',
        "phone": '9864018944', "email": 'dswonag2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'hoshangabad': {
        "district": 'Hoshangabad', "state": 'Madhya Pradesh',
        "address": 'One Stop Centre, Near Red Cross Bhawan, District Hospital Premises, Hoshangabad City, Hoshangabad District, Madhya Pradesh',
        "phone": '9826356898', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'hoshiarpur': {
        "district": 'Hoshiarpur', "state": 'Punjab',
        "address": 'One Stop Centre, Room No.-1, 1A, Private Surgical Ward, Civil Hospital Hoshiarpur.',
        "phone": '882254112', "email": 'osc.hoshiarpur@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'indore': {
        "district": 'Indore', "state": 'Madhya Pradesh',
        "address": 'One Stop Centre, K.E.I. Compound, Opp. Narsingh School, Indore, Indore, District, Madhya Pradesh',
        "phone": '9827321705', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'jabalpur': {
        "district": 'Jabalpur', "state": 'Madhya Pradesh',
        "address": 'One Stop Centre, Near Bhoo Sarvekshan Office, Jabalpur City, Jabalpur District, Madhya Pradesh',
        "phone": '7612422257', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'jaipur': {
        "district": 'Jaipur', "state": 'Rajasthan',
        "address": 'One Stop Centre, Govt. RBD Jaipuria Hospital Premises, JLN Marg- 302018 District, Rajasthan',
        "phone": '0141-2553763', "email": 'wedjpcl@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'jaisalmer': {
        "district": 'Jaisalmer', "state": 'Rajasthan',
        "address": 'Shri Jawahar Hospital Campus, Hanuman Circle, Jaisalmer',
        "phone": '7793057080', "email": 'onestopcentrejaisalmer@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'jalandhar': {
        "district": 'Jalandhar', "state": 'Punjab',
        "address": 'One Stop Centre, MCH Ward, Civil Hospital, Jalandhar City, Jalandhar District, Punjab',
        "phone": '0181-2230181', "email": 'oscjalandhar@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'jalaun': {
        "district": 'Jalaun', "state": 'Uttar Pradesh',
        "address": 'District Hospital Room No. 2',
        "phone": '7234005946', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'jalgaon': {
        "district": 'Jalgaon', "state": 'Maharashtra',
        "address": 'Sakhi One Stop Center Govt. Ashadeep Women Hostel, Plot No- 6, Vijay colony in front of Ashok Bakery,Jalgaon-425001',
        "phone": '0257-2251748', "email": 'sakhioscjal@rediffmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'jalna': {
        "district": 'Jalna', "state": 'Maharashtra',
        "address": 'Mahila Rajya Gruha, Dr.Misal building, near Shani Temple, Old Jalna',
        "phone": '9422183008', "email": 'sakhijalna.mh@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'jalore': {
        "district": 'Jalore', "state": 'Rajasthan',
        "address": 'Dist. Hospital, Jalore City, Jalore District, Rajasthan',
        "phone": '9829796449', "email": 'powejalore@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'jammu': {
        "district": 'Jammu', "state": 'Jammu & Kashmir',
        "address": '245/A, Puran Nagar New Plot Jammu,-180005',
        "phone": '0191-2571213', "email": 'sakhijammu@181jandk.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'jamnagar': {
        "district": 'Jamnagar', "state": 'Gujarat',
        "address": 'One Stop Centre,Opp. Mental Health Hospital,VikasGruh Road,Old P.I.U. Office, Jamnagar',
        "phone": '301043', "email": 'info@grcgujarat.org',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'jamtara': {
        "district": 'Jamtara', "state": 'Jharkhand',
        "address": 'One Stop Center, ANM Training Centre Building, Sadar Hospital, Jamtara- 815351',
        "phone": '488357041', "email": 'dcpsjamtara@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'jamui': {
        "district": 'Jamui', "state": 'Bihar',
        "address": 'Women Helpline-cum-One Stop Centre Near-Treasury Office,Collectorate Campus, Jamui.-811307',
        "phone": '9771468013', "email": 'whl.aurnagabad@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'jangir-champa': {
        "district": 'Jangir-Champa', "state": 'Chhattisgarh',
        "address": 'One Stop Centre, Ram Krishna colony, Behind tritiya varg employee Federation, Kera Road, Jangir-Champa, District, Chhattisgarh',
        "phone": '9340564760', "email": 'janjgirsakhi2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'jashpur': {
        "district": 'Jashpur', "state": 'Chhattisgarh',
        "address": 'One Stop Centre, Near District Hospital, Bhagalpur Road, Jashpur, Jashpur District, Chhattisgarh',
        "phone": '7646936041', "email": 'raipursakhi@181chhattisgarh.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'jaunpur': {
        "district": 'Jaunpur', "state": 'Uttar Pradesh',
        "address": 'Jila Provation Karayalaye Near Sp Office',
        "phone": '7235008628', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'jehanabad': {
        "district": 'Jehanabad', "state": 'Bihar',
        "address": 'Women Helpline-cum-One Stop Centre, Room No-11, Ground Floor,Collectorate Campus, Jehanabad-804408',
        "phone": '771468014', "email": 'whl.aurnagabad@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'jhabua': {
        "district": 'Jhabua', "state": 'Madhya Pradesh',
        "address": 'District Hospital Complex, in front the trauma Centre- 457661',
        "phone": '9407843557', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'jhajjar': {
        "district": 'Jhajjar', "state": 'Haryana',
        "address": 'Purani Tehsil, Jhajjar',
        "phone": '9813064392', "email": 'Pojjr.wcd@gmail.com, Lalitakalra08@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'jhansi': {
        "district": 'Jhansi', "state": 'Uttar Pradesh',
        "address": 'One Stop Centre, Rani Laxmi Bai Asha Jyoti Medical College Complex,Jhansi, Jhansi District, Uttar Pradesh',
        "phone": '93469220', "email": 'dpojhsrajsharma@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'jhunjhunu': {
        "district": 'Jhunjhunu', "state": 'Rajasthan',
        "address": 'One Stop Centre Red Cross Society Building, BDK Govt. Hospital, Jhunjhunu, Jhunjhunu District, Rajasthan',
        "phone": '9828141425', "email": 'viplavneola@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'jind': {
        "district": 'Jind', "state": 'Haryana',
        "address": 'Civil Hospital, Jind',
        "phone": '9588705814', "email": 'Pojnd.wcd@gmail.comRajwantiver ma7@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'jodhpur': {
        "district": 'Jodhpur', "state": 'Rajasthan',
        "address": 'Working Women Hostel, Panchbati Chauraha, Ratanada, Jodhpur-342011',
        "phone": '9828141425', "email": 'oscjodhpur2019@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'jorhat': {
        "district": 'Jorhat', "state": 'Assam',
        "address": 'One Stop Centre, Prerona Pratibandhi ShishuVikash Kendra, Chinamara, Jorhat District, Assam',
        "phone": '9435352138', "email": 'srcwassam@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'junagadh': {
        "district": 'Junagadh', "state": 'Gujarat',
        "address": 'Junagadh OSC Scheme, Near Blood Bank, Old Civil Hospital Campus,Nr. Azad Chowk, Junadagh',
        "phone": '9909926953', "email": 'po.junagadh@gmail.com osc.junagadh@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kabirdham': {
        "district": 'Kabirdham', "state": 'Chhattisgarh',
        "address": 'One Stop Centre, Ambedkar Chowk, front of Bisen Hospital, Behind Bharat mata Murty, Kawardha, District-Kabirdham',
        "phone": '07741-233077', "email": 'sakhikawardha910@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kadapa': {
        "district": 'Kadapa', "state": 'Andhra Pradesh',
        "address": 'One Stop Centre, Marchury Road, Govt. General Hospital, Kadapa- 516004, Andhra Pradesh',
        "phone": '09989623970', "email": 'oscsakhikadapa@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kaimur': {
        "district": 'Kaimur', "state": 'Bihar',
        "address": 'Women Helpline-cum-One Stop Centre Collectorate Campus, Ward No-12, Kaimur 821101',
        "phone": '9771468015', "email": 'whl.aurnagabad@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kaithal': {
        "district": 'Kaithal', "state": 'Haryana',
        "address": 'Balmiki samuday Kendra,Khanori road Kaithal',
        "phone": '9416384609', "email": 'Poktl.wcd@gmail.com, Oshodarshan24@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kamrup': {
        "district": 'Kamrup', "state": 'Assam',
        "address": 'Sakhi One Stop Centre Guest House , Puthimari, Athara P.O. Kamalpur, Dist. Kamrup',
        "phone": '7086254873', "email": 'dswokamr2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kamrup metropolitan': {
        "district": 'Kamrup Metropolitan', "state": 'Assam',
        "address": 'One Stop Centre, H/No 37A, Survey Ajanta Path, Beltola',
        "phone": '9864012581', "email": 'sakhit.oscghy@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kancheepuram': {
        "district": 'Kancheepuram', "state": 'Tamil Nadu',
        "address": 'Government Hospital, Chengalpattu, Kanchipuram - 603001',
        "phone": '044-27433471', "email": 'osckanchipuram@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kanker': {
        "district": 'Kanker', "state": 'Chhattisgarh',
        "address": 'One Stop Centre, Singar Bhat Road, Near Giyani Dhaba kisan Rice mill, Kanker District, Chhattisgarh',
        "phone": '9893396530', "email": 'kankersakhi181@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kannauj': {
        "district": 'Kannauj', "state": 'Uttar Pradesh',
        "address": 'One Stop Centre, Vinod Dixit Hospital, Makrand Nagar, GP Road, Kannauj District, Uttar Pradesh',
        "phone": '7235004554', "email": 'provationkannauj@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kannur': {
        "district": 'Kannur', "state": 'Kerala',
        "address": 'One Stop Centre,Govt. Taluk Hospital, Kuthuparamba, Kannur',
        "phone": '4902367450', "email": 'onestopcentrekpba@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kanpur': {
        "district": 'Kanpur', "state": 'Uttar Pradesh',
        "address": 'One Stop Centre, Rani Laxmi Bai Asha Jyoti Medical College, Sankraamad Rog Sanstha, GolChauraha, Kanpur, Kanpur, District,U.P.',
        "phone": '235004547', "email": 'dpokanpur@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kanpurdehat': {
        "district": 'KanpurDehat', "state": 'Uttar Pradesh',
        "address": 'District Hospital',
        "phone": '7235008635', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kanyakumari': {
        "district": 'Kanyakumari', "state": 'Tamil Nadu',
        "address": 'Agatheeswaran Taluk, Rajakamangalam Block, Kanniyakumari',
        "phone": '94874171127', "email": 'srcwtamilnadu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kapurthala': {
        "district": 'Kapurthala', "state": 'Punjab',
        "address": 'Navkiran Kendra, Ward No. 3, Civil Hospital Kapurthala, Punjab.',
        "phone": '9876502631', "email": 'dpokapurthala@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'karauli': {
        "district": 'Karauli', "state": 'Rajasthan',
        "address": 'District Hospital, Karauli City, Karauli District, Rajasthan',
        "phone": '9001795719', "email": 'pokaroli@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'karbi anglong': {
        "district": 'Karbi Anglong', "state": 'Assam',
        "address": 'Dist, Social Welfare Office complex , Rongkhelan, M G Road , PO/PS - Diphu , Karbi Anglong',
        "phone": '9435352138', "email": 'dswokar2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'karimganj': {
        "district": 'Karimganj', "state": 'Assam',
        "address": 'One Stop Centre, Civil Hospital, MCH Wing P.O. & Dist. Karimganj , Pin 788710',
        "phone": '9435175454', "email": 'dswokganj2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'karnal': {
        "district": 'Karnal', "state": 'Haryana',
        "address": 'One Stop Centre, Mahila Complex, Behind State Transport Corporation, Bus Stand, Karnal, Karnal District, Haryana',
        "phone": '2270175', "email": 'pokrl.wcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'karur': {
        "district": 'Karur', "state": 'Tamil Nadu',
        "address": 'Anbukarangal Old age Home 25, Ganesh Nagar, Vennimalai Karur',
        "phone": '9786998899', "email": 'srcwtamilnadu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kashiramnaga rkasganj': {
        "district": 'KashiramNaga rKasganj', "state": 'Uttar Pradesh',
        "address": 'Rajkiye Mahila Hospital Nadri Gate,Kasganj,203123',
        "phone": '7235008636', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kathua': {
        "district": 'Kathua', "state": 'Jammu & Kashmir',
        "address": 'Ward number-2, Near Kashmir Rice Mill, Opposite Nagri bus adda Kathua- 184101',
        "phone": '7006406004', "email": 'sakhicentrekathua@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'katihar': {
        "district": 'Katihar', "state": 'Bihar',
        "address": 'Women Helpline,Room No- 3, Ground Floor, Vikas Bhawan, Collectorate Campus, Katihar- 854105',
        "phone": '9771468016', "email": 'whl.aurnagabad@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'katni': {
        "district": 'Katni', "state": 'Madhya Pradesh',
        "address": 'One Stop Centre, District Hospital Premises, Bhartiya State Bank Main Branch,Katni City, Katni District, Madhya Pradesh',
        "phone": '7622220727', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kaushambi': {
        "district": 'Kaushambi', "state": 'Uttar Pradesh',
        "address": 'District Hospital Manjhanpur Kaushambi-212207',
        "phone": '9956696685', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kendrapara': {
        "district": 'Kendrapara', "state": 'Odisha',
        "address": 'Shelter for Urban Homeless, Kendrapara-754211',
        "phone": '06727-232004', "email": 'dswokendrapara@nic.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'khagaria': {
        "district": 'Khagaria', "state": 'Bihar',
        "address": 'Women Helpline, Ground floor, Near- District Supply Office, Collectorate Campus, Khagaria - 801205',
        "phone": '9102407316', "email": 'whl.khagaria@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'khandwa': {
        "district": 'Khandwa', "state": 'Madhya Pradesh',
        "address": 'One Stop Centre, State,MahilaAashrayaGreh, Near C.M.H. Office Khandwa, Khandwa District, Madhya Pradesh',
        "phone": '9098807773', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'khargone': {
        "district": 'Khargone', "state": 'Madhya Pradesh',
        "address": 'Smt. Saroj, Dr. Surychandra Joshi, 99 Bhogle Colony, Behind Shardha Hospital',
        "phone": '7282243919', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kheda': {
        "district": 'Kheda', "state": 'Gujarat',
        "address": 'One Stop Center-Sakhi Block E, 2nd Floor, Civil Hospital, Nadiad- Kheda',
        "phone": '9898909707', "email": 'info@grcgujarat.org',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'khowai': {
        "district": 'Khowai', "state": 'Tripura',
        "address": 'One Stop Centre, PWD Complex nearby O/0 the DM and Collector, Khowai District-799201',
        "phone": '9612428092', "email": 'tripuracommissionforwomen@gm ail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'khunti': {
        "district": 'Khunti', "state": 'Jharkhand',
        "address": 'Sakhi- One Stop Center, Old Subdivision Office, Court Campus, District- Khunti',
        "phone": '9102961988', "email": 'awc2.monitoring@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kiphire': {
        "district": 'Kiphire', "state": 'Nagaland',
        "address": 'Sakhi-One Stop Centre Medical Ward, Near District Civil Hospital Kiphire, Nagaland-798611',
        "phone": '6909031762', "email": 'kiphire.sakhiosc@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kishanganj': {
        "district": 'Kishanganj', "state": 'Bihar',
        "address": 'Women Helpline-cum-One Stop Centre,2nd Floor, Yojana Bhawan, Collectorate Campus, Kishanganj- 855107',
        "phone": '9771468017', "email": 'whl.aurnagabad@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kodagu': {
        "district": 'Kodagu', "state": 'Karnataka',
        "address": 'District Hospital Premises, Room No.26, Madikeri Town, Kodagu',
        "phone": '08272-225444', "email": 'adww.dwcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'koderma': {
        "district": 'Koderma', "state": 'Jharkhand',
        "address": 'Sakhi- One Stop Center, Sadar Hospital, Koderma',
        "phone": '8662952702', "email": 'awc8.monitoring@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kohima': {
        "district": 'Kohima', "state": 'Nagaland',
        "address": 'One Stop Centre, Directorate of Social Welfare, Opp Law College, Raj Bhawan area, Kohima-797001',
        "phone": '0370-2240146', "email": 'sakhiosc.kohima@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kokrajhar': {
        "district": 'Kokrajhar', "state": 'Assam',
        "address": 'One Stop Centre, District RNB Hospital, Kokrajhar, Kokrajhar District, Assam',
        "phone": '9435325985', "email": 'srcwassam@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kolar': {
        "district": 'Kolar', "state": 'Karnataka',
        "address": 'District Hospital Premises, Kolar',
        "phone": '08152-222035', "email": 'adww.dwcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kolhapur': {
        "district": 'Kolhapur', "state": 'Maharashtra',
        "address": 'Government Tejaswini Mahila Vastigruh, 857-E-Ulape Building, Randive Col. Kadamwadi Road, Kolhapur-416003',
        "phone": '0231-2604046', "email": 'supdttejaswini@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kondagaon': {
        "district": 'Kondagaon', "state": 'Chhattisgarh',
        "address": 'One Stop Centre, Old Zila Panchayat, Building Near district Court, Kondagaon, District- Kondagaon, Chhattisgarh',
        "phone": '9294737125', "email": 'raipursakhi@181chhattisgarh.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'koppal': {
        "district": 'Koppal', "state": 'Karnataka',
        "address": 'District Hospital Premises, Koppal',
        "phone": '8539225941', "email": 'adww.dwcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'koraput': {
        "district": 'Koraput', "state": 'Odisha',
        "address": 'SahidLakhmanNayak Medical College Campus Koraput-764020',
        "phone": '9078890200', "email": 'sakhikorapur@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'korba': {
        "district": 'Korba', "state": 'Chhattisgarh',
        "address": 'One Stop Centre, H.No.482,Kharmora Road, Near Podi Bahar Road,Korba, Korba District, Chhattisgarh',
        "phone": '8827276746', "email": 'sakhikorba@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'korea': {
        "district": 'Korea', "state": 'Chhattisgarh',
        "address": 'One Stop Centre, Beside Mahalpara City,Baikunthpur, District koriya, Chhattisgarh',
        "phone": '07836-233519', "email": 'sakhicentrekorea@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'krishnagiri': {
        "district": 'Krishnagiri', "state": 'Tamil Nadu',
        "address": 'Government Service Home, Krishnagiri',
        "phone": '7904372356', "email": 'srcwtamilnadu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kupwara': {
        "district": 'Kupwara', "state": 'Jammu & Kashmir',
        "address": 'District Hospital Kupwara-193222',
        "phone": '9596444261', "email": 'sakhikupwara@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kurnool': {
        "district": 'Kurnool', "state": 'Andhra Pradesh',
        "address": 'One Stop Centre, Room No.214, Upstairs, NtrVidyaSeva, Karyalayam, Govt. General Hospital, Kurnool City, Kurnool District, Andhra Pradesh-581002',
        "phone": '08518-255057', "email": 'apsrcw@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kurukshetra': {
        "district": 'Kurukshetra', "state": 'Haryana',
        "address": 'Working Women Hostel, room no.10- 12, Kurukshetra',
        "phone": '9896660260', "email": 'kkrosc@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kushinagar': {
        "district": 'Kushinagar', "state": 'Uttar Pradesh',
        "address": 'Combine District Hopsital Ravindra Nagar Dhush, Kushinagar-274704',
        "phone": '9628298823', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'kutchh': {
        "district": 'Kutchh', "state": 'Gujarat',
        "address": 'One Stop Centre-Sakhi G.K.General Hospital, Room No.27 to 32, Bhuj-Kutch',
        "phone": '9879047047', "email": 'oscbhuj@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'lakhimpur': {
        "district": 'Lakhimpur', "state": 'Assam',
        "address": 'Lakhimpur Akok Abosthan Kendra ,Uttar Lakhimpur, Tirtheswar Hazarika Path , Ward no, 7 , PO - Noth Lakhimpur , Dist, Lakhimpur 787001',
        "phone": '7002385061', "email": 'dswolak2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'lakhisarai': {
        "district": 'Lakhisarai', "state": 'Bihar',
        "address": 'Women Helpline, District Empowerment Office, Collectorate Campus, Lakhisarai-811311',
        "phone": '9102407317', "email": 'whl.lakhisarai@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'lakhmipur kheri': {
        "district": 'Lakhmipur Kheri', "state": 'Uttar Pradesh',
        "address": 'District Probation Office Naurangabad Chauraha Kheri- 262701',
        "phone": '7235008638', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'lalitpur': {
        "district": 'Lalitpur', "state": 'Uttar Pradesh',
        "address": 'DPO Office, Kachahari, VikasBhawan, Lalitpur',
        "phone": '7235008640', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'latehar': {
        "district": 'Latehar', "state": 'Jharkhand',
        "address": 'Gurukul Rajhar Building Top Floor, Latehar',
        "phone": '8271186715', "email": 'awc14.monitoring@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'latur': {
        "district": 'Latur', "state": 'Maharashtra',
        "address": 'One Stop Centre Latur, Plot No R2/239, Netaji Nagar, Near Kalge Hospital Latur, Dist. Maharashtra- 413512',
        "phone": '9284275480', "email": 'dwcdolatur@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'leh': {
        "district": 'Leh', "state": 'Jammu & Kashmir',
        "address": 'Assistant Labour Commissioner office Skampari Leh Ladakh- 194101',
        "phone": '051382522', "email": 'r.angono5790@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'lohardaga': {
        "district": 'Lohardaga', "state": 'Jharkhand',
        "address": 'Sadar Block Campus, Lohardaga,Pincode- 835302',
        "phone": '9572494570', "email": 'awc4.monitoring@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'lohit': {
        "district": 'Lohit', "state": 'Arunachal Pradesh',
        "address": 'Deputy Director (ICDS) Office Building, PO Tezu, District Lohit- 792131',
        "phone": '9436048253', "email": 'ddicdstezu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'longleng': {
        "district": 'Longleng', "state": 'Nagaland',
        "address": 'High school ward, Below Government High School, Longleng. Nagaland-798625',
        "phone": '6009240973', "email": 'longleng.sakhiosc@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'lower dibang valley': {
        "district": 'Lower Dibang Valley', "state": 'Arunachal Pradesh',
        "address": 'Deputy Director (ICDS) Office Building, PO Roing, District Lower Dibang Valley-79210',
        "phone": '9863924023', "email": 'ddicdsroing@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'lower siang': {
        "district": 'Lower Siang', "state": 'Arunachal Pradesh',
        "address": 'Child Development Project Officer Office Building, PO/PS Likabali, District Lower Siang- 791125',
        "phone": '8258018727', "email": 'cdpolikabali@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'lower subansiri': {
        "district": 'Lower Subansiri', "state": 'Arunachal Pradesh',
        "address": 'One Stop Centre, District Hospital Ziro, Gyati Taka General Hospital, Medical Colony-791120',
        "phone": '8471988169', "email": 'onestopcentre3@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'lucknow': {
        "district": 'Lucknow', "state": 'Uttar Pradesh',
        "address": 'One Stop Centre, LokBandhu Hospital, AKJ LDA Kanpur Road Yojna, Lucknow, Uttar Pradesh',
        "phone": '7235004513', "email": 'lkodpo34@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'ludhiana': {
        "district": 'Ludhiana', "state": 'Punjab',
        "address": 'Emergency Ward, One Stop Sakhi Centre, Civil Hospital,Ludhiana.',
        "phone": '99881-00415', "email": 'oscludhiana@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'lunglei': {
        "district": 'Lunglei', "state": 'Mizoram',
        "address": 'One Stop Centre, Christian Hospital Serkawan, Annex Building',
        "phone": '8974243453', "email": 'onestopcentrellionestop@gmail.co m',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'madhepura': {
        "district": 'Madhepura', "state": 'Bihar',
        "address": 'Women Helpline-cum-One Stop Centre Room No- 01, Ground Floor,Collectorate Campus Madhepura-852113',
        "phone": '9771468018', "email": 'whl.aurnagabad@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'madhubani': {
        "district": 'Madhubani', "state": 'Bihar',
        "address": 'Women Helpline-cum-One Stop Centre Near- Treasury, Collectorate Campus, Madhubani- 847211',
        "phone": '9771468019', "email": 'whl.aurnagabad@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'madurai': {
        "district": 'Madurai', "state": 'Tamil Nadu',
        "address": 'Government Hospital, District Social Welfare Office, 35 East 2nd Cross Street K.K. Nagar, Madurai - 625009',
        "phone": '2580181', "email": 'maduraiosc@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'mahasamund': {
        "district": 'Mahasamund', "state": 'Chhattisgarh',
        "address": 'One Stop Centre, District Hospital, G.A.N. Training Centre, Mahasamand, Mahasamand District, Chhattisgarh',
        "phone": '9109917181', "email": 'sakhimahasamund@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'mahboobnagar': {
        "district": 'Mahboobnagar', "state": 'Telangana',
        "address": 'Besides Central Medicine Store, Government General Hospital, Mahabubnagar-590009, Telangana',
        "phone": '08542-273181', "email": 'sakhi.mbnr17@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'mahisagar': {
        "district": 'Mahisagar', "state": 'Gujarat',
        "address": 'One Stop Center-Sakhi Civil Hospital Campus, Lunawada, Mahisagar',
        "phone": '9879348494', "email": 'info@grcgujarat.org',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'mahoba': {
        "district": 'Mahoba', "state": 'Uttar Pradesh',
        "address": 'District Hospital CMO Office , Parmanand Chauraha Mahoba- 210427',
        "phone": '7235008641', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'mahrajganj': {
        "district": 'Mahrajganj', "state": 'Uttar Pradesh',
        "address": 'District Probation Office,Maharajganj-273303',
        "phone": '7235008642', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'mainpuri': {
        "district": 'Mainpuri', "state": 'Uttar Pradesh',
        "address": 'District Hospital, Mainpuri-205001',
        "phone": '7235008643', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'majuli': {
        "district": 'Majuli', "state": 'Assam',
        "address": 'Sakhi One Stop Centre, Garamur Hospital Campus, P.O. Garamur, Dist. Majuli',
        "phone": '9435352138', "email": 'dswodhu2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'mallapuram': {
        "district": 'Mallapuram', "state": 'Kerala',
        "address": 'One Stop Center, Near Mini Civil Station, Perinthalmanna, Mallapuram',
        "phone": '4933297400', "email": 'oscmalappuram@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'mandala': {
        "district": 'Mandala', "state": 'Madhya Pradesh',
        "address": 'Red Cross Bhawan, 1st Floor, Super Bazar, Mandala-481661',
        "phone": '9406786735', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'mandi': {
        "district": 'Mandi', "state": 'Himachal Pradesh',
        "address": 'Jail Road, Mandi Tehsil, Mandi- 175001',
        "phone": '1905223845', "email": 'Dpomandi.wcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'mandsaur': {
        "district": 'Mandsaur', "state": 'Madhya Pradesh',
        "address": '137, Ramtikri, Sudama Nagar, Mandsaur',
        "phone": '8827351039', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'mandya': {
        "district": 'Mandya', "state": 'Karnataka',
        "address": 'District Hospital Premises,Room No.78, Mandya',
        "phone": '8232224316', "email": 'adww.dwcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'mansa': {
        "district": 'Mansa', "state": 'Punjab',
        "address": 'One Stop Center( Sakhi), Swine Flu Ward, 2nd Floor, RoomNo. 1, Civil Hospital, Mansa, Punjab.',
        "phone": '9814223059', "email": 'onestopmansa@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'mathura': {
        "district": 'Mathura', "state": 'Uttar Pradesh',
        "address": 'District Hospital Near Vikas Market Holi Gate Old Bus Stand Mathura 281001',
        "phone": '7235008644', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'mau': {
        "district": 'Mau', "state": 'Uttar Pradesh',
        "address": 'District Hospital Blood Bank Near Mau- 275101',
        "phone": '7235008645', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'mayurbhanj': {
        "district": 'Mayurbhanj', "state": 'Odisha',
        "address": 'District Headquarter Hospital(DHH) Campus, Baripada-757001',
        "phone": '06792-255480', "email": 'rdac_mayurbhanj@yahoo.co.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'medchal': {
        "district": 'Medchal', "state": 'Telangana',
        "address": 'Plot No.93, H.No.37-10/9/3, Defence Colony Sainikpuri,Medchal, Malkajgiri, Telenga.500094',
        "phone": '040-27115144', "email": 'sakhimedchal@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'meerut': {
        "district": 'Meerut', "state": 'Uttar Pradesh',
        "address": 'One Stop Centre, SardarBallabh Bhai Patel Chikitsalya, Gadh Road, Meerut, Meerut District, Uttar Pradesh',
        "phone": '7235004568', "email": 'pandeysudhakarsharan@gmail.co m',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'mirzapur': {
        "district": 'Mirzapur', "state": 'Uttar Pradesh',
        "address": 'One Stop Centre, DPO Office, Next to Collectorate Treasury, Mirzapur District, Uttar Pradesh - 231001',
        "phone": '9506600723', "email": 'mztdpo@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'moga': {
        "district": 'Moga', "state": 'Punjab',
        "address": 'Civil Hospital, Moga',
        "phone": '01636-224216', "email": 'oscmoga@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'mokokchung': {
        "district": 'Mokokchung', "state": 'Nagaland',
        "address": 'Sakhi-One Stop Centre Nemcha Complex Opposite Grace Hall, Arkong Ward Mokokchung, Nagaland - 798601',
        "phone": '6909638829', "email": 'mkg.sakhiosc@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'mon': {
        "district": 'Mon', "state": 'Nagaland',
        "address": 'New Site Shamnyu Ward Near Christ King School, Mon Town, Nagaland- 798621',
        "phone": '6009150274', "email": 'mon.sakhiosc@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'moradabad': {
        "district": 'Moradabad', "state": 'Uttar Pradesh',
        "address": 'Kath Road,Ashiana, Phase-1, C- 145, Near Satbhawana Hospital,',
        "phone": '6395626457', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'morbi': {
        "district": 'Morbi', "state": 'Gujarat',
        "address": 'One Stop Center-Sakhi Hunter College-Vishipara, Near Fatak, Morbi',
        "phone": '9427664290', "email": 'info@grcgujarat.org',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'morena': {
        "district": 'Morena', "state": 'Madhya Pradesh',
        "address": 'One Stop Centre, M-625, New Housing Board Colony, MorenaCity, Morena District, Madhya Pradesh',
        "phone": '9826222582', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'morigaon': {
        "district": 'Morigaon', "state": 'Assam',
        "address": 'Sakhi One Stop Centre, Morigaon Mohila Mehfil, PO & Dist. Morigaon',
        "phone": '9854070895', "email": 'dswodhu2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'motihari (east champaran)': {
        "district": 'Motihari (East Champaran)', "state": 'Bihar',
        "address": 'Women Helpline, Room No- 70, Near- DCLR Officer, Collectorate Campus, Motihari-845401',
        "phone": '9102407315', "email": 'whl.chamaparaneast@wdc.bihar.or g.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'mumbai suburban': {
        "district": 'Mumbai Suburban', "state": 'Maharashtra',
        "address": 'Female Beggers Home, 1st Fl.R.C. Marg, Opp. Jain Mandir, Chembur(E) Mumbai-400071',
        "phone": '2962025', "email": 'sakhisuburbandwcdo@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'mungeli': {
        "district": 'Mungeli', "state": 'Chhattisgarh',
        "address": 'One Stop Centre, District Hospital Ramgarh, Mungeli, Mungeli District, Chhattisgarh',
        "phone": '7999612416', "email": 'sakhiramgarh08@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'munger': {
        "district": 'Munger', "state": 'Bihar',
        "address": 'Women Helpline-cum-One Stop Centre First Floor, Information Bhawan, Collectorate Campus, Near- Fort, Munger-811201',
        "phone": '9771468020', "email": 'whl.aurnagabad@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'muzaffarnagar': {
        "district": 'Muzaffarnagar', "state": 'Uttar Pradesh',
        "address": 'One Stop Centre, Community Health Centre, Vikas Khand, Sadar,Muzaffarnagar District, Uttar Pradesh',
        "phone": '859305150', "email": 'dpomzn1@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'muzaffarpur': {
        "district": 'Muzaffarpur', "state": 'Bihar',
        "address": 'Women Helpline-cum-One Stop Centre, Near- ICDS Officer Collectorate Campus, Muzaffarpur-842001',
        "phone": '9771468021', "email": 'whl.aurnagabad@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'mysore': {
        "district": 'Mysore', "state": 'Karnataka',
        "address": 'One Stop Centre, Cheluvamba Hospital (Children Section), Mysuru',
        "phone": '0821-2423181', "email": 'adww.dwcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'nagaon': {
        "district": 'Nagaon', "state": 'Assam',
        "address": 'One Stop Centre, District Walfare Office, Campus, Amolapatty,Nagaon, Assam',
        "phone": '9435060538', "email": 'srcwassam@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'nagapattinam': {
        "district": 'Nagapattinam', "state": 'Tamil Nadu',
        "address": 'AvvaiNGO, (First floor), 29, Sattaiyappar Mela street, Nagapattinam-611001.',
        "phone": '9087581738', "email": 'srcwtamilnadu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'nagaur': {
        "district": 'Nagaur', "state": 'Rajasthan',
        "address": 'Quarter No. 5, JLN Government Hospital, Bikaner Road, Nagaur',
        "phone": '9828141425', "email": 'sakhioscnagaur@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'nagpur': {
        "district": 'Nagpur', "state": 'Maharashtra',
        "address": 'One Stop Centre, Bharosa Centre, Nagpur, Nagpur District, Maharashtra',
        "phone": '022-22814906', "email": 'dy.commissionerwd@yahoo.comd w_nagpur@rediffmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'nainital': {
        "district": 'Nainital', "state": 'Uttarakhand',
        "address": 'One Stop Centre, Govt. Medical College, Haldwani, Nainital District, Uttarakhand',
        "phone": '9759749998', "email": 'oscntl@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'nalanda': {
        "district": 'Nalanda', "state": 'Bihar',
        "address": 'Women Helpline-cum-One Stop Centre, First Floor, Yojana Bhawan, Collectorate Campus, Nalanda-803101',
        "phone": '9771468022', "email": 'whl.aurnagabad@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'nalbari': {
        "district": 'Nalbari', "state": 'Assam',
        "address": 'Sakhi One Stop Centre,Rajnagar ,( Near Gordon School Field ) , PO & Dist. Nalbari',
        "phone": '9854070895', "email": 'dswokok2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'namakkal': {
        "district": 'Namakkal', "state": 'Tamil Nadu',
        "address": 'Arukkani Chinnappan illam, Pillayar Kovil Street, Thillaipuram, Namakkal',
        "phone": '7904372356', "email": 'srcwtamilnadu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'namsai': {
        "district": 'Namsai', "state": 'Arunachal Pradesh',
        "address": 'CDPO Office building, Near Commissioner East Office, Thana Road, Namsai',
        "phone": '9612789861', "email": 'onestopcentre3@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'nanded': {
        "district": 'Nanded', "state": 'Maharashtra',
        "address": 'One Stop Centre, Ravidas Niwas, H.No.1/12/849, Shastri Nagar, Near Bhagyanagar, Nanded- 431605,',
        "phone": '7038064090', "email": 'sakhioscnanded@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'nandurbar': {
        "district": 'Nandurbar', "state": 'Maharashtra',
        "address": 'One Stop Center, Civil Hospital Area, Sakri Road-425412',
        "phone": '02564-210047', "email": 'oscnandurbar@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'narayanpur': {
        "district": 'Narayanpur', "state": 'Chhattisgarh',
        "address": 'One Stop Centre, Narayanpur, Police station new bus stand',
        "phone": '7781252643', "email": 'sakhioscnpr@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'narmada': {
        "district": 'Narmada', "state": 'Gujarat',
        "address": 'One Stop Center-Sakhi General Hospital, Rajpipla, Narmada',
        "phone": '9712137025', "email": 'info@grcgujarat.org',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'narnaul': {
        "district": 'Narnaul', "state": 'Haryana',
        "address": 'H.No. 772, 1st Floor, Sector-1, Narnaul, Narnaul District, Haryana-123001',
        "phone": '8398891195', "email": 'ponrl.wcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'narsinghpur': {
        "district": 'Narsinghpur', "state": 'Madhya Pradesh',
        "address": 'Sadar media road, near Ashish Hospital, housing board, Narsinghpur',
        "phone": '7792231832', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'nasik': {
        "district": 'Nasik', "state": 'Maharashtra',
        "address": 'Sakhi One Stop Center Government Vatsalya Women Shelter Home, Near Ashok Stambh, Gangapur Road, Nashik- 422001',
        "phone": '022-22814906', "email": 'dy.commissionerwd@yahoo.com, nashiksakhiosc@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'navsari': {
        "district": 'Navsari', "state": 'Gujarat',
        "address": 'One Stop Center-Sakhi 2nd Floor, Referral Hospital & Community Health Center, Khadsupa, Navsari',
        "phone": '9638956885', "email": 'info@grcgujarat.org',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'nawada': {
        "district": 'Nawada', "state": 'Bihar',
        "address": 'Women Helpline-cum-One Stop Centre 2nd Floor, Near-SP Officer, Collectorate Campus, Main Road, Nawada-805110',
        "phone": '9771468023', "email": 'whl.aurnagabad@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'neemuch': {
        "district": 'Neemuch', "state": 'Madhya Pradesh',
        "address": 'Red Cross Bhawan, near District Hospital',
        "phone": '9425368415', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'nellore': {
        "district": 'Nellore', "state": 'Andhra Pradesh',
        "address": 'One Stop Centre, DSR Govt. Hospital, SPS, Nellore City, Nellore District, Andhra Pradesh',
        "phone": '09848653821', "email": 'apsrcw@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'nicobars': {
        "district": 'Nicobars', "state": 'Andaman and Nicobar Islands (UT)',
        "address": 'One Stop Centre, Perka, Headquarters, Car Nicobar, Nicobars- 744301',
        "phone": '03193-265121', "email": 'osccarnic@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'nilgiris': {
        "district": 'Nilgiris', "state": 'Tamil Nadu',
        "address": 'Kerala Club House, Ooty',
        "phone": '9787914125', "email": 'srcwtamilnadu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'north & middle andaman': {
        "district": 'North & Middle Andaman', "state": 'Andaman and Nicobar Islands (UT)',
        "address": 'One Stop Centre, Old DRDA Office, O/o. The Deputy Commissioner, Near State Library, Mayabunder, North & Middle Andaman-744204',
        "phone": '03192-273009', "email": 'sakhiandaman@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'north garo hills': {
        "district": 'North Garo Hills', "state": 'Meghalaya',
        "address": 'One Stop Centre, District Social Welfare Officer, North Garo Hills- 794108',
        "phone": '8014715584', "email": 'dswo.ngh-meg@gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'north goa': {
        "district": 'North Goa', "state": 'Goa',
        "address": 'One Stop Centre, Goa Medical College, NH-17, Bambolim, Tiswadi, North Goa District, Goa- 403202',
        "phone": '0832-2458700', "email": 'dir-wcd.goa.nic.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'nuapada': {
        "district": 'Nuapada', "state": 'Odisha',
        "address": 'District Head Quarter Hospital (DHH) Campus',
        "phone": '9438611588', "email": 'Tapaswini9988@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'osmanabad': {
        "district": 'Osmanabad', "state": 'Maharashtra',
        "address": 'Sakhi One Stop Center, 1st Floor, Civil Hospital, Osmanabad-413501',
        "phone": '02472-222592', "email": 'oscbd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'pakur': {
        "district": 'Pakur', "state": 'Jharkhand',
        "address": 'Sakhi- One Stop Center, Sadar Hospital, Sonajori, Pakur-816107',
        "phone": '9123265651', "email": 'awc20.monitoring@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'palamu': {
        "district": 'Palamu', "state": 'Jharkhand',
        "address": 'Sakhi- One Stop Center, Block Campus, Chainpur, Medininagar, Palamu- 822110',
        "phone": '7277224957', "email": 'awc13.monitoring@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'palghar': {
        "district": 'Palghar', "state": 'Maharashtra',
        "address": 'District women and child development officer, Near Aryan Ground Vishnu Nagar Road, Lokmanya Pada, Palghar',
        "phone": '2525257622', "email": 'dwcdopalghar@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'pali': {
        "district": 'Pali', "state": 'Rajasthan',
        "address": 'Regional BangarDirstrict Hospital, Pali City, Pali District, Rajasthan',
        "phone": '9828141425', "email": 'ddicdspali002@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'palwal': {
        "district": 'Palwal', "state": 'Haryana',
        "address": 'Civil Hospital, Palwal',
        "phone": '8076721376', "email": 'Pojjr.wcd@gmail.com, Lalitakalra08@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'panchkula': {
        "district": 'Panchkula', "state": 'Haryana',
        "address": 'Civil Hospital,Panchkula',
        "phone": '9416075049', "email": 'Popkl.wcd@gmail.com, Payalpruthi555@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'panchmahal': {
        "district": 'Panchmahal', "state": 'Gujarat',
        "address": 'One Stop Center-Sakhi 2nd Floor, Near Dayalisis Department, Civil Hospital, Godhra, Panchmahal',
        "phone": '8141185878', "email": 'info@grcgujarat.org',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'panipat': {
        "district": 'Panipat', "state": 'Haryana',
        "address": 'Red Cross Bhawan, Panipat',
        "phone": '7082403278', "email": 'kasee_06@yahoo.co.in, oscpnp@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'panna': {
        "district": 'Panna', "state": 'Madhya Pradesh',
        "address": 'House of Kherunisha, Ward No.11, Opposite Badshaha Sai Masjid, Civil Line Road, Panna',
        "phone": '7732250022', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'parbhani': {
        "district": 'Parbhani', "state": 'Maharashtra',
        "address": 'Govt. Civil Hospital, Subhash Road, Parbhani Pin.- 431401',
        "phone": '9511886844', "email": 'dwcdopbn@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'patan': {
        "district": 'Patan', "state": 'Gujarat',
        "address": 'One Stop Centre-Sakhi,F-28/29, First Floor, GMERS Medical College/Hospital, Dharpur-Patan',
        "phone": '978443329', "email": 'onestop.patan@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'pathankot': {
        "district": 'Pathankot', "state": 'Punjab',
        "address": 'District Administrative Complex, B- Block, room No.138, Malkpur, Pathankot, Punjab',
        "phone": '94633231071', "email": 'oscpathankot@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'patiala': {
        "district": 'Patiala', "state": 'Punjab',
        "address": 'One Stop Centre, Mini Secretariat Road, Adjoining Red Cross Building, Patiala, Patiala District, Punjab-147001',
        "phone": '1752358713', "email": 'srcwpunjab@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'pedapalli': {
        "district": 'Pedapalli', "state": 'Telangana',
        "address": 'H. No:1-198, SRSP camp, Peddapally.(Opposite to New constructing Collectorate.)',
        "phone": '08728-224224', "email": 'Sakhipeddapally@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'perambalur': {
        "district": 'Perambalur', "state": 'Tamil Nadu',
        "address": 'Annai Engel Swather Grey Home for Women and Girls 39/6 – A new M.G.Puram Perambalur - 621212',
        "phone": '8056808543', "email": 'srcwtamilnadu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'peren': {
        "district": 'Peren', "state": 'Nagaland',
        "address": 'Sakhi-One Stop Centre, Near District Hospital, Mdipuiram colony, Peren Town, Nagaland -797101',
        "phone": '9402623190', "email": 'peren.sakhiosc@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'phek': {
        "district": 'Phek', "state": 'Nagaland',
        "address": 'Sakhi-One Stop Centre Opposite Art & Culture Office, Bethel Colony Phek Town,Nagaland-797108',
        "phone": '6009215728', "email": 'phek.sakhiosc@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'pilibheet': {
        "district": 'Pilibheet', "state": 'Uttar Pradesh',
        "address": 'One Stop Centre, District Hospital, Pilibheet District, Uttar Pradesh',
        "phone": '9450229760', "email": 'probationofficepbt@ gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'porbandar': {
        "district": 'Porbandar', "state": 'Gujarat',
        "address": 'One Stop Center-Sakhi Maharani Rupaniba Hospital (Civil Hospital) Porbandar',
        "phone": '7874216217', "email": 'info@grcgujarat.org',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'puddukottai': {
        "district": 'Puddukottai', "state": 'Tamil Nadu',
        "address": 'Governmt Head Quarters Hospital Pudukkottai',
        "phone": '9788191448', "email": 'srcwtamilnadu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'puducherry': {
        "district": 'Puducherry', "state": 'Puducherry (UT)',
        "address": 'One Stop Centre, Rajiv Gandhi Hospital, 100 Feet Road, Ellaipillaichavadi, Puducherry',
        "phone": '0413-2244964', "email": 'wcd.pon@nic.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'pune -1': {
        "district": 'Pune -1', "state": 'Maharashtra',
        "address": 'Sakhi One Stop Centre, 2nd floor, Dalvi Hospital, Near Shivaji Nagar, S.T. Stand, Pune-411005',
        "phone": '022-22814906', "email": 'pune1osc@gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'pune-2': {
        "district": 'Pune-2', "state": 'Maharashtra',
        "address": 'Sakhi One Stop Centre, 1st floor, Rajiv Gandhi Hospital, Yerawada, Pune- 411006',
        "phone": '7387934588', "email": 'Pune2osc@gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'purnea': {
        "district": 'Purnea', "state": 'Bihar',
        "address": 'Collectorate, Purnea, Bihar',
        "phone": '9774168029', "email": 'support@wcdbihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'raebareli': {
        "district": 'RaeBareli', "state": 'Uttar Pradesh',
        "address": 'Collectrate Near Vikas Bhawan Degree College Chauraha Raibarelliy-229001',
        "phone": '7235008651', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'raichur': {
        "district": 'Raichur', "state": 'Karnataka',
        "address": 'District Hospital Premises, Room No.44, Rims Hospital, Raichur',
        "phone": '08532-221818', "email": 'adww.dwcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'raipur': {
        "district": 'Raipur', "state": 'Chhattisgarh',
        "address": 'One Stop Centre, District Hospital, Janta Colony, Raipur City,Raipur District, Chhattisgarh – 492001',
        "phone": '8269007181', "email": 'sakhiraipur@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'raisen': {
        "district": 'Raisen', "state": 'Madhya Pradesh',
        "address": 'Ward No. 4, Near Collectorate office, Sanchi Road, Raisen',
        "phone": '7974338949', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'rajgarh': {
        "district": 'Rajgarh', "state": 'Madhya Pradesh',
        "address": 'District Hospital Premises, Near O.P.D., District Rajgarh, 465661',
        "phone": '8085041298', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'rajkot': {
        "district": 'Rajkot', "state": 'Gujarat',
        "address": 'One Stop Centre-Sakhi PDU Civil Hospital Campus, Near PM Room, Hospital Chowk, Rajkot',
        "phone": '9925152595', "email": 'oscrajkotjaygurudevtrust@gmail.c om',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'rajnandgaon': {
        "district": 'Rajnandgaon', "state": 'Chhattisgarh',
        "address": 'One Stop Centre, Baldev Baag, Behind Dainik Dava office, Rajnandgaon District,Chhattisgarh',
        "phone": '07744-401406', "email": 'sakhirjn@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'rajouri': {
        "district": 'Rajouri', "state": 'Jammu & Kashmir',
        "address": 'One Stop Centre, ITI Road, near Animal Husbandry Building, Jammu and Kashmir-185151',
        "phone": '01962260140', "email": 'oscrajouri@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'rajsamand': {
        "district": 'Rajsamand', "state": 'Rajasthan',
        "address": 'State R.K. Hospital , Rajsamand City, Rajsamand District, Rajasthan',
        "phone": '9983987188', "email": 'drajsamand.wcd@rajasthan.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'ramanathapuram': {
        "district": 'Ramanathapuram', "state": 'Tamil Nadu',
        "address": 'General Government Hospital, Ramanathapuram',
        "phone": '9944362439', "email": 'srcwtamilnadu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'ramgarh': {
        "district": 'Ramgarh', "state": 'Jharkhand',
        "address": 'Tyre More, Panchayat Murum Kala, Ramgarh',
        "phone": '87890051627', "email": 'awc24.monitoring@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'ramnagar': {
        "district": 'Ramnagar', "state": 'Karnataka',
        "address": 'District Hospital, Premises, Ramnagar',
        "phone": '080-27274358', "email": 'adww.dwcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'rampur': {
        "district": 'Rampur', "state": 'Uttar Pradesh',
        "address": 'District Hopsital Bhgwal Rampur- 244901',
        "phone": '7235008659', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'ranchi': {
        "district": 'Ranchi', "state": 'Jharkhand',
        "address": 'One Stop Centre, Ranchi Institute of Neuro-Psychiatry and Allied Sciences (RINPAS), Kanke District, Ranchi , Jharkhand- 834006',
        "phone": '0651-2451911', "email": 'oscsakhirinpas@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'ratlam': {
        "district": 'Ratlam', "state": 'Madhya Pradesh',
        "address": 'One Stop Centre, Solanki Niwas, 151/1 GroundFloor,Marimata Chauraha, HaatkiChowki, Ratlam, Ratlam District, Madhya Pradesh',
        "phone": '992575', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'ratnagiri': {
        "district": 'Ratnagiri', "state": 'Maharashtra',
        "address": 'Civil Hospital Ratnagiri-415612',
        "phone": '02352-220461', "email": 'rtg_dwcdor@rediffmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'rewa': {
        "district": 'Rewa', "state": 'Madhya Pradesh',
        "address": 'One Stop Centre, H.No.12/652,Bajrang Nagar, Rewa, Rewa District, Madhya Pradesh',
        "phone": '9407820408', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'rewari': {
        "district": 'Rewari', "state": 'Haryana',
        "address": 'One Stop Centre, First Floor in the Trauma Centre General Hospital, Rewari District, Haryana-123401',
        "phone": '9996565104', "email": 'porewari.wcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'ri-bhoi': {
        "district": 'Ri-Bhoi', "state": 'Meghalaya',
        "address": 'One Stop Centre, Nongpoh, Ri- Bhoi, District, Meghalaya- 793102',
        "phone": '9366069211', "email": 'dsworbd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'rohtak': {
        "district": 'Rohtak', "state": 'Haryana',
        "address": 'Mahila Aashram,Gandhi camp,Rohtak.',
        "phone": '9812612047', "email": 'oscrohtak21@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'rohtas': {
        "district": 'Rohtas', "state": 'Bihar',
        "address": 'Women Helpline-cum-One Stop Centre Ground Floor, Vikas Bhawan Collectorate Campus, Rohtas-821115',
        "phone": '9771468026', "email": 'whl.aurnagabad@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'roop nagar': {
        "district": 'Roop Nagar', "state": 'Punjab',
        "address": 'Civil Hospital, Roop nagar',
        "phone": '98556-51185', "email": 'srcwpunjab@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    's.a.s nagar (mohali)': {
        "district": 'S.A.S Nagar (Mohali)', "state": 'Punjab',
        "address": 'Near Janoshdhi Kendra, Civil Hospital, Phase-6, Mohali.',
        "phone": '99144-00406', "email": 'osc.sasnagar@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sabarkantha': {
        "district": 'Sabarkantha', "state": 'Gujarat',
        "address": 'One Stop Center-Sakhi, 3rd Floor, GMERS General Hospital, Near Polytechnic College, Gadhoda Road, Motipura, Himmatnagar, Sabarkantha',
        "phone": '9408004091', "email": 'oscgmershimmatnagar@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sagar': {
        "district": 'Sagar', "state": 'Madhya Pradesh',
        "address": 'One Stop Centre, Near Art & Commerce College,Tilli Road, Sagar,SagarDistrict,Madhya Pradesh',
        "phone": '7582237517', "email": 'sagarosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sahajahanpur': {
        "district": 'Sahajahanpur', "state": 'Uttar Pradesh',
        "address": 'One Stop Centre, Women Hospital Complex, Shahjahanpur District, Uttar Pradesh',
        "phone": '8960639313', "email": 'districtprobationoffice@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'saharanpur': {
        "district": 'Saharanpur', "state": 'Uttar Pradesh',
        "address": 'Baal Kalyan Piduman Nagar Near Jain Degree Collge,Saharanpur- 247001',
        "phone": '7235008660', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'saharsa': {
        "district": 'Saharsa', "state": 'Bihar',
        "address": 'Women Helpline-cum-One Stop Centre Collectorate campus, Saharsa-852201',
        "phone": '9771468027', "email": 'whl.aurnagabad@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sahebganj': {
        "district": 'Sahebganj', "state": 'Jharkhand',
        "address": 'Sakhi- One Stop Center, ANM Training Center, 1 Floor, Sahebganj Sadar Hospital-816109',
        "phone": '8986906157', "email": 'awc18.monitoring@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'salem': {
        "district": 'Salem', "state": 'Tamil Nadu',
        "address": 'Primary Health Center Anna Hospital, Ammapettai, Salem – 636003',
        "phone": '2260267', "email": 'osctnsalem@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sambhal': {
        "district": 'Sambhal', "state": 'Uttar Pradesh',
        "address": 'District Probation Office Pabasa Sambhal-244302',
        "phone": '7235008661', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sambhalpur': {
        "district": 'Sambhalpur', "state": 'Odisha',
        "address": 'One Stop Centre, District Headquarter Hospital, Modipada, Sambhalpur-768004',
        "phone": '7008477474', "email": 'onestopcentresbp@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'samstipur': {
        "district": 'Samstipur', "state": 'Bihar',
        "address": 'Women Helpline, Ist Floor, Vikas Bhawan, Collectorate Campus, Samstipur-848101',
        "phone": '9771468028', "email": 'whl.samastipur@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sangli': {
        "district": 'Sangli', "state": 'Maharashtra',
        "address": 'Sakhi one stop centre Sangli, Bhagini Nivedita pratishthan Vijaydurg, Rajwada Chowk, Sangli- 416416',
        "phone": '9403782309', "email": 'oscsangli@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sangrur': {
        "district": 'Sangrur', "state": 'Punjab',
        "address": 'One Stop Crisis Center, 2nd Floor Opposite to Medical Ward, Civil Hospital, Sangrur, Punjab.',
        "phone": '9501087589', "email": 'oscsangrur@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sant kabir nagar': {
        "district": 'Sant Kabir Nagar', "state": 'Uttar Pradesh',
        "address": 'Bargo District Probation Office Khalilabad Sant Kabir Nagar- 272175',
        "phone": '7235008662', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'saran': {
        "district": 'Saran', "state": 'Bihar',
        "address": 'Collectorate, Saran,Chapra- 841301,Bihar',
        "phone": '9774168029', "email": 'support@wcdbihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sareikela- kharsawan': {
        "district": 'Sareikela- Kharsawan', "state": 'Jharkhand',
        "address": 'ANM Training Center (Civil Surgeon Office) Sareikela',
        "phone": '9431906959', "email": 'awc11.monitoring@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sarguja (ambikapur)': {
        "district": 'Sarguja (Ambikapur)', "state": 'Chhattisgarh',
        "address": 'Jila Chikitsalay Mahila Ward Parisar, Darripara Near sunita sonography, District surguja, Chhattisgarh',
        "phone": '07774-224781', "email": 'sakhisarguja@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'satara': {
        "district": 'Satara', "state": 'Maharashtra',
        "address": 'One Stop Centre, Government Men’s Beggar Home, Satara District, Maharashtra',
        "phone": '02141-228560', "email": 'dwcdosc.satara@gmail.com, oscsatara@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'satna': {
        "district": 'Satna', "state": 'Madhya Pradesh',
        "address": 'One Stop Centre, Near KanyaDdhavari School, Satna District, Madhya Pradesh',
        "phone": '7672222611', "email": 'satnaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sbs nagar': {
        "district": 'SBS Nagar', "state": 'Punjab',
        "address": 'One Stop Centre, Near Civil Hospital,Nawashehar Chandigarh Road, SBS Nagar, Punjab',
        "phone": '01823-298322', "email": 'oscsbsnagar@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sehore': {
        "district": 'Sehore', "state": 'Madhya Pradesh',
        "address": 'Near EnglishpuraMonalisa School, above Vandana Offset, Ward Number-8, 466001',
        "phone": '630881728', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sepahijala': {
        "district": 'Sepahijala', "state": 'Tripura',
        "address": 'One Stop Centre, Bishalgarh Sub Divisional Hospital, Bishalgarh- 799102',
        "phone": '8787796414', "email": 'tripuracommissionforwomen@gm ail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'shadhol': {
        "district": 'Shadhol', "state": 'Madhya Pradesh',
        "address": 'One Stop Centre, Ward No.14 Banganaga Bypass Road, Near Sai Gurukul, Child Protection Bhawan School, Shahdol District, Madhya Pradesh',
        "phone": '7652242870', "email": 'shadholosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'shajapur': {
        "district": 'Shajapur', "state": 'Madhya Pradesh',
        "address": 'Gas Godown Road, Ward No.-3, Shajapur',
        "phone": '9981988162', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'shamli': {
        "district": 'Shamli', "state": 'Uttar Pradesh',
        "address": 'District Probation Office Room No 10 Shamli-247776',
        "phone": '7235008665', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sheikhpura': {
        "district": 'Sheikhpura', "state": 'Bihar',
        "address": 'Women Helpline, Near-Jubinile Justice Court, Old Sub-Division Office, Sheikhpura-811105',
        "phone": '771468032', "email": 'whl.aurnagabad@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sheohar': {
        "district": 'Sheohar', "state": 'Bihar',
        "address": 'Women Help Line,Kishan Bhawan, Near- District Public Grievance Office, Collectoarate Campus, Sheohar- 843329',
        "phone": '9771468033', "email": 'whl.aurnagabad@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sheopur': {
        "district": 'Sheopur', "state": 'Madhya Pradesh',
        "address": 'District Hospital premises, 1st Floor, Shivpuri Road',
        "phone": '9977641311', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'shimla': {
        "district": 'Shimla', "state": 'Himachal Pradesh',
        "address": 'One Stop Centre, C/O Nari Sewa Sadan, Mashobra, PO Mashobra, District Shimla-171007',
        "phone": '0177-2740168', "email": 'dcpushimla@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'shimoga': {
        "district": 'Shimoga', "state": 'Karnataka',
        "address": 'District Hospital Premises, Shimoga',
        "phone": '08182-223055', "email": 'adww.dwcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'shivni': {
        "district": 'Shivni', "state": 'Madhya Pradesh',
        "address": 'Rain BaseraBhawan, District Hospital Premises, Barapathar, Seoni',
        "phone": '9407850004', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'shivpuri': {
        "district": 'Shivpuri', "state": 'Madhya Pradesh',
        "address": 'Anganwadi Training Centre, New Block, Nearby HanshBhavan, Shivpuri',
        "phone": '492221202', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'shrawasti': {
        "district": 'Shrawasti', "state": 'Uttar Pradesh',
        "address": 'New District Hospital Bahriach Road Shrwasti-271831',
        "phone": '7235008667', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'shri muktsar sahib': {
        "district": 'Shri Muktsar Sahib', "state": 'Punjab',
        "address": 'One Stop Centre, Civil Hospital, Room No. 105, Sri Muktsar Sahib, Sri Muktsar Sahib District, Punjab- 152026',
        "phone": '9814041223', "email": 'dpomuktsar@yahoo.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'siddharth nagar': {
        "district": 'Siddharth Nagar', "state": 'Uttar Pradesh',
        "address": 'District Probation Officer Collectorate Office Naugarh Siddharth Nagar -2772207',
        "phone": '7235008669', "email": 'Dposdr15@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sidhi': {
        "district": 'Sidhi', "state": 'Madhya Pradesh',
        "address": 'Near Collectorate Premises, Sidhi- 486661',
        "phone": '7822251144', "email": 'sidhiosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sikar': {
        "district": 'Sikar', "state": 'Rajasthan',
        "address": 'Todi Vishram Grah Govt. S.K. Hospital,Sikar.',
        "phone": '9587262157', "email": 'powedwda@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'simdega': {
        "district": 'Simdega', "state": 'Jharkhand',
        "address": 'Civil Surgeon Office, Sadar Hospital, Simdega, Pincode- 835223',
        "phone": '9835751065', "email": 'awc5.monitoring@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sindhudurg': {
        "district": 'Sindhudurg', "state": 'Maharashtra',
        "address": 'District Civil surgeon Hospital, Sindhudurg, Pin Code-416812',
        "phone": '9921756172', "email": 'oscsindhudurg@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'singrauli': {
        "district": 'Singrauli', "state": 'Madhya Pradesh',
        "address": 'One Stop Centre, A.N.M. Training Centre, Near C.M.H.O. Office, N.C.L. Ground, Behind ZilaPanchayat, Baidhan, SingrauliDistrict,Madhya Pradesh- 486886',
        "phone": '7805297408', "email": 'singrauliosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sirmour': {
        "district": 'Sirmour', "state": 'Himachal Pradesh',
        "address": 'DIET Hostel Building, Housing Board Colony,Tehsil Nahan, District Sirmour- 173001',
        "phone": '1702-225607', "email": 'dpossirmour@gmail.com, dcpusirmour123@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sirsa': {
        "district": 'Sirsa', "state": 'Haryana',
        "address": 'Rajkiye Bahutakniki mahavidyalya, sirsa Quarter no.B- 5.',
        "phone": '9416725599', "email": 'Posrs.wcd@gmail.com Rajeshswami1781@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sitamarhi': {
        "district": 'Sitamarhi', "state": 'Bihar',
        "address": 'Women Helpline,Collectorate',
        "phone": '9771468030', "email": 'whl.aurnagabad@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sitapur': {
        "district": 'Sitapur', "state": 'Uttar Pradesh',
        "address": 'Collectrate Campus Infront District Probation Office Lalbagh Chauraha Sitapur-261001',
        "phone": '7235008670', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sivagangai': {
        "district": 'Sivagangai', "state": 'Tamil Nadu',
        "address": 'Government Service Home – Sivagangai',
        "phone": '9842142388', "email": 'srcwtamilnadu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sivasagar': {
        "district": 'Sivasagar', "state": 'Assam',
        "address": 'Sakhi One Stop Centre, Kumudalaya, Sundrapur , Jaysagar , PO & Dist, Sivasagar -785640',
        "phone": '8638596726', "email": 'dswosiv2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'siwan': {
        "district": 'Siwan', "state": 'Bihar',
        "address": 'Women Helpline Red Cross Building, Near-District Hospital. Siwan- 841226',
        "phone": '9771468031', "email": 'whl.aurnagabad@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'solan': {
        "district": 'Solan', "state": 'Himachal Pradesh',
        "address": 'One Stop Centre , Red Cross Building, Zonal Hospital, Solan- 173212, Himachal Pradesh',
        "phone": '01792-220181', "email": 'neelam_mehta@emri.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'solapur': {
        "district": 'Solapur', "state": 'Maharashtra',
        "address": 'One Stop Centre, Maji Sainik Nagar, Vijapur Road, Solapur- 413004',
        "phone": '9822402860', "email": 'oscsolapur@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sonbhadra': {
        "district": 'Sonbhadra', "state": 'Uttar Pradesh',
        "address": 'District Hospital Lodi near DM office- 231216',
        "phone": '7235008671', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sonitpur': {
        "district": 'Sonitpur', "state": 'Assam',
        "address": 'Sakhi One Stop Centre, Eight Brothers Social Welfare Society Murha Teteli , Near Rupom Petrol Pump, P.O. Tezpur - 784001Dist, Sonitpur',
        "phone": '8876607561', "email": 'dswoson2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'south andaman': {
        "district": 'South Andaman', "state": 'Andaman and Nicobar Islands (UT)',
        "address": 'One Stop Centre, JG 6-Type, V Quarter, Near Ayush, (Govt.) Hospital, Junglighat, Port Blair, South Andaman District, Andaman & Nicobar Islands',
        "phone": '0319-2230504', "email": 'sakhiandaman@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'south garo hills': {
        "district": 'South Garo Hills', "state": 'Meghalaya',
        "address": 'One Stop Centre, C/O D.S.W.O, Baghmara, Bolsal Ading, South Garo Hills, Baghmara-794102',
        "phone": '9402197203', "email": 'dswobagmara@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'south salmara mancachar': {
        "district": 'South Salmara Mancachar', "state": 'Assam',
        "address": 'Sakhi One Stop Centre , P.O. Hatsingimari , Dist. South Salmara Mancachar',
        "phone": '9435103196', "email": 'dswodhu2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'south west garo hills': {
        "district": 'South West Garo Hills', "state": 'Meghalaya',
        "address": 'One Stop Centre, District Social Welfare Officer, South West Garo Hills- 794115',
        "phone": '9862264575', "email": 'dswo.swgh2013@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'south west khasi hills': {
        "district": 'South West Khasi Hills', "state": 'Meghalaya',
        "address": 'One Stop Centre, Mawkyrwat- 793114',
        "phone": '9863113588', "email": 'dswomwt@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'srikakulam': {
        "district": 'Srikakulam', "state": 'Andhra Pradesh',
        "address": 'One Stop Centre, RIMS-General Hospital, Balaga, Srikakulam City, Srikakulam District, Andhra Pradesh-532001',
        "phone": '9110793708', "email": 'apsrcw@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'srinagar': {
        "district": 'Srinagar', "state": 'Jammu & Kashmir',
        "address": 'Sakhi Centre Srinagar,,Opposite New Era School, Rajbagh, Srinagar- 190008',
        "phone": '89622272', "email": 'sakhisrinagar@181jandk.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sukuma': {
        "district": 'Sukuma', "state": 'Chhattisgarh',
        "address": 'One Stop Centre, Mini Ground Inside old, Hospital campus, Sukuma, District, Chhattisgarh',
        "phone": '7646810651', "email": 'sakhisukma2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sultanpur': {
        "district": 'Sultanpur', "state": 'Uttar Pradesh',
        "address": 'Rto Office Amhad Chauraha, Sultanpur-22801',
        "phone": '7235008672', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'sundergarh': {
        "district": 'Sundergarh', "state": 'Odisha',
        "address": 'Rourkela Government Hospital(RGH), Rourkela, 1st Floor, Indoor Patient Ward',
        "phone": '9348291721', "email": 'onestopcentrerourkela@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'supaul': {
        "district": 'Supaul', "state": 'Bihar',
        "address": 'Women Helpline, District Women Empowerment Office, TCP Bhawan, Infront of Collectorate Campus, Supaul-',
        "phone": '9771468034', "email": 'whl.aurnagabad@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'surajpur': {
        "district": 'Surajpur', "state": 'Chhattisgarh',
        "address": 'Old Livelihood College,Opposite Shiv Park, Surajpur, Surajpur District, Chhattisgarh',
        "phone": '07775-266652', "email": 'raipursakhi@181chhattisgarh.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'surat': {
        "district": 'Surat', "state": 'Gujarat',
        "address": 'One Stop Center-Sakhi 1st Floor, Near Trauma center, Civil Hospital Campus, Majura gate, Surat',
        "phone": '9723875118', "email": 'info@grcgujarat.org',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'surendranagar': {
        "district": 'Surendranagar', "state": 'Gujarat',
        "address": 'One Stop Center-Sakhi General Hospital (Gandhi) Surendranagar',
        "phone": '9099322322', "email": 'info@grcgujarat.org',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'tapi': {
        "district": 'Tapi', "state": 'Gujarat',
        "address": 'One Stop Center-Sakhi General Hospital Campus, Near Main Building, Vyara, Tapi',
        "phone": '9998830400', "email": 'info@grcgujarat.org',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'tarntaran': {
        "district": 'Tarntaran', "state": 'Punjab',
        "address": 'Rajesh Kumar, District Child Protection Officer, Room No. 318, 3rd Floor, District Administration Complex, Tarn Taran, 143401, Punjab.',
        "phone": '73037433144', "email": 'dcpotarntaran@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'tawang': {
        "district": 'Tawang', "state": 'Arunachal Pradesh',
        "address": 'One Stop Centre, DFDO Quarter, Craft Centre Colony, Near District Hospital, Tawang-790104',
        "phone": '9862110421', "email": 'onestopcentre3@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'thane': {
        "district": 'Thane', "state": 'Maharashtra',
        "address": 'Chatrapati Shivaji Maharaj Hospital Kalwa (W),Thane-400605',
        "phone": '7977386300', "email": 'dwcdothane@yahoo.co.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'thanjavur': {
        "district": 'Thanjavur', "state": 'Tamil Nadu',
        "address": 'Old District Social Welfare Office, Thanjavur',
        "phone": '9042541930', "email": 'srcwtamilnadu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'theni': {
        "district": 'Theni', "state": 'Tamil Nadu',
        "address": 'Sentech Family Counselling Centre, Theni',
        "phone": '9585225858', "email": 'srcwtamilnadu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'thirunelveli': {
        "district": 'Thirunelveli', "state": 'Tamil Nadu',
        "address": 'Sondam Rehabilitation Centre – Maharajanagar, Tirunelveli',
        "phone": '9894743497', "email": 'srcwtamilnadu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'thiruvallur': {
        "district": 'Thiruvallur', "state": 'Tamil Nadu',
        "address": 'JD office Dept of Animal Husbandry Tiruvallur',
        "phone": '9677866219', "email": 'srcwtamilnadu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'thiruvananthapuram': {
        "district": 'Thiruvananthapuram', "state": 'Kerala',
        "address": 'One Stop Centre, Nirbhaya Cell Office, House-40,First Floor, Chabakanagar, Bakery Junction, Thiruvananthapuram District, Kerala- 695001',
        "phone": '4712324699', "email": 'sakhitvmosc@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'thiruvannamalai': {
        "district": 'Thiruvannamalai', "state": 'Tamil Nadu',
        "address": 'Survey no 159 /12-0.20 Acres Survey any 159/3. 0.720 Hectares at Vengaikkal, Thiruvannamalai',
        "phone": '041765-298033', "email": 'srcwtamilnadu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'thoothukudi': {
        "district": 'Thoothukudi', "state": 'Tamil Nadu',
        "address": 'Empower Short Stay Home A Graind Nagar – West Tuticorin, Thoothukudi',
        "phone": '9942230665', "email": 'srcwtamilnadu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'thoubal': {
        "district": 'Thoubal', "state": 'Manipur',
        "address": 'One Stop Centre, Thoubal Mini Secretariat Complex, Thoubal, Thoubal District, Manipur',
        "phone": '0385-2450513', "email": 'wcdprog@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'thrissur': {
        "district": 'Thrissur', "state": 'Kerala',
        "address": 'One Stop Center, Near Laboratory, General Hospital Campus,Irijalakuda, Thrissur: 680- 121',
        "phone": '9061157676', "email": 'oscirinjalakuda@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'tikamgarh': {
        "district": 'Tikamgarh', "state": 'Madhya Pradesh',
        "address": 'Second Floor, Nurtitional Rehabilitation centre, Rajendra Hospital, Jhansi Road, Tikamgarh',
        "phone": '7683242960', "email": 'tikamgarhosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'tinsukia': {
        "district": 'Tinsukia', "state": 'Assam',
        "address": 'One Stop Centre, Tinsukia, Nera Tinsukia Civil Hospital , Bardoloi Nagar P.O. & Dist Tinsukia-786125',
        "phone": '9435134559', "email": 'dswotin2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'tirap': {
        "district": 'Tirap', "state": 'Arunachal Pradesh',
        "address": 'One Stop Centre, Khonsa, Tirap, Arunachal Pradesh',
        "phone": '8974818624', "email": 'onestopcentre3@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'tiruchirapally': {
        "district": 'Tiruchirapally', "state": 'Tamil Nadu',
        "address": 'One Stop Centre, District Social Welfare Office, Collectorate Old Building, Trichy-620001',
        "phone": '4312413796', "email": 'trichyosc@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'tiruppur': {
        "district": 'Tiruppur', "state": 'Tamil Nadu',
        "address": 'Mariyalaya –8/1E/122, Kasthuri Bai Street Anna Nagar Ammapalayam, Tirupur',
        "phone": '9080126133', "email": 'srcwtamilnadu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'tiruvarur': {
        "district": 'Tiruvarur', "state": 'Tamil Nadu',
        "address": 'Karunalya Short Stay Home, Durgalaiya Road, Tiruvarur',
        "phone": '8825669037', "email": 'srcwtamilnadu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'tonk': {
        "district": 'Tonk', "state": 'Rajasthan',
        "address": 'Mother and Child Health Center, Tonk City, Tonk District, Rajasthan',
        "phone": '9828141425', "email": 'powetonk@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'tuensang': {
        "district": 'Tuensang', "state": 'Nagaland',
        "address": 'Sakhi-One Stop Centre Near District Transport office, Tuensang, Nagaland –798612',
        "phone": '7005773679', "email": 'tuensang.sakhiosc@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'tumkur': {
        "district": 'Tumkur', "state": 'Karnataka',
        "address": 'One Stop Center (Mahlila Chikitsa Ghtataka)1st floor District Hospital,',
        "phone": '0821-2429186', "email": 'adww.dwcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'udalguri': {
        "district": 'Udalguri', "state": 'Assam',
        "address": 'Sakhi One Stop Centre, Barna Gaon, P.O. & Dist. Udalguri',
        "phone": '9435543890', "email": 'dswouda2017@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'udham singh nagar': {
        "district": 'Udham Singh Nagar', "state": 'Uttarakhand',
        "address": 'One Stop Centre, Near G.G.I.C.,Fazalpur, Mehraulla, Rudarpur-263153, Udham Singh Nagar, Uttarakhand',
        "phone": '05944-240426', "email": 'oscusnagar@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'udupi': {
        "district": 'Udupi', "state": 'Karnataka',
        "address": 'One Stop Centre, StreeSevaniketana District Hospital premises, Udupi, Udupi District, Karnataka',
        "phone": '080-22353992', "email": 'deputysecretary123@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'ujjain': {
        "district": 'Ujjain', "state": 'Madhya Pradesh',
        "address": 'One Stop Centre, Madhav Nagar Hospital, Free Ganj, Ujjain District, Madhya Pradesh',
        "phone": '9926017866', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'umaria': {
        "district": 'Umaria', "state": 'Madhya Pradesh',
        "address": 'District Administrative Hospital, in front of Trauma Centre',
        "phone": '765300000', "email": 'umariaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'unnao': {
        "district": 'Unnao', "state": 'Uttar Pradesh',
        "address": 'District Hopsital Rain Baresra Unnao 209801.',
        "phone": '7235008673', "email": 'aapkisakhiajkhq@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'uttara kannada': {
        "district": 'Uttara Kannada', "state": 'Karnataka',
        "address": 'District Government Hospital Premises,Uttara Kannada , Karwar',
        "phone": '8382226768', "email": 'adww.dwcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'vaishali': {
        "district": 'Vaishali', "state": 'Bihar',
        "address": 'Women Helpline S.D.O.Office, Hajipur, 2nd floor, collectorate Campus, Vaishali-844101',
        "phone": '9771468035', "email": 'whl.aurnagabad@wdc.bihar.org.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'valsad': {
        "district": 'Valsad', "state": 'Gujarat',
        "address": 'One Stop Centre-Sakhi GMERS General Hospital, Civil Hospital Campus, Block No. 2, Nanakvada Road, Valsad-395001',
        "phone": '8141522999', "email": 'onestopcentre.valsad@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'varanasi': {
        "district": 'Varanasi', "state": 'Uttar Pradesh',
        "address": 'One Stop Centre, PanditDeenDayal Hospital Near MahaveerMandir, Varanasi, District Uttar Pradesh',
        "phone": '7235004581', "email": 'dpovaranasi1@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'vellore': {
        "district": 'Vellore', "state": 'Tamil Nadu',
        "address": 'Old Government Hospital, Anna Salai, Vellore',
        "phone": '7871210826', "email": 'srcwtamilnadu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'vidisha': {
        "district": 'Vidisha', "state": 'Madhya Pradesh',
        "address": 'Police Station Premises, District Vidisha',
        "phone": '7592490615', "email": 'datiaosc.wcd@mp.gov.in',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'vijayapur': {
        "district": 'Vijayapur', "state": 'Karnataka',
        "address": 'District Government Hospital premises, Vijayapur',
        "phone": '08352-270173', "email": 'adww.dwcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'villupuram': {
        "district": 'Villupuram', "state": 'Tamil Nadu',
        "address": 'Collectorate Campus',
        "phone": '9843806126', "email": 'srcwtamilnadu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'virudhunagar': {
        "district": 'Virudhunagar', "state": 'Tamil Nadu',
        "address": 'Government Childrens Home - Virudhunagar',
        "phone": '6380272960', "email": 'srcwtamilnadu@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'visakhapatnam': {
        "district": 'Visakhapatnam', "state": 'Andhra Pradesh',
        "address": 'One Stop Centre, King George Hospital, Maternity Hospital, Ground Floor, Near Collector Hospital, Vishakapatnam City, Vishakapatnam District, Andhra Pradesh',
        "phone": '040-6281641', "email": 'apsrcw@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'vizianagaram': {
        "district": 'Vizianagaram', "state": 'Andhra Pradesh',
        "address": 'One Stop Centre, The Protection Officer PWDV Act-2005 Cell, Near 29th Ward, Maharaja District Govt. Hospital, Vizianagaram District, Andhra Pradesh- 535003',
        "phone": '08922-277986', "email": 'apsrcw@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'warangal urban': {
        "district": 'Warangal Urban', "state": 'Telangana',
        "address": '2-7-66, Excise Colony, Hanamkonda, Warangal – 506001, Telangana',
        "phone": '08702-452112', "email": 'syosakhi@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'wardha': {
        "district": 'Wardha', "state": 'Maharashtra',
        "address": 'Civil Hospital, Sewagram Road, Wardha- 442001',
        "phone": '07152-242281', "email": 'dwcdowardha@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'washim': {
        "district": 'Washim', "state": 'Maharashtra',
        "address": 'Secura Hospital Malegaon Road, Washim-444505',
        "phone": '07252-234280', "email": 'oscwashim@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'waynad': {
        "district": 'Waynad', "state": 'Kerala',
        "address": 'Sakhi One Stop Centre, Kalpetta Waynad, Kerala',
        "phone": '4936202120', "email": 'oscwaynad@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'west garo hills': {
        "district": 'West Garo Hills', "state": 'Meghalaya',
        "address": 'One Stop Centre, TE- Tengkol, Hawakhana, Tura, West Garo Hills, Meghalaya-794001',
        "phone": '9615456188', "email": 'oscctrura@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'west godavari': {
        "district": 'West Godavari', "state": 'Andhra Pradesh',
        "address": 'One Stop Centre, Beside Satya Saibaba Trust,Govt Hospital, Eluru, West Godavari -534006',
        "phone": '08812-222621', "email": 'sakhiwg@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'west jaintia hills': {
        "district": 'West Jaintia Hills', "state": 'Meghalaya',
        "address": 'One Stop Centre, West Jaintia Hills, District-Jowai-793150, Tpeppale, Meghalaya',
        "phone": '9612942072', "email": 'dswo@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'west khasi hills': {
        "district": 'West Khasi Hills', "state": 'Meghalaya',
        "address": 'Civil Hospital, Nongstoin, Mawiaban-793119',
        "phone": '9862580535', "email": 'oscwkhng@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'west tripura': {
        "district": 'West Tripura', "state": 'Tripura',
        "address": 'One Stop Centre, Office of Tripura Commission for Women, HGB Road, Melarmath, Agartala, West Tripura District, Tripura',
        "phone": '9774499381', "email": 'tripuracommissionforwomen@gm ail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'wokha': {
        "district": 'Wokha', "state": 'Nagaland',
        "address": 'Sakhi-One Stop Centre Opposite DC office Wokha. Nagaland - 797111',
        "phone": '7085479403', "email": 'wokha.sakhiosc@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'yadagiri': {
        "district": 'Yadagiri', "state": 'Karnataka',
        "address": 'District Government Hospital Premises, Yadagiri',
        "phone": '08473-253886', "email": 'adww.dwcd@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'yavatmal': {
        "district": 'Yavatmal', "state": 'Maharashtra',
        "address": 'Vasantrao Naik Shaskiya Mahavidyalaya, Vaidyakiya Mahavidyalaya Ward No.3 Yawantmal.',
        "phone": '7972910488', "email": 'oscyavatmal@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

    'zunheboto': {
        "district": 'Zunheboto', "state": 'Nagaland',
        "address": 'Sakhi-One Stop Centre Project Colony Near DC office Opposite labour office Zunheboto, Nagaland- 798620',
        "phone": '6009165552', "email": 'zunheboto.sakhiosc@gmail.com',
        "contact_person": None, "contact_person_phone": None,
        "verification": 'parsed',
    },

}

# Merge order matters: NATIONAL_DISTRICTS (parsed) is the base layer;
# TELANGANA_DISTRICTS and OTHER_STATE_DISTRICTS (manual) are layered
# on top so a hand-verified entry always wins over a machine-parsed
# one for the same district name -- see module docstring.
DISTRICT_CONTACTS = {**NATIONAL_DISTRICTS, **OTHER_STATE_DISTRICTS, **TELANGANA_DISTRICTS}
