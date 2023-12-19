import requests
from fhirpathpy import evaluate
from datetime import datetime


def separate_data(bundleid, patientIdentifier):
    x = requests.get("https://fosps.gravitatehealth.eu/epi/api/fhir/Bundle/" + bundleid)
    raw_data = x.json()
    subject = raw_data["entry"][0]["resource"]["subject"][0]["reference"]
    # print(subject)
    preproc = requests.get(
        "https://fosps.gravitatehealth.eu/epi/api/fhir/Composition/?subject="
        + subject
        + "&category=http://hl7.eu/fhir/ig/gravitate-health/CodeSystem/epicategory-cs|P&_language=en"
    )
    ips_id_bundle = requests.get(
        "https://fosps.gravitatehealth.eu/ips/api/fhir/Composition?subject.identifier="
        + patientIdentifier
        + "&_elements=identifier,id"
    )
    print(ips_id_bundle.json())
    ips_id = ips_id_bundle.json()["entry"][0]["resource"]["id"]
    print(ips_id)
    ips = requests.get(
        "https://fosps.gravitatehealth.eu/ips/api/fhir/Composition/"
        + ips_id
        + "/$document"
    )
    return preproc.json(), ips.json()


def adult_lenses(preprocessed_bundle, ips):
    print(ips)
    result = evaluate(ips, "Bundle.entry.where(resource.resourceType=='Patient')", [])

    print(result)
    bd = result[0]["resource"]["birthDate"]
    print(bd)

    # Convert the string to a datetime object
    birth_date = datetime.strptime(bd, "%Y-%m-%d")

    # Get the current date
    current_date = datetime.now()

    # Calculate the age
    age = (
        current_date.year
        - birth_date.year
        - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))
    )
    if age > 18:
        print("Adult")
    # print(f"Age: {age} years")
    # age = ips["entry"][0]["resource"]["section"][0]["entry"][0]["resource"]
    return ""
