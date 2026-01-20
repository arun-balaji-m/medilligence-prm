"""
Automatic registry initialization on startup
Add your table schemas here - they will be loaded automatically when the service starts
"""

from quick_business_engine.app.database import registry_collection, embedding_model
from typing import Dict, List

# ==========================================
# DEFINE YOUR TABLE SCHEMAS HERE
# ==========================================

TABLE_SCHEMAS = [
{
    "table_name": "patient",
    "description": "Stores patient master registry including demographic details, contact information, registration metadata, and organizational context in JSONB format",
    "database_name": "public",
    "columns": [
        {
            "name": "id",
            "type": "BIGINT",
            "description": "Unique patient identifier (Primary Key, auto-generated)"
        },
        {
            "name": "data",
            "type": "JSONB",
            "description": "Stores core patient demographic and contact information"
        },
        {
            "name": "other",
            "type": "JSONB",
            "description": "Stores registration, administrative, and organizational metadata"
        },
        {
            "name": "created_at",
            "type": "TIMESTAMP WITH TIME ZONE",
            "description": "Record creation timestamp"
        }
    ],
    "jsonb_columns": [
        {
            "column_name": "data",
            "structure": {
                "id": "integer - Internal patient reference ID",
                "mrn": "string - Medical Record Number",
                "fullName": "string - Patient full name",
                "gender": "string - Patient gender",
                "birthDate": "string (YYYY-MM-DD) - Date of birth",
                "address": [
                    {
                        "houseNo": "string - House or building number",
                        "city": "string - City name",
                        "district": "string - District name",
                        "state": "string - State name",
                        "country": "string - Country name",
                        "pincode": "string - Postal/ZIP code",
                        "type": "string - Address type (e.g., Correspondence Address)",
                        "mobileNo": "string - Contact mobile number",
                        "mobilePrefix": "string - Country dialing code"
                    }
                ],
                "telecom": [
                    {
                        "system": "string - Communication system (phone/email)",
                        "value": "string - Contact value",
                        "use": "string - Usage type (mobile/home/work)",
                        "rank": "integer - Priority ranking"
                    }
                ]
            },
            "example_queries": [
                "data->>'fullName' - Get patient full name",
                "data->>'mrn' - Get medical record number",
                "data->>'gender' - Get gender",
                "data->'address'->0->>'city' - Get primary city",
                "data->'telecom'->0->>'value' - Get primary contact number",
                "jsonb_array_length(data->'address') - Count addresses"
            ]
        },
        {
            "column_name": "other",
            "structure": {
                "tempNumber": "string - Temporary patient number",
                "displayName": "string - Display name for patient",
                "displayNameOther": "string - Alternate display name",
                "mobilePrefix": "string - Country dialing code",
                "registeredOn": "string (ISO timestamp) - Registration datetime",
                "regChargesCollected": "boolean - Whether registration charges were collected",
                "patientType": {
                    "code": "string - Patient type code",
                    "display": "string - Patient type description"
                },
                "registrationUnit": {
                    "id": "integer - Unit ID",
                    "code": "string - Unit code",
                    "name": "string - Unit name",
                    "shortName": "string - Unit short name",
                    "active": "boolean - Unit active status",
                    "partOf": {
                        "id": "integer - Parent organization ID",
                        "code": "string - Parent organization code",
                        "name": "string - Parent organization name",
                        "active": "boolean - Parent organization active status"
                    }
                }
            },
            "example_queries": [
                "other->>'tempNumber' - Get temporary patient number",
                "other->>'displayName' - Get display name",
                "other->'patientType'->>'display' - Get patient type description",
                "other->'registrationUnit'->>'name' - Get registration unit name",
                "other->'registrationUnit'->'partOf'->>'name' - Get parent organization name",
                "other->>'regChargesCollected' - Check if charges were collected"
            ]
        }
    ],
    "indexed_columns": ["id", "created_at"],
    "row_count_estimate": 100000
},
{
    "table_name": "vital_sign_record",
    "description": "Stores patient vital sign observations including patient snapshot details, recorded vital values, and measurement metadata",
    "database_name": "public",
    "columns": [
        {
            "name": "id",
            "type": "BIGINT",
            "description": "Unique vital sign record identifier (Primary Key, auto-generated)"
        },
        {
            "name": "patient",
            "type": "JSONB",
            "description": "Stores snapshot of patient demographic and administrative information at the time of vital recording"
        },
        {
            "name": "concept",
            "type": "JSONB",
            "description": "Stores vital sign measurement details and observation metadata"
        },
        {
            "name": "active",
            "type": "BOOLEAN",
            "description": "Indicates whether the vital sign record is currently active"
        },
        {
            "name": "created_at",
            "type": "TIMESTAMP WITH TIME ZONE",
            "description": "Record creation timestamp"
        }
    ],
    "jsonb_columns": [
        {
            "column_name": "patient",
            "structure": {
                "id": "integer - Internal patient reference ID",
                "mrn": "string - Medical Record Number",
                "tempNumber": "string - Temporary patient number",
                "fullName": "string - Patient full name",
                "displayName": "string - Display name",
                "gender": "string - Patient gender",
                "age": "integer - Patient age at time of recording",
                "birthDate": "string (ISO timestamp) - Date of birth",
                "bloodGroup": "string/null - Blood group",
                "mobileNumber": "string - Primary contact number",
                "confidential": "boolean/null - Confidential patient flag",
                "patientType": {
                    "code": "string - Patient type code",
                    "display": "string - Patient type description"
                }
            },
            "example_queries": [
                "patient->>'fullName' - Get patient name",
                "patient->>'mrn' - Get medical record number",
                "patient->>'gender' - Get gender",
                "patient->>'age' - Get patient age",
                "patient->'patientType'->>'display' - Get patient type",
                "patient->>'mobileNumber' - Get contact number"
            ]
        },
        {
            "column_name": "concept",
            "structure": {
                "vitalSign": {
                    "name": "string - Vital sign name (e.g., Pulse, BP, Temperature)",
                    "value": "string/number - Measured value",
                    "unit": "string - Measurement unit",
                    "recordedTime": "string (ISO timestamp) - Time of measurement"
                }
            },
            "example_queries": [
                "concept->'vitalSign'->>'name' - Get vital sign name",
                "concept->'vitalSign'->>'value' - Get vital value",
                "concept->'vitalSign'->>'unit' - Get unit of measure",
                "concept->'vitalSign'->>'recordedTime' - Get recorded timestamp",
                "concept->'vitalSign' @> '{\"name\": \"Pulse\"}' - Check if vital is Pulse"
            ]
        }
    ],
    "indexed_columns": ["id", "created_at", "active"],
    "row_count_estimate": 200000
},
{
    "table_name": "consultation",
    "description": "Stores patient consultation encounters including patient snapshot details, visit metadata, consulting clinician, department, and encounter classification",
    "database_name": "public",
    "columns": [
        {
            "name": "id",
            "type": "BIGINT",
            "description": "Unique consultation record identifier (Primary Key, auto-generated)"
        },
        {
            "name": "patient",
            "type": "JSONB",
            "description": "Stores snapshot of patient demographic and administrative information at the time of consultation"
        },
        {
            "name": "document",
            "type": "JSONB",
            "description": "Stores consultation document metadata including unit, consultant, department, visit timing, and encounter classification"
        },
        {
            "name": "active",
            "type": "BOOLEAN",
            "description": "Indicates whether the consultation record is currently active"
        },
        {
            "name": "created_at",
            "type": "TIMESTAMP WITH TIME ZONE",
            "description": "Record creation timestamp"
        }
    ],
    "jsonb_columns": [
        {
            "column_name": "patient",
            "structure": {
                "id": "integer - Internal patient reference ID",
                "mrn": "string - Medical Record Number",
                "tempNumber": "string - Temporary patient number",
                "fullName": "string - Patient full name",
                "displayName": "string - Display name",
                "gender": "string - Patient gender",
                "age": "integer - Patient age at time of consultation",
                "birthDate": "string (ISO timestamp) - Date of birth",
                "bloodGroup": "string/null - Blood group",
                "mobileNumber": "string - Primary contact number",
                "confidential": "boolean/null - Confidential patient flag",
                "patientType": {
                    "code": "string - Patient type code",
                    "display": "string - Patient type description"
                }
            },
            "example_queries": [
                "patient->>'fullName' - Get patient name",
                "patient->>'mrn' - Get medical record number",
                "patient->>'gender' - Get gender",
                "patient->>'age' - Get patient age",
                "patient->'patientType'->>'display' - Get patient type",
                "patient->>'mobileNumber' - Get contact number"
            ]
        },
        {
            "column_name": "document",
            "structure": {
                "documentNumber": "string - Consultation/encounter document number",
                "startDate": "string (ISO timestamp) - Consultation start time",
                "visitDate": "string (ISO timestamp) - Visit/encounter date and time",
                "unit": {
                    "id": "integer - Healthcare unit ID",
                    "code": "string - Unit code",
                    "name": "string - Unit name"
                },
                "consultant": {
                    "id": "integer - Consultant ID",
                    "code": "string - Consultant code",
                    "name": "string - Consultant name",
                    "login": "string - Consultant login ID",
                    "employeeNo": "string - Consultant employee number",
                    "displayName": "string - Consultant display name"
                },
                "department": {
                    "id": "integer - Department ID",
                    "code": "string - Department code",
                    "name": "string - Department name"
                },
                "encounterClass": {
                    "id": "integer - Encounter class ID",
                    "code": "string - Encounter class code (e.g., AMB)",
                    "display": "string - Encounter type display (e.g., OP)"
                }
            },
            "example_queries": [
                "document->>'documentNumber' - Get consultation document number",
                "document->'consultant'->>'name' - Get consultant name",
                "document->'department'->>'name' - Get department name",
                "document->'unit'->>'name' - Get unit name",
                "document->'encounterClass'->>'display' - Get encounter type",
                "document->>'visitDate' - Get visit date",
                "document->'consultant' @> '{\"name\": \"Amitabh Sharma\"}' - Filter by consultant"
            ]
        }
    ],
    "indexed_columns": ["id", "created_at", "active"],
    "row_count_estimate": 150000
},
{
    "table_name": "active_medication",
    "description": "Stores active and dispensed medication records linked to patient consultations, including medication details, dosage schedule, and prescription metadata",
    "database_name": "public",
    "columns": [
        {
            "name": "id",
            "type": "BIGINT",
            "description": "Unique active medication record identifier (Primary Key, auto-generated)"
        },
        {
            "name": "patient",
            "type": "JSONB",
            "description": "Stores snapshot of patient demographic and administrative information at the time of medication order"
        },
        {
            "name": "consultation_id",
            "type": "BIGINT",
            "description": "Foreign key reference to consultation.id"
        },
        {
            "name": "document",
            "type": "JSONB",
            "description": "Stores medication order, prescription, and dispensing details"
        },
        {
            "name": "active",
            "type": "BOOLEAN",
            "description": "Indicates whether the medication record is currently active"
        },
        {
            "name": "created_at",
            "type": "TIMESTAMP WITH TIME ZONE",
            "description": "Record creation timestamp"
        }
    ],
    "jsonb_columns": [
        {
            "column_name": "patient",
            "structure": {
                "id": "integer - Internal patient reference ID",
                "mrn": "string - Medical Record Number",
                "tempNumber": "string - Temporary patient number",
                "fullName": "string - Patient full name",
                "displayName": "string - Display name",
                "gender": "string - Patient gender",
                "age": "integer - Patient age at time of prescription",
                "birthDate": "string (ISO timestamp) - Date of birth",
                "bloodGroup": "string/null - Blood group",
                "mobileNumber": "string - Primary contact number",
                "confidential": "boolean/null - Confidential patient flag",
                "patientType": {
                    "code": "string - Patient type code",
                    "display": "string - Patient type description"
                }
            },
            "example_queries": [
                "patient->>'fullName' - Get patient name",
                "patient->>'mrn' - Get medical record number",
                "patient->>'age' - Get patient age",
                "patient->'patientType'->>'display' - Get patient type",
                "patient->>'mobileNumber' - Get contact number"
            ]
        },
        {
            "column_name": "document",
            "structure": {
                "activeMedication": {
                    "status": "string - Medication status (e.g., DISPENSED, ACTIVE, STOPPED)",
                    "startDate": "string (YYYY-MM-DD) - Medication start date",
                    "orderedDate": "string (ISO timestamp) - Date and time medication was ordered",
                    "prescriptionDate": "string/null (ISO timestamp) - Prescription date",
                    "documentNumber": "string - Medication document/order number",
                    "requestLineId": "integer - Request line reference ID",
                    "medicationOrderId": "integer - Medication order ID",
                    "medicationRequestId": "string - External medication request identifier",
                    "noOfRepeatAllowed": "integer - Number of allowed repeats/refills",
                    "foodInstruction": "string/null - Food-related instructions",
                    "patientInstruction": "string - Instructions for patient",
                    "daywiseDosage": {
                        "morning": "string/null - Morning dosage",
                        "afternoon": "string/null - Afternoon dosage",
                        "evening": "string/null - Evening dosage",
                        "night": "string/null - Night dosage"
                    },
                    "medication": {
                        "id": "integer - Medication ID",
                        "code": "string - Medication code",
                        "name": "string - Medication name",
                        "brand": "boolean - Brand indicator"
                    }
                }
            },
            "example_queries": [
                "document->'activeMedication'->>'status' - Get medication status",
                "document->'activeMedication'->'medication'->>'name' - Get medication name",
                "document->'activeMedication'->>'startDate' - Get medication start date",
                "document->'activeMedication'->>'documentNumber' - Get order document number",
                "document->'activeMedication'->>'medicationRequestId' - Get medication request ID",
                "document->'activeMedication'->'daywiseDosage'->>'morning' - Get morning dosage",
                "document->'activeMedication' @> '{\"activeMedication\": {\"status\": \"DISPENSED\"}}' - Filter by dispensed medications"
            ]
        }
    ],
    "indexed_columns": ["id", "consultation_id", "created_at", "active"],
    "row_count_estimate": 250000
}
]


# ==========================================
# REGISTRY INITIALIZATION LOGIC
# ==========================================
def _create_document_from_schema(table_schema: Dict) -> str:
    """Create a text document from table schema for embeddings"""

    # Build column descriptions
    columns_text = "\n".join([
        f"- {col['name']} ({col['type']}): {col.get('description', '')}"
        for col in table_schema['columns']
    ])

    # Build JSONB info if present
    jsonb_text = ""
    if table_schema.get('jsonb_columns'):
        jsonb_parts = []
        for jc in table_schema['jsonb_columns']:
            jsonb_parts.append(f"\nJSONB Column: {jc['column_name']}")
            jsonb_parts.append(f"Structure: {jc.get('structure', {})}")
            if jc.get('example_queries'):
                jsonb_parts.append("Example JSONB queries:")
                jsonb_parts.extend([f"  - {eq}" for eq in jc['example_queries']])
        jsonb_text = "\n".join(jsonb_parts)

    # Build example queries
    examples_text = ""
    if table_schema.get('example_queries'):
        examples_text = "\nExample Queries:\n" + "\n".join([
            f"- {eq}" for eq in table_schema['example_queries']
        ])

    document = f"""
Table: {table_schema['table_name']}
Description: {table_schema['description']}

Columns:
{columns_text}
{jsonb_text}

Indexed Columns: {', '.join(table_schema.get('indexed_columns', []))}
{examples_text}
    """.strip()

    return document


def initialize_registry() -> bool:
    """
    Initialize ChromaDB registry with table schemas on startup
    Returns True if registry was created, False if it already exists
    """
    try:
        # Check if registry already has data
        existing_count = registry_collection.count()

        if existing_count > 0:
            print(f"📋 Registry already contains {existing_count} tables")
            return False

        print(f"📊 Initializing registry with {len(TABLE_SCHEMAS)} tables...")

        # Add all tables to registry
        documents = []
        embeddings = []
        metadatas = []
        ids = []

        for table_schema in TABLE_SCHEMAS:
            # Create document text
            document = _create_document_from_schema(table_schema)
            documents.append(document)

            # Generate embedding
            embedding = embedding_model.encode(document).tolist()
            embeddings.append(embedding)

            # Create metadata
            metadata = {
                'table_name': table_schema['table_name'],
                'database': table_schema.get('database_name', 'main'),
                'has_jsonb': len(table_schema.get('jsonb_columns', [])) > 0,
                'indexed_columns': ','.join(table_schema.get('indexed_columns', []))
            }
            metadatas.append(metadata)

            # Create ID
            ids.append(f"table_{table_schema['table_name']}")

            print(f"  ✅ Prepared: {table_schema['table_name']}")

        # Batch add to ChromaDB
        registry_collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

        print(f"✅ Successfully added {len(TABLE_SCHEMAS)} tables to registry")
        return True

    except Exception as e:
        print(f"❌ Error initializing registry: {e}")
        return False


def add_table_to_registry(table_schema: Dict) -> bool:
    """
    Add a single table to the registry (can be called at runtime)
    """
    try:
        document = _create_document_from_schema(table_schema)
        embedding = embedding_model.encode(document).tolist()

        metadata = {
            'table_name': table_schema['table_name'],
            'database': table_schema.get('database_name', 'main'),
            'has_jsonb': len(table_schema.get('jsonb_columns', [])) > 0,
            'indexed_columns': ','.join(table_schema.get('indexed_columns', []))
        }

        registry_collection.add(
            documents=[document],
            embeddings=[embedding],
            metadatas=[metadata],
            ids=[f"table_{table_schema['table_name']}"]
        )

        print(f"✅ Added table '{table_schema['table_name']}' to registry")
        return True

    except Exception as e:
        print(f"❌ Error adding table to registry: {e}")
        return False


def list_registered_tables() -> List[str]:
    """Get list of all registered table names"""
    try:
        results = registry_collection.get()
        if results and results.get('metadatas'):
            return [meta['table_name'] for meta in results['metadatas']]
        return []
    except:
        return []