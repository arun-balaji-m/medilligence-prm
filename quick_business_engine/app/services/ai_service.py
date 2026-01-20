# from groq import Groq
# from openai import OpenAI
# from quick_business_engine.app.config import get_settings
# from quick_business_engine.app.database import embedding_model, registry_collection
# from quick_business_engine.app.models.database_models import TableSearchResult
# from typing import List, Dict, Any
# import json
# import re
#
# settings = get_settings()
#
# # Initialize API clients
# groq_client = Groq(api_key=settings.GROQ_API_KEY)
# openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
#
#
# class AIService:
#     """Handles all AI operations for the Quick Business Engine"""
#
#     @staticmethod
#     def semantic_search(query: str, top_k: int = 5) -> List[TableSearchResult]:
#         """
#         Tier 1a: Semantic search using local embeddings + ChromaDB
#         """
#         # Generate query embedding locally
#         query_embedding = embedding_model.encode(query).tolist()
#
#         # Search ChromaDB
#         results = registry_collection.query(
#             query_embeddings=[query_embedding],
#             n_results=top_k,
#             include=["documents", "metadatas", "distances"]
#         )
#
#         # Format results
#         search_results = []
#         if results['documents'] and results['documents'][0]:
#             for i, doc in enumerate(results['documents'][0]):
#                 # Distance to relevance score (lower distance = higher relevance)
#                 distance = results['distances'][0][i]
#                 relevance_score = 1 / (1 + distance)  # Convert to 0-1 scale
#
#                 metadata = results['metadatas'][0][i]
#
#                 search_results.append(TableSearchResult(
#                     table_name=metadata.get('table_name', 'unknown'),
#                     relevance_score=relevance_score,
#                     schema=doc,
#                     source="semantic"
#                 ))
#
#         return search_results
#
#     @staticmethod
#     def llama_table_selector(query: str, all_schemas: List[str]) -> List[TableSearchResult]:
#         """
#         Tier 1b: Use Llama via Groq to evaluate and rank tables
#         """
#         prompt = f"""You are a database expert. Analyze the user's query and select the most relevant tables.
#
# USER QUERY: {query}
#
# AVAILABLE TABLES:
# {chr(10).join([f"{i + 1}. {schema[:500]}..." for i, schema in enumerate(all_schemas)])}
#
# TASK: Select the top 3-5 most relevant tables for this query. Consider:
# - Table description relevance
# - Column matches
# - JSONB structure relevance
# - Indexed columns for performance
#
# OUTPUT FORMAT (JSON only):
# {{
#     "selected_tables": [
#         {{
#             "table_name": "table_name",
#             "relevance_score": 0.95,
#             "reasoning": "why this table is relevant"
#         }}
#     ]
# }}
# """
#
#         try:
#             response = groq_client.chat.completions.create(
#                 model=settings.GROQ_MODEL,
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0.1,
#                 max_tokens=1000
#             )
#
#             content = response.choices[0].message.content.strip()
#
#             # Extract JSON from response
#             json_match = re.search(r'\{.*\}', content, re.DOTALL)
#             if json_match:
#                 result = json.loads(json_match.group())
#
#                 llama_results = []
#                 for table in result.get('selected_tables', []):
#                     # Find schema from all_schemas
#                     schema = next((s for s in all_schemas if table['table_name'] in s), "")
#
#                     llama_results.append(TableSearchResult(
#                         table_name=table['table_name'],
#                         relevance_score=table.get('relevance_score', 0.5),
#                         schema=schema,
#                         source="llama"
#                     ))
#
#                 return llama_results
#         except Exception as e:
#             print(f"Llama selection error: {e}")
#             return []
#
#     @staticmethod
#     def merge_and_rank_tables(semantic_results: List[TableSearchResult],
#                               llama_results: List[TableSearchResult]) -> List[Dict[str, Any]]:
#         """
#         Combine results from semantic search and Llama, return top 3
#         """
#         # Create a scoring system
#         table_scores = {}
#
#         # Add semantic search results (weight: 0.4)
#         for result in semantic_results:
#             if result.table_name not in table_scores:
#                 table_scores[result.table_name] = {
#                     'schema': result.schema,
#                     'score': 0,
#                     'sources': []
#                 }
#             table_scores[result.table_name]['score'] += result.relevance_score * 0.4
#             table_scores[result.table_name]['sources'].append('semantic')
#
#         # Add Llama results (weight: 0.6 - trust Llama's reasoning more)
#         for result in llama_results:
#             if result.table_name not in table_scores:
#                 table_scores[result.table_name] = {
#                     'schema': result.schema,
#                     'score': 0,
#                     'sources': []
#                 }
#             table_scores[result.table_name]['score'] += result.relevance_score * 0.6
#             table_scores[result.table_name]['sources'].append('llama')
#
#         # Sort by combined score
#         ranked_tables = sorted(
#             table_scores.items(),
#             key=lambda x: x[1]['score'],
#             reverse=True
#         )[:3]  # Top 3
#
#         # Format output
#         top_tables = []
#         for table_name, data in ranked_tables:
#             top_tables.append({
#                 'table_name': table_name,
#                 'schema': data['schema'],
#                 'combined_score': data['score'],
#                 'sources': list(set(data['sources']))  # Unique sources
#             })
#
#         return top_tables
#
#     @staticmethod
#     def generate_sql_query(user_query: str, top_tables: List[Dict[str, Any]]) -> str:
#         """
#         Tier 2: Use OpenAI to generate final SQL query
#         """
#         # Format table schemas for prompt
#         schemas_text = "\n\n".join([
#             f"TABLE: {t['table_name']}\n{t['schema']}"
#             for t in top_tables
#         ])
#
#         prompt = f"""You are a PostgreSQL expert. Generate a SELECT query based on the user's request.
#
# USER REQUEST: {user_query}
#
# AVAILABLE TABLES (use ONLY these):
# {schemas_text}
#
# CRITICAL REQUIREMENTS:
# 1. Generate ONLY SELECT queries (no INSERT, UPDATE, DELETE, DROP, etc.)
# 2. Use proper PostgreSQL syntax
# 3. For JSONB columns:
#    - Use -> for object navigation: data->'field'
#    - Use ->> for text extraction: data->>'field'
#    - Use @> for containment: data @> '{{"key": "value"}}'
#    - For nested: data->'parent'->'child'->>'field'
# 4. Utilize indexed columns in WHERE clauses when possible
# 5. Use proper JOIN syntax if multiple tables needed
# 6. Do NOT include LIMIT clause (handled automatically)
# 7. Return valid column names only
#
# OUTPUT: Return ONLY the SQL query, nothing else. No markdown, no explanations.
#
# EXAMPLE:
# User: "Show patients born after 1990"
# Output: SELECT * FROM patient WHERE dob > '1990-12-31'
# """
#
#         try:
#             response = openai_client.chat.completions.create(
#                 model=settings.OPENAI_MODEL,
#                 messages=[
#                     {"role": "system", "content": "You are a PostgreSQL expert. Generate only valid SELECT queries."},
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=0.1,
#                 max_tokens=500
#             )
#
#             sql_query = response.choices[0].message.content.strip()
#
#             # Clean up the query
#             sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
#
#             return sql_query
#
#         except Exception as e:
#             raise Exception(f"SQL generation failed: {str(e)}")
#
#     @staticmethod
#     def validate_sql_query(query: str) -> tuple[bool, str]:
#         """
#         Validate that the query is safe to execute
#         """
#         query_upper = query.upper().strip()
#
#         # Check for dangerous keywords
#         dangerous_keywords = [
#             'DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER',
#             'TRUNCATE', 'CREATE', 'GRANT', 'REVOKE', 'EXEC'
#         ]
#
#         for keyword in dangerous_keywords:
#             if keyword in query_upper:
#                 return False, f"Query contains forbidden keyword: {keyword}"
#
#         # Must start with SELECT
#         if not query_upper.startswith('SELECT'):
#             return False, "Query must be a SELECT statement"
#
#         # Check for SQL injection patterns
#         suspicious_patterns = [
#             r';\s*DROP',
#             r';\s*DELETE',
#             r'--\s*$',
#             r'/\*.*\*/',
#             r'UNION.*SELECT',
#             r'INTO\s+OUTFILE',
#             r'INTO\s+DUMPFILE'
#         ]
#
#         for pattern in suspicious_patterns:
#             if re.search(pattern, query_upper):
#                 return False, f"Query contains suspicious pattern: {pattern}"
#
#         return True, "Query is valid"


from groq import Groq
from openai import OpenAI
from quick_business_engine.app.config import get_settings
from quick_business_engine.app.database import embedding_model, registry_collection
from quick_business_engine.app.models.database_models import TableSearchResult
from typing import List, Dict, Any
import json
import re

settings = get_settings()

# Initialize API clients
groq_client = Groq(api_key=settings.GROQ_API_KEY)
openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)


class AIService:
    """Handles all AI operations for the Quick Business Engine"""

    @staticmethod
    def semantic_search(query: str, top_k: int = 5) -> List[TableSearchResult]:
        """
        Tier 1a: Semantic search using local embeddings + ChromaDB
        """
        # Generate query embedding locally
        query_embedding = embedding_model.encode(query).tolist()

        # Search ChromaDB
        results = registry_collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        # Format results
        search_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                # Distance to relevance score (lower distance = higher relevance)
                distance = results['distances'][0][i]
                relevance_score = 1 / (1 + distance)  # Convert to 0-1 scale

                metadata = results['metadatas'][0][i]

                search_results.append(TableSearchResult(
                    table_name=metadata.get('table_name', 'unknown'),
                    relevance_score=relevance_score,
                    schema=doc,
                    source="semantic"
                ))

        return search_results

    @staticmethod
    def llama_table_selector(query: str, all_schemas: List[str]) -> List[TableSearchResult]:
        """
        Tier 1b: Use Llama via Groq to evaluate and rank tables
        """
        prompt = f"""You are a database expert. Analyze the user's query and select the most relevant tables.

        USER QUERY: {query}

        AVAILABLE TABLES:
        {chr(10).join([f"{i + 1}. {schema[:500]}..." for i, schema in enumerate(all_schemas)])}

        TASK: Select the top 3-5 most relevant tables for this query. Consider:
        - Table description relevance
        - Column matches
        - JSONB structure relevance
        - Indexed columns for performance

        OUTPUT FORMAT (JSON only):
        {{
            "selected_tables": [
                {{
                    "table_name": "table_name",
                    "relevance_score": 0.95,
                    "reasoning": "why this table is relevant"
                }}
            ]
        }}
        """

        try:
            response = groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )

            content = response.choices[0].message.content.strip()

            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())

                llama_results = []
                for table in result.get('selected_tables', []):
                    # Find schema from all_schemas
                    schema = next((s for s in all_schemas if table['table_name'] in s), "")

                    llama_results.append(TableSearchResult(
                        table_name=table['table_name'],
                        relevance_score=table.get('relevance_score', 0.5),
                        schema=schema,
                        source="llama"
                    ))

                return llama_results
        except Exception as e:
            print(f"Llama selection error: {e}")
            return []

    @staticmethod
    def merge_and_rank_tables(semantic_results: List[TableSearchResult],
                              llama_results: List[TableSearchResult]) -> List[Dict[str, Any]]:
        """
        Combine results from semantic search and Llama, return top 3
        """
        # Create a scoring system
        table_scores = {}

        # Add semantic search results (weight: 0.4)
        for result in semantic_results:
            if result.table_name not in table_scores:
                table_scores[result.table_name] = {
                    'schema': result.schema,
                    'score': 0,
                    'sources': []
                }
            table_scores[result.table_name]['score'] += result.relevance_score * 0.4
            table_scores[result.table_name]['sources'].append('semantic')

        # Add Llama results (weight: 0.6 - trust Llama's reasoning more)
        for result in llama_results:
            if result.table_name not in table_scores:
                table_scores[result.table_name] = {
                    'schema': result.schema,
                    'score': 0,
                    'sources': []
                }
            table_scores[result.table_name]['score'] += result.relevance_score * 0.6
            table_scores[result.table_name]['sources'].append('llama')

        # Sort by combined score
        ranked_tables = sorted(
            table_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )[:3]  # Top 3

        # Format output
        top_tables = []
        for table_name, data in ranked_tables:
            top_tables.append({
                'table_name': table_name,
                'schema': data['schema'],
                'combined_score': data['score'],
                'sources': list(set(data['sources']))  # Unique sources
            })

        return top_tables

    @staticmethod
    def generate_sql_query(user_query: str, top_tables: List[Dict[str, Any]]) -> str:
        """
        Tier 2: Use OpenAI to generate final SQL query
        """
        # Format table schemas for prompt
        schemas_text = "\n\n".join([
            f"TABLE: {t['table_name']}\n{t['schema']}"
            for t in top_tables
        ])

        prompt = f"""You are a PostgreSQL expert. Generate a SELECT query based on the user's request.

        USER REQUEST: {user_query}

        AVAILABLE TABLES (use ONLY these):
        {schemas_text}

        CRITICAL REQUIREMENTS:
        1. Generate ONLY SELECT queries (no INSERT, UPDATE, DELETE, DROP, etc.)
        2. Use proper PostgreSQL syntax
        3. For JSONB columns - ALWAYS expand them into separate columns:
           - WRONG: SELECT * FROM table
           - RIGHT: SELECT id, data->>'field1' as field1, data->>'field2' as field2, data->'nested'->>'field3' as field3 FROM table
           - Extract ALL relevant JSONB fields as separate columns with meaningful aliases
           - Use ->> for text values, -> for nested objects
        4. NEVER use SELECT * - always specify columns explicitly
        5. For nested JSONB: data->'parent'->'child'->>'field' as descriptive_name
        6. Utilize indexed columns in WHERE clauses when possible
        7. Use proper JOIN syntax if multiple tables needed
        8. Do NOT include LIMIT clause (handled automatically)

        EXAMPLE:
        User: "Show patients born after 1990"
        BAD: SELECT * FROM patient WHERE (data->>'birthDate')::date > '1990-12-31'
        GOOD: SELECT id, data->>'mrn' as mrn, data->>'fullName' as full_name, data->>'birthDate' as birth_date, data->>'gender' as gender, data->'address'->>'city' as city FROM patient WHERE (data->>'birthDate')::date > '1990-12-31'

        OUTPUT: Return ONLY the SQL query, nothing else. No markdown, no explanations.
        """

        try:
            response = openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system",
                     "content": "You are a PostgreSQL expert. Always expand JSONB columns into separate columns. Never use SELECT *."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )

            sql_query = response.choices[0].message.content.strip()

            # Clean up the query
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()

            return sql_query

        except Exception as e:
            raise Exception(f"SQL generation failed: {str(e)}")

    @staticmethod
    def validate_sql_query(query: str) -> tuple[bool, str]:
        """
        Validate that the query is safe to execute
        """
        if not query:
            return False, "Empty query"

        query_stripped = query.strip()
        query_upper = query_stripped.upper()

        # Must start with SELECT
        if not query_upper.startswith("SELECT"):
            return False, "Query must be a SELECT statement"

        # Block multiple statements (semicolon in the middle)
        if ";" in query_stripped[:-1]:
            return False, "Multiple SQL statements are not allowed"

        # Dangerous SQL keywords (DDL / DML)
        dangerous_keywords = [
            "DROP", "DELETE", "INSERT", "UPDATE", "ALTER",
            "TRUNCATE", "CREATE", "GRANT", "REVOKE", "EXEC"
        ]

        for keyword in dangerous_keywords:
            # Match whole words only
            if re.search(rf"\b{keyword}\b", query_upper):
                return False, f"Query contains forbidden keyword: {keyword}"

        # SQL injection / abuse patterns
        suspicious_patterns = [
            r"--",  # SQL comment
            r"/\*.*?\*/",  # Block comments
            r"\bUNION\b\s+\bSELECT\b",
            r"\bINTO\b\s+\bOUTFILE\b",
            r"\bINTO\b\s+\bDUMPFILE\b"
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, query_upper, re.DOTALL):
                return False, f"Query contains suspicious pattern: {pattern}"

        return True, "Query is valid"