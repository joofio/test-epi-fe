import requests
from fhirpathpy import evaluate
from datetime import datetime
import json
import copy
import uuid


def separate_data(bundleid, patientIdentifier):
    x = requests.get("https://fosps.gravitatehealth.eu/epi/api/fhir/Bundle/" + bundleid)
    raw_data = x.json()
    subject = raw_data["entry"][0]["resource"]["subject"][0]["reference"]
    print(subject)
    preproc_ids = requests.get(
        "https://fosps.gravitatehealth.eu/epi/api/fhir/Composition?subject="
        + subject
        + "&category=http://hl7.eu/fhir/ig/gravitate-health/CodeSystem/epicategory-cs|P&_language=en"
    )
    lkid = preproc_ids.json()["entry"][0]["resource"]["id"]
    preproc_bundle = requests.get(
        "https://fosps.gravitatehealth.eu/epi/api/fhir/Bundle?type=document&_count=100"
    )

    for entry in preproc_bundle.json()["entry"]:
        # print(entry)
        for ii in entry["resource"]["entry"]:
            if ii["resource"]["id"] == lkid:
                return_bundle = entry["resource"]
                break
    ips_id_bundle = requests.get(
        "https://fosps.gravitatehealth.eu/ips/api/fhir/Composition?subject.identifier="
        + patientIdentifier
        + "&_elements=identifier,id"
    )
    # print(ips_id_bundle.json())
    ips_id = ips_id_bundle.json()["entry"][0]["resource"]["id"]
    # print(ips_id)
    ips = requests.get(
        "https://fosps.gravitatehealth.eu/ips/api/fhir/Composition/"
        + ips_id
        + "/$document"
    )
    return return_bundle, ips.json()


def check_extensions(composition, list_of_code_and_system):
    exts = evaluate(
        composition,
        "Composition.extension.where(url='http://hl7.eu/fhir/ig/gravitate-health/StructureDefinition/HtmlElementLink')",
        [],
    )

    for idx, ext1 in enumerate(exts):
        print(ext1)
        for ext2 in ext1["extension"]:
            if ext2["url"] == "concept":
                systemcode = ext2["valueCodeableReference"]["concept"]["coding"][0][
                    "system"
                ]
                systemcode += ext2["valueCodeableReference"]["concept"]["coding"][0][
                    "code"
                ]
                if systemcode in list_of_code_and_system:
                    print(systemcode)
                    return exts[idx]["extension"][0]["valueString"]


def add_class_to_epi(element_class, class_to_add, composition):
    for section in composition[0]["resource"]["section"]:
        for subsection in section["section"]:
            # print(subsection["text"]["div"])
            subsection["text"]["div"] = subsection["text"]["div"].replace(
                element_class, element_class + " " + class_to_add
            )
    unique_id = uuid.uuid4()
    composition[0]["fullUrl"] = (
        "http://hl7.eu/fhir/ig/gravitate-health/Composition/" + str(unique_id)
    )
    composition[0]["resource"]["id"] = str(unique_id)

    return composition


def adult_lenses(preprocessed_bundle, ips):
    """
    Adds a obscure class to the html element of the pregnancy section of the epi if the patient is an woman (age > 73)
    Current supported codes: http://snomed.info/sct#77386006
    """
    # print(ips)
    result = evaluate(ips, "Bundle.entry.where(resource.resourceType=='Patient')", [])

    # print(result)
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
    if age > 73:
        print("no children")
        print(f"Age: {age} years")

        # find pregnancy code for div html
        # print(preprocessed_bundle)
        comp = evaluate(
            preprocessed_bundle,
            "Bundle.entry.where(resource.resourceType=='Composition')",
            [],
        )
        # print(comp)

        element_class = check_extensions(
            comp[0]["resource"], ["http://snomed.info/sct77386006"]
        )
        print(element_class)
        class_to_add = "obscure"
        focused_comp = add_class_to_epi(element_class, class_to_add, comp)
        focused_bundle = copy.deepcopy(preprocessed_bundle)
        focused_bundle["entry"][0]["resource"] = focused_comp
        # print(focused_bundle)
        # Generate a unique ID
        unique_id = uuid.uuid4()
        focused_bundle["id"] = unique_id

        return focused_bundle
    else:
        return preprocessed_bundle
