from typing import Annotated, TypedDict

from fastapi import Depends
from langchain.embeddings.openai import OpenAIEmbeddings
from models.databases.supabase.supabase import SupabaseDB
from pydantic import BaseSettings
from supabase.client import Client, create_client
from vectorstore.supabase import SupabaseVectorStore


class BrainRateLimiting(BaseSettings):
    max_brain_size: int = 52428800
    max_brain_per_user: int = 5


class BrainSettings(BaseSettings):
    openai_api_key: str
    anthropic_api_key: str
    supabase_url: str
    supabase_service_key: str
    pg_database_url: str
    resend_api_key: str = "null"
    resend_email_address: str = "brain@mail.quivr.app"


class LLMSettings(BaseSettings):
    private: bool = False
    model_path: str = "./local_models/ggml-gpt4all-j-v1.3-groovy.bin"


class CommonDependencies(TypedDict):
    supabase: Client
    db: SupabaseDB
    embeddings: OpenAIEmbeddings
    documents_vector_store: SupabaseVectorStore


def get_embeddings() -> OpenAIEmbeddings:
    settings = BrainSettings()  # pyright: ignore reportPrivateUsage=none
    embeddings = OpenAIEmbeddings(
        openai_api_key=settings.openai_api_key
    )  # pyright: ignore reportPrivateUsage=none
    return embeddings


def get_documents_vector_store() -> SupabaseVectorStore:
    settings = BrainSettings()  # pyright: ignore reportPrivateUsage=none
    embeddings = get_embeddings()
    supabase_client: Client = create_client(
        settings.supabase_url, settings.supabase_service_key
    )
    documents_vector_store = SupabaseVectorStore(
        supabase_client, embeddings, table_name="vectors"
    )
    return documents_vector_store


def common_dependencies() -> CommonDependencies:
    settings = BrainSettings()  # pyright: ignore reportPrivateUsage=none
    embeddings = OpenAIEmbeddings(
        openai_api_key=settings.openai_api_key
    )  # pyright: ignore reportPrivateUsage=none
    supabase_client: Client = create_client(
        settings.supabase_url, settings.supabase_service_key
    )
    documents_vector_store = SupabaseVectorStore(
        supabase_client, embeddings, table_name="vectors"
    )

    db = None
    db = SupabaseDB(supabase_client)

    return {
        "supabase": supabase_client,
        "db": db,
        "embeddings": embeddings,
        "documents_vector_store": documents_vector_store,
    }


CommonsDep = Annotated[dict, Depends(common_dependencies)]
