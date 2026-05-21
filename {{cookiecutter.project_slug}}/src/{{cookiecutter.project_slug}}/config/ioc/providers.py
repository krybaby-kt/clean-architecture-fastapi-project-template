from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

{% if cookiecutter.use_broker == "kafka" %}
from faststream.kafka import KafkaBroker as _BrokerType
{% elif cookiecutter.use_broker == "rabbitmq" %}
from faststream.rabbit import RabbitBroker as _BrokerType
{% elif cookiecutter.use_broker == "nats" %}
from faststream.nats import NatsBroker as _BrokerType
{% endif %}

{% if cookiecutter.use_cache in ["redis", "keydb", "dragonfly"] %}
import redis.asyncio as redis
{% endif %}

from {{cookiecutter.project_slug}}.application.interfaces.cache import CacheProtocol
from {{cookiecutter.project_slug}}.application.interfaces.http_clients import (
    ExternalMuseumAPIProtocol,
    PublicCatalogAPIProtocol,
)
from {{cookiecutter.project_slug}}.application.interfaces.mappers import DtoEntityMapperProtocol
from {{cookiecutter.project_slug}}.application.interfaces.message_broker import MessageBrokerPublisherProtocol
from {{cookiecutter.project_slug}}.application.interfaces.repositories import ArtifactRepositoryProtocol
from {{cookiecutter.project_slug}}.application.interfaces.serialization import SerializationMapperProtocol
from {{cookiecutter.project_slug}}.application.interfaces.uow import UnitOfWorkProtocol
from {{cookiecutter.project_slug}}.application.mappers import ArtifactMapper
from {{cookiecutter.project_slug}}.application.use_cases.fetch_artifact_from_museum_api import (
    FetchArtifactFromMuseumAPIUseCase,
)
from {{cookiecutter.project_slug}}.application.use_cases.process_artifact import ProcessArtifactUseCase
from {{cookiecutter.project_slug}}.application.use_cases.get_artifact_from_cache import (
    GetArtifactFromCacheUseCase,
)
from {{cookiecutter.project_slug}}.application.use_cases.get_artifact_from_repo import (
    GetArtifactFromRepoUseCase,
)
from {{cookiecutter.project_slug}}.application.use_cases.publish_artifact_to_broker import (
    PublishArtifactToBrokerUseCase,
)
from {{cookiecutter.project_slug}}.application.use_cases.publish_artifact_to_catalog import (
    PublishArtifactToCatalogUseCase,
)
from {{cookiecutter.project_slug}}.application.use_cases.save_artifact_to_cache import (
    SaveArtifactToCacheUseCase,
)
from {{cookiecutter.project_slug}}.application.use_cases.save_artifact_to_repo import (
    SaveArtifactToRepoUseCase,
)
from {{cookiecutter.project_slug}}.config.base import Settings
from {{cookiecutter.project_slug}}.infrastructures.broker.publisher import MessageBrokerPublisher
from {{cookiecutter.project_slug}}.infrastructures.cache.redis_client import CacheClient
from {{cookiecutter.project_slug}}.infrastructures.db.mappers.artifact_db_mapper import ArtifactDBMapper
from {{cookiecutter.project_slug}}.infrastructures.db.repositories.artifact import ArtifactRepositorySQLAlchemy
from {{cookiecutter.project_slug}}.infrastructures.db.session import create_engine, get_session_factory
from {{cookiecutter.project_slug}}.infrastructures.db.uow import UnitOfWorkSQLAlchemy
from {{cookiecutter.project_slug}}.infrastructures.http.clients import (
    ExternalMuseumAPIClient,
    PublicCatalogAPIClient,
)
from {{cookiecutter.project_slug}}.infrastructures.mappers.artifact import InfrastructureArtifactMapper
from {{cookiecutter.project_slug}}.presentation.api.rest.v1.mappers.artifact_mapper import ArtifactPresentationMapper


class SettingsProvider(Provider):
    """Provides application settings."""

    @provide(scope=Scope.APP)
    def get_settings(self) -> Settings:
        return Settings()


class DatabaseProvider(Provider):
    """Provides database session factory and per-request sessions."""

    @provide(scope=Scope.APP)
    async def get_session_factory(
        self, settings: Settings
    ) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
        engine = create_engine(str(settings.database_url), is_echo=settings.debug)
        session_factory = get_session_factory(engine)
        try:
            yield session_factory
        finally:
            await engine.dispose()

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterator[AsyncSession]:
        async with factory() as session:
            yield session


class HTTPClientProvider(Provider):
    """Provides an asynchronous HTTP client."""

    @provide(scope=Scope.APP)
    async def get_http_client(self, settings: Settings) -> AsyncIterator[AsyncClient]:
        client = AsyncClient(timeout=settings.http_timeout)
        try:
            yield client
        finally:
            await client.aclose()


{% if cookiecutter.use_broker != "none" %}
class BrokerProvider(Provider):
    """Provides the message broker connection."""

    @provide(scope=Scope.APP)
    async def get_broker(self, settings: Settings) -> AsyncIterator[_BrokerType]:
        broker = _BrokerType(settings.broker_url)
        try:
            yield broker
        finally:
            await broker.stop()
{% endif %}


class RepositoryProvider(Provider):
    """Provides repository implementations."""

    @provide(scope=Scope.REQUEST)
    def get_artifact_repository(
        self, session: AsyncSession, db_mapper: ArtifactDBMapper
    ) -> ArtifactRepositoryProtocol:
        return ArtifactRepositorySQLAlchemy(session=session, mapper=db_mapper)


class UnitOfWorkProvider(Provider):
    """Provides Unit of Work implementations."""

    @provide(scope=Scope.REQUEST)
    def get_unit_of_work(
        self,
        session: AsyncSession,
        repository: ArtifactRepositoryProtocol,
    ) -> UnitOfWorkProtocol:
        return UnitOfWorkSQLAlchemy(session=session, repository=repository)


class ServiceProvider(Provider):
    """Provides service clients for external integrations."""

    @provide(scope=Scope.REQUEST)
    def get_external_museum_api_client(
        self,
        client: AsyncClient,
        settings: Settings,
        infrastructure_mapper: SerializationMapperProtocol,
    ) -> ExternalMuseumAPIProtocol:
        return ExternalMuseumAPIClient(
            base_url=settings.museum_api_base,
            client=client,
            mapper=infrastructure_mapper,
        )

    @provide(scope=Scope.REQUEST)
    def get_public_catalog_api_client(
        self,
        client: AsyncClient,
        settings: Settings,
        infrastructure_mapper: SerializationMapperProtocol,
    ) -> PublicCatalogAPIProtocol:
        return PublicCatalogAPIClient(
            base_url=settings.catalog_api_base_url,
            client=client,
            mapper=infrastructure_mapper,
        )

{% if cookiecutter.use_broker != "none" %}
    @provide(scope=Scope.REQUEST)
    def get_message_broker(
        self,
        broker: _BrokerType,
        infrastructure_mapper: SerializationMapperProtocol,
    ) -> MessageBrokerPublisherProtocol:
        return MessageBrokerPublisher(
            broker=broker,
            mapper=infrastructure_mapper,
        )
{% else %}
    @provide(scope=Scope.REQUEST)
    def get_message_broker(self) -> MessageBrokerPublisherProtocol:
        return MessageBrokerPublisher()
{% endif %}


class MapperProvider(Provider):
    """Provides various mapper implementations for different layers."""

    @provide(scope=Scope.APP)
    def get_artifact_mapper(self) -> DtoEntityMapperProtocol:
        return ArtifactMapper()

    @provide(scope=Scope.REQUEST)
    def get_db_mapper(self) -> ArtifactDBMapper:
        return ArtifactDBMapper()

    @provide(scope=Scope.REQUEST)
    def get_infrastructure_artifact_mapper(self) -> SerializationMapperProtocol:
        return InfrastructureArtifactMapper()

    @provide(scope=Scope.REQUEST)
    def get_presentation_artifact_mapper(self) -> ArtifactPresentationMapper:
        return ArtifactPresentationMapper()


class CacheProvider(Provider):
    """Provides the cache client."""

    @provide(scope=Scope.APP)
    async def get_cache_service(
        self, settings: Settings
    ) -> AsyncIterator[CacheProtocol]:
{% if cookiecutter.use_cache in ["redis", "keydb", "dragonfly"] %}
        redis_client = redis.from_url(
            str(settings.redis_url),
            encoding="utf-8",
            decode_responses=True,
            health_check_interval=30,
            max_connections=10,
            retry_on_timeout=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        cache_service = CacheClient(
            client=redis_client, ttl=settings.redis_cache_ttl
        )
        try:
            yield cache_service
        finally:
            await cache_service.close()
{% else %}
        cache_service = CacheClient()
        try:
            yield cache_service
        finally:
            await cache_service.close()
{% endif %}


class UseCaseProvider(Provider):
    """Provides application use cases."""

    @provide(scope=Scope.REQUEST)
    def get_get_artifact_from_cache_use_case(
        self,
        cache_client: CacheProtocol,
        serialization_mapper: SerializationMapperProtocol,
    ) -> GetArtifactFromCacheUseCase:
        return GetArtifactFromCacheUseCase(
            cache_client=cache_client, serialization_mapper=serialization_mapper
        )

    @provide(scope=Scope.REQUEST)
    def get_get_artifact_from_repo_use_case(
        self, uow: UnitOfWorkProtocol, artifact_mapper: DtoEntityMapperProtocol
    ) -> GetArtifactFromRepoUseCase:
        return GetArtifactFromRepoUseCase(uow=uow, artifact_mapper=artifact_mapper)

    @provide(scope=Scope.REQUEST)
    def get_fetch_artifact_from_museum_api_use_case(
        self,
        museum_api_client: ExternalMuseumAPIProtocol,
    ) -> FetchArtifactFromMuseumAPIUseCase:
        return FetchArtifactFromMuseumAPIUseCase(museum_api_client=museum_api_client)

    @provide(scope=Scope.REQUEST)
    def get_save_artifact_to_repo_use_case(
        self, uow: UnitOfWorkProtocol, artifact_mapper: DtoEntityMapperProtocol
    ) -> SaveArtifactToRepoUseCase:
        return SaveArtifactToRepoUseCase(uow=uow, artifact_mapper=artifact_mapper)

    @provide(scope=Scope.REQUEST)
    def get_save_artifact_to_cache_use_case(
        self,
        cache_client: CacheProtocol,
        serialization_mapper: SerializationMapperProtocol,
    ) -> SaveArtifactToCacheUseCase:
        return SaveArtifactToCacheUseCase(
            cache_client=cache_client, serialization_mapper=serialization_mapper
        )

    @provide(scope=Scope.REQUEST)
    def get_publish_artifact_to_broker_use_case(
        self,
        message_broker: MessageBrokerPublisherProtocol,
        artifact_mapper: DtoEntityMapperProtocol,
    ) -> PublishArtifactToBrokerUseCase:
        return PublishArtifactToBrokerUseCase(
            message_broker=message_broker, artifact_mapper=artifact_mapper
        )

    @provide(scope=Scope.REQUEST)
    def get_publish_artifact_to_catalog_use_case(
        self,
        catalog_api_client: PublicCatalogAPIProtocol,
        artifact_mapper: DtoEntityMapperProtocol,
    ) -> PublishArtifactToCatalogUseCase:
        return PublishArtifactToCatalogUseCase(
            catalog_api_client=catalog_api_client, artifact_mapper=artifact_mapper
        )

    @provide(scope=Scope.REQUEST)
    def get_register_artifact_use_case(
        self,
        get_artifact_from_cache_use_case: GetArtifactFromCacheUseCase,
        get_artifact_from_repo_use_case: GetArtifactFromRepoUseCase,
        fetch_artifact_from_museum_api_use_case: FetchArtifactFromMuseumAPIUseCase,
        save_artifact_to_repo_use_case: SaveArtifactToRepoUseCase,
        save_artifact_to_cache_use_case: SaveArtifactToCacheUseCase,
        publish_artifact_to_broker_use_case: PublishArtifactToBrokerUseCase,
        publish_artifact_to_catalog_use_case: PublishArtifactToCatalogUseCase,
    ) -> ProcessArtifactUseCase:
        return ProcessArtifactUseCase(
            get_artifact_from_cache_use_case=get_artifact_from_cache_use_case,
            get_artifact_from_repo_use_case=get_artifact_from_repo_use_case,
            fetch_artifact_from_museum_api_use_case=fetch_artifact_from_museum_api_use_case,
            save_artifact_to_repo_use_case=save_artifact_to_repo_use_case,
            save_artifact_to_cache_use_case=save_artifact_to_cache_use_case,
            publish_artifact_to_broker_use_case=publish_artifact_to_broker_use_case,
            publish_artifact_to_catalog_use_case=publish_artifact_to_catalog_use_case,
        )
