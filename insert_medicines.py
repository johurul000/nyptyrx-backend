from inventory.models import CentralMedicine, MedicineCategory

# Get or create categories
painkiller_category = MedicineCategory.objects.get_or_create(name='Painkiller')[0]
antibiotic_category = MedicineCategory.objects.get_or_create(name='Antibiotic')[0]
diabetes_category = MedicineCategory.objects.get_or_create(name='Diabetes')[0]

# Create medicines
medicines = [
    {'name': 'Paracetamol', 'description': 'Used to treat pain and fever.', 'manufacturer': 'XYZ Pharmaceuticals', 'barcode': '123456789012', 'category': painkiller_category},
    {'name': 'Aspirin', 'description': 'Used as a pain reliever and anti-inflammatory.', 'manufacturer': 'ABC Corp', 'barcode': '234567890123', 'category': painkiller_category},
    {'name': 'Amoxicillin', 'description': 'An antibiotic used to treat bacterial infections.', 'manufacturer': 'MediHealth', 'barcode': '345678901234', 'category': antibiotic_category},
    {'name': 'Ibuprofen', 'description': 'Used to reduce fever, pain, and inflammation.', 'manufacturer': 'MediPharma', 'barcode': '456789012345', 'category': painkiller_category},
    {'name': 'Metformin', 'description': 'Used to treat type 2 diabetes.', 'manufacturer': 'HealthPlus', 'barcode': '567890123456', 'category': diabetes_category},
    {'name': 'Ciprofloxacin', 'description': 'An antibiotic used to treat infections.', 'manufacturer': 'MediPharma', 'barcode': '678901234567', 'category': antibiotic_category},
    {'name': 'Diclofenac', 'description': 'Used to treat pain and inflammation.', 'manufacturer': 'PharmaTech', 'barcode': '789012345678', 'category': painkiller_category},
    {'name': 'Azithromycin', 'description': 'An antibiotic used to treat various infections.', 'manufacturer': 'MediHealth', 'barcode': '890123456789', 'category': antibiotic_category},
    {'name': 'Insulin', 'description': 'Used to control blood sugar levels.', 'manufacturer': 'HealthPlus', 'barcode': '901234567890', 'category': diabetes_category},
    {'name': 'Hydroxychloroquine', 'description': 'Used to treat malaria and autoimmune diseases.', 'manufacturer': 'PharmaCare', 'barcode': '112345678901', 'category': antibiotic_category},
    {'name': 'Glibenclamide', 'description': 'Used to manage type 2 diabetes.', 'manufacturer': 'MediTech', 'barcode': '223456789012', 'category': diabetes_category},
    {'name': 'Ranitidine', 'description': 'Used to treat acid reflux and ulcers.', 'manufacturer': 'AcidRelief Co.', 'barcode': '334567890123', 'category': painkiller_category},
    {'name': 'Lisinopril', 'description': 'Used to treat high blood pressure.', 'manufacturer': 'HeartHealth', 'barcode': '445678901234', 'category': painkiller_category},
    {'name': 'Clopidogrel', 'description': 'Used to prevent blood clots.', 'manufacturer': 'VascularLife', 'barcode': '556789012345', 'category': painkiller_category},
    {'name': 'Levothyroxine', 'description': 'Used to treat hypothyroidism.', 'manufacturer': 'ThyroMed', 'barcode': '667890123456', 'category': diabetes_category},
    {'name': 'Prednisone', 'description': 'Used to reduce inflammation.', 'manufacturer': 'SteroidMeds', 'barcode': '778901234567', 'category': painkiller_category},
    {'name': 'Warfarin', 'description': 'Used to prevent blood clots.', 'manufacturer': 'AntiCoag Co.', 'barcode': '889012345678', 'category': painkiller_category},
    {'name': 'Fluconazole', 'description': 'Used to treat fungal infections.', 'manufacturer': 'FungiCare', 'barcode': '990123456789', 'category': antibiotic_category},
    {'name': 'Naproxen', 'description': 'Used to reduce pain and inflammation.', 'manufacturer': 'PainEase', 'barcode': '101234567890', 'category': painkiller_category},
    {'name': 'Sitagliptin', 'description': 'Used to treat type 2 diabetes.', 'manufacturer': 'GlucoHealth', 'barcode': '211234567890', 'category': diabetes_category},
    {'name': 'Rosuvastatin', 'description': 'Used to lower cholesterol.', 'manufacturer': 'CholCare', 'barcode': '321234567890', 'category': painkiller_category},
    {'name': 'Gabapentin', 'description': 'Used to treat nerve pain and seizures.', 'manufacturer': 'NeuroPharma', 'barcode': '431234567890', 'category': painkiller_category},
    {'name': 'Doxycycline', 'description': 'An antibiotic used for various infections.', 'manufacturer': 'BroadMeds', 'barcode': '541234567890', 'category': antibiotic_category},
    {'name': 'Tramadol', 'description': 'Used to treat moderate to severe pain.', 'manufacturer': 'PainRelief Inc.', 'barcode': '651234567890', 'category': painkiller_category},
    {'name': 'Amlodipine', 'description': 'Used to treat high blood pressure.', 'manufacturer': 'HeartCare', 'barcode': '761234567890', 'category': painkiller_category},
    {'name': 'Metronidazole', 'description': 'Used to treat infections caused by bacteria and parasites.', 'manufacturer': 'AntiBact Inc.', 'barcode': '871234567890', 'category': antibiotic_category},
    {'name': 'Sulfasalazine', 'description': 'Used to treat inflammatory bowel diseases.', 'manufacturer': 'GutRelief', 'barcode': '981234567890', 'category': antibiotic_category},
    {'name': 'Albuterol', 'description': 'Used to treat asthma and breathing disorders.', 'manufacturer': 'AirHealth', 'barcode': '192345678901', 'category': painkiller_category},
    {'name': 'Loratadine', 'description': 'Used to treat allergies.', 'manufacturer': 'AllergyCare', 'barcode': '293456789012', 'category': painkiller_category},
    {'name': 'Meloxicam', 'description': 'Used to treat arthritis and inflammation.', 'manufacturer': 'ArthCare', 'barcode': '394567890123', 'category': painkiller_category},
    {'name': 'Furosemide', 'description': 'Used to treat fluid retention.', 'manufacturer': 'FluidBalance Inc.', 'barcode': '495678901234', 'category': diabetes_category},
    {'name': 'Omeprazole', 'description': 'Used to treat acid reflux and ulcers.', 'manufacturer': 'StomachEase', 'barcode': '596789012345', 'category': painkiller_category},
    {'name': 'Ceftriaxone', 'description': 'An antibiotic used for severe infections.', 'manufacturer': 'StrongMeds', 'barcode': '697890123456', 'category': antibiotic_category},
    {'name': 'Candesartan', 'description': 'Used to treat high blood pressure.', 'manufacturer': 'BPBalance', 'barcode': '798901234567', 'category': painkiller_category},
    {'name': 'Allopurinol', 'description': 'Used to treat gout.', 'manufacturer': 'UricHealth', 'barcode': '899012345678', 'category': painkiller_category},
    {'name': 'Vildagliptin', 'description': 'Used to treat type 2 diabetes.', 'manufacturer': 'SugarControl', 'barcode': '911123456789', 'category': diabetes_category},
    {'name': 'Hydrochlorothiazide', 'description': 'Used to treat high blood pressure and fluid retention.', 'manufacturer': 'BPFluid Co.', 'barcode': '122234567890', 'category': diabetes_category},
    {'name': 'Ketorolac', 'description': 'Used for short-term pain management.', 'manufacturer': 'FastRelief', 'barcode': '233345678901', 'category': painkiller_category},
    {'name': 'Phenylephrine', 'description': 'Used as a decongestant.', 'manufacturer': 'NasalClear', 'barcode': '344456789012', 'category': painkiller_category},
    {'name': 'Levofloxacin', 'description': 'An antibiotic for severe bacterial infections.', 'manufacturer': 'BioMeds', 'barcode': '455567890123', 'category': antibiotic_category},
    {'name': 'Propranolol', 'description': 'Used to treat high blood pressure and anxiety.', 'manufacturer': 'BPRelax', 'barcode': '566678901234', 'category': painkiller_category},
    {'name': 'Terbinafine', 'description': 'Used to treat fungal infections.', 'manufacturer': 'AntiFungi Labs', 'barcode': '677789012345', 'category': antibiotic_category},
    {'name': 'Citalopram', 'description': 'Used to treat depression and anxiety.', 'manufacturer': 'MentalCare', 'barcode': '788890123456', 'category': painkiller_category},
    {'name': 'Carbamazepine', 'description': 'Used to treat epilepsy and nerve pain.', 'manufacturer': 'NeuroRelief', 'barcode': '899901234567', 'category': painkiller_category},
    {'name': 'Montelukast', 'description': 'Used to prevent asthma attacks.', 'manufacturer': 'BreathWell', 'barcode': '912012345678', 'category': painkiller_category},
    {'name': 'Esomeprazole', 'description': 'Used to reduce stomach acid.', 'manufacturer': 'AcidEase', 'barcode': '123102345678', 'category': painkiller_category},
    {'name': 'Rivaroxaban', 'description': 'Used to prevent blood clots.', 'manufacturer': 'CoagHealth', 'barcode': '234203456789', 'category': painkiller_category},
    {'name': 'Tamsulosin', 'description': 'Used to treat enlarged prostate.', 'manufacturer': 'ProstateCare', 'barcode': '345304567890', 'category': painkiller_category},
    {'name': 'Clarithromycin', 'description': 'An antibiotic used for respiratory infections.', 'manufacturer': 'RespiraMeds', 'barcode': '456405678901', 'category': antibiotic_category},
    {'name': 'Valacyclovir', 'description': 'Used to treat viral infections like herpes.', 'manufacturer': 'ViralEase', 'barcode': '567506789012', 'category': antibiotic_category},
    {'name': 'Bisoprolol', 'description': 'Used to treat high blood pressure.', 'manufacturer': 'HeartWell', 'barcode': '678607890123', 'category': painkiller_category},
    {'name': 'Aripiprazole', 'description': 'Used to treat mental health disorders.', 'manufacturer': 'MindBalance', 'barcode': '789708901234', 'category': painkiller_category},
    {'name': 'Moxifloxacin', 'description': 'An antibiotic for severe bacterial infections.', 'manufacturer': 'BioPharma', 'barcode': '890809012345', 'category': antibiotic_category}

]

for medicine_data in medicines:
    CentralMedicine.objects.create(
        name=medicine_data['name'],
        description=medicine_data['description'],
        manufacturer=medicine_data['manufacturer'],
        barcode=medicine_data['barcode'],
        category=medicine_data['category']
    )

print("Medicines have been inserted successfully!")