from services.ml_service import MLService

print('Testing Fixed Integration of Your 3 Models...')

ml_service = MLService()

test_project = {
    'projectType': 'Overhead Line',  # Valid category
    'state': 'Maharashtra',          # Valid category  
    'terrain': 'Plains',             # Valid category
    'baseCost': 150.0,
    'plannedTimeline': 24.0,
    'vendorReliability': 0.8,
    'materialAvailability': 0.8,
    'demandSupplyPressure': 'Medium' # Valid category instead of 0.5
}

print('Making prediction...')
predictions = ml_service.predict(test_project)

print('Results:')
for key, value in predictions.items():
    print(f'  {key}: {value}')

print('Done!')